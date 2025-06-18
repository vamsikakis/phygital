import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Typography,
  TextField,
  Button,
  Paper,
  Grid,
  Card,
  CardContent,
  Chip,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  IconButton,
  CircularProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  SelectChangeEvent
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import QuestionAnswerIcon from '@mui/icons-material/QuestionAnswer';
import HistoryIcon from '@mui/icons-material/History';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';
import PendingIcon from '@mui/icons-material/Pending';

// Import our OpenAI service
import openAIService from '../services/openaiService';

interface ChatMessage {
  role: 'system' | 'user';
  content: string;
  timestamp: string;
}

const HelpDesk: React.FC = () => {
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('chat');
  const [ticketCategory, setTicketCategory] = useState('');
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Chat history with initial greeting
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([
    { 
      role: 'system', 
      content: 'Hello! I am your Gopalan Atlantis AI assistant. How can I help you today?',
      timestamp: new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})
    }
  ]);

  // Mock data for tickets
  const tickets = [
    {
      id: 'TKT123',
      subject: 'Water Leakage in Bathroom',
      description: 'There is water leaking from the bathroom ceiling.',
      status: 'Open',
      category: 'Maintenance',
      createdAt: '2025-06-05',
      lastUpdated: '2025-06-05'
    },
    {
      id: 'TKT122',
      subject: 'Access Card Not Working',
      description: 'My access card is not working at the main gate.',
      status: 'In Progress',
      category: 'Security',
      createdAt: '2025-06-01',
      lastUpdated: '2025-06-03'
    },
    {
      id: 'TKT120',
      subject: 'Noise Complaint',
      description: 'There is excessive noise coming from apartment 305 after 11 PM.',
      status: 'Closed',
      category: 'General',
      createdAt: '2025-05-28',
      lastUpdated: '2025-06-01'
    }
  ];

  // FAQs for the help section
  const faqs = [
    {
      question: "How do I submit a maintenance request?",
      answer: "You can submit a maintenance request through this Help Desk section. Use the 'Create Ticket' option and select the 'Maintenance' category. Provide a clear description of the issue, and your request will be addressed within 48 hours."
    },
    {
      question: "What are the pool hours?",
      answer: "The community pool is open from 6:00 AM to 10:00 PM daily. Children under 12 must be accompanied by an adult. Please follow all posted safety rules."
    },
    {
      question: "How do I pay my maintenance fees?",
      answer: "Maintenance fees can be paid online through the resident portal, by direct deposit, or by check at the management office. Payments are due on the 5th of each month."
    },
    {
      question: "What should I do in case of an emergency?",
      answer: "In case of fire or medical emergencies, call 911 immediately. For building-related emergencies like water leaks or power outages, contact the 24-hour emergency maintenance line at 555-123-4567."
    }
  ];

  // Scroll to bottom of chat when messages change
  useEffect(() => {
    scrollToBottom();
  }, [chatHistory]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = async () => {
    if (!query.trim()) return;

    // Reset any previous errors
    setError(null);

    // Add user message to chat history
    const userMessage: ChatMessage = {
      role: 'user',
      content: query,
      timestamp: new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})
    };

    setChatHistory(prev => [...prev, userMessage]);

    // Store the query before clearing the input
    const currentQuery = query;
    setQuery('');

    // Send query to OpenAI service
    setIsLoading(true);
    try {
      const response = await openAIService.askAI(currentQuery, 'all');

      // Add AI response to chat history
      const aiMessage: ChatMessage = {
        role: 'system',
        content: response.answer,
        timestamp: new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})
      };

      setChatHistory(prev => [...prev, aiMessage]);
    } catch (err: any) {
      console.error('Error getting AI response:', err);
      setError(err.message || 'Failed to get response from AI assistant');

      // Add error message to chat
      const errorMessage: ChatMessage = {
        role: 'system',
        content: 'Sorry, I encountered an error processing your request. Please try again later.',
        timestamp: new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})
      };

      setChatHistory(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCategoryChange = (event: SelectChangeEvent) => {
    setTicketCategory(event.target.value as string);
  };

  return (
    <Box>
      <Typography variant="h5" component="h1" gutterBottom>
        Help Desk
      </Typography>

      <Grid container spacing={3}>
        {/* Main Content */}
        <Grid item xs={12} md={8}>
          <Paper elevation={2} sx={{ p: 2, mb: 3 }}>
            <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
              <Button 
                variant={activeTab === 'chat' ? 'contained' : 'outlined'} 
                onClick={() => setActiveTab('chat')}
                startIcon={<QuestionAnswerIcon />}
              >
                AI Assistant
              </Button>
              <Button 
                variant={activeTab === 'tickets' ? 'contained' : 'outlined'} 
                onClick={() => setActiveTab('tickets')}
                startIcon={<HistoryIcon />}
              >
                My Tickets
              </Button>
            </Box>

            <Divider sx={{ mb: 2 }} />

            {/* Chat with AI Assistant */}
            {activeTab === 'chat' && (
              <Box>
                <Box sx={{ 
                  height: '400px', 
                  overflowY: 'auto', 
                  mb: 2, 
                  p: 2, 
                  bgcolor: '#f5f5f5', 
                  borderRadius: 1 
                }}>
                  {chatHistory.map((msg, index) => (
                    <Box 
                      key={index} 
                      sx={{
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: msg.role === 'user' ? 'flex-end' : 'flex-start',
                        mb: 2
                      }}
                    >
                      <Paper 
                        elevation={1} 
                        sx={{
                          p: 1.5,
                          maxWidth: '80%',
                          bgcolor: msg.role === 'user' ? '#e3f2fd' : 'white',
                          borderRadius: 2
                        }}
                      >
                        <Typography variant="body1">{msg.content}</Typography>
                      </Paper>
                      <Typography variant="caption" sx={{ mt: 0.5, color: 'text.secondary' }}>
                        {msg.timestamp}
                      </Typography>
                    </Box>
                  ))}
                  {/* Error message if any */}
                  {error && (
                    <Box sx={{ p: 2, color: 'error.main', textAlign: 'center' }}>
                      <Typography variant="body2">{error}</Typography>
                    </Box>
                  )}
                  {/* Auto-scroll reference */}
                  <div ref={messagesEndRef} />
                </Box>

                <Box sx={{ display: 'flex', gap: 1 }}>
                  <TextField
                    fullWidth
                    placeholder="Ask me anything about the apartment complex..."
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                    disabled={isLoading}
                  />
                  <Button
                    variant="contained"
                    color="primary"
                    endIcon={isLoading ? <CircularProgress size={20} color="inherit" /> : <SendIcon />}
                    onClick={handleSendMessage}
                    disabled={isLoading || !query.trim()}
                  >
                    {isLoading ? 'Sending...' : 'Send'}
                  </Button>
                </Box>
              </Box>
            )}

            {/* My Tickets */}
            {activeTab === 'tickets' && (
              <List>
                {tickets.map((ticket) => (
                  <Card key={ticket.id} sx={{ mb: 2 }}>
                    <CardContent>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Typography variant="subtitle1" fontWeight="medium">
                          {ticket.subject}
                        </Typography>
                        <Chip 
                          label={ticket.status} 
                          color={
                            ticket.status === 'Open' ? 'primary' : 
                            ticket.status === 'In Progress' ? 'warning' : 'success'
                          }
                          size="small"
                        />
                      </Box>
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                        {ticket.description}
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 2 }}>
                        <Chip label={ticket.category} size="small" variant="outlined" />
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <AccessTimeIcon fontSize="small" sx={{ mr: 0.5 }} />
                          <Typography variant="caption">
                            {ticket.createdAt}
                          </Typography>
                        </Box>
                      </Box>
                      <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 1 }}>
                        <Button size="small" variant="outlined">View Details</Button>
                      </Box>
                    </CardContent>
                  </Card>
                ))}
              </List>
            )}
            
            {/* Create Ticket */}
            {activeTab === 'create' && (
              <Box>
                <Typography variant="subtitle1" gutterBottom>
                  Submit a New Support Ticket
                </Typography>
                <Box component="form" sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  <TextField
                    required
                    label="Subject"
                    fullWidth
                    placeholder="Brief description of the issue"
                  />
                  
                  <FormControl fullWidth required>
                    <InputLabel id="category-select-label">Category</InputLabel>
                    <Select
                      labelId="category-select-label"
                      value={ticketCategory}
                      label="Category"
                      onChange={handleCategoryChange}
                    >
                      <MenuItem value="Maintenance">Maintenance</MenuItem>
                      <MenuItem value="Security">Security</MenuItem>
                      <MenuItem value="Amenities">Amenities</MenuItem>
                      <MenuItem value="Billing">Billing</MenuItem>
                      <MenuItem value="General">General</MenuItem>
                    </Select>
                  </FormControl>
                  
                  <TextField
                    required
                    label="Description"
                    multiline
                    rows={4}
                    fullWidth
                    placeholder="Please provide details about your issue"
                  />
                  
                  <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2, mt: 2 }}>
                    <Button variant="outlined" onClick={() => setActiveTab('chat')}>
                      Cancel
                    </Button>
                    <Button variant="contained" color="primary">
                      Submit Ticket
                    </Button>
                  </Box>
                </Box>
              </Box>
            )}
          </Paper>
        </Grid>
        
        {/* FAQs and Status Sidebar */}
        <Grid item xs={12} md={4}>
          <Paper elevation={2} sx={{ p: 2, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Frequently Asked Questions
            </Typography>
            <Divider sx={{ mb: 2 }} />
            
            {faqs.map((faq, index) => (
              <Accordion key={index} elevation={0}>
                <AccordionSummary
                  expandIcon={<ExpandMoreIcon />}
                  aria-controls={`panel${index}-content`}
                  id={`panel${index}-header`}
                >
                  <Typography variant="subtitle2">{faq.question}</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Typography variant="body2" color="text.secondary">
                    {faq.answer}
                  </Typography>
                </AccordionDetails>
              </Accordion>
            ))}
          </Paper>
          
          <Paper elevation={2} sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Service Status
            </Typography>
            <List dense>
              <ListItem>
                <ListItemIcon>
                  <CheckCircleOutlineIcon color="success" />
                </ListItemIcon>
                <ListItemText primary="Maintenance Services" secondary="Normal Operations" />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <CheckCircleOutlineIcon color="success" />
                </ListItemIcon>
                <ListItemText primary="Security Systems" secondary="Normal Operations" />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <PendingIcon color="warning" />
                </ListItemIcon>
                <ListItemText primary="Swimming Pool" secondary="Maintenance Scheduled (Jun 20-22)" />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <CheckCircleOutlineIcon color="success" />
                </ListItemIcon>
                <ListItemText primary="Gym Facilities" secondary="Normal Operations" />
              </ListItem>
            </List>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default HelpDesk;
