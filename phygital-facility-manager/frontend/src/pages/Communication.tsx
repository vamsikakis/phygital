import React, { useState } from 'react';
import {
  Box,
  Typography,
  Tabs,
  Tab,
  Card,
  CardContent,
  Chip,
  Button,
  Grid,
  Paper,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Avatar,
  IconButton
} from '@mui/material';
import EventIcon from '@mui/icons-material/Event';
import AnnouncementIcon from '@mui/icons-material/Announcement';
import PollIcon from '@mui/icons-material/Poll';
import CalendarTodayIcon from '@mui/icons-material/CalendarToday';
import LocationOnIcon from '@mui/icons-material/LocationOn';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import AddIcon from '@mui/icons-material/Add';
import FlagIcon from '@mui/icons-material/Flag';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ pt: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

function a11yProps(index: number) {
  return {
    id: `simple-tab-${index}`,
    'aria-controls': `simple-tabpanel-${index}`,
  };
}

const Communication: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };
  
  // Mock data for announcements
  const announcements = [
    {
      id: 'ann001',
      title: 'Monthly Maintenance Schedule',
      content: 'The maintenance team will be servicing all common areas on the 15th of this month.',
      date: '2025-06-05',
      priority: 'normal'
    },
    {
      id: 'ann002',
      title: 'Swimming Pool Closure',
      content: 'The swimming pool will be closed for maintenance from June 20th to June 22nd.',
      date: '2025-06-08',
      priority: 'high'
    },
    {
      id: 'ann003',
      title: 'Community Gathering',
      content: 'Join us for a community BBQ on the 25th of this month at the central garden. All residents are welcome to join. Food and beverages will be provided. Please RSVP by the 20th.',
      date: '2025-06-10',
      priority: 'normal'
    }
  ];
  
  // Mock data for events
  const events = [
    {
      id: 'evt001',
      title: 'Community BBQ',
      description: 'Summer community gathering with food and games.',
      date: '2025-06-25',
      time: '18:00-21:00',
      location: 'Central Garden'
    },
    {
      id: 'evt002',
      title: 'Yoga Session',
      description: 'Weekly yoga session for all residents.',
      date: '2025-06-15',
      time: '08:00-09:00',
      location: 'Community Hall'
    },
    {
      id: 'evt003',
      title: 'Residents Association Meeting',
      description: 'Quarterly meeting to discuss community issues and updates.',
      date: '2025-07-05',
      time: '19:00-20:30',
      location: 'Conference Room'
    }
  ];
  
  // Mock data for polls
  const polls = [
    {
      id: 'poll001',
      title: 'Garden Renovation Options',
      description: 'Vote for your preferred garden renovation design.',
      options: ['Modern design', 'Traditional design', 'Eco-friendly design'],
      closingDate: '2025-06-20',
      votes: {
        'Modern design': 15,
        'Traditional design': 8,
        'Eco-friendly design': 22
      }
    },
    {
      id: 'poll002',
      title: 'Community Event Preference',
      description: 'What type of community event would you prefer for next month?',
      options: ['Movie night', 'Sports tournament', 'Cultural festival'],
      closingDate: '2025-06-18',
      votes: {
        'Movie night': 18,
        'Sports tournament': 12,
        'Cultural festival': 25
      }
    }
  ];

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h5" component="h1">
          Community Communication
        </Typography>
        <Button 
          variant="contained" 
          color="primary" 
          startIcon={<AddIcon />}
          size="small"
        >
          New Post
        </Button>
      </Box>
      
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={tabValue} onChange={handleTabChange} aria-label="communication tabs">
          <Tab 
            icon={<AnnouncementIcon />} 
            label="Announcements" 
            {...a11yProps(0)} 
          />
          <Tab 
            icon={<EventIcon />}
            label="Events" 
            {...a11yProps(1)} 
          />
          <Tab 
            icon={<PollIcon />}
            label="Polls" 
            {...a11yProps(2)} 
          />
        </Tabs>
      </Box>
      
      {/* Announcements Tab */}
      <TabPanel value={tabValue} index={0}>
        <List>
          {announcements.map((announcement) => (
            <Card key={announcement.id} sx={{ mb: 2 }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'flex-start' }}>
                  <ListItemAvatar>
                    <Avatar sx={{ 
                      bgcolor: announcement.priority === 'high' ? 'error.main' : 'primary.main' 
                    }}>
                      {announcement.priority === 'high' ? <FlagIcon /> : <AnnouncementIcon />}
                    </Avatar>
                  </ListItemAvatar>
                  <Box sx={{ width: '100%' }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Typography variant="subtitle1" component="div" fontWeight="bold">
                        {announcement.title}
                      </Typography>
                      <Chip 
                        label={announcement.date} 
                        size="small" 
                        color="default" 
                        variant="outlined"
                      />
                    </Box>
                    <Typography variant="body2" sx={{ mt: 1 }}>
                      {announcement.content}
                    </Typography>
                    {announcement.priority === 'high' && (
                      <Chip 
                        label="Important" 
                        color="error" 
                        size="small" 
                        sx={{ mt: 1 }}
                      />
                    )}
                  </Box>
                </Box>
              </CardContent>
            </Card>
          ))}
        </List>
      </TabPanel>
      
      {/* Events Tab */}
      <TabPanel value={tabValue} index={1}>
        <Grid container spacing={2}>
          {events.map((event) => (
            <Grid item xs={12} md={6} key={event.id}>
              <Card sx={{ height: '100%' }}>
                <CardContent>
                  <Typography variant="h6" component="div">
                    {event.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    {event.description}
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <CalendarTodayIcon fontSize="small" sx={{ mr: 1, color: 'primary.main' }} />
                    <Typography variant="body2">
                      {event.date}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <AccessTimeIcon fontSize="small" sx={{ mr: 1, color: 'primary.main' }} />
                    <Typography variant="body2">
                      {event.time}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <LocationOnIcon fontSize="small" sx={{ mr: 1, color: 'primary.main' }} />
                    <Typography variant="body2">
                      {event.location}
                    </Typography>
                  </Box>
                  <Button 
                    variant="outlined" 
                    color="primary" 
                    sx={{ mt: 2 }}
                    fullWidth
                  >
                    RSVP
                  </Button>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </TabPanel>
      
      {/* Polls Tab */}
      <TabPanel value={tabValue} index={2}>
        {polls.map((poll) => (
          <Paper key={poll.id} elevation={2} sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              {poll.title}
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              {poll.description}
            </Typography>
            <Divider sx={{ my: 2 }} />
            
            {poll.options.map((option) => {
              const votes = poll.votes[option];
              const totalVotes = Object.values(poll.votes).reduce((a: number, b: number) => a + b, 0);
              const percentage = Math.round((votes / totalVotes) * 100);
              
              return (
                <Box key={option} sx={{ mb: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                    <Typography variant="body2">{option}</Typography>
                    <Typography variant="body2">{percentage}% ({votes} votes)</Typography>
                  </Box>
                  <Box sx={{ width: '100%', backgroundColor: '#e0e0e0', borderRadius: 1, height: 8 }}>
                    <Box
                      sx={{
                        width: `${percentage}%`,
                        backgroundColor: 'primary.main',
                        height: '100%',
                        borderRadius: 1,
                      }}
                    />
                  </Box>
                </Box>
              );
            })}
            
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 2 }}>
              <Chip 
                label={`Closes: ${poll.closingDate}`}
                variant="outlined"
                size="small"
              />
              <Button variant="contained" color="primary" size="small">
                Vote Now
              </Button>
            </Box>
          </Paper>
        ))}
      </TabPanel>
    </Box>
  );
};

export default Communication;
