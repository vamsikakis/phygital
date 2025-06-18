import React, { useState, useEffect, useRef } from 'react';
import { 
  Box, 
  TextField, 
  Button, 
  Typography, 
  Paper, 
  CircularProgress,
  Alert,
  List,
  ListItem,
  ListItemText,
  Avatar,
  Divider,
  IconButton
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import PersonIcon from '@mui/icons-material/Person';
import DeleteIcon from '@mui/icons-material/Delete';
import useOpenAIAssistant from '../hooks/useOpenAIAssistant';
import { MessageResponse } from '../services/openaiAssistantService';
import { format } from 'date-fns';

const OpenAIChatView: React.FC = () => {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { 
    isInitialized,
    isInitializing,
    initError,
    threadId,
    messages,
    isLoading,
    error,
    initialize,
    createThread,
    sendMessage,
    loadMessages
  } = useOpenAIAssistant({ autoInitialize: true });

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Create a thread when initialized
  useEffect(() => {
    if (isInitialized && !threadId && !isLoading) {
      createThread();
    }
  }, [isInitialized, threadId, isLoading, createThread]);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    
    const message = input.trim();
    setInput('');
    await sendMessage(message);
  };

  const formatTimestamp = (timestamp: number): string => {
    return format(new Date(timestamp * 1000), 'MMM d, h:mm a');
  };

  // Sort messages by created_at
  const sortedMessages = [...messages].sort((a, b) => a.created_at - b.created_at);

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
        <Typography variant="h6" component="div">
          AI Assistant
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Ask me anything about the apartment complex
        </Typography>
      </Box>

      {/* Initialization Status */}
      {!isInitialized && (
        <Box sx={{ p: 2 }}>
          {isInitializing ? (
            <Alert severity="info" icon={<CircularProgress size={20} />}>
              Initializing AI Assistant...
            </Alert>
          ) : (
            <Alert 
              severity="warning" 
              action={
                <Button color="inherit" size="small" onClick={initialize}>
                  Retry
                </Button>
              }
            >
              {initError ? `Failed to initialize: ${initError.message}` : 'Not initialized'}
            </Alert>
          )}
        </Box>
      )}

      {/* Error Display */}
      {error && (
        <Box sx={{ p: 2 }}>
          <Alert severity="error">{error.message}</Alert>
        </Box>
      )}

      {/* Messages */}
      <Box sx={{ 
        flexGrow: 1, 
        overflow: 'auto', 
        p: 2,
        display: 'flex',
        flexDirection: 'column',
        gap: 2
      }}>
        {sortedMessages.length === 0 && isInitialized && !isLoading && (
          <Box sx={{ 
            display: 'flex', 
            flexDirection: 'column', 
            alignItems: 'center', 
            justifyContent: 'center',
            height: '100%',
            opacity: 0.7
          }}>
            <SmartToyIcon sx={{ fontSize: 60, mb: 2 }} />
            <Typography variant="body1">
              Ask me anything about Gopalan Atlantis!
            </Typography>
          </Box>
        )}

        {sortedMessages.map((message) => (
          <Box
            key={message.message_id}
            sx={{
              display: 'flex',
              flexDirection: 'column',
              alignSelf: message.role === 'user' ? 'flex-end' : 'flex-start',
              maxWidth: '80%'
            }}
          >
            <Box sx={{ 
              display: 'flex', 
              alignItems: 'flex-start',
              flexDirection: message.role === 'user' ? 'row-reverse' : 'row',
              gap: 1
            }}>
              <Avatar sx={{ bgcolor: message.role === 'user' ? 'primary.main' : 'secondary.main' }}>
                {message.role === 'user' ? <PersonIcon /> : <SmartToyIcon />}
              </Avatar>
              <Paper
                elevation={1}
                sx={{
                  p: 2,
                  borderRadius: 2,
                  bgcolor: message.role === 'user' ? 'primary.light' : 'background.paper',
                }}
              >
                <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                  {message.content}
                </Typography>
              </Paper>
            </Box>
            <Typography 
              variant="caption" 
              sx={{ 
                mt: 0.5, 
                alignSelf: message.role === 'user' ? 'flex-end' : 'flex-start',
                color: 'text.secondary'
              }}
            >
              {formatTimestamp(message.created_at)}
            </Typography>
          </Box>
        ))}

        {isLoading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', my: 2 }}>
            <CircularProgress size={24} />
          </Box>
        )}
        
        <div ref={messagesEndRef} />
      </Box>

      {/* Input */}
      <Box 
        component="form" 
        onSubmit={handleSendMessage}
        sx={{ 
          p: 2, 
          borderTop: 1, 
          borderColor: 'divider',
          display: 'flex',
          gap: 1
        }}
      >
        <TextField
          fullWidth
          variant="outlined"
          placeholder="Type your message..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={!isInitialized || isLoading}
          size="small"
        />
        <Button 
          variant="contained" 
          color="primary" 
          endIcon={<SendIcon />}
          type="submit"
          disabled={!isInitialized || isLoading || !input.trim()}
        >
          Send
        </Button>
      </Box>
    </Box>
  );
};

export default OpenAIChatView;
