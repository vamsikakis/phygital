import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Button,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  Divider,
  Container,
} from '@mui/material';
import {
  Add as AddIcon,
  Campaign as CommunicationIcon,
  Upload as UploadIcon,
  People as PeopleIcon,
  Business as PropertyIcon,
  Assignment as TaskIcon,
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';

// Dashboard data interface
interface DashboardStats {
  totalUsers: number;
  activeProperties: number;
  pendingTasks: number;
  recentCommunications: string[];
}

const Home: React.FC = () => {
  const navigate = useNavigate();
  const { user, hasRole } = useAuth();
  const [stats, setStats] = useState<DashboardStats>({
    totalUsers: 1250,
    activeProperties: 85,
    pendingTasks: 12,
    recentCommunications: [
      'Swimming pool maintenance scheduled',
      'Community gathering announcement',
      'Monthly maintenance reminder',
    ],
  });

  // Quick action buttons based on user role
  const getQuickActions = () => {
    const actions = [];

    if (hasRole(['admin', 'management'])) {
      actions.push({
        label: 'Add New User',
        icon: <AddIcon />,
        onClick: () => navigate('/user-management'),
        color: 'primary',
      });
    }

    if (hasRole(['admin', 'management', 'fm'])) {
      actions.push(
        {
          label: 'Create Announcement',
          icon: <CommunicationIcon />,
          onClick: () => navigate('/communication'),
          color: 'secondary',
        },
        {
          label: 'Upload Document',
          icon: <UploadIcon />,
          onClick: () => navigate('/document-management'),
          color: 'primary',
        }
      );
    }

    return actions;
  };

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* Header with Quick Actions */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" sx={{ mb: 3, fontWeight: 700 }}>
          Welcome back, {user?.name}!
        </Typography>

        {/* Quick Action Buttons */}
        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', mb: 4 }}>
          {getQuickActions().map((action, index) => (
            <Button
              key={index}
              variant="contained"
              startIcon={action.icon}
              onClick={action.onClick}
              sx={{
                borderRadius: 2,
                px: 3,
                py: 1.5,
                fontWeight: 600,
              }}
              color={action.color as any}
            >
              {action.label}
            </Button>
          ))}
        </Box>
      </Box>

      {/* Dashboard Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {/* Total Users Card */}
        {hasRole(['admin', 'management']) && (
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ p: 3, textAlign: 'center' }}>
              <PeopleIcon sx={{ fontSize: 40, color: 'primary.main', mb: 2 }} />
              <Typography variant="h3" sx={{ fontWeight: 700, mb: 1 }}>
                {stats.totalUsers.toLocaleString()}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                TOTAL USERS
              </Typography>
            </Card>
          </Grid>
        )}

        {/* Active Properties Card */}
        {hasRole(['admin', 'management', 'fm']) && (
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ p: 3, textAlign: 'center' }}>
              <PropertyIcon sx={{ fontSize: 40, color: 'secondary.main', mb: 2 }} />
              <Typography variant="h3" sx={{ fontWeight: 700, mb: 1 }}>
                {stats.activeProperties}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                ACTIVE PROPERTIES
              </Typography>
            </Card>
          </Grid>
        )}

        {/* Pending Tasks Card */}
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ p: 3, textAlign: 'center' }}>
            <TaskIcon sx={{ fontSize: 40, color: 'warning.main', mb: 2 }} />
            <Typography variant="h3" sx={{ fontWeight: 700, mb: 1 }}>
              {stats.pendingTasks}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              PENDING TASKS
            </Typography>
          </Card>
        </Grid>

        {/* Recent Communications Card */}
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ p: 3, height: '100%' }}>
            <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
              RECENT COMMUNICATIONS
            </Typography>
            <Box>
              {[1, 2, 3].map((item) => (
                <Box key={item} sx={{ mb: 1 }}>
                  <LinearProgress
                    variant="determinate"
                    value={Math.random() * 100}
                    sx={{
                      height: 8,
                      borderRadius: 4,
                      backgroundColor: 'grey.200',
                      '& .MuiLinearProgress-bar': {
                        backgroundColor: 'primary.main',
                      },
                    }}
                  />
                </Box>
              ))}
            </Box>
          </Card>
        </Grid>
      </Grid>

      {/* Recent Activity */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Card sx={{ p: 3 }}>
            <Typography variant="h6" sx={{ mb: 3, fontWeight: 600 }}>
              Recent Activity
            </Typography>
            <List>
              {stats.recentCommunications.map((communication, index) => (
                <React.Fragment key={index}>
                  <ListItem sx={{ px: 0 }}>
                    <ListItemText
                      primary={communication}
                      secondary={`${Math.floor(Math.random() * 24)} hours ago`}
                    />
                  </ListItem>
                  {index < stats.recentCommunications.length - 1 && <Divider />}
                </React.Fragment>
              ))}
            </List>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card sx={{ p: 3 }}>
            <Typography variant="h6" sx={{ mb: 3, fontWeight: 600 }}>
              Quick Links
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <Button
                variant="outlined"
                fullWidth
                onClick={() => navigate('/knowledge-base')}
                sx={{ justifyContent: 'flex-start' }}
              >
                Knowledge Base
              </Button>
              <Button
                variant="outlined"
                fullWidth
                onClick={() => navigate('/openai-assistant')}
                sx={{ justifyContent: 'flex-start' }}
              >
                AI Assistant
              </Button>
              {hasRole(['admin', 'management', 'fm']) && (
                <Button
                  variant="outlined"
                  fullWidth
                  onClick={() => navigate('/financial-dashboard')}
                  sx={{ justifyContent: 'flex-start' }}
                >
                  Financial Dashboard
                </Button>
              )}
            </Box>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Home;
