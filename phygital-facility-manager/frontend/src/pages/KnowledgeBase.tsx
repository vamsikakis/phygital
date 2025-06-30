import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  TextField,
  InputAdornment,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Card,
  CardContent,
  Divider,
  Chip,
  IconButton,
  Paper,
  Grid,
  Button,
  CircularProgress,
  Alert,
  Menu,
  MenuItem,
  Tooltip
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import DescriptionIcon from '@mui/icons-material/Description';
import GavelIcon from '@mui/icons-material/Gavel';
import HandymanIcon from '@mui/icons-material/Handyman';
import PoolIcon from '@mui/icons-material/Pool';
import WarningIcon from '@mui/icons-material/Warning';
import FileDownloadIcon from '@mui/icons-material/FileDownload';
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import RefreshIcon from '@mui/icons-material/Refresh';
import MoreVertIcon from '@mui/icons-material/MoreVert';

interface Document {
  id: string;
  title?: string;
  filename?: string;
  description?: string;
  created_at?: string;
  uploaded_at?: string;
  category?: string;
  file_id?: string;
  file_size?: number;
  meta_data?: {
    size?: number;
    purpose?: string;
  };
  source?: 'openai' | 'community_drive';
  downloadable?: boolean;
}

const KnowledgeBase: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [downloadingId, setDownloadingId] = useState<string | null>(null);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedDoc, setSelectedDoc] = useState<Document | null>(null);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    setLoading(true);
    setError(null);
    try {
      // Load from both OpenAI and Community Drive
      const [openaiResponse, communityResponse] = await Promise.all([
        fetch('/api/documents'),
        fetch('/api/community-drive/documents')
      ]);

      const openaiData = await openaiResponse.json();
      const communityData = await communityResponse.json();

      let allDocuments = [];

      // Add OpenAI documents (not downloadable)
      if (openaiResponse.ok && openaiData.documents) {
        const openaiDocs = openaiData.documents.map(doc => ({
          ...doc,
          source: 'openai',
          downloadable: false
        }));
        allDocuments = [...allDocuments, ...openaiDocs];
      }

      // Add Community Drive documents (downloadable)
      if (communityResponse.ok && communityData.documents) {
        const communityDocs = communityData.documents.map(doc => ({
          ...doc,
          source: 'community_drive',
          downloadable: true
        }));
        allDocuments = [...allDocuments, ...communityDocs];
      }

      // Remove duplicates (prefer community drive versions)
      const uniqueDocuments = [];
      const seenFilenames = new Set();

      // First add community drive documents
      allDocuments.filter(doc => doc.source === 'community_drive').forEach(doc => {
        uniqueDocuments.push(doc);
        seenFilenames.add(doc.filename);
      });

      // Then add OpenAI documents that aren't already in community drive
      allDocuments.filter(doc => doc.source === 'openai').forEach(doc => {
        if (!seenFilenames.has(doc.filename)) {
          uniqueDocuments.push(doc);
        }
      });

      setDocuments(uniqueDocuments);

    } catch (error) {
      setError('Failed to connect to server');
      console.error('Error loading documents:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async (doc: Document & { source?: string; downloadable?: boolean }) => {
    setDownloadingId(doc.id);
    try {
      if (doc.source === 'community_drive' && doc.downloadable) {
        // Download from community drive
        const response = await fetch(`/api/community-drive/documents/${doc.id}/download`);

        if (response.ok) {
          // Create blob and download
          const blob = await response.blob();
          const url = window.URL.createObjectURL(blob);
          const link = document.createElement('a');
          link.href = url;
          link.download = doc.filename || doc.title;
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
          window.URL.revokeObjectURL(url);
        } else {
          const data = await response.json();
          setError(data.error || 'Failed to download document');
        }
      } else {
        // Handle OpenAI documents (not downloadable)
        setError(
          `This document is stored in the AI system and cannot be downloaded directly.\n\n` +
          `Alternatives:\n` +
          `• Ask the AI Assistant about this document's content\n` +
          `• Contact facility management for a downloadable copy\n` +
          `• Check if a downloadable version is available in the community drive`
        );
      }
    } catch (error) {
      setError('Failed to connect to server');
      console.error('Error downloading document:', error);
    } finally {
      setDownloadingId(null);
    }
  };

  const handleGeneratePDF = async (doc: Document) => {
    setDownloadingId(doc.id);
    try {
      const response = await fetch(`/api/documents/${doc.id}/pdf`);
      const data = await response.json();

      if (response.ok && data.download_url) {
        // Create a temporary link to download the PDF
        const link = document.createElement('a');
        link.href = data.download_url;
        link.download = `${doc.title}.pdf`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      } else {
        // Handle the limitation message
        const message = data.message || data.error || 'PDF generation not available';
        const alternatives = data.alternatives || [];

        let fullMessage = message;
        if (alternatives.length > 0) {
          fullMessage += '\n\nAlternatives:\n' + alternatives.map(alt => `• ${alt}`).join('\n');
        }

        setError(fullMessage);
      }
    } catch (error) {
      setError('Failed to connect to server');
      console.error('Error generating PDF:', error);
    } finally {
      setDownloadingId(null);
    }
  };

  const handleMenuClick = (event: React.MouseEvent<HTMLElement>, docItem: Document) => {
    setAnchorEl(event.currentTarget);
    setSelectedDoc(docItem);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedDoc(null);
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const uploadedFile = event.target.files?.[0];
    if (!uploadedFile) return;

    setUploading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', uploadedFile);
      formData.append('category', 'general');
      formData.append('description', `Community document: ${uploadedFile.name}`);

      // Upload to community drive (which also uploads to OpenAI)
      const response = await fetch('/api/community-drive/documents/upload', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (response.ok) {
        // Reload documents to show the new upload
        await loadDocuments();
        setError(null);
      } else {
        setError(data.error || 'Failed to upload document');
      }
    } catch (error) {
      setError('Failed to upload document');
      console.error('Error uploading document:', error);
    } finally {
      setUploading(false);
      // Reset the input
      event.target.value = '';
    }
  };

  const getDocumentIcon = (filename: string = '', category: string = '') => {
    const ext = filename.split('.').pop()?.toLowerCase() || '';

    if (ext === 'pdf') return <PictureAsPdfIcon />;
    if (category === 'bylaws') return <GavelIcon />;
    if (category === 'maintenance') return <HandymanIcon />;
    if (category === 'amenities' || category === 'facilities') return <PoolIcon />;
    if (category === 'emergency' || category === 'security') return <WarningIcon />;

    return <DescriptionIcon />;
  };

  const getDocumentColor = (category: string = '') => {
    switch (category.toLowerCase()) {
      case 'bylaws': return '#3f51b5';
      case 'maintenance': return '#ff9800';
      case 'amenities':
      case 'facilities': return '#2196f3';
      case 'emergency':
      case 'security': return '#f44336';
      case 'general': return '#4caf50';
      case 'official': return '#9c27b0';
      default: return '#4caf50';
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleDateString();
    } catch {
      return dateString;
    }
  };

  // Filter documents based on search query
  const filteredDocuments = documents.filter(doc => {
    const title = doc.title || '';
    const description = doc.description || '';
    const filename = doc.filename || '';
    const query = searchQuery.toLowerCase();

    return title.toLowerCase().includes(query) ||
           description.toLowerCase().includes(query) ||
           filename.toLowerCase().includes(query);
  });

  // FAQ data
  const faqs = [
    {
      question: "What are the rules for using the swimming pool?",
      answer: "The pool is open from 6 AM to 10 PM daily. No diving is allowed, and children under 12 must be accompanied by an adult. No food or glass containers are permitted in the pool area."
    },
    {
      question: "How do I submit a maintenance request?",
      answer: "You can submit maintenance requests through the Help Desk section of this app. Requests are typically addressed within 48 hours depending on urgency."
    },
    {
      question: "What are the parking regulations?",
      answer: "Each unit is assigned specific parking slots. Visitor parking is available for guests but limited to 24 hours unless approved by management. No commercial vehicles are allowed to be parked overnight."
    }
  ];

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h5" component="h1">
          Apartment Knowledge Base
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <input
            accept=".pdf,.doc,.docx,.txt"
            style={{ display: 'none' }}
            id="upload-file"
            type="file"
            onChange={handleFileUpload}
          />
          <label htmlFor="upload-file">
            <Button
              variant="contained"
              component="span"
              startIcon={<CloudUploadIcon />}
              disabled={uploading}
            >
              {uploading ? 'Uploading...' : 'Upload Document'}
            </Button>
          </label>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={loadDocuments}
            disabled={loading}
          >
            Refresh
          </Button>
        </Box>
      </Box>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Search Bar */}
      <TextField
        fullWidth
        variant="outlined"
        placeholder="Search for documents, policies, or information..."
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
        margin="normal"
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <SearchIcon />
            </InputAdornment>
          ),
        }}
        sx={{ mb: 3 }}
      />
      
      {/* Main Content */}
      <Grid container spacing={3}>
        {/* Document List */}
        <Grid item xs={12} md={8}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">
              Documents & Resources ({filteredDocuments.length})
            </Typography>
          </Box>

          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
              <CircularProgress />
            </Box>
          ) : filteredDocuments.length === 0 ? (
            <Paper sx={{ p: 4, textAlign: 'center' }}>
              <Typography variant="body1" color="text.secondary">
                {documents.length === 0 ? 'No documents uploaded yet.' : 'No documents match your search.'}
              </Typography>
            </Paper>
          ) : (
            <List>
              {filteredDocuments.map((doc) => (
                <Card key={doc.id} sx={{ mb: 2 }}>
                  <CardContent sx={{ padding: 2 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                      <Box sx={{ display: 'flex', alignItems: 'flex-start', flex: 1 }}>
                        <ListItemIcon sx={{ color: getDocumentColor(doc.category || ''), minWidth: 40 }}>
                          {getDocumentIcon(doc.filename || '', doc.category || '')}
                        </ListItemIcon>
                        <Box sx={{ flex: 1 }}>
                          <Typography variant="subtitle1" component="div">
                            {doc.title || doc.filename || 'Untitled Document'}
                          </Typography>
                          <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                            {doc.description || 'No description available'}
                          </Typography>
                          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                            <Chip
                              label={`${formatFileSize(doc.meta_data?.size || doc.file_size || 0)}`}
                              size="small"
                              variant="outlined"
                            />
                            <Chip
                              label={`Uploaded: ${formatDate(doc.created_at || doc.uploaded_at)}`}
                              size="small"
                              variant="outlined"
                            />
                            <Chip
                              label={doc.category || 'general'}
                              size="small"
                              sx={{ backgroundColor: getDocumentColor(doc.category || ''), color: 'white' }}
                            />
                            {(doc as any).downloadable ? (
                              <Chip
                                label="Downloadable"
                                size="small"
                                sx={{ backgroundColor: '#4caf50', color: 'white' }}
                              />
                            ) : (
                              <Chip
                                label="AI Only"
                                size="small"
                                sx={{ backgroundColor: '#ff9800', color: 'white' }}
                              />
                            )}
                          </Box>
                        </Box>
                      </Box>
                      <Box sx={{ display: 'flex', alignItems: 'center', ml: 1 }}>
                        <Tooltip title="Download Original">
                          <IconButton
                            onClick={() => handleDownload(doc)}
                            disabled={downloadingId === doc.id}
                            size="small"
                          >
                            {downloadingId === doc.id ? (
                              <CircularProgress size={20} />
                            ) : (
                              <FileDownloadIcon />
                            )}
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="More Options">
                          <IconButton
                            onClick={(e) => handleMenuClick(e, doc)}
                            size="small"
                          >
                            <MoreVertIcon />
                          </IconButton>
                        </Tooltip>
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              ))}
            </List>
          )}
        </Grid>
        
        {/* FAQ Section */}
        <Grid item xs={12} md={4}>
          <Paper elevation={2} sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Frequently Asked Questions
            </Typography>
            <Divider sx={{ mb: 2 }} />
            {faqs.map((faq, index) => (
              <Box key={index} sx={{ mb: 3 }}>
                <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                  {faq.question}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {faq.answer}
                </Typography>
                {index < faqs.length - 1 && <Divider sx={{ mt: 2 }} />}
              </Box>
            ))}
          </Paper>
        </Grid>
      </Grid>

      {/* Context Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={() => {
          if (selectedDoc) handleDownload(selectedDoc);
          handleMenuClose();
        }}>
          <FileDownloadIcon sx={{ mr: 1 }} />
          Download Original
        </MenuItem>
        <MenuItem onClick={() => {
          if (selectedDoc) handleGeneratePDF(selectedDoc);
          handleMenuClose();
        }}>
          <PictureAsPdfIcon sx={{ mr: 1 }} />
          Generate PDF
        </MenuItem>
      </Menu>
    </Box>
  );
};

export default KnowledgeBase;
