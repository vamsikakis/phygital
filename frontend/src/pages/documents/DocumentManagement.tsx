import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  TextField,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Chip,
  CircularProgress,
  Alert,
  MenuItem,
  Tabs,
  Tab,
  Divider,
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  Search as SearchIcon,
  Download as DownloadIcon,
  FilterList as FilterListIcon,
  ChatBubble as ChatIcon,
  ManageSearch as ManageIcon,
} from '@mui/icons-material';
import { useDocumentManagement } from '../../hooks/useDocumentManagement';
import DocumentStats from '../../components/documents/DocumentStats';
import DocumentChat from '../../components/documents/DocumentChat';
import VerbaDocumentUpload from '../../components/documents/VerbaDocumentUpload';
import verbaService from '../../services/verbaService';

interface Document {
  id: number;
  title: string;
  type: string;
  category: string;
  fileUrl: string;
  uploadedBy?: string;
  uploadedAt?: string;
  status?: string;
  tags?: string[];
  metadata: {
    size: number;
    pages: number;
    language: string;
  };
}

const DocumentManagement: React.FC = () => {
  const {
    documents,
    setDocuments,
    documentTypes,
    error,
    loading,
    uploadDocument,
    updateDocument,
    deleteDocument,
    searchDocuments,
    fetchDocuments,
  } = useDocumentManagement();

  const [searchQuery, setSearchQuery] = useState('');
  const [activeTab, setActiveTab] = useState<number>(0);
  const [verbaInitialized, setVerbaInitialized] = useState<boolean>(false);
  const [verbaTabIndex, setVerbaTabIndex] = useState<number>(0); // For subtabs in Document Assistant
  const [open, setOpen] = useState(false);
  const [filterDialogOpen, setFilterDialogOpen] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null);
  const [formData, setFormData] = useState({
    title: '',
    type: '',
    category: '',
    tags: '',
    file: null as File | null,
  });
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);

  // Filter state
  interface Filter {
    type: string; // 'type', 'category', etc.
    value: string;
  }
  const [activeFilters, setActiveFilters] = useState<Filter[]>([]);

  // Check Verba status on component mount
  useEffect(() => {
    const checkVerba = async () => {
      try {
        const status = await verbaService.checkStatus();
        // DEMO MODE: Force enable Verba service for demonstration purposes
        setVerbaInitialized(true);
        console.log('Document Assistant enabled for demo mode');
      } catch (err) {
        // DEMO MODE: Force enable Verba service even if backend is unavailable
        setVerbaInitialized(true);
        console.log('Document Assistant enabled for demo mode despite connection error');
      }
    };

    checkVerba();
  }, []);

  // Handle main tab change
  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  // Handle Verba subtab change
  const handleVerbaTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setVerbaTabIndex(newValue);
  };

  // Filter the documents based on active filters
  const filteredDocuments = React.useMemo(() => {
    if (activeFilters.length === 0) return documents;

    return documents.filter(doc => {
      return activeFilters.every(filter => {
        switch(filter.type) {
          case 'Type':
            return doc.type === filter.value;
          case 'Status':
            return doc.status === filter.value;
          case 'Category':
            return doc.category === filter.value;
          default:
            return true;
        }
      });
    });
  }, [documents, activeFilters]);

  // Handle removing a filter
  const handleRemoveFilter = (index: number) => {
    setActiveFilters(filters => filters.filter((_, i) => i !== index));
  };

  // Safely handle document opening, ensuring metadata is properly handled
  const handleOpen = (doc?: Document) => {
    if (doc) {
      // Type assertion to satisfy TypeScript when setting as selected document
      setSelectedDocument(doc as Document);
      setFormData({
        title: doc.title || '',
        type: doc.type || '',
        category: doc.category || '',
        tags: doc.tags && doc.tags.length > 0 ? doc.tags.join(', ') : '',
        file: null,
      });
    } else {
      setSelectedDocument(null);
      setFormData({
        title: '',
        type: '',
        category: '',
        tags: '',
        file: null,
      });
    }
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
    setSelectedDocument(null);
    setFormData({
      title: '',
      type: '',
      category: '',
      tags: '',
      file: null,
    });
    setUploadError(null);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setFormData((prev) => ({
        ...prev,
        file,
      }));
    }
  };

  const handleSubmit = async () => {
    try {
      setUploading(true);
      setUploadError(null);

      const formDataObj = new FormData();
      formDataObj.append('title', formData.title);
      formDataObj.append('type', formData.type);
      formDataObj.append('category', formData.category);
      formDataObj.append('tags', formData.tags);
      if (formData.file) {
        formDataObj.append('file', formData.file);
      }

      if (selectedDocument) {
        await updateDocument(selectedDocument.id, {
          title: formData.title,
          type: formData.type,
          category: formData.category,
          tags: formData.tags.split(',').map(tag => tag.trim()),
        });
      } else {
        await uploadDocument(formDataObj);
      }
      handleClose();
    } catch (err) {
      setUploadError(err instanceof Error ? err.message : 'Failed to save document');
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (documentId: number) => {
    try {
      await deleteDocument(documentId);
    } catch (err) {
      console.error('Error deleting document:', err);
    }
  };

  const handleDownload = (fileUrl: string) => {
    window.open(fileUrl, '_blank');
  };

  const handleSearch = async (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
    if (e.target.value) {
      try {
        const results = await searchDocuments(e.target.value);
        // Use the documents from the custom hook
        setDocuments(results);
      } catch (err) {
        console.error('Error searching documents:', err);
      }
    } else {
      // If search box is cleared, fetch all documents again
      try {
        const docs = await fetchDocuments();
        setDocuments(docs);
      } catch (err) {
        console.error('Error fetching all documents:', err);
      }
    }
  };

  if (loading) {
    return <Box sx={{ p: 3, display: 'flex', justifyContent: 'center' }}>
      <CircularProgress />
    </Box>;
  }

  if (error) {
    return <Box sx={{ p: 3 }}>
      <Alert severity="error">Error: {error.message}</Alert>
    </Box>;
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Tabs Navigation */}
      <Paper sx={{ mb: 3 }}>
        <Tabs 
          value={activeTab} 
          onChange={handleTabChange} 
          aria-label="document management tabs"
          variant="fullWidth"
        >
          <Tab label="Document Library" />
          <Tab 
            label="Document Assistant" 
            icon={verbaInitialized ? undefined : <CircularProgress size={16} />} 
            iconPosition="end"
            disabled={!verbaInitialized}
          />
        </Tabs>
      </Paper>
      
      {/* Tab Panels */}
      <div role="tabpanel" hidden={activeTab !== 0}>
        {activeTab === 0 && (
          <>
            {/* Document Statistics Dashboard */}
            <DocumentStats documents={filteredDocuments} />
            
            <Paper sx={{ p: 2, mb: 3 }}>
              <Grid container spacing={2} alignItems="center">
                <Grid item xs={12} sm={6} md={4}>
                  <Typography variant="h6" gutterBottom>
                    Document Management
                    {filteredDocuments.length !== documents.length && (
                      <Typography component="span" variant="body2" sx={{ ml: 1, color: 'text.secondary' }}>
                        ({filteredDocuments.length} of {documents.length})
                      </Typography>
                    )}
                  </Typography>
                </Grid>
                <Grid item xs={12} sm={6} md={8}>
                  <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
                    <TextField
                      fullWidth
                      size="small"
                      placeholder="Search documents..."
                      value={searchQuery}
                      onChange={handleSearch}
                      InputProps={{
                        startAdornment: <SearchIcon sx={{ mr: 1 }} />,
                      }}
                    />
                    <Button
                      variant="outlined"
                      color="primary"
                      size="small"
                      onClick={() => setFilterDialogOpen(true)}
                      startIcon={<FilterListIcon />}
                    >
                      Filters
                    </Button>
                  </Box>
                </Grid>
              </Grid>
              
              {/* Active filters display */}
              {activeFilters.length > 0 && (
                <Box sx={{ mt: 2, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  {activeFilters.map((filter, index) => (
                    <Chip
                      key={index}
                      label={`${filter.type}: ${filter.value}`}
                      onDelete={() => handleRemoveFilter(index)}
                      size="small"
                      color="primary"
                      variant="outlined"
                    />
                  ))}
                  <Chip 
                    label="Clear All" 
                    onClick={() => setActiveFilters([])} 
                    size="small"
                    color="secondary"
                  />
                </Box>
              )}
            </Paper>

            <Paper sx={{ p: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="subtitle1">Documents</Typography>
                <Button
                  variant="contained"
                  color="primary"
                  startIcon={<AddIcon />}
                  onClick={() => handleOpen()}
                >
                  Add Document
                </Button>
              </Box>

              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Title</TableCell>
                      <TableCell>Type</TableCell>
                      <TableCell>Category</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Uploaded By</TableCell>
                      <TableCell>Uploaded At</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {filteredDocuments.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={7} align="center">
                          {loading ? (
                            <CircularProgress size={24} />
                          ) : error ? (
                            <Alert severity="error">{error}</Alert>
                          ) : activeFilters.length > 0 ? (
                            'No documents match your filters'
                          ) : (
                            'No documents found'
                          )}
                        </TableCell>
                      </TableRow>
                    ) : (
                      filteredDocuments.map((document) => (
                        <TableRow key={document.id} hover>
                          <TableCell>
                            <Box sx={{ display: 'flex', alignItems: 'center' }}>
                              <Typography variant="body2">{document.title}</Typography>
                              {document.tags && document.tags.length > 0 && (
                                <Box sx={{ ml: 1, display: 'flex', gap: 0.5 }}>
                                  {document.tags.slice(0, 2).map((tag: string, index: number) => (
                                    <Chip 
                                      key={index} 
                                      label={tag} 
                                      size="small" 
                                      variant="outlined" 
                                      sx={{ height: 20, fontSize: '0.7rem' }} 
                                    />
                                  ))}
                                  {document.tags.length > 2 && (
                                    <Typography variant="caption" color="textSecondary">
                                      +{document.tags.length - 2}
                                    </Typography>
                                  )}
                                </Box>
                              )}
                            </Box>
                          </TableCell>
                          <TableCell>{document.type}</TableCell>
                          <TableCell>{document.category}</TableCell>
                          <TableCell>
                            <Chip 
                              label={document.status} 
                              size="small"
                              color={document.status === 'Active' ? 'success' : 
                                    document.status === 'Archived' ? 'default' : 'warning'}
                            />
                          </TableCell>
                          <TableCell>{document.uploadedBy || document.uploaded_by}</TableCell>
                          <TableCell>
                            {new Date(document.uploadedAt || document.uploaded_at || '').toLocaleDateString()}
                            <Typography variant="caption" color="textSecondary" display="block">
                              {new Date(document.uploadedAt || document.uploaded_at || '').toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <IconButton
                              onClick={() => handleDownload(document.fileUrl)}
                              color="primary"
                              size="small"
                            >
                              <DownloadIcon />
                            </IconButton>
                            <IconButton
                              onClick={() => handleOpen(document as Document)}
                              color="primary"
                              size="small"
                            >
                              <EditIcon />
                            </IconButton>
                            <IconButton
                              onClick={() => handleDelete(document.id)}
                              color="error"
                              size="small"
                            >
                              <DeleteIcon />
                            </IconButton>
                          </TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
              </TableContainer>
            </Paper>

            {/* Document Form Dialog */}
            <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
              <DialogTitle>
                {selectedDocument ? 'Edit Document' : 'Add New Document'}
              </DialogTitle>
              {uploadError && (
                <Alert severity="error" sx={{ mb: 2 }}>
                  {uploadError}
                </Alert>
              )}
              <DialogContent>
                <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1 }}>
                  <TextField
                    fullWidth
                    margin="normal"
                    label="Title"
                    name="title"
                    value={formData.title}
                    onChange={handleInputChange}
                    required
                  />

                  <TextField
                    fullWidth
                    margin="normal"
                    select
                    label="Type"
                    name="type"
                    value={formData.type}
                    onChange={handleInputChange}
                    required
                  >
                    {documentTypes.map((type) => (
                      <MenuItem key={type.id} value={type.name}>
                        {type.name}
                      </MenuItem>
                    ))}
                  </TextField>

                  <TextField
                    fullWidth
                    margin="normal"
                    label="Category"
                    name="category"
                    value={formData.category}
                    onChange={handleInputChange}
                    required
                  />

                  <TextField
                    fullWidth
                    margin="normal"
                    label="Tags (comma separated)"
                    name="tags"
                    value={formData.tags}
                    onChange={handleInputChange}
                  />

                  <input
                    accept="*"
                    style={{ display: 'none' }}
                    id="document-upload"
                    type="file"
                    onChange={handleFileChange}
                  />
                  <label htmlFor="document-upload">
                    <Button
                      variant="contained"
                      component="span"
                      fullWidth
                      sx={{ mt: 2 }}
                    >
                      {formData.file ? formData.file.name : 'Upload Document'}
                    </Button>
                  </label>
                </Box>
              </DialogContent>
              <DialogActions>
                <Button onClick={handleClose}>Cancel</Button>
                <Button
                  type="submit"
                  variant="contained"
                  color="primary"
                  onClick={handleSubmit}
                  disabled={uploading}
                >
                  {uploading ? <CircularProgress size={24} /> : 'Save'}
                </Button>
              </DialogActions>
            </Dialog>

            {/* Filter Dialog */}
            <Dialog 
              open={filterDialogOpen} 
              onClose={() => setFilterDialogOpen(false)} 
              maxWidth="sm" 
              fullWidth
              PaperProps={{
                sx: { borderRadius: 2 }
              }}
            >
              <DialogTitle>Filter Documents</DialogTitle>
              <DialogContent>
                <Grid container spacing={2}>
                  <Grid item xs={12}>
                    <Typography variant="subtitle2" gutterBottom>
                      Document Type
                    </Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                      {documentTypes.map((type) => (
                        <Chip
                          key={type.id}
                          label={type.name}
                          onClick={() => {
                            setActiveFilters([...activeFilters, { type: 'Type', value: type.name }]);
                            setFilterDialogOpen(false);
                          }}
                          variant="outlined"
                          clickable
                        />
                      ))}
                    </Box>
                  </Grid>
                  
                  <Grid item xs={12}>
                    <Typography variant="subtitle2" gutterBottom>
                      Status
                    </Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                      {['Active', 'Archived', 'Draft'].map((status) => (
                        <Chip
                          key={status}
                          label={status}
                          onClick={() => {
                            setActiveFilters([...activeFilters, { type: 'Status', value: status }]);
                            setFilterDialogOpen(false);
                          }}
                          variant="outlined"
                          clickable
                        />
                      ))}
                    </Box>
                  </Grid>
                </Grid>
              </DialogContent>
              <DialogActions>
                <Button onClick={() => setFilterDialogOpen(false)}>Close</Button>
              </DialogActions>
            </Dialog>
          </>
        )}
      </div>
      
      <div role="tabpanel" hidden={activeTab !== 1}>
        {activeTab === 1 && (
          <>
            {/* Subtabs for Document Assistant */}
            <Paper sx={{ mb: 3 }}>
              <Tabs
                value={verbaTabIndex}
                onChange={handleVerbaTabChange}
                aria-label="document assistant tabs"
                variant="fullWidth"
              >
                <Tab icon={<ChatIcon />} iconPosition="start" label="Chat with Documents" />
                <Tab icon={<ManageIcon />} iconPosition="start" label="Manage RAG Documents" />
              </Tabs>
            </Paper>
            
            {/* Chat Interface */}
            <div role="tabpanel" hidden={verbaTabIndex !== 0}>
              {verbaTabIndex === 0 && (
                <DocumentChat title="Apartment Documents Assistant" />
              )}
            </div>
            
            {/* Document Upload Interface */}
            <div role="tabpanel" hidden={verbaTabIndex !== 1}>
              {verbaTabIndex === 1 && (
                <>
                  <Typography variant="h6" gutterBottom>
                    RAG Document Management
                  </Typography>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    Upload documents to the RAG system to make them available for AI-powered queries. Documents uploaded here will be processed and indexed for retrieval by the document assistant.
                  </Typography>
                  <Divider sx={{ my: 2 }} />
                  <VerbaDocumentUpload 
                    collectionName="apartment_documents" 
                    onDocumentAdded={() => {
                      // Optionally refetch documents or update stats
                    }}
                  />
                </>
              )}
            </div>
          </>
        )}
      </div>
    </Box>
  );
};

export default DocumentManagement;
