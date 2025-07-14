import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Box,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Typography,
  Avatar,
  Divider,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  People as PeopleIcon,
  Business as PropertyIcon,
  Description as DocumentIcon,
  Campaign as CommunicationIcon,
  AccountBalance as FinancialIcon,
  Assignment as TaskIcon,
  SmartToy as AIIcon,
  Settings as SettingsIcon,
  Person as PersonIcon,
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';

// Navigation items with role-based access
const navigationItems = [
  {
    label: 'Dashboard',
    path: '/',
    icon: <DashboardIcon />,
    roles: ['admin', 'management', 'fm', 'owner'],
  },
  {
    label: 'User Management',
    path: '/user-management',
    icon: <PeopleIcon />,
    roles: ['admin', 'management'],
  },
  {
    label: 'Property Management',
    path: '/property-management',
    icon: <PropertyIcon />,
    roles: ['admin', 'management', 'fm'],
  },
  {
    label: 'Document Management',
    path: '/document-management',
    icon: <DocumentIcon />,
    roles: ['admin', 'management', 'fm', 'owner'],
  },
  {
    label: 'Communication Management',
    path: '/communication',
    icon: <CommunicationIcon />,
    roles: ['admin', 'management', 'fm'],
  },
  {
    label: 'Financial Management',
    path: '/financial-dashboard',
    icon: <FinancialIcon />,
    roles: ['admin', 'management', 'fm'],
  },
  {
    label: 'Task Management',
    path: '/clickup-tasks',
    icon: <TaskIcon />,
    roles: ['admin', 'management', 'fm'],
  },
  {
    label: 'AI Assistant',
    path: '/openai-assistant',
    icon: <AIIcon />,
    roles: ['admin', 'management', 'fm', 'owner'],
  },
  {
    label: 'System Settings',
    path: '/settings',
    icon: <SettingsIcon />,
    roles: ['admin'],
  },
];

interface SidebarProps {
  open?: boolean;
  onClose?: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ open = true, onClose }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, hasRole } = useAuth();

  // Filter navigation items based on user role
  const filteredItems = navigationItems.filter(item => 
    hasRole(item.roles)
  );

  const handleNavigation = (path: string) => {
    navigate(path);
    if (onClose) onClose();
  };

  return (
    <Box
      sx={{
        width: 280,
        height: '100vh',
        background: 'linear-gradient(180deg, #5B5CE6 0%, #4A4BC4 100%)',
        color: 'white',
        display: 'flex',
        flexDirection: 'column',
        position: 'fixed',
        left: 0,
        top: 0,
        zIndex: 1200,
        transform: open ? 'translateX(0)' : 'translateX(-100%)',
        transition: 'transform 0.3s ease-in-out',
      }}
    >
      {/* User Profile Section */}
      <Box sx={{ p: 3, textAlign: 'center' }}>
        <Avatar
          sx={{
            width: 60,
            height: 60,
            mx: 'auto',
            mb: 2,
            backgroundColor: 'rgba(255, 255, 255, 0.2)',
            fontSize: '1.5rem',
            fontWeight: 600,
          }}
        >
          <PersonIcon />
        </Avatar>
        <Typography variant="h6" sx={{ fontWeight: 600, mb: 0.5 }}>
          {user?.name || 'User'}
        </Typography>
        <Typography
          variant="body2"
          sx={{
            opacity: 0.8,
            textTransform: 'capitalize',
            backgroundColor: 'rgba(255, 255, 255, 0.1)',
            px: 2,
            py: 0.5,
            borderRadius: 1,
            display: 'inline-block',
          }}
        >
          {user?.role}
        </Typography>
      </Box>

      <Divider sx={{ borderColor: 'rgba(255, 255, 255, 0.1)' }} />

      {/* Navigation Items */}
      <Box sx={{ flex: 1, overflow: 'auto' }}>
        <List sx={{ px: 2, py: 1 }}>
          {filteredItems.map((item) => {
            const isActive = location.pathname === item.path;
            
            return (
              <ListItem key={item.path} disablePadding sx={{ mb: 0.5 }}>
                <ListItemButton
                  onClick={() => handleNavigation(item.path)}
                  sx={{
                    borderRadius: 2,
                    py: 1.5,
                    px: 2,
                    backgroundColor: isActive ? 'rgba(255, 255, 255, 0.15)' : 'transparent',
                    '&:hover': {
                      backgroundColor: 'rgba(255, 255, 255, 0.1)',
                    },
                    '&.Mui-selected': {
                      backgroundColor: 'rgba(255, 255, 255, 0.15)',
                    },
                  }}
                  selected={isActive}
                >
                  <ListItemIcon
                    sx={{
                      color: 'white',
                      minWidth: 40,
                      opacity: isActive ? 1 : 0.8,
                    }}
                  >
                    {item.icon}
                  </ListItemIcon>
                  <ListItemText
                    primary={item.label}
                    primaryTypographyProps={{
                      fontSize: '0.95rem',
                      fontWeight: isActive ? 600 : 500,
                      opacity: isActive ? 1 : 0.9,
                    }}
                  />
                </ListItemButton>
              </ListItem>
            );
          })}
        </List>
      </Box>
    </Box>
  );
};

export default Sidebar;
