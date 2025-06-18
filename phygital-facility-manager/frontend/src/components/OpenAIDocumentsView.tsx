import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
  IconButton,
  Divider,
  CircularProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Chip
} from '@mui/material';
import {
  CloudUpload as CloudUploadIcon,
  Description as DescriptionIcon,
  Delete as DeleteIcon,
  Refresh as RefreshIcon,
  PictureAsPdf as PdfIcon,
  InsertDriveFile as FileIcon,
  Image as ImageIcon
} from '@mui/icons-material';
import openaiAssistantService, { FileResponse } from '../services/openaiAssistantService';

const OpenAIDocumentsView: React.FC = () => {
  const [files, setFiles] = useState<FileResponse[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [uploadLoading, setUploadLoading] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [fileToDelete, setFileToDelete] = useState<FileResponse | null>(null);

  // Load files on component mount
  useEffect(() => {
    loadFiles();
  }, []);

  const loadFiles = async () => {
    setLoading(true);
    setError(null);
    try {
      const filesList = await openaiAssistantService.listFiles();
      setFiles(filesList);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load files');
      console.error('Error loading files:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = event.target.files;
    if (!selectedFiles || selectedFiles.length === 0) return;

    setUploadLoading(true);
    setError(null);

    try {
      // Upload each file
      for (let i = 0; i < selectedFiles.length; i++) {
        const file = selectedFiles[i];
        await openaiAssistantService.uploadFile(file);
      }
      
      // Reload the file list
      await loadFiles();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to upload file');
      console.error('Error uploading file:', err);
    } finally {
      setUploadLoading(false);
      // Reset the file input
      event.target.value = '';
    }
  };

  const openDeleteDialog = (file: FileResponse) => {
    setFileToDelete(file);
    setDeleteDialogOpen(true);
  };

  const closeDeleteDialog = () => {
    setDeleteDialogOpen(false);
    setFileToDelete(null);
  };

  const handleDeleteFile = async () => {
    if (!fileToDelete) return;
    
    setDeleteDialogOpen(false);
    setLoading(true);
    setError(null);
    
    try {
      await openaiAssistantService.deleteFile(fileToDelete.file_id);
      setFiles(files.filter(f => f.file_id !== fileToDelete.file_id));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete file');
      console.error('Error deleting file:', err);
    } finally {
      setLoading(false);
      setFileToDelete(null);
    }
  };

  const getFileIcon = (filename: string) => {
    const extension = filename.split('.').pop()?.toLowerCase();
    
    if (extension === 'pdf') {
      return <PdfIcon />;
    } else if (['jpg', 'jpeg', 'png', 'gif', 'svg'].includes(extension || '')) {
      return <ImageIcon />;
    } else {
      return <FileIcon />;
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const formatDate = (timestamp: number): string => {
    return new Date(timestamp * 1000).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
        <Typography variant="h6" component="div">
          Knowledge Base Documents
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Manage documents for the AI Assistant
        </Typography>
      </Box>

      {/* Actions */}
      <Box sx={{ p: 2, display: 'flex', gap: 2 }}>
        <Button
          variant="contained"
          startIcon={<CloudUploadIcon />}
          component="label"
          disabled={uploadLoading}
        >
          {uploadLoading ? 'Uploading...' : 'Upload Document'}
          <input
            type="file"
            hidden
            onChange={handleFileUpload}
            multiple
            accept=".pdf,.txt,.md,.doc,.docx,.csv,.json"
          />
        </Button>
        <Button
          variant="outlined"
          startIcon={<RefreshIcon />}
          onClick={loadFiles}
          disabled={loading}
        >
          Refresh
        </Button>
      </Box>

      {/* Error Display */}
      {error && (
        <Box sx={{ px: 2, pb: 2 }}>
          <Alert severity="error" onClose={() => setError(null)}>
            {error}
          </Alert>
        </Box>
      )}

      {/* Loading Indicator */}
      {(loading || uploadLoading) && (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 2 }}>
          <CircularProgress size={24} />
        </Box>
      )}

      {/* Files List */}
      <Box sx={{ flexGrow: 1, overflow: 'auto', p: 2 }}>
        <Paper elevation={1}>
          {files.length === 0 ? (
            <Box sx={{ p: 4, textAlign: 'center' }}>
              <DescriptionIcon sx={{ fontSize: 60, color: 'text.secondary', mb: 2 }} />
              <Typography variant="body1" color="text.secondary">
                No documents uploaded yet
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                Upload documents to enhance the AI Assistant's knowledge
              </Typography>
            </Box>
          ) : (
            <List>
              {files.map((file, index) => (
                <React.Fragment key={file.file_id}>
                  {index > 0 && <Divider />}
                  <ListItem>
                    <ListItemIcon>
                      {getFileIcon(file.filename)}
                    </ListItemIcon>
                    <ListItemText
                      primary={file.filename}
                      secondary={
                        <React.Fragment>
                          <Typography variant="body2" component="span" color="text.secondary">
                            {formatFileSize(file.bytes)} • Uploaded {formatDate(file.created_at)}
                          </Typography>
                          <Box sx={{ mt: 1 }}>
                            <Chip 
                              size="small" 
                              label={file.purpose} 
                              color="primary" 
                              variant="outlined" 
                              sx={{ mr: 1 }}
                            />
                          </Box>
                        </React.Fragment>
                      }
                    />
                    <ListItemSecondaryAction>
                      <IconButton 
                        edge="end" 
                        aria-label="delete"
                        onClick={() => openDeleteDialog(file)}
                      >
                        <DeleteIcon />
                      </IconButton>
                    </ListItemSecondaryAction>
                  </ListItem>
                </React.Fragment>
              ))}
            </List>
          )}
        </Paper>
      </Box>

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={closeDeleteDialog}
        aria-labelledby="delete-dialog-title"
        aria-describedby="delete-dialog-description"
      >
        <DialogTitle id="delete-dialog-title">
          Delete Document
        </DialogTitle>
        <DialogContent>
          <DialogContentText id="delete-dialog-description">
            Are you sure you want to delete "{fileToDelete?.filename}"? 
            This will remove the document from the AI Assistant's knowledge base.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={closeDeleteDialog} color="primary">
            Cancel
          </Button>
          <Button onClick={handleDeleteFile} color="error" autoFocus>
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default OpenAIDocumentsView;
