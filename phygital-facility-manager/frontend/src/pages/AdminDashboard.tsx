import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  Avatar,
  LinearProgress,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  People as PeopleIcon,
  Business as PropertyIcon,
  Settings as SettingsIcon,
  TrendingUp as TrendingUpIcon,
  Notifications as NotificationsIcon,
  Security as SecurityIcon,
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';

interface User {
  id: string;
  name: string;
  email: string;
  role: string;
  apartment?: string;
  status: 'active' | 'inactive';
  lastLogin?: string;
}

interface Property {
  id: string;
  unit: string;
  owner: string;
  status: 'occupied' | 'vacant' | 'maintenance';
  type: 'apartment' | 'commercial';
  size: string;
}

const AdminDashboard: React.FC = () => {
  const { user, hasRole } = useAuth();
  const [users, setUsers] = useState<User[]>([]);
  const [properties, setProperties] = useState<Property[]>([]);
  const [userDialogOpen, setUserDialogOpen] = useState(false);
  const [propertyDialogOpen, setPropertyDialogOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [selectedProperty, setSelectedProperty] = useState<Property | null>(null);
  const [loading, setLoading] = useState(true);

  // Mock data - replace with actual API calls
  useEffect(() => {
    const mockUsers: User[] = [
      { id: '1', name: 'John Doe', email: 'john@example.com', role: 'owner', apartment: 'A-101', status: 'active', lastLogin: '2025-01-12' },
      { id: '2', name: 'Jane Smith', email: 'jane@example.com', role: 'fm', status: 'active', lastLogin: '2025-01-11' },
      { id: '3', name: 'Bob Wilson', email: 'bob@example.com', role: 'management', apartment: 'B-205', status: 'active', lastLogin: '2025-01-10' },
    ];

    const mockProperties: Property[] = [
      { id: '1', unit: 'A-101', owner: 'John Doe', status: 'occupied', type: 'apartment', size: '2BHK' },
      { id: '2', unit: 'A-102', owner: 'Jane Smith', status: 'vacant', type: 'apartment', size: '3BHK' },
      { id: '3', unit: 'B-201', owner: 'Bob Wilson', status: 'maintenance', type: 'apartment', size: '2BHK' },
    ];

    setUsers(mockUsers);
    setProperties(mockProperties);
    setLoading(false);
  }, []);

  const handleAddUser = () => {
    setSelectedUser(null);
    setUserDialogOpen(true);
  };

  const handleEditUser = (user: User) => {
    setSelectedUser(user);
    setUserDialogOpen(true);
  };

  const handleAddProperty = () => {
    setSelectedProperty(null);
    setPropertyDialogOpen(true);
  };

  const handleEditProperty = (property: Property) => {
    setSelectedProperty(property);
    setPropertyDialogOpen(true);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
      case 'occupied':
        return 'success';
      case 'inactive':
      case 'vacant':
        return 'warning';
      case 'maintenance':
        return 'error';
      default:
        return 'default';
    }
  };

  const getRoleColor = (role: string) => {
    switch (role) {
      case 'admin':
        return 'error';
      case 'management':
        return 'warning';
      case 'fm':
        return 'info';
      case 'owner':
        return 'success';
      default:
        return 'default';
    }
  };

  if (!hasRole(['admin', 'management'])) {
    return (
      <Container maxWidth="xl" sx={{ py: 4 }}>
        <Typography variant="h4" color="error">
          Access Denied
        </Typography>
        <Typography variant="body1">
          You don't have permission to access the admin dashboard.
        </Typography>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" sx={{ mb: 1, fontWeight: 700 }}>
          Admin Dashboard
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Manage users, properties, and system settings
        </Typography>
      </Box>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ p: 3, textAlign: 'center' }}>
            <PeopleIcon sx={{ fontSize: 40, color: 'primary.main', mb: 2 }} />
            <Typography variant="h3" sx={{ fontWeight: 700, mb: 1 }}>
              {users.length}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              TOTAL USERS
            </Typography>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ p: 3, textAlign: 'center' }}>
            <PropertyIcon sx={{ fontSize: 40, color: 'secondary.main', mb: 2 }} />
            <Typography variant="h3" sx={{ fontWeight: 700, mb: 1 }}>
              {properties.length}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              PROPERTIES
            </Typography>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ p: 3, textAlign: 'center' }}>
            <TrendingUpIcon sx={{ fontSize: 40, color: 'success.main', mb: 2 }} />
            <Typography variant="h3" sx={{ fontWeight: 700, mb: 1 }}>
              95%
            </Typography>
            <Typography variant="body2" color="text.secondary">
              OCCUPANCY RATE
            </Typography>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ p: 3, textAlign: 'center' }}>
            <SecurityIcon sx={{ fontSize: 40, color: 'warning.main', mb: 2 }} />
            <Typography variant="h3" sx={{ fontWeight: 700, mb: 1 }}>
              3
            </Typography>
            <Typography variant="body2" color="text.secondary">
              PENDING ISSUES
            </Typography>
          </Card>
        </Grid>
      </Grid>

      {/* User Management */}
      <Grid container spacing={3}>
        <Grid item xs={12} lg={8}>
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h6" sx={{ fontWeight: 600 }}>
                  User Management
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={handleAddUser}
                >
                  Add User
                </Button>
              </Box>

              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>User</TableCell>
                      <TableCell>Role</TableCell>
                      <TableCell>Apartment</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Last Login</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {users.map((user) => (
                      <TableRow key={user.id}>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                            <Avatar sx={{ width: 32, height: 32 }}>
                              {user.name.charAt(0)}
                            </Avatar>
                            <Box>
                              <Typography variant="body2" sx={{ fontWeight: 600 }}>
                                {user.name}
                              </Typography>
                              <Typography variant="caption" color="text.secondary">
                                {user.email}
                              </Typography>
                            </Box>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={user.role.toUpperCase()}
                            color={getRoleColor(user.role) as any}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>{user.apartment || '-'}</TableCell>
                        <TableCell>
                          <Chip
                            label={user.status.toUpperCase()}
                            color={getStatusColor(user.status) as any}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>{user.lastLogin || '-'}</TableCell>
                        <TableCell>
                          <IconButton size="small" onClick={() => handleEditUser(user)}>
                            <EditIcon />
                          </IconButton>
                          <IconButton size="small" color="error">
                            <DeleteIcon />
                          </IconButton>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>

          {/* Property Management */}
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h6" sx={{ fontWeight: 600 }}>
                  Property Management
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={handleAddProperty}
                >
                  Add Property
                </Button>
              </Box>

              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Unit</TableCell>
                      <TableCell>Owner</TableCell>
                      <TableCell>Type</TableCell>
                      <TableCell>Size</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {properties.map((property) => (
                      <TableRow key={property.id}>
                        <TableCell sx={{ fontWeight: 600 }}>{property.unit}</TableCell>
                        <TableCell>{property.owner}</TableCell>
                        <TableCell>{property.type}</TableCell>
                        <TableCell>{property.size}</TableCell>
                        <TableCell>
                          <Chip
                            label={property.status.toUpperCase()}
                            color={getStatusColor(property.status) as any}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          <IconButton size="small" onClick={() => handleEditProperty(property)}>
                            <EditIcon />
                          </IconButton>
                          <IconButton size="small" color="error">
                            <DeleteIcon />
                          </IconButton>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* System Overview */}
        <Grid item xs={12} lg={4}>
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 3 }}>
                System Health
              </Typography>
              
              <Box sx={{ mb: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">Database</Typography>
                  <Typography variant="body2" color="success.main">98%</Typography>
                </Box>
                <LinearProgress variant="determinate" value={98} color="success" />
              </Box>

              <Box sx={{ mb: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">API Response</Typography>
                  <Typography variant="body2" color="success.main">95%</Typography>
                </Box>
                <LinearProgress variant="determinate" value={95} color="success" />
              </Box>

              <Box sx={{ mb: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">Storage</Typography>
                  <Typography variant="body2" color="warning.main">78%</Typography>
                </Box>
                <LinearProgress variant="determinate" value={78} color="warning" />
              </Box>
            </CardContent>
          </Card>

          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 3 }}>
                Quick Actions
              </Typography>
              
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Button variant="outlined" startIcon={<SettingsIcon />} fullWidth>
                  System Settings
                </Button>
                <Button variant="outlined" startIcon={<NotificationsIcon />} fullWidth>
                  Send Announcement
                </Button>
                <Button variant="outlined" startIcon={<SecurityIcon />} fullWidth>
                  Security Logs
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* User Dialog - Placeholder */}
      <Dialog open={userDialogOpen} onClose={() => setUserDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>{selectedUser ? 'Edit User' : 'Add User'}</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary">
            User management form would go here
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setUserDialogOpen(false)}>Cancel</Button>
          <Button variant="contained">Save</Button>
        </DialogActions>
      </Dialog>

      {/* Property Dialog - Placeholder */}
      <Dialog open={propertyDialogOpen} onClose={() => setPropertyDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>{selectedProperty ? 'Edit Property' : 'Add Property'}</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary">
            Property management form would go here
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPropertyDialogOpen(false)}>Cancel</Button>
          <Button variant="contained">Save</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default AdminDashboard;
