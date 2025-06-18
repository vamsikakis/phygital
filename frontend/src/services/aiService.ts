import axios from 'axios';

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

interface ChatResponse {
  role: 'assistant';
  content: string;
}

export class AIService {
  private static instance: AIService;
  private readonly API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

  private constructor() {}

  static getInstance(): AIService {
    if (!AIService.instance) {
      AIService.instance = new AIService();
    }
    return AIService.instance;
  }

  async sendMessage(messages: ChatMessage[]): Promise<ChatResponse> {
    try {
      const response = await axios.post(`${this.API_URL}/api/chat`, {
        messages,
      });
      return response.data;
    } catch (error) {
      console.error('Error sending message to AI:', error);
      throw error;
    }
  }

  async getDocumentSummary(documentId: string): Promise<string> {
    try {
      const response = await axios.get(`${this.API_URL}/api/documents/${documentId}/summary`);
      return response.data.summary;
    } catch (error) {
      console.error('Error getting document summary:', error);
      throw error;
    }
  }

  async getCommunityAnnouncements(): Promise<string[]> {
    try {
      const response = await axios.get(`${this.API_URL}/api/announcements`);
      return response.data.announcements;
    } catch (error) {
      console.error('Error getting community announcements:', error);
      throw error;
    }
  }
}

export const aiService = AIService.getInstance();
