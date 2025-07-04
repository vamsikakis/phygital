import axios from 'axios';

// Define interfaces for API responses
export interface AssistantResponse {
  assistant_id: string;
  vector_store_id: string;
  message?: string;
}

export interface ThreadResponse {
  thread_id: string;
  created_at: number;
  metadata?: Record<string, any>;
}

export interface MessageResponse {
  message_id: string;
  thread_id: string;
  role: string;
  content: string;
  created_at: number;
}

export interface RunResponse {
  run_id: string;
  thread_id: string;
  status: string;
  response: string;
  created_at: number;
  completed_at: number;
}

export interface FileResponse {
  file_id: string;
  filename: string;
  purpose: string;
  bytes: number;
  created_at: number;
  status?: string;
}

class OpenAIAssistantService {
  private API_BASE = `${import.meta.env.VITE_API_URL || 'https://phygital-s839.onrender.com'}/api/assistant`;
  private assistantId: string | null = null;
  private vectorStoreId: string | null = null;
  private _isInitialized = false;

  public get isInitialized(): boolean {
    return this._isInitialized;
  }

  public async initAssistant(): Promise<AssistantResponse> {
    try {
      console.log('Initializing OpenAI Assistant and Vector Store...');
      const response = await axios.get(`${this.API_BASE}/init`);
      this.assistantId = response.data.assistant_id;
      this.vectorStoreId = response.data.vector_store_id;
      this._isInitialized = true;
      return response.data;
    } catch (error) {
      console.error('Failed to initialize OpenAI Assistant:', error);
      this._isInitialized = false;
      throw error;
    }
  }

  public async createThread(): Promise<ThreadResponse> {
    try {
      const response = await axios.post(`${this.API_BASE}/threads`);
      return response.data;
    } catch (error) {
      console.error('Failed to create thread:', error);
      throw error;
    }
  }

  public async getThread(threadId: string): Promise<ThreadResponse> {
    try {
      const response = await axios.get(`${this.API_BASE}/threads/${threadId}`);
      return response.data;
    } catch (error) {
      console.error(`Failed to get thread ${threadId}:`, error);
      throw error;
    }
  }

  public async listThreads(limit: number = 10): Promise<ThreadResponse[]> {
    try {
      const response = await axios.get(`${this.API_BASE}/threads?limit=${limit}`);
      return response.data.threads;
    } catch (error) {
      console.error('Failed to list threads:', error);
      throw error;
    }
  }

  public async deleteThread(threadId: string): Promise<{ thread_id: string; deleted: boolean }> {
    try {
      const response = await axios.delete(`${this.API_BASE}/threads/${threadId}`);
      return response.data;
    } catch (error) {
      console.error(`Failed to delete thread ${threadId}:`, error);
      throw error;
    }
  }

  public async addMessage(threadId: string, content: string, role: string = 'user'): Promise<MessageResponse> {
    try {
      const response = await axios.post(`${this.API_BASE}/threads/${threadId}/messages`, {
        content,
        role
      });
      return response.data;
    } catch (error) {
      console.error(`Failed to add message to thread ${threadId}:`, error);
      throw error;
    }
  }

  public async getMessages(threadId: string, limit: number = 100): Promise<MessageResponse[]> {
    try {
      const response = await axios.get(`${this.API_BASE}/threads/${threadId}/messages?limit=${limit}`);
      return response.data.messages;
    } catch (error) {
      console.error(`Failed to get messages from thread ${threadId}:`, error);
      throw error;
    }
  }

  public async runAssistant(threadId: string, instructions?: string): Promise<RunResponse> {
    try {
      const payload = instructions ? { instructions } : {};
      const response = await axios.post(`${this.API_BASE}/threads/${threadId}/run`, payload);
      return response.data;
    } catch (error) {
      console.error(`Failed to run assistant on thread ${threadId}:`, error);
      throw error;
    }
  }

  public async uploadFile(file: File): Promise<FileResponse> {
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await axios.post(`${this.API_BASE}/files`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      return response.data;
    } catch (error) {
      console.error('Failed to upload file:', error);
      throw error;
    }
  }

  public async listFiles(): Promise<FileResponse[]> {
    try {
      const response = await axios.get(`${this.API_BASE}/files`);
      return response.data.files;
    } catch (error) {
      console.error('Failed to list files:', error);
      throw error;
    }
  }

  public async deleteFile(fileId: string): Promise<{ file_id: string; deleted: boolean }> {
    try {
      const response = await axios.delete(`${this.API_BASE}/files/${fileId}`);
      return response.data;
    } catch (error) {
      console.error(`Failed to delete file ${fileId}:`, error);
      throw error;
    }
  }

  // Helper method to handle a complete conversation flow
  public async sendMessage(threadId: string, message: string): Promise<string> {
    try {
      // Ensure we have a valid thread
      let currentThreadId = threadId;
      if (!currentThreadId) {
        const thread = await this.createThread();
        currentThreadId = thread.thread_id;
      }
      
      // Add the user message
      await this.addMessage(currentThreadId, message);
      
      // Run the assistant
      const runResult = await this.runAssistant(currentThreadId);
      
      // Return the assistant's response
      return runResult.response;
    } catch (error) {
      console.error('Error in sendMessage flow:', error);
      throw error;
    }
  }
}

// Create a singleton instance
const openaiAssistantService = new OpenAIAssistantService();
export default openaiAssistantService;
