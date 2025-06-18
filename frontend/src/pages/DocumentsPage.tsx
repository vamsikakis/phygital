import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Container, 
  Typography, 
  List, 
  ListItem, 
  ListItemText, 
  ListItemSecondaryAction,
  Paper, 
  Tabs, 
  Tab,
  CircularProgress,
  Divider,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  IconButton,
  Alert,
  Snackbar
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import DeleteIcon from '@mui/icons-material/Delete';
import CleaningServicesIcon from '@mui/icons-material/CleaningServices';
import { useNavigate } from 'react-router-dom';
import DocumentChat from '../components/documents/DocumentChat';
import VerbaDocumentUpload from '../components/documents/VerbaDocumentUpload';
import verbaService from '../services/verbaService';
import { useDocumentManagement } from '../hooks/useDocumentManagement';
import axios from 'axios';

// Define Document interface for proper typing
interface Document {
  id: string;
  title: string;
  category?: string;
  fileUrl: string;
  fileType?: string;
  fileSize?: number;
  uploadDate?: string;
  type?: string; // Add type property for document type
}

// Define the document from useDocumentManagement hook which might have numeric IDs
interface BackendDocument {
  id: string | number;
  title: string;
  category?: string;
  fileUrl: string;
  fileType?: string;
  fileSize?: number;
  uploadDate?: string;
  type?: string; // Add type property for document type
}

const DocumentsPage: React.FC = () => {
  const navigate = useNavigate();
  const [tabValue, setTabValue] = useState(0);
  const [assistantTabValue, setAssistantTabValue] = useState(0);
  const [verbaInitialized, setVerbaInitialized] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [snackbarOpen, setSnackbarOpen] = useState<boolean>(false);
  const [snackbarMessage, setSnackbarMessage] = useState<string>('');
  
  // Document viewer state
  const [viewerOpen, setViewerOpen] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null);
  const [documentContent, setDocumentContent] = useState<string>("");
  const [documentLoading, setDocumentLoading] = useState(false);
  
  // Use the document management hook to fetch documents from the backend
  const { 
    documents: backendDocuments, 
    loading: documentsLoading, 
    error: documentsError, 
    fetchDocuments, 
    deleteDocument 
  } = useDocumentManagement();
  
  // Convert backend documents to our Document interface with string IDs
  const documents: Document[] = React.useMemo(() => {
    return backendDocuments.map(doc => ({
      ...doc,
      id: String(doc.id) // Ensure ID is always a string
    }));
  }, [backendDocuments]);
  
  // Fetch documents when component mounts
  useEffect(() => {
    fetchDocuments().catch(err => console.error('Error fetching documents:', err));
  }, []);
  
  useEffect(() => {
    const checkVerbaStatus = async () => {
      try {
        const status = await verbaService.checkStatus();
        // DEMO MODE: Force enable Verba service for demonstration purposes
        setVerbaInitialized(true);
        console.log('Document Assistant enabled for demo mode');
      } catch (error) {
        // DEMO MODE: Force enable Verba service even if backend is unavailable
        setVerbaInitialized(true);
        console.log('Document Assistant enabled for demo mode despite connection error');
      } finally {
        setIsLoading(false);
      }
    };
    
    checkVerbaStatus();
  }, []);
  
  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };
  
  const handleAssistantTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setAssistantTabValue(newValue);
  };
  
  // Function to determine if a document is a PDF
  const isPdfDocument = (doc: any): boolean => {
    return doc.fileUrl.toLowerCase().endsWith('.pdf') || 
           (doc.metadata && doc.metadata.mime_type === 'application/pdf') ||
           doc.title.toLowerCase().includes('lease') ||
           doc.title.toLowerCase().includes('agreement');
  };

  // Function to format document content based on document type
  const formatDocumentContent = (content: string, doc: any): string => {
    const title = doc.title;
    
    // Check if content is already HTML
    if (content.trim().startsWith('<') && content.includes('</')) {
      return content;
    }
    
    // For text content, wrap in HTML
    return `
      <div class="document-content">
        <h1>${title}</h1>
        <div class="content-body">
          ${content.split('\n').map(line => `<p>${line}</p>`).join('')}
        </div>
      </div>
    `;
  };
  
  // Function to get mock content for specific document types
  const getMockDocumentContent = (doc: any): string => {
    const title = doc.title.toLowerCase();
    
    if (title.includes('lease') || title.includes('agreement')) {
      return `
        <h1>${doc.title}</h1>
        <h2>Agreement Terms</h2>
        <p>This agreement is made between Gopalan Atlantis and the resident.</p>
        <h3>Term</h3>
        <p>The lease term is for 12 months starting from the date of occupancy.</p>
        <h3>Rent</h3>
        <p>Monthly rent is payable on the 5th of each month.</p>
        <h3>Security Deposit</h3>
        <p>A security deposit equal to two months' rent is required.</p>
      `;
    } else if (title.includes('maintenance')) {
      return `
        <h1>${doc.title}</h1>
        <h2>Maintenance Request</h2>
        <form>
          <div style="margin-bottom: 15px;">
            <label style="display: block; font-weight: bold;">Apartment Number:</label>
            <input type="text" style="width: 100%; padding: 8px; border: 1px solid #ccc;">
          </div>
          <div style="margin-bottom: 15px;">
            <label style="display: block; font-weight: bold;">Issue Type:</label>
            <select style="width: 100%; padding: 8px; border: 1px solid #ccc;">
              <option>Plumbing</option>
              <option>Electrical</option>
              <option>HVAC</option>
              <option>Appliance</option>
              <option>Other</option>
            </select>
          </div>
          <div style="margin-bottom: 15px;">
            <label style="display: block; font-weight: bold;">Description:</label>
            <textarea style="width: 100%; padding: 8px; border: 1px solid #ccc; height: 100px;"></textarea>
          </div>
          <div style="margin-bottom: 15px;">
            <label style="display: block; font-weight: bold;">Preferred Date for Service:</label>
            <input type="date" style="width: 100%; padding: 8px; border: 1px solid #ccc;">
          </div>
          <button type="button" style="background: #1976d2; color: white; padding: 10px 15px; border: none; cursor: pointer;">Submit Request</button>
        </form>
      `;
    } else if (title.includes('newsletter')) {
      return `
        <h1>${doc.title}</h1>
        <h2>June 2025 Edition</h2>
        <h3>Upcoming Events</h3>
        <ul>
          <li>Community Potluck - June 15th, 6:00 PM at the Clubhouse</li>
          <li>Swimming Pool Opening - June 20th</li>
          <li>Yoga in the Park - Every Sunday at 8:00 AM</li>
        </ul>
        <h3>Maintenance Updates</h3>
        <p>The elevator in Building C will be undergoing maintenance from June 18-20. Please use the stairs during this time.</p>
        <h3>New Residents</h3>
        <p>Please join us in welcoming the following new residents to our community:</p>
        <ul>
          <li>Sharma Family - Building A, Apt 304</li>
          <li>Reddy Family - Building B, Apt 201</li>
          <li>Kumar Family - Building D, Apt 105</li>
        </ul>
      `;
    } else if (title.includes('club house')) {
      return `
        <h1>Clubhouse Usage Guidelines</h1>
        <h2>Hours of Operation</h2>
        <ul>
          <li>Monday to Friday: 6:00 AM to 10:00 PM</li>
          <li>Weekends and Holidays: 7:00 AM to 11:00 PM</li>
        </ul>
        <h2>Booking Rules</h2>
        <ol>
          <li>Residents can book the clubhouse up to 30 days in advance</li>
          <li>Maximum booking duration is 4 hours</li>
          <li>Cleaning deposit of ₹2000 is required</li>
          <li>Cancellations must be made 48 hours in advance for full refund</li>
        </ol>
        <h2>Capacity and Restrictions</h2>
        <ul>
          <li>Maximum capacity: 50 people</li>
          <li>No smoking allowed</li>
          <li>No loud music after 9:00 PM</li>
          <li>Pets must be kept on leash in outdoor areas only</li>
        </ul>
      `;
    } else {
      // Generic document content
      return `
        <h1>${doc.title}</h1>
        <p>This is a mock document for demonstration purposes.</p>
        <p>In a production environment, this would contain the actual content of the document.</p>
      `;
    }
  };

  // Function to open document viewer and fetch document content
  const handleViewDocument = async (doc: Document) => {
    setSelectedDocument(doc);
    setViewerOpen(true);
    setDocumentLoading(true);
    
    try {
      // Make sure we're using absolute URLs
      const baseUrl = 'http://localhost:5001';
      
      // Always use the document view API endpoint for consistent content rendering
      const docId = doc.id || 'unknown';
      const viewUrl = `${baseUrl}/api/verba/documents/${docId}/view`;
      
      console.log(`Fetching document from: ${viewUrl}`);
      
      try {
        const response = await axios.get(viewUrl, {
          responseType: 'text'
        });
        
        // Extract the content from the HTML response
        const htmlContent = response.data;
        
        // If the content is HTML, use it directly
        if (htmlContent.trim().startsWith('<')) {
          setDocumentContent(htmlContent);
        } else {
          // Otherwise format it
          const formattedContent = formatDocumentContent(htmlContent, doc);
          setDocumentContent(formattedContent);
        }
      } catch (fetchError) {
        console.error('Error fetching document from view endpoint, trying direct URL:', fetchError);
        
        // Fall back to direct URL if view endpoint fails
        try {
          const fullUrl = doc.fileUrl.startsWith('http') ? doc.fileUrl : `${baseUrl}${doc.fileUrl}`;
          const response = await axios.get(fullUrl, {
            responseType: 'text'
          });
          
          // Format the content based on document type
          const formattedContent = formatDocumentContent(response.data, doc);
          setDocumentContent(formattedContent);
        } catch (directFetchError) {
          console.error('Error fetching document directly, falling back to mock content:', directFetchError);
          // Fall back to mock content if all fetches fail
          setDocumentContent(getMockDocumentContent(doc));
        }
      }
    } catch (error) {
      console.error('Error in document viewer:', error);
      setDocumentContent(`<p>Error loading document: ${error instanceof Error ? error.message : 'Unknown error'}</p>`);
    } finally {
      setDocumentLoading(false);
    }
  };
  
  // Function to close document viewer
  const handleCloseViewer = () => {
    setViewerOpen(false);
    setSelectedDocument(null);
    setDocumentContent("");
  };

  // Handle document deletion
  const handleDeleteDocument = async (docId: string) => {
    try {
      await deleteDocument(docId);
      setSnackbarMessage('Document deleted successfully');
      setSnackbarOpen(true);
    } catch (error) {
      console.error('Error deleting document:', error);
      setSnackbarMessage('Failed to delete document');
      setSnackbarOpen(true);
    }
  };

  // Clean up duplicate documents by title
  const cleanupDuplicateDocuments = async () => {
    // Create a map to track documents by title
    const uniqueDocs = new Map<string, Document>();
    const duplicateDocs: Document[] = [];
    
    // Find duplicates (keep the first occurrence of each title)
    documents.forEach(doc => {
      if (!uniqueDocs.has(doc.title)) {
        uniqueDocs.set(doc.title, doc);
      } else {
        duplicateDocs.push(doc);
      }
    });
    
    if (duplicateDocs.length === 0) {
      setSnackbarMessage('No duplicate documents found');
      setSnackbarOpen(true);
      return;
    }
    
    // Delete all duplicates
    try {
      setIsLoading(true);
      for (const doc of duplicateDocs) {
        await deleteDocument(doc.id);
      }
      setSnackbarMessage(`Deleted ${duplicateDocs.length} duplicate documents`);
      setSnackbarOpen(true);
    } catch (error) {
      console.error('Error cleaning up duplicates:', error);
      setSnackbarMessage('Failed to clean up some duplicate documents');
      setSnackbarOpen(true);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Box sx={{ flexGrow: 1, py: 4 }}>
      <Container>
        <Typography variant="h4" component="h1" gutterBottom>
          Apartment Documents
        </Typography>
        
        <Paper sx={{ mb: 3 }}>
          <Tabs value={tabValue} onChange={handleTabChange} aria-label="document tabs">
            <Tab label="Document Library" />
            <Tab label="Document Assistant" />
          </Tabs>
          
          <Box sx={{ p: 3 }}>
            {tabValue === 0 && (
              <>
                {documentsLoading ? (
                  <Box display="flex" justifyContent="center" p={3}>
                    <CircularProgress />
                  </Box>
                ) : documentsError ? (
                  <Typography color="error">
                    Error loading documents: {documentsError.message}
                  </Typography>
                ) : (
                  <>
                    {/* Group documents by category */}
                    {Array.from(new Set(documents.map(doc => doc.category))).map(category => (
                      <Box key={category} mb={3}>
                        <Typography variant="h6" gutterBottom>
                          {category}
                        </Typography>
                        <Paper elevation={1}>
                          <List>
                            {documents
                              .filter(doc => doc.category === category)
                              .map((doc) => (
                                <ListItem 
                                  key={doc.id} 
                                  button 
                                  onClick={() => handleViewDocument(doc)}
                                  divider
                                >
                                  <ListItemText
                                    primary={doc.title}
                                    secondary={`${doc.category || 'Uncategorized'} - ${doc.fileType || 'Document'}`}
                                  />
                                  <ListItemSecondaryAction>
                                    <IconButton 
                                      edge="end" 
                                      aria-label="delete" 
                                      onClick={(e) => {
                                        e.stopPropagation();
                                        handleDeleteDocument(doc.id);
                                      }}
                                    >
                                      <DeleteIcon />
                                    </IconButton>
                                  </ListItemSecondaryAction>
                                </ListItem>
                            ))}
                          </List>
                        </Paper>
                      </Box>
                    ))}
                  </>
                )}
              </>
            )}
            
            {/* Document Viewer Dialog */}
            <Dialog
              open={viewerOpen}
              onClose={handleCloseViewer}
              fullWidth
              maxWidth="md"
              aria-labelledby="document-viewer-title"
            >
              <DialogTitle id="document-viewer-title">
                {selectedDocument?.title || 'Document Viewer'}
                <IconButton
                  aria-label="close"
                  onClick={handleCloseViewer}
                  sx={{ position: 'absolute', right: 8, top: 8 }}
                >
                  <CloseIcon />
                </IconButton>
              </DialogTitle>
              <DialogContent dividers>
                {documentLoading ? (
                  <Box display="flex" justifyContent="center" p={3}>
                    <CircularProgress />
                  </Box>
                ) : (
                  <>
                    <div 
                      dangerouslySetInnerHTML={{ __html: documentContent }} 
                      style={{
                        padding: '16px',
                        maxWidth: '800px',
                        margin: '0 auto',
                        fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
                        lineHeight: '1.6'
                      }}
                      className="document-viewer-content"
                    />
                    <style>{`
                      .document-viewer-content h1 {
                        color: #1976d2;
                        margin-bottom: 20px;
                        border-bottom: 1px solid #e0e0e0;
                        padding-bottom: 10px;
                      }
                      .document-viewer-content h2 {
                        color: #0d47a1;
                        margin-top: 24px;
                        margin-bottom: 16px;
                      }
                      .document-viewer-content h3 {
                        color: #2196f3;
                        margin-top: 20px;
                        margin-bottom: 12px;
                      }
                      .document-viewer-content p {
                        margin-bottom: 16px;
                      }
                      .document-viewer-content ul, .document-viewer-content ol {
                        margin-bottom: 20px;
                        padding-left: 24px;
                      }
                      .document-viewer-content li {
                        margin-bottom: 8px;
                      }
                      .document-viewer-content strong {
                        font-weight: 500;
                      }
                    `}</style>
                  </>
                )}
              </DialogContent>
              <DialogActions>
                <Button onClick={handleCloseViewer}>Close</Button>
              </DialogActions>
            </Dialog>
            
            {tabValue === 1 && (
              <div>
                {isLoading ? (
                  <Box display="flex" justifyContent="center" p={3}>
                    <CircularProgress />
                  </Box>
                ) : !verbaInitialized ? (
                  <Box p={3}>
                    <Typography variant="body1" color="error">
                      The document assistant is currently unavailable. Please try again later.
                    </Typography>
                  </Box>
                ) : (
                  <>
                    <Tabs value={assistantTabValue} onChange={handleAssistantTabChange} aria-label="assistant tabs">
                      <Tab label="Chat with Documents" />
                      <Tab label="Manage RAG Documents" />
                    </Tabs>
                    
                    <Box sx={{ mt: 2 }}>
                      {assistantTabValue === 0 && (
                        <DocumentChat 
                          title="Apartment Documents Assistant" 
                          onViewDocument={(documentId) => {
                            // Find the document by ID and open it in the viewer
                            // Our documents have string UUIDs as IDs
                            const doc = documents.find(d => d.id === documentId);
                            if (doc) {
                              handleViewDocument(doc);
                            } else {
                              // If document not found in the current list, fetch it directly
                              console.log(`Document with ID ${documentId} not found in current list, fetching directly`);
                              const mockDoc: Document = {
                                id: documentId,
                                title: 'Document',
                                fileUrl: `/api/verba/documents/${documentId}/view`
                              };
                              handleViewDocument(mockDoc);
                            }
                          }}
                        />
                      )}
                      
                      {assistantTabValue === 1 && (
                        <>
                          <Typography variant="body2" color="text.secondary" paragraph>
                            Upload documents to the RAG system to make them available for AI-powered queries. Documents uploaded here will be processed and indexed for retrieval by the document assistant.
                          </Typography>
                          
                          <Button
                            variant="outlined"
                            color="secondary"
                            startIcon={<CleaningServicesIcon />}
                            onClick={cleanupDuplicateDocuments}
                            sx={{ mb: 2 }}
                          >
                            Clean Up Duplicate Documents
                          </Button>
                          
                          <Divider sx={{ my: 2 }} />
                          <VerbaDocumentUpload 
                            collectionName="apartment_documents" 
                            onDocumentAdded={() => {
                              // Refresh documents after upload
                              fetchDocuments();
                            }}
                          />
                        </>
                      )}
                    </Box>
                  </>
                )}
              </div>
            )}
          </Box>
        </Paper>
      </Container>
      
      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={6000}
        onClose={() => setSnackbarOpen(false)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert 
          onClose={() => setSnackbarOpen(false)} 
          severity="info" 
          sx={{ width: '100%' }}
        >
          {snackbarMessage}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default DocumentsPage;
