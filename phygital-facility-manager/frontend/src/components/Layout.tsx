import React, { useState, useEffect } from 'react';
import { Outlet, useLocation, useNavigate } from 'react-router-dom';
import { 
  AppBar, 
  Box, 
  Toolbar, 
  Typography, 
  IconButton, 
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  BottomNavigation,
  BottomNavigationAction,
  useMediaQuery,
  useTheme,
  Container,
  Avatar
} from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import HomeIcon from '@mui/icons-material/Home';
import ArticleIcon from '@mui/icons-material/Article';
import ForumIcon from '@mui/icons-material/Forum';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import AccountBalanceIcon from '@mui/icons-material/AccountBalance';
import ClickUpIcon from './icons/ClickUpIcon';

const Layout: React.FC = () => {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [value, setValue] = useState(0);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const location = useLocation();
  const navigate = useNavigate();
  
  // Map routes to navigation indexes
  useEffect(() => {
    const pathToIndex: { [key: string]: number } = {
      '/': 0,
      '/knowledge-base': 1,
      '/communication': 2,
      '/clickup-tasks': 3,
      '/openai-assistant': 4,
    };
    setValue(pathToIndex[location.pathname] || 0);
  }, [location.pathname]);

  const handleNavigation = (newValue: number) => {
    setValue(newValue);
    const indexToPath = ['/', '/knowledge-base', '/communication', '/financial-dashboard', '/clickup-tasks', '/openai-assistant'];
    navigate(indexToPath[newValue]);
  };

  const navigationItems = [
    { label: 'Home', icon: <HomeIcon />, path: '/' },
    { label: 'Knowledge Base', icon: <ArticleIcon />, path: '/knowledge-base' },
    { label: 'Communication', icon: <ForumIcon />, path: '/communication' },
    { label: 'Financial Dashboard', icon: <AccountBalanceIcon />, path: '/financial-dashboard' },
    { label: 'ClickUp Tasks', icon: <ClickUpIcon size={24} />, path: '/clickup-tasks' },
    { label: 'AI Assistant', icon: <SmartToyIcon />, path: '/openai-assistant' },
  ];

  const toggleDrawer = () => {
    setDrawerOpen(!drawerOpen);
  };

  const drawer = (
    <Box sx={{ width: 250 }} role="presentation" onClick={toggleDrawer}>
      <List>
        {navigationItems.map((item, index) => (
          <ListItem 
            button 
            key={item.label}
            onClick={() => navigate(item.path)}
            selected={value === index}
          >
            <ListItemIcon>{item.icon}</ListItemIcon>
            <ListItemText primary={item.label} />
          </ListItem>
        ))}
      </List>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <AppBar position="static">
        <Toolbar>
          <IconButton
            size="large"
            edge="start"
            color="inherit"
            aria-label="menu"
            sx={{ mr: 2, display: { sm: 'none' } }}
            onClick={toggleDrawer}
          >
            <MenuIcon />
          </IconButton>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Avatar 
              alt="Gopalan Atlantis" 
              src="/logo192.png" 
              sx={{ mr: 1, width: 40, height: 40 }}
            />
            <Typography variant="h6" component="div">
              Gopalan Atlantis
            </Typography>
          </Box>
          <Box sx={{ flexGrow: 1 }} />
          <Box sx={{ display: { xs: 'none', sm: 'flex' } }}>
            {navigationItems.map((item, index) => (
              <IconButton
                key={item.label}
                color="inherit"
                onClick={() => handleNavigation(index)}
              >
                {item.icon}
              </IconButton>
            ))}
          </Box>
        </Toolbar>
      </AppBar>
      
      <Drawer
        anchor="left"
        open={drawerOpen}
        onClose={toggleDrawer}
      >
        {drawer}
      </Drawer>
      
      <Container component="main" className="content" sx={{ flexGrow: 1, py: 3 }}>
        <Outlet />
      </Container>
      
      {isMobile && (
        <BottomNavigation
          value={value}
          onChange={(_, newValue) => {
            handleNavigation(newValue);
          }}
          showLabels
          className="bottom-nav"
        >
          {navigationItems.map((item) => (
            <BottomNavigationAction key={item.label} label={item.label} icon={item.icon} />
          ))}
        </BottomNavigation>
      )}
    </Box>
  );
};

export default Layout;
