import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { ThemeProvider, CssBaseline, Box, AppBar, Toolbar, Typography, Button } from '@mui/material';
import theme from './theme/theme';
import ResponsiveLayout from './components/layout/ResponsiveLayout';
import HomePage from './pages/HomePage';
import DocumentsPage from './pages/DocumentsPage';
import HelpDeskPage from './pages/HelpDeskPage';
import FinancialDashboard from './pages/financial/FinancialDashboard';
import ExpenseManagement from './pages/financial/ExpenseManagement';
import BudgetManagement from './pages/financial/BudgetManagement';
import ExpenseAnalytics from './pages/financial/ExpenseAnalytics';
import FinancialReports from './pages/financial/FinancialReports';
import VendorManagement from './pages/financial/VendorManagement';
import SLATracking from './pages/financial/SLATracking';

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <ResponsiveLayout>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/documents" element={<DocumentsPage />} />
            <Route path="/helpdesk" element={<HelpDeskPage />} />
            <Route path="/financial/dashboard" element={<FinancialDashboard />} />
            <Route path="/financial/expenses" element={<ExpenseManagement />} />
            <Route path="/financial/budget" element={<BudgetManagement />} />
            <Route path="/financial/analytics" element={<ExpenseAnalytics />} />
            <Route path="/financial/reports" element={<FinancialReports />} />
            <Route path="/financial/vendors" element={<VendorManagement />} />
            <Route path="/financial/sla" element={<SLATracking />} />
          </Routes>
        </ResponsiveLayout>
      </Router>
    </ThemeProvider>
  );
};

export default App;
