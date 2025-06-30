import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

// Pages
import Home from './pages/Home';
import KnowledgeBase from './pages/KnowledgeBase';
import Communication from './pages/Communication';
import FinancialDashboard from './pages/FinancialDashboard';
import ClickUpTasksPage from './pages/ClickUpTasksPage';
import OpenAIAssistantPage from './pages/OpenAIAssistantPage';

// Components
import Layout from './components/Layout';

// Create a theme instance
const theme = createTheme({
  palette: {
    primary: {
      main: '#3f51b5',
    },
    secondary: {
      main: '#f50057',
    },
    background: {
      default: '#f5f5f5',
    },
  },
  typography: {
    fontFamily: [
      'Roboto',
      '"Helvetica Neue"',
      'Arial',
      'sans-serif',
    ].join(','),
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<Home />} />
            <Route path="knowledge-base" element={<KnowledgeBase />} />
            <Route path="communication" element={<Communication />} />
            <Route path="financial-dashboard" element={<FinancialDashboard />} />
            <Route path="clickup-tasks" element={<ClickUpTasksPage />} />
            <Route path="openai-assistant" element={<OpenAIAssistantPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App;
