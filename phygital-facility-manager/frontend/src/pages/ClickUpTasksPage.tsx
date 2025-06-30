import React from 'react';
import { Container, Typography, Box } from '@mui/material';
import ClickUpTaskManager from '../components/ClickUpTaskManager';

const ClickUpTasksPage: React.FC = () => {
  return (
    <Container maxWidth="xl">
      <Box sx={{ py: 3 }}>
        <Typography variant="h3" component="h1" gutterBottom>
          Task Management
        </Typography>
        <Typography variant="subtitle1" color="text.secondary" sx={{ mb: 4 }}>
          Manage facility maintenance and operational tasks through ClickUp integration
        </Typography>
        
        <ClickUpTaskManager />
      </Box>
    </Container>
  );
};

export default ClickUpTasksPage;
