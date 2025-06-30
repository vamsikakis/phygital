import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Chip,
  Alert,
  Grid,
  Autocomplete
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Receipt as ReceiptIcon,
  TrendingUp as IncomeIcon,
  TrendingDown as ExpenseIcon
} from '@mui/icons-material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';

interface Transaction {
  id: string;
  date: string;
  description: string;
  amount: string;
  currency_code: string;
  source_name: string;
  destination_name: string;
  category_name?: string;
  type: string;
  notes?: string;
}

interface Account {
  id: string;
  name: string;
  type: string;
}

interface Category {
  id: string;
  name: string;
}

interface TransactionManagerProps {
  onTransactionsChange?: () => void;
}

const TransactionManager: React.FC<TransactionManagerProps> = ({ onTransactionsChange }) => {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingTransaction, setEditingTransaction] = useState<Transaction | null>(null);
  const [formData, setFormData] = useState({
    type: 'withdrawal',
    description: '',
    amount: '',
    date: new Date(),
    source_account_id: '',
    destination_account_id: '',
    category_name: '',
    notes: ''
  });

  const transactionTypes = [
    { value: 'withdrawal', label: 'Expense', icon: <ExpenseIcon />, color: '#f44336' },
    { value: 'deposit', label: 'Income', icon: <IncomeIcon />, color: '#4caf50' },
    { value: 'transfer', label: 'Transfer', icon: <ReceiptIcon />, color: '#2196f3' }
  ];

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      // Load transactions
      const transResponse = await fetch('/api/firefly/transactions?limit=100');
      const transData = await transResponse.json();
      if (transData.success) {
        setTransactions(transData.transactions);
      }

      // Load accounts
      const accountsResponse = await fetch('/api/firefly/accounts');
      const accountsData = await accountsResponse.json();
      if (accountsData.success) {
        setAccounts(accountsData.accounts);
      }

      // Load categories
      const categoriesResponse = await fetch('/api/firefly/categories');
      const categoriesData = await categoriesResponse.json();
      if (categoriesData.success) {
        setCategories(categoriesData.categories);
      }
    } catch (error) {
      setError('Error loading data');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTransaction = () => {
    setEditingTransaction(null);
    setFormData({
      type: 'withdrawal',
      description: '',
      amount: '',
      date: new Date(),
      source_account_id: '',
      destination_account_id: '',
      category_name: '',
      notes: ''
    });
    setDialogOpen(true);
  };

  const handleSaveTransaction = async () => {
    try {
      const transactionData = {
        type: formData.type,
        description: formData.description,
        amount: formData.amount,
        date: formData.date.toISOString().split('T')[0],
        source_id: formData.source_account_id,
        destination_id: formData.destination_account_id,
        category_name: formData.category_name,
        notes: formData.notes
      };

      const response = await fetch('/api/firefly/transactions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(transactionData),
      });

      const data = await response.json();
      
      if (data.success) {
        setDialogOpen(false);
        loadData();
        if (onTransactionsChange) onTransactionsChange();
        setError(null);
      } else {
        setError(data.error || 'Failed to save transaction');
      }
    } catch (error) {
      setError('Error saving transaction');
    }
  };

  const formatCurrency = (amount: string, currency: string = 'INR') => {
    const numAmount = parseFloat(amount);
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: currency,
    }).format(Math.abs(numAmount));
  };

  const getTransactionTypeInfo = (type: string) => {
    return transactionTypes.find(t => t.value === type) || transactionTypes[0];
  };

  const getAssetAccounts = () => accounts.filter(acc => acc.type === 'asset');
  const getExpenseAccounts = () => accounts.filter(acc => acc.type === 'expense');
  const getRevenueAccounts = () => accounts.filter(acc => acc.type === 'revenue');

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <Box>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <ReceiptIcon />
            Transaction Management
          </Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleCreateTransaction}
          >
            Add Transaction
          </Button>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Date</TableCell>
                <TableCell>Description</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Category</TableCell>
                <TableCell>From/To</TableCell>
                <TableCell align="right">Amount</TableCell>
                <TableCell align="center">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {transactions.map((transaction) => {
                const typeInfo = getTransactionTypeInfo(transaction.type);
                const isIncome = parseFloat(transaction.amount) > 0;
                
                return (
                  <TableRow key={transaction.id}>
                    <TableCell>
                      {new Date(transaction.date).toLocaleDateString()}
                    </TableCell>
                    <TableCell>
                      <Box>
                        <Typography variant="body2" fontWeight="medium">
                          {transaction.description}
                        </Typography>
                        {transaction.notes && (
                          <Typography variant="caption" color="text.secondary">
                            {transaction.notes}
                          </Typography>
                        )}
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip
                        icon={typeInfo.icon}
                        label={typeInfo.label}
                        size="small"
                        sx={{ color: typeInfo.color }}
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell>
                      {transaction.category_name && (
                        <Chip label={transaction.category_name} size="small" />
                      )}
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {isIncome ? transaction.source_name : transaction.destination_name}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Typography 
                        fontWeight="bold"
                        color={isIncome ? '#4caf50' : '#f44336'}
                      >
                        {isIncome ? '+' : '-'}{formatCurrency(transaction.amount, transaction.currency_code)}
                      </Typography>
                    </TableCell>
                    <TableCell align="center">
                      <IconButton size="small" color="primary">
                        <EditIcon />
                      </IconButton>
                      <IconButton size="small" color="error">
                        <DeleteIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </TableContainer>

        {/* Create Transaction Dialog */}
        <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="md" fullWidth>
          <DialogTitle>Add New Transaction</DialogTitle>
          <DialogContent>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel>Transaction Type</InputLabel>
                  <Select
                    value={formData.type}
                    label="Transaction Type"
                    onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                  >
                    {transactionTypes.map((type) => (
                      <MenuItem key={type.value} value={type.value}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          {type.icon}
                          {type.label}
                        </Box>
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} md={6}>
                <DatePicker
                  label="Transaction Date"
                  value={formData.date}
                  onChange={(newValue) => setFormData({ ...formData, date: newValue || new Date() })}
                  renderInput={(params) => <TextField {...params} fullWidth />}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Description"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  required
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Amount"
                  type="number"
                  value={formData.amount}
                  onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
                  required
                  InputProps={{
                    startAdornment: '₹'
                  }}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <Autocomplete
                  options={categories}
                  getOptionLabel={(option) => option.name}
                  value={categories.find(cat => cat.name === formData.category_name) || null}
                  onChange={(event, newValue) => {
                    setFormData({ ...formData, category_name: newValue?.name || '' });
                  }}
                  renderInput={(params) => (
                    <TextField {...params} label="Category" fullWidth />
                  )}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel>From Account</InputLabel>
                  <Select
                    value={formData.source_account_id}
                    label="From Account"
                    onChange={(e) => setFormData({ ...formData, source_account_id: e.target.value })}
                  >
                    {getAssetAccounts().map((account) => (
                      <MenuItem key={account.id} value={account.id}>
                        {account.name}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel>To Account</InputLabel>
                  <Select
                    value={formData.destination_account_id}
                    label="To Account"
                    onChange={(e) => setFormData({ ...formData, destination_account_id: e.target.value })}
                  >
                    {(formData.type === 'withdrawal' ? getExpenseAccounts() : 
                      formData.type === 'deposit' ? getRevenueAccounts() : 
                      getAssetAccounts()).map((account) => (
                      <MenuItem key={account.id} value={account.id}>
                        {account.name}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Notes"
                  multiline
                  rows={3}
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                />
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
            <Button onClick={handleSaveTransaction} variant="contained">
              Add Transaction
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </LocalizationProvider>
  );
};

export default TransactionManager;
