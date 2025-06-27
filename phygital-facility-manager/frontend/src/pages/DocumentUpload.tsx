import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Typography,
  Button,
  Paper,
  Grid,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  CircularProgress,
  Alert,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Divider,
  Card,
  CardContent,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  Tabs,
  Tab
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import DeleteIcon from '@mui/icons-material/Delete';
import DescriptionIcon from '@mui/icons-material/Description';
import ArticleIcon from '@mui/icons-material/Article';
import DownloadIcon from '@mui/icons-material/Download';
import SearchIcon from '@mui/icons-material/Search';
import UploadIcon from '@mui/icons-material/Upload';
import documentService, { Document } from '../services/documentService';
import SemanticSearch from '../components/SemanticSearch';

// Using the Document interface imported from documentService

const DocumentUpload: React.FC = () => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [title, setTitle] = useState('');
  const [category, setCategory] = useState('');
  const [documentType, setDocumentType] = useState('');
  const [tags, setTags] = useState<string[]>([]);
  const [tagInput, setTagInput] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [documentToDelete, setDocumentToDelete] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState(0);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Document categories and types
  const categories = ['Community Rules', 'Maintenance', 'Amenities', 'Security', 'Billing', 'General'];
  const documentTypes = ['PDF', 'Word Document', 'Image', 'Spreadsheet', 'Presentation', 'Other'];

  // Load documents on component mount
  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    setIsLoading(true);
    try {
      const response = await documentService.getDocuments();
      setDocuments(response);
      setError(null);
    } catch (err: any) {
      console.error('Error fetching documents:', err);
      setError('Failed to load documents. Please try again later.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      setSelectedFile(event.target.files[0]);
    }
  };

  const handleTagInputKeyDown = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' || event.key === ',') {
      event.preventDefault();
      addTag();
    }
  };

  const addTag = () => {
    const trimmedTag = tagInput.trim();
    if (trimmedTag && !tags.includes(trimmedTag)) {
      setTags([...tags, trimmedTag]);
      setTagInput('');
    }
  };

  const removeTag = (tagToRemove: string) => {
    setTags(tags.filter(tag => tag !== tagToRemove));
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    
    if (!title || !category || !documentType || !selectedFile) {
      setError('Please fill in all required fields and select a file.');
      return;
    }

    setIsUploading(true);
    setError(null);
    setSuccess(null);

    try {
      // Use the correct parameters for createDocument based on its interface
      await documentService.createDocument(
        title,
        selectedFile.name, // Using filename as description
        category,
        tags,
        selectedFile
      );
      
      // Reset form
      setTitle('');
      setCategory('');
      setDocumentType('');
      setTags([]);
      setSelectedFile(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
      
      setSuccess('Document uploaded successfully!');
      
      // Refresh document list
      fetchDocuments();
    } catch (err: any) {
      console.error('Error uploading document:', err);
      setError(err.message || 'Failed to upload document. Please try again.');
    } finally {
      setIsUploading(false);
    }
  };

  const handleDeleteClick = (documentId: string) => {
    setDocumentToDelete(documentId);
    setDeleteDialogOpen(true);
  };

  const confirmDelete = async () => {
    if (!documentToDelete) return;
    
    try {
      await documentService.deleteDocument(documentToDelete);
      setDocuments(documents.filter(doc => doc.id !== documentToDelete));
      setSuccess('Document deleted successfully!');
    } catch (err: any) {
      console.error('Error deleting document:', err);
      setError(err.message || 'Failed to delete document. Please try again.');
    } finally {
      setDeleteDialogOpen(false);
      setDocumentToDelete(null);
    }
  };

  const handleDownload = async (documentId: string) => {
    try {
      await documentService.downloadDocument(documentId);
    } catch (err: any) {
      console.error('Error downloading document:', err);
      setError(err.message || 'Failed to download document. Please try again.');
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return bytes + ' bytes';
    else if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
    else return (bytes / 1048576).toFixed(1) + ' MB';
  };

  const getFileIcon = (fileType?: string) => {
    switch (fileType) {
      case 'application/pdf':
        return <ArticleIcon color="error" />;
      case 'application/msword':
      case 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
        return <ArticleIcon color="primary" />;
      case 'application/vnd.ms-excel':
      case 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
        return <ArticleIcon color="success" />;
      default:
        return <DescriptionIcon />;
    }
  };

  return (
    <Box>
      <Typography variant="h5" component="h1" gutterBottom>
        Knowledge Base Document Management
      </Typography>

      {/* Tabs */}
      <Paper elevation={1} sx={{ mb: 3 }}>
        <Tabs
          value={activeTab}
          onChange={(_, newValue) => setActiveTab(newValue)}
          variant="fullWidth"
        >
          <Tab
            icon={<UploadIcon />}
            label="Upload & Manage"
            id="tab-0"
            aria-controls="tabpanel-0"
          />
          <Tab
            icon={<SearchIcon />}
            label="Semantic Search"
            id="tab-1"
            aria-controls="tabpanel-1"
          />
        </Tabs>
      </Paper>

      {/* Tab Content */}
      {activeTab === 0 && (
        <Grid container spacing={3}>
        {/* Upload Form */}
        <Grid item xs={12} md={5}>
          <Paper elevation={2} sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Upload New Document
            </Typography>
            <Divider sx={{ mb: 2 }} />

            {error && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {error}
              </Alert>
            )}

            {success && (
              <Alert severity="success" sx={{ mb: 2 }}>
                {success}
              </Alert>
            )}

            <Box component="form" onSubmit={handleSubmit} sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <TextField
                label="Document Title"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                fullWidth
                required
              />

              <FormControl fullWidth required>
                <InputLabel>Category</InputLabel>
                <Select
                  value={category}
                  label="Category"
                  onChange={(e) => setCategory(e.target.value)}
                >
                  {categories.map((cat) => (
                    <MenuItem key={cat} value={cat}>{cat}</MenuItem>
                  ))}
                </Select>
              </FormControl>

              <FormControl fullWidth required>
                <InputLabel>Document Type</InputLabel>
                <Select
                  value={documentType}
                  label="Document Type"
                  onChange={(e) => setDocumentType(e.target.value)}
                >
                  {documentTypes.map((type) => (
                    <MenuItem key={type} value={type}>{type}</MenuItem>
                  ))}
                </Select>
              </FormControl>

              <Box>
                <TextField
                  label="Tags (press Enter to add)"
                  value={tagInput}
                  onChange={(e) => setTagInput(e.target.value)}
                  onKeyDown={handleTagInputKeyDown}
                  onBlur={addTag}
                  fullWidth
                />
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 1 }}>
                  {tags.map((tag) => (
                    <Chip
                      key={tag}
                      label={tag}
                      onDelete={() => removeTag(tag)}
                      size="small"
                    />
                  ))}
                </Box>
              </Box>

              <Box sx={{ mt: 1 }}>
                <input
                  accept="application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document,image/*"
                  style={{ display: 'none' }}
                  id="file-upload"
                  type="file"
                  onChange={handleFileChange}
                  ref={fileInputRef}
                />
                <label htmlFor="file-upload">
                  <Button
                    variant="outlined"
                    component="span"
                    startIcon={<CloudUploadIcon />}
                    fullWidth
                  >
                    {selectedFile ? selectedFile.name : 'Select File'}
                  </Button>
                </label>
                {selectedFile && (
                  <Typography variant="caption" display="block" sx={{ mt: 1 }}>
                    Size: {formatFileSize(selectedFile.size)}
                  </Typography>
                )}
              </Box>

              <Button
                type="submit"
                variant="contained"
                color="primary"
                disabled={isUploading}
                startIcon={isUploading ? <CircularProgress size={20} /> : <CloudUploadIcon />}
                sx={{ mt: 2 }}
              >
                {isUploading ? 'Uploading...' : 'Upload Document'}
              </Button>
            </Box>
          </Paper>
        </Grid>

        {/* Document List */}
        <Grid item xs={12} md={7}>
          <Paper elevation={2} sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Knowledge Base Documents
            </Typography>
            <Divider sx={{ mb: 2 }} />

            {isLoading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
                <CircularProgress />
              </Box>
            ) : documents.length === 0 ? (
              <Alert severity="info">No documents found. Upload your first document!</Alert>
            ) : (
              <List>
                {documents.map((doc) => (
                  <Card key={doc.id} sx={{ mb: 2 }}>
                    <CardContent sx={{ pb: 1 }}>
                      <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 1 }}>
                        <Box sx={{ mr: 2 }}>
                          {getFileIcon(doc.file_type)}
                        </Box>
                        <Box sx={{ flexGrow: 1 }}>
                          <Typography variant="subtitle1" component="div">
                            {doc.title}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            {doc.category || 'Uncategorized'} • {doc.file_type || 'Document'} • {formatFileSize(doc.file_size || 0)}
                          </Typography>
                          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mt: 1 }}>
                            {doc.tags && doc.tags.map((tag) => (
                              <Chip key={tag} label={tag} size="small" variant="outlined" />
                            ))}
                          </Box>
                        </Box>
                        <Box>
                          <IconButton 
                            aria-label="download" 
                            onClick={() => handleDownload(doc.id)}
                            size="small"
                          >
                            <DownloadIcon fontSize="small" />
                          </IconButton>
                          <IconButton 
                            aria-label="delete" 
                            onClick={() => handleDeleteClick(doc.id)}
                            size="small"
                            color="error"
                          >
                            <DeleteIcon fontSize="small" />
                          </IconButton>
                        </Box>
                      </Box>
                      {doc.summary && (
                        <Typography variant="body2" color="text.secondary" sx={{ mt: 1, fontSize: '0.875rem' }}>
                          {doc.summary}
                        </Typography>
                      )}
                    </CardContent>
                  </Card>
                ))}
              </List>
            )}
          </Paper>
        </Grid>
      </Grid>
      )}

      {/* Semantic Search Tab */}
      {activeTab === 1 && (
        <Box>
          <Typography variant="h6" gutterBottom>
            AI-Powered Document Search
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            Search through uploaded documents using natural language. The AI will find relevant documents based on meaning, not just keywords.
          </Typography>

          <SemanticSearch
            onResultSelect={(result) => {
              console.log('Selected document:', result);
              // You can add custom handling here, like opening the document
            }}
            maxResults={20}
            showFilters={true}
          />
        </Box>
      )}

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
      >
        <DialogTitle>Confirm Deletion</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete this document? This action cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
          <Button onClick={confirmDelete} color="error" autoFocus>
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default DocumentUpload;
