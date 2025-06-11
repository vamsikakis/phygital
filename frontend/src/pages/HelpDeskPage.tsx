import React, { useState } from 'react';
import { Box, Container, Typography, TextField, Button, Paper, List, ListItem, ListItemText } from '@mui/material';
import { useNavigate } from 'react-router-dom';

const HelpDeskPage: React.FC = () => {
  const navigate = useNavigate();
  const [message, setMessage] = useState('');
  const [chatHistory, setChatHistory] = useState<Array<{ role: 'user' | 'assistant'; content: string }>>([]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim()) return;

    // Add user message to chat history
    setChatHistory([...chatHistory, { role: 'user', content: message }]);
    setMessage('');

    // TODO: Send message to backend and get AI response
    // Simulate AI response
    setTimeout(() => {
      setChatHistory(prev => [...prev, {
        role: 'assistant',
        content: 'Thank you for your query. I am processing your request...'
      }]);
    }, 1000);
  };

  return (
    <Box sx={{ flexGrow: 1, py: 4 }}>
      <Container>
        <Typography variant="h4" component="h1" gutterBottom>
          Help Desk
        </Typography>
        <Paper sx={{ p: 2, mt: 2, height: 'calc(100vh - 200px)', display: 'flex', flexDirection: 'column' }}>
          <List sx={{ flex: 1, overflow: 'auto' }}>
            {chatHistory.map((message, index) => (
              <ListItem key={index} sx={{ justifyContent: message.role === 'user' ? 'flex-end' : 'flex-start' }}>
                <ListItemText
                  primary={message.content}
                  sx={{
                    backgroundColor: message.role === 'user' ? 'primary.light' : 'secondary.light',
                    borderRadius: 1,
                    p: 1
                  }}
                />
              </ListItem>
            ))}
          </List>
          <Box sx={{ mt: 2, display: 'flex', gap: 1 }}>
            <TextField
              fullWidth
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Type your message here..."
              variant="outlined"
            />
            <Button variant="contained" onClick={handleSubmit}>
              Send
            </Button>
          </Box>
        </Paper>
      </Container>
    </Box>
  );
};

export default HelpDeskPage;
