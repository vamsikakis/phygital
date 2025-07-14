import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

// Context
import { AuthProvider } from './contexts/AuthContext';

// Pages
import Login from './pages/Login';
import Signup from './pages/Signup';
import ForgotPassword from './pages/ForgotPassword';
import SetupPassword from './pages/SetupPassword';
import ResetPassword from './pages/ResetPassword';
import Home from './pages/Home';
import AdminDashboard from './pages/AdminDashboard';
import KnowledgeBase from './pages/KnowledgeBase';
import Communication from './pages/Communication';
import FinancialDashboard from './pages/FinancialDashboard';
import ClickUpTasksPage from './pages/ClickUpTasksPage';
import OpenAIAssistantPage from './pages/OpenAIAssistantPage';

// Components
import MainLayout from './components/MainLayout';
import ProtectedRoute from './components/ProtectedRoute';

// Create Gopalan Atlantis theme instance
const theme = createTheme({
  palette: {
    primary: {
      main: '#5B5CE6', // Gopalan Atlantis Purple
      light: '#8B8CF0',
      dark: '#4A4BC4',
      contrastText: '#FFFFFF',
    },
    secondary: {
      main: '#7C7CE8', // Lighter purple for secondary actions
      light: '#A5A5F0',
      dark: '#5A5AC4',
      contrastText: '#FFFFFF',
    },
    background: {
      default: '#F5F5F7', // Light gray background
      paper: '#FFFFFF',
    },
    text: {
      primary: '#1D1D1F', // Dark navy for primary text
      secondary: '#6E6E73', // Gray for secondary text
    },
    grey: {
      50: '#FAFAFA',
      100: '#F5F5F7',
      200: '#E5E5EA',
      300: '#D1D1D6',
      400: '#C7C7CC',
      500: '#AEAEB2',
      600: '#8E8E93',
      700: '#6E6E73',
      800: '#48484A',
      900: '#1D1D1F',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontWeight: 700,
      fontSize: '2.5rem',
      color: '#1D1D1F',
    },
    h2: {
      fontWeight: 600,
      fontSize: '2rem',
      color: '#1D1D1F',
    },
    h3: {
      fontWeight: 600,
      fontSize: '1.5rem',
      color: '#1D1D1F',
    },
    h4: {
      fontWeight: 600,
      fontSize: '1.25rem',
      color: '#1D1D1F',
    },
    h5: {
      fontWeight: 600,
      fontSize: '1.125rem',
      color: '#1D1D1F',
    },
    h6: {
      fontWeight: 600,
      fontSize: '1rem',
      color: '#1D1D1F',
    },
    body1: {
      fontSize: '1rem',
      color: '#1D1D1F',
    },
    body2: {
      fontSize: '0.875rem',
      color: '#6E6E73',
    },
  },
  shape: {
    borderRadius: 12, // More rounded corners like in wireframes
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          textTransform: 'none',
          fontWeight: 600,
          padding: '12px 24px',
          boxShadow: 'none',
          '&:hover': {
            boxShadow: '0 4px 12px rgba(91, 92, 230, 0.3)',
          },
        },
        contained: {
          background: 'linear-gradient(135deg, #5B5CE6 0%, #7C7CE8 100%)',
          '&:hover': {
            background: 'linear-gradient(135deg, #4A4BC4 0%, #6B6BD6 100%)',
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 16,
          boxShadow: '0 2px 12px rgba(0, 0, 0, 0.08)',
          border: '1px solid #E5E5EA',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 16,
          boxShadow: '0 2px 12px rgba(0, 0, 0, 0.08)',
        },
      },
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AuthProvider>
        <Router>
          <Routes>
            {/* Public Routes */}
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />
            <Route path="/forgot-password" element={<ForgotPassword />} />
            <Route path="/setup-password" element={<SetupPassword />} />
            <Route path="/reset-password" element={<ResetPassword />} />

            {/* Protected Routes */}
            <Route path="/" element={
              <ProtectedRoute fallbackPath="/signup">
                <MainLayout />
              </ProtectedRoute>
            }>
              <Route index element={<Home />} />
              <Route path="admin-dashboard" element={
                <ProtectedRoute requiredRoles={['admin', 'management']}>
                  <AdminDashboard />
                </ProtectedRoute>
              } />
              <Route path="knowledge-base" element={<KnowledgeBase />} />
              <Route path="communication" element={
                <ProtectedRoute requiredRoles={['admin', 'management', 'fm']}>
                  <Communication />
                </ProtectedRoute>
              } />
              <Route path="financial-dashboard" element={
                <ProtectedRoute requiredRoles={['admin', 'management', 'fm']}>
                  <FinancialDashboard />
                </ProtectedRoute>
              } />
              <Route path="clickup-tasks" element={
                <ProtectedRoute requiredRoles={['admin', 'management', 'fm']}>
                  <ClickUpTasksPage />
                </ProtectedRoute>
              } />
              <Route path="openai-assistant" element={<OpenAIAssistantPage />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Route>
          </Routes>
        </Router>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
