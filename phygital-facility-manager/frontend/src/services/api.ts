import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'https://phygital-backend.onrender.com/api';

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  },
});

// API functions for Knowledge Base module (AKC)
export const knowledgeBaseAPI = {
  getDocuments: async () => {
    try {
      const response = await apiClient.get('/akc/documents');
      return response.data.documents;
    } catch (error) {
      console.error('Error fetching documents:', error);
      throw error;
    }
  },
  
  searchDocuments: async (query: string) => {
    try {
      const response = await apiClient.get(`/akc/search?q=${encodeURIComponent(query)}`);
      return response.data.results;
    } catch (error) {
      console.error('Error searching documents:', error);
      throw error;
    }
  }
};

// API functions for Owner Communication module (OCE)
export const communicationAPI = {
  getAnnouncements: async () => {
    try {
      const response = await apiClient.get('/oce/announcements');
      return response.data.announcements;
    } catch (error) {
      console.error('Error fetching announcements:', error);
      throw error;
    }
  },
  
  getEvents: async () => {
    try {
      const response = await apiClient.get('/oce/events');
      return response.data.events;
    } catch (error) {
      console.error('Error fetching events:', error);
      throw error;
    }
  },
  
  getPolls: async () => {
    try {
      const response = await apiClient.get('/oce/polls');
      return response.data.polls;
    } catch (error) {
      console.error('Error fetching polls:', error);
      throw error;
    }
  }
};

// API functions for Help Desk module (HDC)
export const helpDeskAPI = {
  createTicket: async (ticketData: any) => {
    try {
      const response = await apiClient.post('/hdc/create-ticket', ticketData);
      return response.data;
    } catch (error) {
      console.error('Error creating ticket:', error);
      throw error;
    }
  },
  
  getTickets: async () => {
    try {
      const response = await apiClient.get('/hdc/tickets');
      return response.data.tickets;
    } catch (error) {
      console.error('Error fetching tickets:', error);
      throw error;
    }
  },
  
  getTicketById: async (ticketId: string) => {
    try {
      const response = await apiClient.get(`/hdc/tickets/${ticketId}`);
      return response.data.ticket;
    } catch (error) {
      console.error(`Error fetching ticket ${ticketId}:`, error);
      throw error;
    }
  }
};

// API function for querying the AI agent
export const queryAI = async (query: string, module: string = 'auto') => {
  try {
    const response = await apiClient.post('/query', { query, module });
    return response.data.response;
  } catch (error) {
    console.error('Error querying AI:', error);
    throw error;
  }
};

export default {
  knowledgeBaseAPI,
  communicationAPI,
  helpDeskAPI,
  queryAI
};
