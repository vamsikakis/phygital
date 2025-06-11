import axios from 'axios';

export interface VerbaQueryRequest {
  query: string;
  collection?: string;
  limit?: number;
}

export interface VerbaSource {
  content: string;
  document: string;
  document_id?: string;
  metadata: {
    [key: string]: any;
  };
  score: number;
}

export interface VerbaQueryResponse {
  answer: string;
  sources: VerbaSource[];
  error?: string;
}

export interface VerbaDocument {
  id: string;
  content: string;
  metadata: {
    title?: string;
    category?: string;
    type?: string;
    uploaded_at?: string;
    file_name?: string;
    [key: string]: any;
  };
}

/**
 * Service for interacting with Verba RAG API
 */
const verbaService = {
  /**
   * Check if Verba service is available and initialized
   */
  checkStatus: async (): Promise<{initialized: boolean, error?: string}> => {
    try {
      // Use fetch API with a timeout to check connection more reliably
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 2000); // 2s timeout
      
      try {
        const fetchResponse = await fetch('http://localhost:5001/api/verba/status', {
          signal: controller.signal,
          method: 'GET',
          mode: 'cors',
        });
        
        clearTimeout(timeoutId);
        
        if (!fetchResponse.ok) {
          throw new Error(`HTTP error! status: ${fetchResponse.status}`);
        }
        
        const data = await fetchResponse.json();
        return { initialized: data.initialized || false };
      } catch (fetchError) {
        clearTimeout(timeoutId);
        throw fetchError;
      }
    } catch (error) {
      // Silent fail in development - don't spam console
      console.log('Verba service not available (backend probably not running)');
      return { initialized: false, error: 'Service unavailable' };
    }
  },

  /**
   * Get all available collections
   */
  getCollections: async (): Promise<string[]> => {
    try {
      console.log('Fetching collections from Verba...');
      const response = await fetch('http://localhost:5001/api/verba/collections', {
        method: 'GET',
        mode: 'cors',
        credentials: 'omit',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error(`HTTP error! status: ${response.status}, response: ${errorText}`);
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('Collections received:', data);
      return data.collections || [];
    } catch (error) {
      console.error('Error getting Verba collections:', error);
      return [];
    }
  },

  /**
   * Get all indexed documents metadata
   */
  getDocuments: async (collection = 'apartment_documents'): Promise<VerbaDocument[]> => {
    try {
      console.log(`Fetching documents from collection: ${collection}...`);
      const response = await fetch(`http://localhost:5001/api/verba/documents?collection=${collection}`, {
        method: 'GET',
        mode: 'cors',
        credentials: 'omit',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error(`HTTP error! status: ${response.status}, response: ${errorText}`);
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('Documents received:', data);
      return data.documents || [];
    } catch (error) {
      console.error('Error getting Verba documents:', error);
      return [];
    }
  },

  /**
   * Upload document to Verba for indexing
   */
  uploadDocument: async (formData: FormData): Promise<any> => {
    try {
      console.log('Uploading document to Verba...', formData);
      
      // Log form data contents for debugging
      console.log('Form data contents:');
      for (const pair of formData.entries()) {
        console.log(pair[0] + ': ' + (pair[0] === 'file' ? 'File object' : pair[1]));
      }
      
      const response = await fetch('http://localhost:5001/api/verba/upload', {
        method: 'POST',
        mode: 'cors',
        credentials: 'omit',
        body: formData,
        // Do not set Content-Type header for multipart/form-data with fetch
        // It will be set automatically with the correct boundary
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error(`HTTP error! status: ${response.status}, response: ${errorText}`);
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const result = await response.json();
      console.log('Upload response:', result);
      return result;
    } catch (error) {
      console.error('Error uploading document to Verba:', error);
      throw error;
    }
  },

  /**
   * Query documents using Verba RAG
   */
  queryDocuments: async (queryRequest: VerbaQueryRequest): Promise<VerbaQueryResponse> => {
    try {
      const response = await fetch('http://localhost:5001/api/verba/query', {
        method: 'POST',
        mode: 'cors',
        credentials: 'omit',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify(queryRequest),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error querying Verba:', error);
      return {
        answer: '',
        sources: [],
        error: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }
};

export default verbaService;
