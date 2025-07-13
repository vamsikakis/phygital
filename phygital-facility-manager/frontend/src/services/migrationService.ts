import axios from 'axios';

export interface MigrationResult {
  weaviate_id?: string;
  openai_file_id?: string;
  file_path?: string;
  title: string;
  status: 'migrated' | 'failed';
  error?: string;
}

export interface MigrationResponse {
  message: string;
  results: MigrationResult[];
}

export interface MigrationStatus {
  status: string;
  document_counts: {
    openai_count: number;
    weaviate_count: number | string;
  };
  timestamp: string;
}

class MigrationService {
  private API_BASE = `${import.meta.env.VITE_API_URL || 'https://phygital-backend.onrender.com'}/api/migration`;

  public async migrateFromWeaviate(documents: any[]): Promise<MigrationResponse> {
    try {
      const response = await axios.post(`${this.API_BASE}/weaviate-to-openai`, documents);
      return response.data;
    } catch (error) {
      console.error('Failed to migrate from Weaviate:', error);
      throw error;
    }
  }

  public async migrateFile(file: File, metadata: { title?: string; category?: string; tags?: string[] }): Promise<MigrationResult> {
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      if (metadata.title) {
        formData.append('title', metadata.title);
      }
      
      if (metadata.category) {
        formData.append('category', metadata.category);
      }
      
      if (metadata.tags && metadata.tags.length > 0) {
        formData.append('tags', metadata.tags.join(','));
      }
      
      const response = await axios.post(`${this.API_BASE}/file`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      return response.data.result;
    } catch (error) {
      console.error('Failed to migrate file:', error);
      throw error;
    }
  }

  public async getMigrationStatus(weaviateCount?: number): Promise<MigrationStatus> {
    try {
      const url = weaviateCount !== undefined 
        ? `${this.API_BASE}/status?weaviate_count=${weaviateCount}`
        : `${this.API_BASE}/status`;
        
      const response = await axios.get(url);
      return response.data;
    } catch (error) {
      console.error('Failed to get migration status:', error);
      throw error;
    }
  }
}

// Create a singleton instance
const migrationService = new MigrationService();
export default migrationService;
