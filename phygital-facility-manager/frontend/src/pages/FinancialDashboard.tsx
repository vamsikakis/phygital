import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  Alert,
  CircularProgress,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Tabs,
  Tab,
  LinearProgress,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  AccountBalance as AccountBalanceIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Receipt as ReceiptIcon,
  Category as CategoryIcon,
  Refresh as RefreshIcon,
  Add as AddIcon,
  Assessment as AssessmentIcon,
  Settings as SettingsIcon
} from '@mui/icons-material';

// Import financial management components
import AccountManager from '../components/financial/AccountManager';
import TransactionManager from '../components/financial/TransactionManager';
import BudgetManager from '../components/financial/BudgetManager';

// API Configuration
const API_BASE = import.meta.env.VITE_API_URL || 'https://phygital-backend.onrender.com';

interface FinancialSummary {
  total_assets: number;
  total_liabilities: number;
  net_worth: number;
  accounts_count: number;
  recent_transactions_count: number;
  recent_transactions: Transaction[];
}

interface Transaction {
  id: string;
  date: string;
  description: string;
  amount: string;
  currency_code: string;
  source_name: string;
  destination_name: string;
  category_name: string;
  type: string;
}

interface Account {
  id: string;
  name: string;
  type: string;
  current_balance: string;
  currency_code: string;
  active: boolean;
}

interface Budget {
  id: string;
  name: string;
  active: boolean;
  auto_budget_amount: string;
  auto_budget_period: string;
}

const FinancialDashboard: React.FC = () => {
  const [summary, setSummary] = useState<FinancialSummary | null>(null);
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [budgets, setBudgets] = useState<Budget[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [tabValue, setTabValue] = useState(0);
  const [fireflyConnected, setFireflyConnected] = useState<boolean | null>(null); // null = checking, false = failed, true = connected

  useEffect(() => {
    testFireflyConnection();
  }, []);

  useEffect(() => {
    if (fireflyConnected === true) {
      loadDashboardData();
    }
  }, [fireflyConnected]);

  const testFireflyConnection = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/firefly/test`);
      const data = await response.json();
      setFireflyConnected(data.success);

      if (!data.success) {
        setError(`Firefly III connection failed: ${data.error || 'Unknown error'}`);
      } else {
        setError(null); // Clear any previous errors
      }
    } catch (error) {
      setFireflyConnected(false);
      setError('Failed to connect to Firefly III service');
    }
  };

  const loadDashboardData = async () => {
    if (!fireflyConnected) return;
    
    setLoading(true);
    setError(null);

    try {
      // Load summary data
      const summaryResponse = await fetch(`${API_BASE}/api/firefly/summary`);
      const summaryData = await summaryResponse.json();

      if (summaryData.success) {
        setSummary(summaryData.summary);
      }

      // Load accounts
      const accountsResponse = await fetch(`${API_BASE}/api/firefly/accounts`);
      const accountsData = await accountsResponse.json();

      if (accountsData.success) {
        setAccounts(accountsData.accounts);
      }

      // Load budgets
      const budgetsResponse = await fetch(`${API_BASE}/api/firefly/budgets`);
      const budgetsData = await budgetsResponse.json();
      
      if (budgetsData.success) {
        setBudgets(budgetsData.budgets);
      }

    } catch (error) {
      setError('Failed to load financial data');
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number | string, currency: string = 'INR') => {
    const numAmount = typeof amount === 'string' ? parseFloat(amount) : amount;
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: 2
    }).format(numAmount);
  };

  const getTransactionColor = (amount: string) => {
    const numAmount = parseFloat(amount);
    return numAmount >= 0 ? '#4caf50' : '#f44336';
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  // Show loading while checking connection
  if (fireflyConnected === null) {
    return (
      <Box>
        <Typography variant="h5" component="h1" gutterBottom>
          Financial Dashboard
        </Typography>
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
          <CircularProgress />
          <Typography variant="body1" sx={{ ml: 2 }}>
            Checking Firefly III connection...
          </Typography>
        </Box>
      </Box>
    );
  }

  // Show setup instructions if connection failed
  if (fireflyConnected === false) {
    return (
      <Box>
        <Typography variant="h5" component="h1" gutterBottom>
          Financial Dashboard
        </Typography>
        
        <Alert severity="warning" sx={{ mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            🏦 Firefly III Financial Management Setup Required
          </Typography>
          <Typography variant="body2" paragraph>
            To use the Financial Dashboard, you need to set up Firefly III integration.
            Firefly III is a powerful open-source personal finance manager.
          </Typography>

          <Typography variant="body2" paragraph>
            <strong>📋 Quick Setup Instructions:</strong>
          </Typography>

          <Typography variant="body2" component="div" sx={{ mb: 2 }}>
            <strong>1. Install Firefly III with Docker:</strong><br/>
            <Box component="code" sx={{
              display: 'block',
              backgroundColor: '#f5f5f5',
              padding: 1,
              borderRadius: 1,
              fontSize: '0.875rem',
              mt: 1,
              overflowX: 'auto'
            }}>
              docker run -d --name firefly-iii -p 8080:8080 \<br/>
              &nbsp;&nbsp;-e APP_KEY=$(head /dev/urandom | LC_ALL=C tr -dc 'A-Za-z0-9' | head -c 32) \<br/>
              &nbsp;&nbsp;-e DB_CONNECTION=sqlite \<br/>
              &nbsp;&nbsp;-e APP_URL=https://firefly-iii-production.onrender.com \<br/>
              &nbsp;&nbsp;-v firefly_iii_upload:/var/www/html/storage/upload \<br/>
              &nbsp;&nbsp;fireflyiii/core:latest
            </Box>
          </Typography>

          <Typography variant="body2" component="div" sx={{ mb: 2 }}>
            <strong>2. Complete Initial Setup:</strong><br/>
            • Open <a href="https://firefly-iii-production.onrender.com" target="_blank" rel="noopener noreferrer">https://firefly-iii-production.onrender.com</a><br/>
            • Create your admin account<br/>
            • Complete the setup wizard
          </Typography>

          <Typography variant="body2" component="div" sx={{ mb: 2 }}>
            <strong>3. Create Personal Access Token:</strong><br/>
            • Login to Firefly III<br/>
            • Go to Profile → OAuth → Personal Access Tokens<br/>
            • Click "Create new token"<br/>
            • Name it "Facility Manager Integration"<br/>
            • Copy the very long token
          </Typography>

          <Typography variant="body2" component="div">
            <strong>4. Update Environment Configuration:</strong><br/>
            Add these to your <code>.env</code> file:<br/>
            <Box component="code" sx={{
              display: 'block',
              backgroundColor: '#f5f5f5',
              padding: 1,
              borderRadius: 1,
              fontSize: '0.875rem',
              mt: 1
            }}>
              FIREFLY_BASE_URL=https://firefly-iii-production.onrender.com<br/>
              FIREFLY_API_TOKEN=your_very_long_token_here
            </Box>
          </Typography>
        </Alert>

        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
          <Button
            variant="contained"
            startIcon={<RefreshIcon />}
            onClick={testFireflyConnection}
          >
            Test Connection
          </Button>

          <Button
            variant="outlined"
            href="https://firefly-iii-production.onrender.com"
            target="_blank"
            rel="noopener noreferrer"
          >
            Open Firefly III
          </Button>

          <Button
            variant="outlined"
            href="https://docs.firefly-iii.org/how-to/firefly-iii/installation/docker/"
            target="_blank"
            rel="noopener noreferrer"
          >
            Full Setup Guide
          </Button>

          <Button
            variant="text"
            href="/FIREFLY_SETUP.md"
            target="_blank"
            rel="noopener noreferrer"
          >
            Local Setup Guide
          </Button>
        </Box>
      </Box>
    );
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" component="h1">
          Financial Dashboard
        </Typography>
        <Box>
          <Tooltip title="Refresh Data">
            <IconButton onClick={loadDashboardData} disabled={loading}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            sx={{ ml: 1 }}
            href="https://firefly-iii-production.onrender.com"
            target="_blank"
            rel="noopener noreferrer"
          >
            Open Firefly III
          </Button>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {loading && <LinearProgress sx={{ mb: 3 }} />}

      {/* Financial Summary Cards */}
      {summary && (
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <TrendingUpIcon sx={{ color: '#4caf50', mr: 1 }} />
                  <Typography variant="h6" color="text.secondary">
                    Total Assets
                  </Typography>
                </Box>
                <Typography variant="h4" color="#4caf50">
                  {formatCurrency(summary.total_assets)}
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <TrendingDownIcon sx={{ color: '#f44336', mr: 1 }} />
                  <Typography variant="h6" color="text.secondary">
                    Total Liabilities
                  </Typography>
                </Box>
                <Typography variant="h4" color="#f44336">
                  {formatCurrency(summary.total_liabilities)}
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <AccountBalanceIcon sx={{ color: '#2196f3', mr: 1 }} />
                  <Typography variant="h6" color="text.secondary">
                    Net Worth
                  </Typography>
                </Box>
                <Typography variant="h4" color="#2196f3">
                  {formatCurrency(summary.net_worth)}
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <AssessmentIcon sx={{ color: '#ff9800', mr: 1 }} />
                  <Typography variant="h6" color="text.secondary">
                    Accounts
                  </Typography>
                </Box>
                <Typography variant="h4" color="#ff9800">
                  {summary.accounts_count}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Tabs for different views */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={tabValue} onChange={handleTabChange}>
          <Tab label="Dashboard" />
          <Tab label="Transactions" />
          <Tab label="Accounts" />
          <Tab label="Budgets" />
          <Tab label="Manage" />
        </Tabs>
      </Box>

      {/* Tab Panels */}
      {tabValue === 0 && summary && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Recent Transactions
            </Typography>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Date</TableCell>
                    <TableCell>Description</TableCell>
                    <TableCell>Category</TableCell>
                    <TableCell>From/To</TableCell>
                    <TableCell align="right">Amount</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {summary.recent_transactions.map((transaction) => (
                    <TableRow key={transaction.id}>
                      <TableCell>{new Date(transaction.date).toLocaleDateString()}</TableCell>
                      <TableCell>{transaction.description}</TableCell>
                      <TableCell>
                        {transaction.category_name && (
                          <Chip label={transaction.category_name} size="small" />
                        )}
                      </TableCell>
                      <TableCell>
                        {parseFloat(transaction.amount) >= 0 
                          ? transaction.source_name 
                          : transaction.destination_name}
                      </TableCell>
                      <TableCell align="right">
                        <Typography 
                          color={getTransactionColor(transaction.amount)}
                          fontWeight="bold"
                        >
                          {formatCurrency(parseFloat(transaction.amount), transaction.currency_code)}
                        </Typography>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      )}

      {tabValue === 1 && (
        <TransactionManager onTransactionsChange={loadDashboardData} />
      )}

      {tabValue === 2 && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Accounts Overview
            </Typography>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Account Name</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell align="right">Balance</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {accounts.map((account) => (
                    <TableRow key={account.id}>
                      <TableCell>{account.name}</TableCell>
                      <TableCell>
                        <Chip label={account.type} size="small" variant="outlined" />
                      </TableCell>
                      <TableCell>
                        <Chip 
                          label={account.active ? 'Active' : 'Inactive'} 
                          size="small"
                          color={account.active ? 'success' : 'default'}
                        />
                      </TableCell>
                      <TableCell align="right">
                        <Typography fontWeight="bold">
                          {formatCurrency(parseFloat(account.current_balance || '0'), account.currency_code)}
                        </Typography>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      )}

      {tabValue === 3 && (
        <BudgetManager onBudgetsChange={loadDashboardData} />
      )}

      {tabValue === 4 && (
        <Box>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <AccountManager onAccountsChange={loadDashboardData} />
            </Grid>
          </Grid>
        </Box>
      )}
    </Box>
  );
};

export default FinancialDashboard;
