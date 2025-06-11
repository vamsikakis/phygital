import { useState, useEffect } from 'react';
import axios from 'axios';

interface Document {
  id: string;
  title: string;
  type?: string;
  category?: string;
  fileUrl: string;
  uploadedBy?: string;
  uploaded_by?: string;
  uploadDate?: string;
  uploadedAt?: string;
  uploaded_at?: string;
  status?: string;
  tags?: string[];
  fileType?: string;
  fileSize?: number;
  metadata?: {
    size?: number;
    pages?: number;
    language?: string;
  };
}

interface DocumentType {
  id: number;
  name: string;
  description: string;
  icon: string;
}

export const useDocumentManagement = () => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [documentTypes, setDocumentTypes] = useState<DocumentType[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  // Define fetchDocuments outside of useEffect for reuse
  const fetchDocuments = async () => {
    try {
      console.log('Fetching documents from Verba server...');
      const response = await axios.get('http://localhost:5001/api/verba/documents');
      console.log('Documents received:', response.data);
      setDocuments(response.data);
      return response.data;
    } catch (err) {
      console.error('Error fetching documents:', err);
      setError(err instanceof Error ? err : new Error('Failed to fetch documents'));
      throw err;
    }
  };

  const fetchDocumentTypes = async () => {
    try {
      console.log('Fetching document types from mock server...');
      const response = await axios.get('http://localhost:5001/api/documents/types');
      console.log('Document types received:', response.data);
      setDocumentTypes(response.data);
      return response.data;
    } catch (err) {
      console.error('Error fetching document types:', err);
      setError(err instanceof Error ? err : new Error('Failed to fetch document types'));
      throw err;
    }
  };

  useEffect(() => {
    Promise.all([fetchDocuments(), fetchDocumentTypes()])
      .catch(err => console.error('Error initializing documents:', err))
      .finally(() => {
        setLoading(false);
      });
  }, []);

  const uploadDocument = async (formData: FormData) => {
    try {
      console.log('Uploading document to Verba server...');
      const response = await axios.post('http://localhost:5001/api/verba/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      console.log('Upload response:', response.data);
      
      // Refresh the document list after upload
      await fetchDocuments();
      
      return response.data;
    } catch (err) {
      console.error('Error uploading document:', err);
      throw err instanceof Error ? err : new Error('Failed to upload document');
    }
  };

  const updateDocument = async (documentId: string, updateData: Partial<Document>) => {
    try {
      console.log(`Updating document ${documentId} with data:`, updateData);
      const response = await axios.put(`http://localhost:5001/api/documents/${documentId}`, updateData);
      console.log('Update response:', response.data);
      setDocuments((prev) =>
        prev.map((doc) =>
          doc.id === documentId ? { ...doc, ...response.data } : doc
        )
      );
      return response.data;
    } catch (err) {
      console.error('Error updating document:', err);
      throw err instanceof Error ? err : new Error('Failed to update document');
    }
  };

  const deleteDocument = async (documentId: string) => {
    try {
      console.log(`Deleting document ${documentId}`);
      await axios.delete(`http://localhost:5001/api/verba/documents/${documentId}/delete`);
      console.log(`Document ${documentId} deleted successfully`);
      setDocuments((prev) => prev.filter((doc) => doc.id !== documentId));
      
      // Refresh the document list after deletion
      await fetchDocuments();
    } catch (err) {
      console.error('Error deleting document:', err);
      throw err instanceof Error ? err : new Error('Failed to delete document');
    }
  };

  const searchDocuments = async (query: string) => {
    try {
      console.log(`Searching documents with query: ${query}`);
      const response = await axios.get(`http://localhost:5001/api/documents/search?query=${query}`);
      console.log('Search results:', response.data);
      return response.data;
    } catch (err) {
      console.error('Error searching documents:', err);
      throw err instanceof Error ? err : new Error('Failed to search documents');
    }
  };

  return {
    documents,
    setDocuments,
    documentTypes,
    loading,
    error,
    uploadDocument,
    updateDocument,
    deleteDocument,
    searchDocuments,
    fetchDocuments,
  };
};
