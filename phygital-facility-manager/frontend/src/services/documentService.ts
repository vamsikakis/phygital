import axios from 'axios';

export interface Document {
  id: string;
  title: string;
  description?: string;
  file_path?: string;
  file_type?: string;
  file_size?: number;
  category?: string;
  tags?: string[];
  created_at: string;
  updated_at: string;
  created_by?: string;
  status?: string;
  summary?: string;
  is_public?: boolean;
}

export interface DocumentUploadResponse {
  document: Document;
  upload_url?: string;
}

class DocumentService {
  private readonly API_BASE = `${import.meta.env.VITE_API_URL || 'https://phygital-backend.onrender.com'}/api/documents`;

  /**
   * Get all documents
   */
  public async getDocuments(category?: string, tags?: string[]): Promise<Document[]> {
    try {
      let url = this.API_BASE;
      const params = new URLSearchParams();
      
      if (category) {
        params.append('category', category);
      }
      
      if (tags && tags.length > 0) {
        params.append('tags', tags.join(','));
      }
      
      if (params.toString()) {
        url += `?${params.toString()}`;
      }
      
      const response = await axios.get(url);
      return response.data.documents;
    } catch (error) {
      console.error('Error fetching documents:', error);
      throw error;
    }
  }

  /**
   * Get a single document by ID
   */
  public async getDocument(documentId: string): Promise<Document> {
    try {
      const response = await axios.get(`${this.API_BASE}/${documentId}`);
      return response.data.document;
    } catch (error) {
      console.error(`Error fetching document ${documentId}:`, error);
      throw error;
    }
  }

  /**
   * Create a new document
   */
  public async createDocument(
    title: string, 
    description: string, 
    category: string, 
    tags: string[] = [],
    file?: File
  ): Promise<DocumentUploadResponse> {
    try {
      // First create the document metadata
      const formData = new FormData();
      formData.append('title', title);
      formData.append('description', description);
      formData.append('category', category);
      
      if (tags.length > 0) {
        formData.append('tags', JSON.stringify(tags));
      }
      
      if (file) {
        formData.append('file', file);
      }
      
      const response = await axios.post(this.API_BASE, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      return response.data;
    } catch (error) {
      console.error('Error creating document:', error);
      throw error;
    }
  }

  /**
   * Update an existing document
   */
  public async updateDocument(
    documentId: string,
    updates: Partial<Document>
  ): Promise<Document> {
    try {
      const response = await axios.put(`${this.API_BASE}/${documentId}`, updates);
      return response.data.document;
    } catch (error) {
      console.error(`Error updating document ${documentId}:`, error);
      throw error;
    }
  }

  /**
   * Delete a document
   */
  public async deleteDocument(documentId: string): Promise<void> {
    try {
      await axios.delete(`${this.API_BASE}/${documentId}`);
    } catch (error) {
      console.error(`Error deleting document ${documentId}:`, error);
      throw error;
    }
  }

  /**
   * Generate a summary for a document using OpenAI
   */
  public async generateSummary(documentId: string): Promise<string> {
    try {
      const response = await axios.post(`${this.API_BASE}/${documentId}/summary`);
      return response.data.summary;
    } catch (error) {
      console.error(`Error generating summary for document ${documentId}:`, error);
      throw error;
    }
  }

  /**
   * Download a document
   */
  public async downloadDocument(documentId: string): Promise<Blob> {
    try {
      const response = await axios.get(`${this.API_BASE}/${documentId}/download`, {
        responseType: 'blob'
      });
      return response.data;
    } catch (error) {
      console.error(`Error downloading document ${documentId}:`, error);
      throw error;
    }
  }
}

export default new DocumentService();
