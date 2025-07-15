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
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormControlLabel,
  Switch,
  Alert,
  Fab,
  Menu
} from '@mui/material';
import { DatePicker, TimePicker } from '@mui/x-date-pickers';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import EventIcon from '@mui/icons-material/Event';
import AnnouncementIcon from '@mui/icons-material/Announcement';
import PollIcon from '@mui/icons-material/Poll';
import CalendarTodayIcon from '@mui/icons-material/CalendarToday';
import LocationOnIcon from '@mui/icons-material/LocationOn';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import AddIcon from '@mui/icons-material/Add';
import FlagIcon from '@mui/icons-material/Flag';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import CloseIcon from '@mui/icons-material/Close';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

interface Announcement {
  id: string;
  title: string;
  content: string;
  date: string;
  priority: 'normal' | 'high' | 'urgent';
  author: string;
}

interface Event {
  id: string;
  title: string;
  description: string;
  date: string;
  time: string;
  location: string;
  maxAttendees?: number;
  rsvpRequired: boolean;
  author: string;
}

interface Poll {
  id: string;
  title: string;
  description: string;
  options: string[];
  closingDate: string;
  allowMultiple: boolean;
  votes: { [option: string]: number };
  author: string;
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
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [createType, setCreateType] = useState<'announcement' | 'event' | 'poll'>('announcement');
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Form states
  const [announcementForm, setAnnouncementForm] = useState({
    title: '',
    content: '',
    priority: 'normal' as 'normal' | 'high' | 'urgent'
  });

  const [eventForm, setEventForm] = useState({
    title: '',
    description: '',
    date: new Date(),
    time: new Date(),
    location: '',
    maxAttendees: '',
    rsvpRequired: true
  });

  const [pollForm, setPollForm] = useState({
    title: '',
    description: '',
    options: ['', ''],
    closingDate: new Date(),
    allowMultiple: false
  });

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleCreateClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleCreateMenuClose = () => {
    setAnchorEl(null);
  };

  const handleCreateType = (type: 'announcement' | 'event' | 'poll') => {
    setCreateType(type);
    setCreateDialogOpen(true);
    setAnchorEl(null);
  };
  
  // State for data
  const [announcements, setAnnouncements] = useState<Announcement[]>([
    {
      id: 'ann001',
      title: 'Monthly Maintenance Schedule',
      content: 'The maintenance team will be servicing all common areas on the 15th of this month.',
      date: '2025-06-05',
      priority: 'normal',
      author: 'Facility Manager'
    },
    {
      id: 'ann002',
      title: 'Swimming Pool Closure',
      content: 'The swimming pool will be closed for maintenance from June 20th to June 22nd.',
      date: '2025-06-08',
      priority: 'high',
      author: 'Maintenance Team'
    },
    {
      id: 'ann003',
      title: 'Community Gathering',
      content: 'Join us for a community BBQ on the 25th of this month at the central garden. All residents are welcome to join. Food and beverages will be provided. Please RSVP by the 20th.',
      date: '2025-06-10',
      priority: 'normal',
      author: 'Community Manager'
    }
  ]);
  
  const [events, setEvents] = useState<Event[]>([
    {
      id: 'evt001',
      title: 'Community BBQ',
      description: 'Summer community gathering with food and games.',
      date: '2025-06-25',
      time: '18:00-21:00',
      location: 'Central Garden',
      maxAttendees: 50,
      rsvpRequired: true,
      author: 'Community Manager'
    },
    {
      id: 'evt002',
      title: 'Yoga Session',
      description: 'Weekly yoga session for all residents.',
      date: '2025-06-15',
      time: '08:00-09:00',
      location: 'Community Hall',
      rsvpRequired: false,
      author: 'Wellness Committee'
    },
    {
      id: 'evt003',
      title: 'Residents Association Meeting',
      description: 'Quarterly meeting to discuss community issues and updates.',
      date: '2025-07-05',
      time: '19:00-20:30',
      location: 'Conference Room',
      rsvpRequired: true,
      author: 'Residents Association'
    }
  ]);
  
  const [polls, setPolls] = useState<Poll[]>([
    {
      id: 'poll001',
      title: 'Garden Renovation Options',
      description: 'Vote for your preferred garden renovation design.',
      options: ['Modern design', 'Traditional design', 'Eco-friendly design'],
      closingDate: '2025-06-20',
      allowMultiple: false,
      votes: {
        'Modern design': 15,
        'Traditional design': 8,
        'Eco-friendly design': 22
      },
      author: 'Landscape Committee'
    },
    {
      id: 'poll002',
      title: 'Community Event Preference',
      description: 'What type of community event would you prefer for next month?',
      options: ['Movie night', 'Sports tournament', 'Cultural festival'],
      closingDate: '2025-06-18',
      allowMultiple: false,
      votes: {
        'Movie night': 18,
        'Sports tournament': 12,
        'Cultural festival': 25
      },
      author: 'Events Committee'
    }
  ]);

  // Creation handlers
  const handleCreateAnnouncement = () => {
    if (!announcementForm.title || !announcementForm.content) {
      setError('Please fill in all required fields');
      return;
    }

    const newAnnouncement: Announcement = {
      id: `ann${Date.now()}`,
      title: announcementForm.title,
      content: announcementForm.content,
      priority: announcementForm.priority,
      date: new Date().toISOString().split('T')[0],
      author: 'Current User' // In real app, get from auth context
    };

    setAnnouncements([newAnnouncement, ...announcements]);
    setAnnouncementForm({ title: '', content: '', priority: 'normal' });
    setCreateDialogOpen(false);
    setSuccess('Announcement created successfully!');
  };

  const handleCreateEvent = () => {
    if (!eventForm.title || !eventForm.description || !eventForm.location) {
      setError('Please fill in all required fields');
      return;
    }

    const newEvent: Event = {
      id: `evt${Date.now()}`,
      title: eventForm.title,
      description: eventForm.description,
      date: eventForm.date.toISOString().split('T')[0],
      time: eventForm.time.toTimeString().slice(0, 5),
      location: eventForm.location,
      maxAttendees: eventForm.maxAttendees ? parseInt(eventForm.maxAttendees) : undefined,
      rsvpRequired: eventForm.rsvpRequired,
      author: 'Current User'
    };

    setEvents([newEvent, ...events]);
    setEventForm({
      title: '',
      description: '',
      date: new Date(),
      time: new Date(),
      location: '',
      maxAttendees: '',
      rsvpRequired: true
    });
    setCreateDialogOpen(false);
    setSuccess('Event created successfully!');
  };

  const handleCreatePoll = () => {
    const validOptions = pollForm.options.filter(option => option.trim() !== '');

    if (!pollForm.title || !pollForm.description || validOptions.length < 2) {
      setError('Please provide a title, description, and at least 2 options');
      return;
    }

    const newPoll: Poll = {
      id: `poll${Date.now()}`,
      title: pollForm.title,
      description: pollForm.description,
      options: validOptions,
      closingDate: pollForm.closingDate.toISOString().split('T')[0],
      allowMultiple: pollForm.allowMultiple,
      votes: validOptions.reduce((acc, option) => ({ ...acc, [option]: 0 }), {}),
      author: 'Current User'
    };

    setPolls([newPoll, ...polls]);
    setPollForm({
      title: '',
      description: '',
      options: ['', ''],
      closingDate: new Date(),
      allowMultiple: false
    });
    setCreateDialogOpen(false);
    setSuccess('Poll created successfully!');
  };

  const handleSubmit = () => {
    setError(null);

    switch (createType) {
      case 'announcement':
        handleCreateAnnouncement();
        break;
      case 'event':
        handleCreateEvent();
        break;
      case 'poll':
        handleCreatePoll();
        break;
    }
  };

  const addPollOption = () => {
    setPollForm({
      ...pollForm,
      options: [...pollForm.options, '']
    });
  };

  const removePollOption = (index: number) => {
    if (pollForm.options.length > 2) {
      const newOptions = pollForm.options.filter((_, i) => i !== index);
      setPollForm({ ...pollForm, options: newOptions });
    }
  };

  const updatePollOption = (index: number, value: string) => {
    const newOptions = [...pollForm.options];
    newOptions[index] = value;
    setPollForm({ ...pollForm, options: newOptions });
  };

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <Box>
        {/* Success/Error Messages */}
        {success && (
          <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess(null)}>
            {success}
          </Alert>
        )}
        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h5" component="h1">
            Community Communication
          </Typography>
          <Button
            variant="contained"
            color="primary"
            startIcon={<AddIcon />}
            onClick={handleCreateClick}
            size="small"
          >
            Create New
          </Button>

          {/* Create Menu */}
          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleCreateMenuClose}
          >
            <MenuItem onClick={() => handleCreateType('announcement')}>
              <AnnouncementIcon sx={{ mr: 1 }} />
              Announcement
            </MenuItem>
            <MenuItem onClick={() => handleCreateType('event')}>
              <EventIcon sx={{ mr: 1 }} />
              Event
            </MenuItem>
            <MenuItem onClick={() => handleCreateType('poll')}>
              <PollIcon sx={{ mr: 1 }} />
              Poll
            </MenuItem>
          </Menu>
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
        <Typography variant="h6" sx={{ mb: 2 }}>Recent Announcements</Typography>
        <List>
          {announcements.map((announcement) => (
            <Card key={announcement.id} sx={{ mb: 2 }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'flex-start' }}>
                  <ListItemAvatar>
                    <Avatar sx={{
                      bgcolor: announcement.priority === 'urgent' ? '#d32f2f' :
                               announcement.priority === 'high' ? '#f57c00' : '#1976d2'
                    }}>
                      {announcement.priority === 'urgent' || announcement.priority === 'high' ? <FlagIcon /> : <AnnouncementIcon />}
                    </Avatar>
                  </ListItemAvatar>
                  <Box sx={{ width: '100%' }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                      <Box sx={{ flex: 1 }}>
                        <Typography variant="subtitle1" component="div" fontWeight="bold">
                          {announcement.title}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          By {announcement.author} • {announcement.date}
                        </Typography>
                      </Box>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        {announcement.priority !== 'normal' && (
                          <Chip
                            label={announcement.priority.toUpperCase()}
                            color={announcement.priority === 'urgent' ? 'error' : 'warning'}
                            size="small"
                          />
                        )}
                        <IconButton size="small">
                          <MoreVertIcon />
                        </IconButton>
                      </Box>
                    </Box>
                    <Typography variant="body2" sx={{ mt: 1 }}>
                      {announcement.content}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          ))}
        </List>
      </TabPanel>
      
      {/* Events Tab */}
      <TabPanel value={tabValue} index={1}>
        <Typography variant="h6" sx={{ mb: 2 }}>Upcoming Events</Typography>
        <Grid container spacing={2}>
          {events.map((event) => (
            <Grid item xs={12} md={6} key={event.id}>
              <Card sx={{ height: '100%' }}>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                    <Typography variant="h6" component="div">
                      {event.title}
                    </Typography>
                    <IconButton size="small">
                      <MoreVertIcon />
                    </IconButton>
                  </Box>
                  <Typography variant="caption" color="text.secondary" sx={{ mb: 1, display: 'block' }}>
                    Organized by {event.author}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    {event.description}
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <CalendarTodayIcon fontSize="small" sx={{ mr: 1, color: 'primary.main' }} />
                    <Typography variant="body2">
                      {new Date(event.date).toLocaleDateString()}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <AccessTimeIcon fontSize="small" sx={{ mr: 1, color: 'primary.main' }} />
                    <Typography variant="body2">
                      {event.time}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <LocationOnIcon fontSize="small" sx={{ mr: 1, color: 'primary.main' }} />
                    <Typography variant="body2">
                      {event.location}
                    </Typography>
                  </Box>
                  {event.maxAttendees && (
                    <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1 }}>
                      Max Attendees: {event.maxAttendees}
                    </Typography>
                  )}
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <Button
                      variant="contained"
                      color="primary"
                      size="small"
                      fullWidth
                    >
                      {event.rsvpRequired ? 'RSVP' : 'Join Event'}
                    </Button>
                    {event.rsvpRequired && (
                      <Chip label="RSVP Required" size="small" color="info" />
                    )}
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </TabPanel>
      
      {/* Polls Tab */}
      <TabPanel value={tabValue} index={2}>
        <Typography variant="h6" sx={{ mb: 2 }}>Active Polls</Typography>
        {polls.map((poll) => (
          <Paper key={poll.id} elevation={2} sx={{ p: 3, mb: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
              <Typography variant="h6" gutterBottom>
                {poll.title}
              </Typography>
              <IconButton size="small">
                <MoreVertIcon />
              </IconButton>
            </Box>
            <Typography variant="caption" color="text.secondary" sx={{ mb: 1, display: 'block' }}>
              Created by {poll.author}
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              {poll.description}
            </Typography>
            {poll.allowMultiple && (
              <Chip label="Multiple selections allowed" size="small" color="info" sx={{ mb: 2 }} />
            )}
            <Divider sx={{ my: 2 }} />

            {poll.options.map((option) => {
              const votes = poll.votes[option];
              const totalVotes = Object.values(poll.votes).reduce((a: number, b: number) => a + b, 0);
              const percentage = totalVotes > 0 ? Math.round((votes / totalVotes) * 100) : 0;

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
              <Box sx={{ display: 'flex', gap: 1 }}>
                <Chip
                  label={`Closes: ${new Date(poll.closingDate).toLocaleDateString()}`}
                  variant="outlined"
                  size="small"
                />
                <Chip
                  label={`${Object.values(poll.votes).reduce((a, b) => a + b, 0)} total votes`}
                  variant="outlined"
                  size="small"
                />
              </Box>
              <Button variant="contained" color="primary" size="small">
                Vote Now
              </Button>
            </Box>
          </Paper>
        ))}
      </TabPanel>

      {/* Creation Dialog */}
      <Dialog
        open={createDialogOpen}
        onClose={() => setCreateDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          Create New {createType.charAt(0).toUpperCase() + createType.slice(1)}
          <IconButton onClick={() => setCreateDialogOpen(false)}>
            <CloseIcon />
          </IconButton>
        </DialogTitle>

        <DialogContent>
          {createType === 'announcement' && (
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Announcement Title"
                  value={announcementForm.title}
                  onChange={(e) => setAnnouncementForm({ ...announcementForm, title: e.target.value })}
                  required
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Content"
                  multiline
                  rows={4}
                  value={announcementForm.content}
                  onChange={(e) => setAnnouncementForm({ ...announcementForm, content: e.target.value })}
                  required
                />
              </Grid>
              <Grid item xs={12}>
                <FormControl fullWidth>
                  <InputLabel>Priority</InputLabel>
                  <Select
                    value={announcementForm.priority}
                    label="Priority"
                    onChange={(e) => setAnnouncementForm({ ...announcementForm, priority: e.target.value as 'normal' | 'high' | 'urgent' })}
                  >
                    <MenuItem value="normal">Normal</MenuItem>
                    <MenuItem value="high">High</MenuItem>
                    <MenuItem value="urgent">Urgent</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
            </Grid>
          )}

          {createType === 'event' && (
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Event Title"
                  value={eventForm.title}
                  onChange={(e) => setEventForm({ ...eventForm, title: e.target.value })}
                  required
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Description"
                  multiline
                  rows={3}
                  value={eventForm.description}
                  onChange={(e) => setEventForm({ ...eventForm, description: e.target.value })}
                  required
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <DatePicker
                  label="Event Date"
                  value={eventForm.date}
                  onChange={(newValue) => setEventForm({ ...eventForm, date: newValue || new Date() })}
                  renderInput={(params) => <TextField {...params} fullWidth />}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TimePicker
                  label="Event Time"
                  value={eventForm.time}
                  onChange={(newValue) => setEventForm({ ...eventForm, time: newValue || new Date() })}
                  renderInput={(params) => <TextField {...params} fullWidth />}
                />
              </Grid>
              <Grid item xs={12} md={8}>
                <TextField
                  fullWidth
                  label="Location"
                  value={eventForm.location}
                  onChange={(e) => setEventForm({ ...eventForm, location: e.target.value })}
                  required
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  label="Max Attendees"
                  type="number"
                  value={eventForm.maxAttendees}
                  onChange={(e) => setEventForm({ ...eventForm, maxAttendees: e.target.value })}
                />
              </Grid>
              <Grid item xs={12}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={eventForm.rsvpRequired}
                      onChange={(e) => setEventForm({ ...eventForm, rsvpRequired: e.target.checked })}
                    />
                  }
                  label="RSVP Required"
                />
              </Grid>
            </Grid>
          )}

          {createType === 'poll' && (
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Poll Title"
                  value={pollForm.title}
                  onChange={(e) => setPollForm({ ...pollForm, title: e.target.value })}
                  required
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Description"
                  multiline
                  rows={2}
                  value={pollForm.description}
                  onChange={(e) => setPollForm({ ...pollForm, description: e.target.value })}
                  required
                />
              </Grid>
              <Grid item xs={12}>
                <Typography variant="subtitle1" gutterBottom>
                  Poll Options
                </Typography>
                {pollForm.options.map((option, index) => (
                  <Box key={index} sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <TextField
                      fullWidth
                      label={`Option ${index + 1}`}
                      value={option}
                      onChange={(e) => updatePollOption(index, e.target.value)}
                      required
                    />
                    {pollForm.options.length > 2 && (
                      <IconButton onClick={() => removePollOption(index)} color="error">
                        <DeleteIcon />
                      </IconButton>
                    )}
                  </Box>
                ))}
                <Button
                  startIcon={<AddIcon />}
                  onClick={addPollOption}
                  variant="outlined"
                  size="small"
                >
                  Add Option
                </Button>
              </Grid>
              <Grid item xs={12} md={6}>
                <DatePicker
                  label="Closing Date"
                  value={pollForm.closingDate}
                  onChange={(newValue) => setPollForm({ ...pollForm, closingDate: newValue || new Date() })}
                  renderInput={(params) => <TextField {...params} fullWidth />}
                />
              </Grid>
              <Grid item xs={12}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={pollForm.allowMultiple}
                      onChange={(e) => setPollForm({ ...pollForm, allowMultiple: e.target.checked })}
                    />
                  }
                  label="Allow Multiple Selections"
                />
              </Grid>
            </Grid>
          )}
        </DialogContent>

        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>
            Cancel
          </Button>
          <Button onClick={handleSubmit} variant="contained">
            Create {createType.charAt(0).toUpperCase() + createType.slice(1)}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
    </LocalizationProvider>
  );
};

export default Communication;
