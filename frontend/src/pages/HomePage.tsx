import React from 'react';
import { Box, Container, Typography, Button } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';

const HomePage: React.FC = () => {
  return (
    <Box sx={{ flexGrow: 1, py: 4 }}>
      <Container>
        <Typography variant="h4" component="h1" gutterBottom>
          Welcome to Gopalan Atlantis Facility Manager
        </Typography>
        <Typography variant="body1" paragraph>
          Your comprehensive facility management platform for apartment residents.
        </Typography>
        
        <Box sx={{ mt: 4, display: 'flex', gap: 2 }}>
          <Button
            component={RouterLink}
            to="/documents"
            variant="contained"
            color="primary"
          >
            Apartment Documents
          </Button>
          <Button
            component={RouterLink}
            to="/communications"
            variant="contained"
            color="primary"
          >
            Community Communications
          </Button>
          <Button
            component={RouterLink}
            to="/helpdesk"
            variant="contained"
            color="primary"
          >
            Help Desk
          </Button>
        </Box>
      </Container>
    </Box>
  );
};

export default HomePage;
