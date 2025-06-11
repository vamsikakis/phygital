import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Paper, 
  Typography, 
  Button, 
  TextField, 
  Grid, 
  CircularProgress, 
  Alert, 
  IconButton, 
  Chip,
  Card,
  CardContent,
  CardActions,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  MenuItem
} from '@mui/material';
import { 
  CloudUpload as UploadIcon, 
  Delete as DeleteIcon,
  Refresh as RefreshIcon,
  ArticleIcon
} from '@mui/icons-material';
import verbaService, { VerbaDocument } from '../../services/verbaService';

interface VerbaDocumentUploadProps {
  collectionName?: string;
  onDocumentAdded?: () => void;
}

interface SampleDocument {
  title: string;
  filename: string;
  category: string;
}

const VerbaDocumentUpload: React.FC<VerbaDocumentUploadProps> = ({ 
  collectionName = 'apartment_documents',
  onDocumentAdded 
}) => {
  // State for form data
  const [formData, setFormData] = useState({
    title: '',
    category: '',
    tags: '',
  });
  
  // File upload state
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<{
    success: boolean;
    message: string;
  } | null>(null);
  
  // Indexed documents state
  const [indexedDocuments, setIndexedDocuments] = useState<VerbaDocument[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [collections, setCollections] = useState<string[]>([]);
  const [selectedCollection, setSelectedCollection] = useState(collectionName);

  // Fetch indexed documents and collections on component mount
  useEffect(() => {
    fetchDocuments();
    fetchCollections();
  }, [selectedCollection]);

  // Fetch available collections
  const fetchCollections = async () => {
    try {
      const collections = await verbaService.getCollections();
      setCollections(collections);
    } catch (error) {
      console.error('Error fetching collections:', error);
    }
  };

  // Fetch indexed documents
  const fetchDocuments = async () => {
    setIsLoading(true);
    try {
      const documents = await verbaService.getDocuments(selectedCollection);
      setIndexedDocuments(documents);
    } catch (error) {
      console.error('Error fetching indexed documents:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle file selection
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setSelectedFile(e.target.files[0]);
    }
  };

  // Handle form input changes
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!selectedFile) {
      setUploadStatus({
        success: false,
        message: 'Please select a file to upload',
      });
      return;
    }
    
    setIsUploading(true);
    setUploadStatus(null);
    
    try {
      // Create FormData object with file and metadata
      const uploadData = new FormData();
      uploadData.append('file', selectedFile);
      uploadData.append('collection', selectedCollection);
      uploadData.append('title', formData.title || selectedFile.name);
      uploadData.append('category', formData.category);
      uploadData.append('tags', formData.tags);
      
      // Upload document to Verba
      const response = await verbaService.uploadDocument(uploadData);
      
      setUploadStatus({
        success: true,
        message: `Document "${formData.title || selectedFile.name}" uploaded successfully`,
      });
      
      // Reset form
      setFormData({
        title: '',
        category: '',
        tags: '',
      });
      setSelectedFile(null);
      
      // Refresh document list
      fetchDocuments();
      
      // Notify parent component
      if (onDocumentAdded) {
        onDocumentAdded();
      }
      
    } catch (error) {
      setUploadStatus({
        success: false,
        message: error instanceof Error ? error.message : 'Upload failed. Please try again.',
      });
    } finally {
      setIsUploading(false);
    }
  };

  // Format file size for display
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  // Sample documents for quick upload
  const sampleDocuments: SampleDocument[] = [
    { title: 'Clubhouse Usage Guidelines', filename: 'clubhouse_usage.txt', category: 'Apartment Rules & Regulations' },
    { title: 'Gym Rules', filename: 'gym_rules.txt', category: 'Apartment Rules & Regulations' },
    { title: 'Swimming Pool Rules', filename: 'swimming_pool_rules.txt', category: 'Apartment Rules & Regulations' },
    { title: 'Pet Policy', filename: 'pet_policy.txt', category: 'Apartment Rules & Regulations' },
    { title: 'Waste Segregation Policy', filename: 'waste_segregation_policy.txt', category: 'Apartment Rules & Regulations' },
    { title: 'Security Guidelines', filename: 'security_guidelines.txt', category: 'Apartment Rules & Regulations' },
    { title: 'Barbeque Usage Policy', filename: 'barbeque_usage_policy.txt', category: 'Apartment Rules & Regulations' },
    { title: 'Printer Usage Policy', filename: 'printer_usage_policy.txt', category: 'Apartment Rules & Regulations' },
  ];

  // Available document categories
  const documentCategories = [
    'General',
    'Apartment Policies',
    'Apartment Rules & Regulations',
    'Maintenance',
    'Security',
    'Amenities',
    'Contracts',
    'Communications'
  ];

  // Sample document content mapping
  const sampleDocumentContent: Record<string, string> = {
    'clubhouse_usage.txt': `# Clubhouse Usage Guidelines\n\n## Hours of Operation\n- Monday to Friday: 6:00 AM to 10:00 PM\n- Weekends and Holidays: 7:00 AM to 11:00 PM\n\n## Booking Rules\n1. Residents can book the clubhouse up to 30 days in advance\n2. Maximum booking duration is 4 hours\n3. Cleaning deposit of ₹2000 is required`,
    
    'gym_rules.txt': `# Gym Rules and Regulations\n\n## Hours\n- Open daily from 5:00 AM to 11:00 PM\n\n## General Rules\n1. Proper athletic attire required\n2. Wipe down equipment after use\n3. No children under 14 without adult supervision\n4. Return weights to racks after use`,
    
    'swimming_pool_rules.txt': `# Swimming Pool Rules\n\n## Pool Hours\n- Daily: 6:00 AM to 9:00 PM\n- Maintenance: Mondays 9:00 AM to 12:00 PM\n\n## Safety Rules\n1. No diving in shallow areas\n2. Children under 12 must be supervised\n3. Shower before entering pool\n4. No food or glass containers in pool area`,
    
    'pet_policy.txt': `# Pet Policy\n\n## Allowed Pets\n- Dogs (max 2 per apartment)\n- Cats (max 2 per apartment)\n- Small caged animals\n\n## Restrictions\n1. Maximum weight: 25kg per dog\n2. Prohibited breeds: Rottweilers, Pit Bulls\n3. All pets must be registered with management`,
    
    'waste_segregation_policy.txt': `# Waste Segregation Policy\n\n## Categories\n1. Wet waste (green bins)\n2. Dry waste (blue bins)\n3. Hazardous waste (red bins)\n\n## Collection Schedule\n- Wet waste: Daily collection\n- Dry waste: Monday, Wednesday, Friday\n- Hazardous waste: Last Saturday of month`,
    
    'security_guidelines.txt': `# Security Guidelines\n\n## Visitor Management\n1. All visitors must register at security gate\n2. Pre-authorize guests through resident portal\n3. Delivery personnel restricted to lobby area\n\n## Access Control\n1. Keep access cards secure\n2. Report lost cards immediately\n3. Do not allow tailgating through secure doors`,
    
    'barbeque_usage_policy.txt': `# Barbeque Usage Policy\n\n## Designated Areas\n- Terrace garden BBQ zone\n- Poolside BBQ stations\n\n## Reservation\n1. Book through resident portal 48 hours in advance\n2. Maximum duration: 3 hours\n3. Clean area after use\n\n## Safety\n1. Never leave grill unattended\n2. Keep fire extinguisher nearby\n3. No BBQ during high wind conditions`,
    
    'printer_usage_policy.txt': `# Printer Usage Policy\n## Gopalan Atlantis Apartment Complex\n\n### Printer Locations\n1. **Business Center (Main Lobby)**\n   - 2 Color Laser Printers\n   - 1 Black & White Laser Printer\n   - 1 Scanner/Copier\n\n### Usage Fees\n1. **Printing Costs**\n   - Black & White: ₹2 per page\n   - Color: ₹10 per page\n\n### Payment Methods\n1. Charges are automatically added to monthly maintenance bill\n2. Prepaid cards available at the management office`
  };

  // Function to upload a sample document
  const uploadSampleDocument = async (sample: SampleDocument) => {
    setIsUploading(true);
    try {
      // Get the content for this sample document
      const content = sampleDocumentContent[sample.filename] || 
        `# ${sample.title}\n\nThis is a sample document for ${sample.title}.`;
      
      // Create a blob with the content
      const blob = new Blob([content], { type: 'text/plain' });
      const file = new File([blob], sample.filename, { type: 'text/plain' });
      
      console.log(`Created sample document: ${sample.title}, size: ${file.size} bytes`);
      
      // Create form data and upload
      const formData = new FormData();
      formData.append('file', file);
      formData.append('title', sample.title);
      formData.append('category', sample.category);
      formData.append('collection', 'apartment_documents');
      
      console.log('Uploading document with form data:', {
        title: sample.title,
        category: sample.category,
        filename: file.name,
        size: file.size
      });
      
      const result = await verbaService.uploadDocument(formData);
      console.log('Sample upload result:', result);
      
      // Show success message with link
      setUploadStatus({
        success: true,
        message: `Document "${sample.title}" uploaded successfully`,
      });
      
      // Notify parent component
      if (onDocumentAdded) {
        onDocumentAdded();
      }
    } catch (error) {
      console.error('Error uploading sample document:', error);
      setUploadStatus({
        success: false,
        message: `Error uploading ${sample.title}: ${error instanceof Error ? error.message : 'Unknown error'}`,
      });
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <Box sx={{ mb: 4 }}>
      <Grid container spacing={3}>
        {/* Upload Form */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <Typography variant="h6" gutterBottom>
              Add Document to RAG Knowledge Base
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Upload documents to be processed by the Verba RAG system. These documents will be indexed and made available for AI queries.
            </Typography>
            
            <Box component="form" onSubmit={handleSubmit} noValidate>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <TextField
                    name="title"
                    label="Document Title"
                    value={formData.title}
                    onChange={handleInputChange}
                    fullWidth
                    placeholder={selectedFile ? selectedFile.name : 'Enter document title'}
                  />
                </Grid>
                
                <Grid item xs={12}>
                  <TextField
                    name="category"
                    label="Category"
                    value={formData.category}
                    onChange={handleInputChange}
                    fullWidth
                    select
                  >
                    {documentCategories.map((category) => (
                      <MenuItem key={category} value={category}>{category}</MenuItem>
                    ))}
                  </TextField>
                </Grid>
                
                <Grid item xs={12}>
                  <TextField
                    name="tags"
                    label="Tags (comma separated)"
                    value={formData.tags}
                    onChange={handleInputChange}
                    fullWidth
                    placeholder="e.g., important, reference, official"
                  />
                </Grid>
              </Grid>
              
              {/* File upload area */}
              <Box 
                sx={{ 
                  mt: 3, 
                  p: 3, 
                  border: '2px dashed #ccc', 
                  borderRadius: 2,
                  textAlign: 'center',
                  bgcolor: 'background.default',
                  cursor: 'pointer',
                  '&:hover': {
                    bgcolor: 'action.hover'
                  }
                }}
                onClick={() => document.getElementById('verba-file-upload')?.click()}
              >
                <input
                  type="file"
                  id="verba-file-upload"
                  style={{ display: 'none' }}
                  onChange={handleFileChange}
                />
                <UploadIcon color="primary" sx={{ fontSize: 40, mb: 1 }} />
                {selectedFile ? (
                  <Box>
                    <Typography variant="body1" gutterBottom>
                      {selectedFile.name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {formatFileSize(selectedFile.size)}
                    </Typography>
                    <Button 
                      size="small" 
                      onClick={(e) => {
                        e.stopPropagation();
                        setSelectedFile(null);
                      }}
                      sx={{ mt: 1 }}
                    >
                      Clear
                    </Button>
                  </Box>
                ) : (
                  <Typography variant="body1">
                    Drop a file here or click to select
                  </Typography>
                )}
              </Box>
              
              {/* Upload status message */}
              {uploadStatus && (
                <Alert 
                  severity={uploadStatus.success ? "success" : "error"} 
                  sx={{ mt: 2 }}
                  onClose={() => setUploadStatus(null)}
                >
                  {uploadStatus.message}
                </Alert>
              )}
              
              {/* Submit button */}
              <Button
                type="submit"
                fullWidth
                variant="contained"
                color="primary"
                disabled={isUploading || !selectedFile}
                sx={{ mt: 3, mb: 2 }}
                startIcon={isUploading ? <CircularProgress size={20} /> : <UploadIcon />}
              >
                {isUploading ? 'Uploading...' : 'Upload to RAG'}
              </Button>
            </Box>
          </Paper>
        </Grid>
        
        {/* Indexed Documents List */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">
                Indexed RAG Documents
              </Typography>
              <IconButton onClick={fetchDocuments} disabled={isLoading} size="small">
                <RefreshIcon />
              </IconButton>
            </Box>
            
            {isLoading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
                <CircularProgress />
              </Box>
            ) : indexedDocuments.length === 0 ? (
              <Alert severity="info" sx={{ mt: 2 }}>
                No documents found in the RAG index. Upload documents to start building your knowledge base.
              </Alert>
            ) : (
              <List>
                {indexedDocuments.map((doc, index) => (
                  <React.Fragment key={doc.id || index}>
                    {index > 0 && <Divider />}
                    <ListItem>
                      <ListItemText
                        primary={doc.metadata.title || doc.metadata.file_name || `Document ${index + 1}`}
                        secondary={
                          <React.Fragment>
                            <Typography variant="body2" component="span" display="block">
                              {doc.metadata.category && `Category: ${doc.metadata.category}`}
                            </Typography>
                            {doc.metadata.uploaded_at && (
                              <Typography variant="caption" color="text.secondary">
                                Added: {new Date(doc.metadata.uploaded_at).toLocaleString()}
                              </Typography>
                            )}
                          </React.Fragment>
                        }
                      />
                    </ListItem>
                  </React.Fragment>
                ))}
              </List>
            )}
          </Paper>
        </Grid>
        
        {/* Sample Documents for Quick Upload */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Quick Upload Sample Documents
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              Click on any document to upload it to the Document Assistant system.
            </Typography>
            
            <Divider sx={{ my: 2 }} />
            
            <Grid container spacing={2}>
              {sampleDocuments.map((doc, index) => (
                <Grid item xs={12} sm={6} md={3} key={index}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="h6" component="div">
                        {doc.title}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Category: {doc.category}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        Filename: {doc.filename}
                      </Typography>
                    </CardContent>
                    <CardActions>
                      <Button 
                        size="small" 
                        onClick={() => uploadSampleDocument(doc)}
                        disabled={isUploading}
                        startIcon={<UploadIcon />}
                      >
                        Upload
                      </Button>
                    </CardActions>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default VerbaDocumentUpload;
