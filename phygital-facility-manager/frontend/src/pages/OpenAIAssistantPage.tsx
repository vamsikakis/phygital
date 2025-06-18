import React from 'react';
import { Container, Typography, Box } from '@mui/material';
import OpenAIDocumentAssistant from '../components/OpenAIDocumentAssistant';

const OpenAIAssistantPage: React.FC = () => {
  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4, height: 'calc(100vh - 120px)' }}>
      <Typography variant="h4" gutterBottom>
        AI Document Assistant
      </Typography>
      <Typography variant="body1" paragraph>
        Chat with the AI assistant about apartment information or manage knowledge base documents.
      </Typography>
      <Box sx={{ height: 'calc(100% - 100px)' }}>
        <OpenAIDocumentAssistant />
      </Box>
    </Container>
  );
};

export default OpenAIAssistantPage;
