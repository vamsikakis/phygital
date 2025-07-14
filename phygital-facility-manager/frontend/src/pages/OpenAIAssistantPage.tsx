import React, { useState, useRef, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Grid,
  Chip,
  Avatar,
  Paper,
  IconButton,
  Divider,
} from '@mui/material';
import {
  Send as SendIcon,
  SmartToy as AIIcon,
  Person as PersonIcon,
  Lightbulb as SuggestionIcon,
  Home as HomeIcon,
  Build as MaintenanceIcon,
  Event as EventIcon,
  AccountBalance as FinanceIcon,
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'ai';
  timestamp: Date;
}

const OpenAIAssistantPage: React.FC = () => {
  const { user } = useAuth();
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: `Hello ${user?.name || 'there'}! I'm your Gopalan Atlantis AI Assistant. I can help you with facility management, answer questions about your apartment, and assist with various tasks. How can I help you today?`,
      sender: 'ai',
      timestamp: new Date(),
    },
  ]);
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const suggestedActions = [
    { label: 'Check maintenance schedule', icon: <MaintenanceIcon />, query: 'What is the maintenance schedule for this month?' },
    { label: 'Upcoming events', icon: <EventIcon />, query: 'What events are coming up in the community?' },
    { label: 'Payment information', icon: <FinanceIcon />, query: 'How can I pay my monthly maintenance fees?' },
    { label: 'Facility rules', icon: <HomeIcon />, query: 'What are the facility rules and regulations?' },
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (text: string = inputText) => {
    if (!text.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: text.trim(),
      sender: 'user',
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setLoading(true);

    try {
      // Simulate AI response - replace with actual API call
      setTimeout(() => {
        const aiResponse: Message = {
          id: (Date.now() + 1).toString(),
          text: `I understand you're asking about "${text}". Let me help you with that. This is a simulated response - in the actual implementation, this would connect to the OpenAI assistant with access to your facility's knowledge base.`,
          sender: 'ai',
          timestamp: new Date(),
        };
        setMessages(prev => [...prev, aiResponse]);
        setLoading(false);
      }, 1000);
    } catch (error) {
      console.error('Error sending message:', error);
      setLoading(false);
    }
  };

  const handleSuggestionClick = (query: string) => {
    handleSendMessage(query);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <Container maxWidth="xl" sx={{ py: 4, height: 'calc(100vh - 120px)' }}>
      <Grid container spacing={3} sx={{ height: '100%' }}>
        {/* Chat Interface */}
        <Grid item xs={12} lg={8}>
          <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            {/* Header */}
            <CardContent sx={{ pb: 1 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Avatar sx={{ backgroundColor: 'primary.main' }}>
                  <AIIcon />
                </Avatar>
                <Box>
                  <Typography variant="h6" sx={{ fontWeight: 600 }}>
                    Gopalan Atlantis AI Assistant
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Your intelligent facility management companion
                  </Typography>
                </Box>
              </Box>
            </CardContent>

            <Divider />

            {/* Messages */}
            <Box sx={{ flex: 1, overflow: 'auto', p: 2 }}>
              {messages.map((message) => (
                <Box
                  key={message.id}
                  sx={{
                    display: 'flex',
                    justifyContent: message.sender === 'user' ? 'flex-end' : 'flex-start',
                    mb: 2,
                  }}
                >
                  <Box
                    sx={{
                      display: 'flex',
                      alignItems: 'flex-start',
                      gap: 1,
                      maxWidth: '70%',
                      flexDirection: message.sender === 'user' ? 'row-reverse' : 'row',
                    }}
                  >
                    <Avatar
                      sx={{
                        width: 32,
                        height: 32,
                        backgroundColor: message.sender === 'user' ? 'secondary.main' : 'primary.main',
                      }}
                    >
                      {message.sender === 'user' ? <PersonIcon /> : <AIIcon />}
                    </Avatar>
                    <Paper
                      sx={{
                        p: 2,
                        backgroundColor: message.sender === 'user' ? 'primary.main' : 'grey.100',
                        color: message.sender === 'user' ? 'white' : 'text.primary',
                        borderRadius: 2,
                      }}
                    >
                      <Typography variant="body1">{message.text}</Typography>
                      <Typography
                        variant="caption"
                        sx={{
                          opacity: 0.7,
                          display: 'block',
                          mt: 1,
                        }}
                      >
                        {message.timestamp.toLocaleTimeString()}
                      </Typography>
                    </Paper>
                  </Box>
                </Box>
              ))}
              {loading && (
                <Box sx={{ display: 'flex', justifyContent: 'flex-start', mb: 2 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Avatar sx={{ width: 32, height: 32, backgroundColor: 'primary.main' }}>
                      <AIIcon />
                    </Avatar>
                    <Paper sx={{ p: 2, backgroundColor: 'grey.100', borderRadius: 2 }}>
                      <Typography variant="body1">Thinking...</Typography>
                    </Paper>
                  </Box>
                </Box>
              )}
              <div ref={messagesEndRef} />
            </Box>

            {/* Input */}
            <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
              <Box sx={{ display: 'flex', gap: 1 }}>
                <TextField
                  fullWidth
                  multiline
                  maxRows={3}
                  placeholder="Ask me anything about Gopalan Atlantis..."
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  onKeyPress={handleKeyPress}
                  disabled={loading}
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      borderRadius: 2,
                    },
                  }}
                />
                <IconButton
                  color="primary"
                  onClick={() => handleSendMessage()}
                  disabled={!inputText.trim() || loading}
                  sx={{
                    backgroundColor: 'primary.main',
                    color: 'white',
                    '&:hover': {
                      backgroundColor: 'primary.dark',
                    },
                    '&:disabled': {
                      backgroundColor: 'grey.300',
                    },
                  }}
                >
                  <SendIcon />
                </IconButton>
              </Box>
            </Box>
          </Card>
        </Grid>

        {/* Sidebar */}
        <Grid item xs={12} lg={4}>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
            {/* Suggested Actions */}
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                  <SuggestionIcon color="primary" />
                  <Typography variant="h6" sx={{ fontWeight: 600 }}>
                    Quick Actions
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                  {suggestedActions.map((action, index) => (
                    <Button
                      key={index}
                      variant="outlined"
                      startIcon={action.icon}
                      onClick={() => handleSuggestionClick(action.query)}
                      sx={{
                        justifyContent: 'flex-start',
                        textAlign: 'left',
                        borderRadius: 2,
                      }}
                    >
                      {action.label}
                    </Button>
                  ))}
                </Box>
              </CardContent>
            </Card>

            {/* AI Capabilities */}
            <Card>
              <CardContent>
                <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
                  What I Can Help With
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  {[
                    'Maintenance Requests',
                    'Community Events',
                    'Payment Information',
                    'Facility Rules',
                    'Emergency Contacts',
                    'Amenity Booking',
                    'Document Search',
                    'General Inquiries',
                  ].map((capability) => (
                    <Chip
                      key={capability}
                      label={capability}
                      size="small"
                      variant="outlined"
                      color="primary"
                    />
                  ))}
                </Box>
              </CardContent>
            </Card>

            {/* Tips */}
            <Card>
              <CardContent>
                <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
                  Tips for Better Results
                </Typography>
                <Typography variant="body2" color="text.secondary" paragraph>
                  • Be specific in your questions
                </Typography>
                <Typography variant="body2" color="text.secondary" paragraph>
                  • Include your apartment number when relevant
                </Typography>
                <Typography variant="body2" color="text.secondary" paragraph>
                  • Ask about specific dates for events or maintenance
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  • Use the quick actions for common queries
                </Typography>
              </CardContent>
            </Card>
          </Box>
        </Grid>
      </Grid>
    </Container>
  );
};

export default OpenAIAssistantPage;
