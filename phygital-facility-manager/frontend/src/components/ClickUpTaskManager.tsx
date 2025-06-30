import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Grid,
  Card,
  CardContent,
  CardActions,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Tabs,
  Tab
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Comment as CommentIcon,
  Refresh as RefreshIcon,
  Assignment as TaskIcon
} from '@mui/icons-material';

interface Task {
  id: string;
  name: string;
  description: string;
  status: any; // ClickUp status object
  priority: any; // ClickUp priority object
  due_date?: number;
  assignees: any[];
  tags: any[]; // ClickUp tag objects
  url?: string;
}

interface TaskFormData {
  name: string;
  description: string;
  priority: string;
  status: string;
  due_date: string;
  tags: string;
  assignees: string[];
}

const ClickUpTaskManager: React.FC = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [tabValue, setTabValue] = useState(0);
  const [config, setConfig] = useState<any>(null);
  const [teamMembers, setTeamMembers] = useState<any[]>([]);

  const [formData, setFormData] = useState<TaskFormData>({
    name: '',
    description: '',
    priority: 'normal',
    status: 'to do',
    due_date: '',
    tags: '',
    assignees: []
  });

  useEffect(() => {
    loadConfig();
    loadTasks();
    loadTeamMembers();
  }, []);

  const loadConfig = async () => {
    try {
      const response = await fetch('/api/clickup/config');
      const data = await response.json();
      if (data.success) {
        setConfig(data.config);
      }
    } catch (error) {
      console.error('Failed to load ClickUp config:', error);
    }
  };

  const loadTasks = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('/api/clickup/tasks');
      const data = await response.json();
      
      if (data.success) {
        setTasks(data.tasks);
      } else {
        setError(data.error || 'Failed to load tasks');
      }
    } catch (error) {
      setError('Failed to connect to ClickUp API');
    } finally {
      setLoading(false);
    }
  };

  const loadTeamMembers = async () => {
    try {
      const response = await fetch('/api/clickup/team/members');
      const data = await response.json();

      if (data.success) {
        setTeamMembers(data.members);
      } else {
        console.error('Failed to load team members:', data.error);
      }
    } catch (error) {
      console.error('Failed to connect to ClickUp API for team members:', error);
    }
  };

  const handleCreateTask = async () => {
    if (!formData.name.trim()) {
      setError('Task name is required');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const taskData = {
        name: formData.name,
        description: formData.description,
        priority: formData.priority,
        status: formData.status,
        due_date: formData.due_date || null,
        tags: formData.tags.split(',').map(tag => tag.trim()).filter(tag => tag),
        assignees: formData.assignees
      };

      const response = await fetch('/api/clickup/tasks', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(taskData)
      });

      const data = await response.json();
      
      if (data.success) {
        setSuccess('Task created successfully');
        setOpenDialog(false);
        resetForm();
        loadTasks();
      } else {
        setError(data.error || 'Failed to create task');
      }
    } catch (error) {
      setError('Failed to create task');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateTask = async () => {
    if (!editingTask) return;

    setLoading(true);
    setError(null);
    try {
      const taskData = {
        name: formData.name,
        description: formData.description,
        priority: formData.priority,
        status: formData.status,
        due_date: formData.due_date || null,
        tags: formData.tags.split(',').map(tag => tag.trim()).filter(tag => tag)
      };

      const response = await fetch(`/api/clickup/tasks/${editingTask.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(taskData)
      });

      const data = await response.json();
      
      if (data.success) {
        setSuccess('Task updated successfully');
        setOpenDialog(false);
        setEditingTask(null);
        resetForm();
        loadTasks();
      } else {
        setError(data.error || 'Failed to update task');
      }
    } catch (error) {
      setError('Failed to update task');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteTask = async (taskId: string) => {
    if (!window.confirm('Are you sure you want to delete this task?')) {
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`/api/clickup/tasks/${taskId}`, {
        method: 'DELETE'
      });

      const data = await response.json();
      
      if (data.success) {
        setSuccess('Task deleted successfully');
        loadTasks();
      } else {
        setError(data.error || 'Failed to delete task');
      }
    } catch (error) {
      setError('Failed to delete task');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateMaintenanceRequest = async () => {
    const maintenanceData = {
      title: 'Pool Maintenance Required',
      description: 'The pool filter needs cleaning and chemical balancing',
      apartment: 'A-101',
      category: 'Maintenance',
      priority: 'high',
      contact_name: 'John Doe',
      contact_phone: '+91-9876543210',
      contact_email: 'john.doe@example.com',
      requested_date: new Date().toISOString().split('T')[0]
    };

    setLoading(true);
    setError(null);
    try {
      const response = await fetch('/api/clickup/facility/maintenance-request', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(maintenanceData)
      });

      const data = await response.json();
      
      if (data.success) {
        setSuccess(`Maintenance request created successfully! Task URL: ${data.task_url}`);
        loadTasks();
      } else {
        setError(data.error || 'Failed to create maintenance request');
      }
    } catch (error) {
      setError('Failed to create maintenance request');
    } finally {
      setLoading(false);
    }
  };

  const openEditDialog = (task: Task) => {
    setEditingTask(task);
    setFormData({
      name: task.name,
      description: task.description,
      priority: getPriorityString(task.priority),
      status: task.status?.status || task.status || 'to do',
      due_date: task.due_date ? new Date(task.due_date).toISOString().split('T')[0] : '',
      tags: task.tags ? task.tags.map(tag => tag?.name || tag).join(', ') : '',
      assignees: task.assignees ? task.assignees.map(a => a.id) : []
    });
    setOpenDialog(true);
  };

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      priority: 'normal',
      status: 'to do',
      due_date: '',
      tags: '',
      assignees: []
    });
    setEditingTask(null);
  };

  const getPriorityString = (priority: number): string => {
    const priorityMap: { [key: number]: string } = {
      1: 'urgent',
      2: 'high',
      3: 'normal',
      4: 'low'
    };
    return priorityMap[priority] || 'normal';
  };

  const getPriorityColor = (priority: number): string => {
    const colorMap: { [key: number]: string } = {
      1: 'error',
      2: 'warning',
      3: 'primary',
      4: 'default'
    };
    return colorMap[priority] || 'default';
  };

  const testConnection = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('/api/clickup/test');
      const data = await response.json();
      
      if (data.success) {
        setSuccess(`ClickUp connection successful! Found ${data.teams_count} teams.`);
      } else {
        setError(data.error || 'ClickUp connection failed');
      }
    } catch (error) {
      setError('Failed to test ClickUp connection');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        <TaskIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
        ClickUp Task Management
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      )}

      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={tabValue} onChange={(_, newValue) => setTabValue(newValue)}>
          <Tab label="Tasks" />
          <Tab label="Configuration" />
        </Tabs>
      </Box>

      {tabValue === 0 && (
        <Box>
          <Box sx={{ mb: 3, display: 'flex', gap: 2, flexWrap: 'wrap' }}>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => {
                resetForm();
                setOpenDialog(true);
              }}
            >
              Create Task
            </Button>
            <Button
              variant="outlined"
              startIcon={<RefreshIcon />}
              onClick={loadTasks}
              disabled={loading}
            >
              Refresh
            </Button>
            <Button
              variant="outlined"
              color="secondary"
              onClick={handleCreateMaintenanceRequest}
              disabled={loading}
            >
              Create Sample Maintenance Request
            </Button>
          </Box>

          {loading && (
            <Box sx={{ display: 'flex', justifyContent: 'center', my: 3 }}>
              <CircularProgress />
            </Box>
          )}

          <Grid container spacing={2}>
            {tasks.map((task) => (
              <Grid item xs={12} md={6} lg={4} key={task.id}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      {task.name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      {task.description}
                    </Typography>
                    <Box sx={{ mb: 2 }}>
                      <Chip
                        label={task.status?.status || task.status || 'Unknown'}
                        size="small"
                        sx={{ mr: 1 }}
                      />
                      <Chip
                        label={task.priority?.priority || getPriorityString(task.priority) || 'Normal'}
                        size="small"
                        color={getPriorityColor(task.priority) as any}
                      />
                    </Box>
                    {task.tags && task.tags.length > 0 && (
                      <Box sx={{ mb: 2 }}>
                        {task.tags.map((tag, index) => (
                          <Chip
                            key={index}
                            label={tag?.name || tag || 'Tag'}
                            size="small"
                            variant="outlined"
                            sx={{ mr: 0.5, mb: 0.5 }}
                          />
                        ))}
                      </Box>
                    )}
                    {task.assignees && task.assignees.length > 0 && (
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="caption" color="text.secondary" sx={{ mb: 1, display: 'block' }}>
                          Assignees:
                        </Typography>
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                          {task.assignees.map((assignee, index) => (
                            <Chip
                              key={index}
                              label={assignee?.username || assignee?.email || 'Unknown'}
                              size="small"
                              sx={{
                                backgroundColor: assignee?.color || '#e0e0e0',
                                color: 'white'
                              }}
                            />
                          ))}
                        </Box>
                      </Box>
                    )}
                  </CardContent>
                  <CardActions>
                    <IconButton
                      size="small"
                      onClick={() => openEditDialog(task)}
                    >
                      <EditIcon />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={() => handleDeleteTask(task.id)}
                      color="error"
                    >
                      <DeleteIcon />
                    </IconButton>
                    {task.url && (
                      <Button
                        size="small"
                        href={task.url}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        Open in ClickUp
                      </Button>
                    )}
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>
      )}

      {tabValue === 1 && (
        <Box>
          <Typography variant="h6" gutterBottom>
            ClickUp Configuration
          </Typography>
          
          <Button
            variant="outlined"
            onClick={testConnection}
            disabled={loading}
            sx={{ mb: 2 }}
          >
            Test Connection
          </Button>

          {config && (
            <Paper sx={{ p: 2 }}>
              <Typography variant="subtitle1" gutterBottom>
                Current Configuration:
              </Typography>
              <List>
                <ListItem>
                  <ListItemText
                    primary="API Configured"
                    secondary={config.api_configured ? 'Yes' : 'No'}
                  />
                </ListItem>
                <ListItem>
                  <ListItemText
                    primary="Team ID"
                    secondary={config.team_id || 'Not configured'}
                  />
                </ListItem>
                <ListItem>
                  <ListItemText
                    primary="Space ID"
                    secondary={config.space_id || 'Not configured'}
                  />
                </ListItem>
                <ListItem>
                  <ListItemText
                    primary="List ID"
                    secondary={config.list_id || 'Not configured'}
                  />
                </ListItem>
              </List>
            </Paper>
          )}
        </Box>
      )}

      {/* Task Creation/Edit Dialog */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingTask ? 'Edit Task' : 'Create New Task'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Task Name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Description"
                multiline
                rows={3}
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              />
            </Grid>
            <Grid item xs={6}>
              <FormControl fullWidth>
                <InputLabel>Priority</InputLabel>
                <Select
                  value={formData.priority}
                  onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
                >
                  <MenuItem value="urgent">Urgent</MenuItem>
                  <MenuItem value="high">High</MenuItem>
                  <MenuItem value="normal">Normal</MenuItem>
                  <MenuItem value="low">Low</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={6}>
              <FormControl fullWidth>
                <InputLabel>Status</InputLabel>
                <Select
                  value={formData.status}
                  onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                >
                  <MenuItem value="to do">To Do</MenuItem>
                  <MenuItem value="in progress">In Progress</MenuItem>
                  <MenuItem value="review">Review</MenuItem>
                  <MenuItem value="complete">Complete</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={6}>
              <TextField
                fullWidth
                label="Due Date"
                type="date"
                value={formData.due_date}
                onChange={(e) => setFormData({ ...formData, due_date: e.target.value })}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            <Grid item xs={6}>
              <FormControl fullWidth>
                <InputLabel>Assignees</InputLabel>
                <Select
                  multiple
                  value={formData.assignees}
                  onChange={(e) => setFormData({ ...formData, assignees: e.target.value as string[] })}
                  renderValue={(selected) => (
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                      {selected.map((value) => {
                        const member = teamMembers.find(m => m.id === value);
                        return (
                          <Chip
                            key={value}
                            label={member?.username || value}
                            size="small"
                            sx={{ backgroundColor: member?.color || '#e0e0e0' }}
                          />
                        );
                      })}
                    </Box>
                  )}
                >
                  {teamMembers.map((member) => (
                    <MenuItem key={member.id} value={member.id}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        {member.profilePicture ? (
                          <img
                            src={member.profilePicture}
                            alt={member.username}
                            style={{ width: 24, height: 24, borderRadius: '50%' }}
                          />
                        ) : (
                          <Box
                            sx={{
                              width: 24,
                              height: 24,
                              borderRadius: '50%',
                              backgroundColor: member.color || '#e0e0e0',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              fontSize: '12px',
                              fontWeight: 'bold',
                              color: 'white'
                            }}
                          >
                            {member.initials || member.username?.charAt(0)?.toUpperCase()}
                          </Box>
                        )}
                        <Typography>{member.username}</Typography>
                        {member.email && (
                          <Typography variant="caption" color="text.secondary">
                            ({member.email})
                          </Typography>
                        )}
                      </Box>
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Tags (comma separated)"
                value={formData.tags}
                onChange={(e) => setFormData({ ...formData, tags: e.target.value })}
                placeholder="maintenance, urgent, facility"
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button
            onClick={editingTask ? handleUpdateTask : handleCreateTask}
            variant="contained"
            disabled={loading}
          >
            {loading ? <CircularProgress size={20} /> : (editingTask ? 'Update' : 'Create')}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ClickUpTaskManager;
