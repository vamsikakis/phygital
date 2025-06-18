import React, { useState } from 'react';
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
  Grid
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import DescriptionIcon from '@mui/icons-material/Description';
import GavelIcon from '@mui/icons-material/Gavel';
import HandymanIcon from '@mui/icons-material/Handyman';
import PoolIcon from '@mui/icons-material/Pool';
import WarningIcon from '@mui/icons-material/Warning';
import FileDownloadIcon from '@mui/icons-material/FileDownload';

const KnowledgeBase: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  
  // Mock document data
  const documents = [
    {
      id: 'bylaws',
      title: 'Gopalan Atlantis Bylaws',
      description: 'Official bylaws governing the Gopalan Atlantis community',
      lastUpdated: '2025-01-15',
      icon: <GavelIcon />,
      color: '#3f51b5'
    },
    {
      id: 'rules',
      title: 'Community Rules and Regulations',
      description: 'Detailed rules for residents including noise policies, common area usage, and pet policies',
      lastUpdated: '2025-03-20',
      icon: <DescriptionIcon />,
      color: '#f44336'
    },
    {
      id: 'maintenance',
      title: 'Maintenance Procedures',
      description: 'Guidelines for requesting and scheduling maintenance services',
      lastUpdated: '2025-05-01',
      icon: <HandymanIcon />,
      color: '#ff9800'
    },
    {
      id: 'amenities',
      title: 'Amenities Guide',
      description: 'Information about community amenities, hours, and usage policies',
      lastUpdated: '2025-04-10',
      icon: <PoolIcon />,
      color: '#2196f3'
    },
    {
      id: 'emergency',
      title: 'Emergency Procedures',
      description: 'Steps to follow during emergencies, including contact information',
      lastUpdated: '2025-02-28',
      icon: <WarningIcon />,
      color: '#f44336'
    }
  ];

  // Filter documents based on search query
  const filteredDocuments = documents.filter(doc => 
    doc.title.toLowerCase().includes(searchQuery.toLowerCase()) || 
    doc.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

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
      <Typography variant="h5" component="h1" gutterBottom>
        Apartment Knowledge Base
      </Typography>
      
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
          <Typography variant="h6" gutterBottom>
            Documents & Resources
          </Typography>
          <List>
            {filteredDocuments.map((doc) => (
              <Card key={doc.id} sx={{ mb: 2 }}>
                <CardContent sx={{ padding: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <Box sx={{ display: 'flex', alignItems: 'flex-start' }}>
                      <ListItemIcon sx={{ color: doc.color, minWidth: 40 }}>
                        {doc.icon}
                      </ListItemIcon>
                      <Box>
                        <Typography variant="subtitle1" component="div">
                          {doc.title}
                        </Typography>
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                          {doc.description}
                        </Typography>
                        <Chip 
                          label={`Updated: ${doc.lastUpdated}`} 
                          size="small" 
                          variant="outlined"
                        />
                      </Box>
                    </Box>
                    <IconButton aria-label="download" sx={{ ml: 1 }}>
                      <FileDownloadIcon />
                    </IconButton>
                  </Box>
                </CardContent>
              </Card>
            ))}
          </List>
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
    </Box>
  );
};

export default KnowledgeBase;
