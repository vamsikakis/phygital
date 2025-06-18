import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

// Pages
import Home from './pages/Home';
import KnowledgeBase from './pages/KnowledgeBase';
import Communication from './pages/Communication';
import HelpDesk from './pages/HelpDesk';
import DocumentUpload from './pages/DocumentUpload';
import OpenAIAssistantPage from './pages/OpenAIAssistantPage';
import MigrationDashboard from './pages/MigrationDashboard';

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
            <Route path="/help-desk" element={<HelpDesk />} />
            <Route path="/document-upload" element={<DocumentUpload />} />
            <Route path="/openai-assistant" element={<OpenAIAssistantPage />} />
            <Route path="/migration" element={<MigrationDashboard />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App;
