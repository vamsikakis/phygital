import React from 'react';
import { Box, Typography, Paper } from '@mui/material';

interface ChatMessageProps {
  message: string;
  role: 'user' | 'assistant';
  timestamp?: string;
}

const ChatMessage: React.FC<ChatMessageProps> = ({ message, role, timestamp }) => {
  const isUser = role === 'user';
  
  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: isUser ? 'flex-end' : 'flex-start',
        width: '100%',
        mb: 2,
      }}
    >
      <Paper
        elevation={1}
        sx={{
          maxWidth: '80%',
          backgroundColor: isUser ? 'primary.light' : 'secondary.light',
          borderRadius: 2,
          p: 2,
        }}
      >
        <Typography variant="body1" color="textPrimary">
          {message}
        </Typography>
        {timestamp && (
          <Typography variant="caption" color="textSecondary" sx={{ mt: 0.5 }}>
            {timestamp}
          </Typography>
        )}
      </Paper>
    </Box>
  );
};

export default ChatMessage;
