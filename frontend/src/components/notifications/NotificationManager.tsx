import React, { useState, useEffect } from 'react';
import {
  Snackbar,
  Alert,
  IconButton,
  Box,
  Badge,
  Tooltip,
} from '@mui/material';
import NotificationsIcon from '@mui/icons-material/Notifications';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

interface Notification {
  id: number;
  title: string;
  message: string;
  type: 'success' | 'error' | 'warning' | 'info';
  read: boolean;
  createdAt: string;
  action?: {
    label: string;
    path: string;
  };
}

const NotificationManager: React.FC = () => {
  const navigate = useNavigate();
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [open, setOpen] = useState(false);
  const [activeNotification, setActiveNotification] = useState<Notification | null>(null);

  useEffect(() => {
    const fetchNotifications = async () => {
      try {
        const response = await axios.get('/api/notifications');
        setNotifications(response.data);
      } catch (error) {
        console.error('Error fetching notifications:', error);
      }
    };

    fetchNotifications();
    const interval = setInterval(fetchNotifications, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const markAsRead = async (notificationId: number) => {
    try {
      await axios.put(`/api/notifications/${notificationId}/read`);
      setNotifications((prev) =>
        prev.map((n) =>
          n.id === notificationId ? { ...n, read: true } : n
        )
      );
    } catch (error) {
      console.error('Error marking notification as read:', error);
    }
  };

  const handleAction = (notification: Notification) => {
    if (notification.action) {
      navigate(notification.action.path);
      markAsRead(notification.id);
    }
  };

  const handleNotificationClick = (notification: Notification) => {
    setActiveNotification(notification);
    setOpen(true);
    markAsRead(notification.id);
  };

  const handleClose = () => {
    setOpen(false);
    setActiveNotification(null);
  };

  const unreadCount = notifications.filter((n) => !n.read).length;

  return (
    <Box>
      <Tooltip title="Notifications">
        <IconButton
          color="inherit"
          onClick={() => {
            if (notifications.length > 0) {
              handleNotificationClick(notifications[0]);
            }
          }}
        >
          <Badge badgeContent={unreadCount} color="error">
            <NotificationsIcon />
          </Badge>
        </IconButton>
      </Tooltip>

      {notifications.map((notification) => (
        <Snackbar
          key={notification.id}
          open={activeNotification?.id === notification.id}
          autoHideDuration={6000}
          onClose={handleClose}
          anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
        >
          <Alert
            onClose={handleClose}
            severity={notification.type}
            sx={{ width: '100%' }}
            action={
              notification.action && (
                <IconButton
                  size="small"
                  color="inherit"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleAction(notification);
                  }}
                >
                  {notification.action.label}
                </IconButton>
              )
            }
          >
            {notification.title}
            <br />
            <small style={{ display: 'block' }}>
              {notification.message}
            </small>
          </Alert>
        </Snackbar>
      ))}
    </Box>
  );
};

export default NotificationManager;
