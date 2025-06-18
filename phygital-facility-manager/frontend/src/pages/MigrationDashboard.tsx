import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  Button,
  Grid,
  List,
  ListItem,
  ListItemText,
  Divider,
  CircularProgress,
  Alert,
  TextField,
  Chip,
  Card,
  CardContent,
  LinearProgress,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  OutlinedInput,
  SelectChangeEvent
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  CloudUpload as CloudUploadIcon,
  Check as CheckIcon,
  Error as ErrorIcon,
  Delete as DeleteIcon
} from '@mui/icons-material';
import migrationService, { MigrationResult, MigrationStatus } from '../services/migrationService';

const MigrationDashboard: React.FC = () => {
  const [migrationStatus, setMigrationStatus] = useState<MigrationStatus | null>(null);
  const [weaviateCount, setWeaviateCount] = useState<number>(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<MigrationResult[]>([]);
  const [file, setFile] = useState<File | null>(null);
  const [fileTitle, setFileTitle] = useState('');
  const [fileCategory, setFileCategory] = useState('general');
  const [fileTags, setFileTags] = useState<string[]>([]);
  const [uploadLoading, setUploadLoading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [confirmDialogOpen, setConfirmDialogOpen] = useState(false);

  // Fetch migration status on component mount
  useEffect(() => {
    fetchMigrationStatus();
  }, []);

  const fetchMigrationStatus = async () => {
    setLoading(true);
    setError(null);
    try {
      const status = await migrationService.getMigrationStatus(weaviateCount || undefined);
      setMigrationStatus(status);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch migration status');
      console.error('Error fetching migration status:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleWeaviateCountChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseInt(e.target.value);
    setWeaviateCount(isNaN(value) ? 0 : value);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const selectedFile = e.target.files[0];
      setFile(selectedFile);
      if (!fileTitle) {
        setFileTitle(selectedFile.name);
      }
    }
  };

  const handleTagsChange = (event: SelectChangeEvent<string[]>) => {
    const value = event.target.value;
    setFileTags(typeof value === 'string' ? value.split(',') : value);
  };

  const handleUploadFile = async () => {
    if (!file) return;

    setUploadLoading(true);
    setUploadError(null);
    try {
      const result = await migrationService.migrateFile(file, {
        title: fileTitle || file.name,
        category: fileCategory,
        tags: fileTags
      });

      setResults(prev => [result, ...prev]);
      
      // Reset form
      setFile(null);
      setFileTitle('');
      setFileCategory('general');
      setFileTags([]);
      
      // Refresh migration status
      fetchMigrationStatus();
    } catch (err) {
      setUploadError(err instanceof Error ? err.message : 'Failed to upload file');
      console.error('Error uploading file:', err);
    } finally {
      setUploadLoading(false);
    }
  };

  const openConfirmDialog = () => {
    setConfirmDialogOpen(true);
  };

  const closeConfirmDialog = () => {
    setConfirmDialogOpen(false);
  };

  const handleMigrateWeaviate = async () => {
    // This is a placeholder - in a real implementation, you would:
    // 1. Fetch documents from Weaviate
    // 2. Send them to the migration service
    // For now, we'll just show an alert that this would require backend implementation
    alert('This feature requires backend implementation to fetch documents from Weaviate first.');
    closeConfirmDialog();
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        Migration Dashboard
      </Typography>
      <Typography variant="body1" paragraph>
        Manage the migration from Weaviate to OpenAI Vector Store
      </Typography>

      {/* Status Card */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Migration Status
              </Typography>
              
              {loading ? (
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <CircularProgress size={20} sx={{ mr: 1 }} />
                  <Typography variant="body2">Loading status...</Typography>
                </Box>
              ) : error ? (
                <Alert severity="error">{error}</Alert>
              ) : migrationStatus ? (
                <>
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary">
                      Status: {migrationStatus.status}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Last Updated: {new Date(migrationStatus.timestamp).toLocaleString()}
                    </Typography>
                  </Box>
                  
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="subtitle2">Document Counts</Typography>
                    <Grid container spacing={2}>
                      <Grid item xs={6}>
                        <Typography variant="body2">
                          OpenAI: {migrationStatus.document_counts.openai_count}
                        </Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="body2">
                          Weaviate: {migrationStatus.document_counts.weaviate_count}
                        </Typography>
                      </Grid>
                    </Grid>
                  </Box>
                  
                  {typeof migrationStatus.document_counts.weaviate_count === 'number' && 
                   typeof migrationStatus.document_counts.openai_count === 'number' && (
                    <Box sx={{ width: '100%', mb: 1 }}>
                      <LinearProgress 
                        variant="determinate" 
                        value={Math.min(
                          (migrationStatus.document_counts.openai_count / 
                           (migrationStatus.document_counts.weaviate_count || 1)) * 100, 
                          100
                        )} 
                      />
                      <Typography variant="body2" align="right" sx={{ mt: 0.5 }}>
                        {Math.round(
                          (migrationStatus.document_counts.openai_count / 
                           (migrationStatus.document_counts.weaviate_count || 1)) * 100
                        )}% Complete
                      </Typography>
                    </Box>
                  )}
                </>
              ) : (
                <Typography variant="body2" color="text.secondary">
                  No status information available
                </Typography>
              )}
              
              <Box sx={{ mt: 2, display: 'flex', alignItems: 'center' }}>
                <TextField
                  label="Weaviate Document Count"
                  type="number"
                  size="small"
                  value={weaviateCount}
                  onChange={handleWeaviateCountChange}
                  sx={{ mr: 2, flexGrow: 1 }}
                />
                <Button
                  variant="outlined"
                  startIcon={<RefreshIcon />}
                  onClick={fetchMigrationStatus}
                  disabled={loading}
                >
                  Refresh
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Migration Actions
              </Typography>
              
              <Box sx={{ mb: 3 }}>
                <Button
                  variant="contained"
                  color="primary"
                  startIcon={<CloudUploadIcon />}
                  fullWidth
                  onClick={openConfirmDialog}
                  sx={{ mb: 2 }}
                >
                  Migrate All Weaviate Documents
                </Button>
                
                <Typography variant="body2" color="text.secondary">
                  This will migrate all documents from Weaviate to OpenAI Vector Store.
                  Make sure you have backed up your data before proceeding.
                </Typography>
              </Box>
              
              <Divider sx={{ my: 2 }} />
              
              <Typography variant="subtitle1" gutterBottom>
                Upload Single Document
              </Typography>
              
              <Box component="form" sx={{ mt: 2 }}>
                <Button
                  variant="outlined"
                  component="label"
                  startIcon={<CloudUploadIcon />}
                  fullWidth
                  sx={{ mb: 2 }}
                >
                  Select File
                  <input
                    type="file"
                    hidden
                    onChange={handleFileChange}
                    accept=".pdf,.txt,.md,.doc,.docx,.csv,.json"
                  />
                </Button>
                
                {file && (
                  <Box sx={{ mb: 2 }}>
                    <Chip 
                      label={file.name} 
                      onDelete={() => setFile(null)}
                      sx={{ maxWidth: '100%' }}
                    />
                  </Box>
                )}
                
                <TextField
                  label="Document Title"
                  fullWidth
                  value={fileTitle}
                  onChange={(e) => setFileTitle(e.target.value)}
                  margin="normal"
                  size="small"
                />
                
                <FormControl fullWidth margin="normal" size="small">
                  <InputLabel>Category</InputLabel>
                  <Select
                    value={fileCategory}
                    onChange={(e) => setFileCategory(e.target.value)}
                    label="Category"
                  >
                    <MenuItem value="general">General</MenuItem>
                    <MenuItem value="policy">Policy</MenuItem>
                    <MenuItem value="manual">Manual</MenuItem>
                    <MenuItem value="guide">Guide</MenuItem>
                    <MenuItem value="faq">FAQ</MenuItem>
                  </Select>
                </FormControl>
                
                <FormControl fullWidth margin="normal" size="small">
                  <InputLabel>Tags</InputLabel>
                  <Select
                    multiple
                    value={fileTags}
                    onChange={handleTagsChange}
                    input={<OutlinedInput label="Tags" />}
                    renderValue={(selected) => (
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                        {selected.map((value) => (
                          <Chip key={value} label={value} size="small" />
                        ))}
                      </Box>
                    )}
                  >
                    <MenuItem value="apartment">Apartment</MenuItem>
                    <MenuItem value="facility">Facility</MenuItem>
                    <MenuItem value="maintenance">Maintenance</MenuItem>
                    <MenuItem value="amenities">Amenities</MenuItem>
                    <MenuItem value="rules">Rules</MenuItem>
                  </Select>
                </FormControl>
                
                {uploadError && (
                  <Alert severity="error" sx={{ mt: 2 }}>
                    {uploadError}
                  </Alert>
                )}
                
                <Button
                  variant="contained"
                  color="primary"
                  onClick={handleUploadFile}
                  disabled={!file || uploadLoading}
                  fullWidth
                  sx={{ mt: 2 }}
                >
                  {uploadLoading ? 'Uploading...' : 'Upload & Migrate'}
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Results List */}
      <Paper sx={{ p: 2, mb: 4 }}>
        <Typography variant="h6" gutterBottom>
          Migration Results
        </Typography>
        
        {results.length === 0 ? (
          <Typography variant="body2" color="text.secondary" sx={{ py: 2 }}>
            No migration results to display
          </Typography>
        ) : (
          <List>
            {results.map((result, index) => (
              <React.Fragment key={index}>
                {index > 0 && <Divider />}
                <ListItem>
                  <ListItemText
                    primary={result.title}
                    secondary={
                      <>
                        <Typography component="span" variant="body2" color="text.primary">
                          Status: {result.status === 'migrated' ? 'Success' : 'Failed'}
                        </Typography>
                        {result.error && (
                          <Typography component="span" variant="body2" color="error" display="block">
                            Error: {result.error}
                          </Typography>
                        )}
                        {result.openai_file_id && (
                          <Typography component="span" variant="body2" display="block">
                            File ID: {result.openai_file_id}
                          </Typography>
                        )}
                      </>
                    }
                  />
                  {result.status === 'migrated' ? (
                    <Chip 
                      icon={<CheckIcon />} 
                      label="Success" 
                      color="success" 
                      variant="outlined" 
                    />
                  ) : (
                    <Chip 
                      icon={<ErrorIcon />} 
                      label="Failed" 
                      color="error" 
                      variant="outlined" 
                    />
                  )}
                </ListItem>
              </React.Fragment>
            ))}
          </List>
        )}
      </Paper>

      {/* Confirmation Dialog */}
      <Dialog
        open={confirmDialogOpen}
        onClose={closeConfirmDialog}
      >
        <DialogTitle>Confirm Migration</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to migrate all documents from Weaviate to OpenAI Vector Store?
            This process cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={closeConfirmDialog} color="primary">
            Cancel
          </Button>
          <Button onClick={handleMigrateWeaviate} color="primary" variant="contained">
            Confirm Migration
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default MigrationDashboard;
