import axios from 'axios';

interface AIQueryRequest {
  query: string;
  context_type?: string;
  options?: Record<string, any>;
}

interface AIQueryResponse {
  answer: string;
  sources?: Array<{
    title: string;
    url?: string;
    content?: string;
    id: string;
  }>;
  suggestions?: string[];
}

interface QueryHistoryItem {
  id: string;
  query: string;
  response: string;
  context_type: string;
  sources: Array<any>;
  created_at: string;
}

interface QueryHistoryResponse {
  history: QueryHistoryItem[];
  total: number;
  limit: number;
  offset: number;
}

class OpenAIService {
  private readonly API_BASE = `${import.meta.env.VITE_API_URL || 'https://phygital-backend.onrender.com'}/api/ai_query`;

  /**
   * Send a query to the AI assistant
   */
  public async askAI(query: string, contextType: string = 'all', options: Record<string, any> = {}): Promise<AIQueryResponse> {
    try {
      console.log('Sending query to AI assistant:', query);
      const payload: AIQueryRequest = {
        query,
        context_type: contextType,
        options
      };
      
      const response = await axios.post(`${this.API_BASE}/ask`, payload);
      return response.data;
    } catch (error) {
      console.error('Error querying AI assistant:', error);
      throw error;
    }
  }

  /**
   * Get query history for the current user
   */
  public async getQueryHistory(limit: number = 20, offset: number = 0): Promise<QueryHistoryResponse> {
    try {
      const response = await axios.get(`${this.API_BASE}/history?limit=${limit}&offset=${offset}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching query history:', error);
      throw error;
    }
  }

  /**
   * Delete a query from history
   */
  public async deleteQueryHistoryItem(queryId: string): Promise<void> {
    try {
      await axios.delete(`${this.API_BASE}/history/${queryId}`);
    } catch (error) {
      console.error('Error deleting query history item:', error);
      throw error;
    }
  }
}

export default new OpenAIService();
