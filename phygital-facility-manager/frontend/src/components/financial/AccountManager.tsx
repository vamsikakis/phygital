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
  Switch,
  FormControlLabel
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  AccountBalance as AccountIcon
} from '@mui/icons-material';

interface Account {
  id: string;
  name: string;
  type: string;
  account_role?: string;
  currency_code: string;
  current_balance: string;
  active: boolean;
  account_number?: string;
  notes?: string;
}

interface AccountManagerProps {
  onAccountsChange?: () => void;
}

const AccountManager: React.FC<AccountManagerProps> = ({ onAccountsChange }) => {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingAccount, setEditingAccount] = useState<Account | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    type: 'asset',
    account_role: 'defaultAsset',
    currency_code: 'INR',
    opening_balance: '0',
    account_number: '',
    notes: '',
    active: true
  });

  const accountTypes = [
    { value: 'asset', label: 'Asset Account' },
    { value: 'expense', label: 'Expense Account' },
    { value: 'revenue', label: 'Revenue Account' },
    { value: 'liability', label: 'Liability Account' }
  ];

  const accountRoles = {
    asset: [
      { value: 'defaultAsset', label: 'Default Asset' },
      { value: 'sharedAsset', label: 'Shared Asset' },
      { value: 'savingAsset', label: 'Savings Account' },
      { value: 'ccAsset', label: 'Credit Card' }
    ],
    expense: [
      { value: null, label: 'Default Expense' }
    ],
    revenue: [
      { value: null, label: 'Default Revenue' }
    ],
    liability: [
      { value: 'defaultLiability', label: 'Default Liability' }
    ]
  };

  useEffect(() => {
    loadAccounts();
  }, []);

  const loadAccounts = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/firefly/accounts');
      const data = await response.json();
      if (data.success) {
        setAccounts(data.accounts);
      } else {
        setError('Failed to load accounts');
      }
    } catch (error) {
      setError('Error loading accounts');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateAccount = () => {
    setEditingAccount(null);
    setFormData({
      name: '',
      type: 'asset',
      account_role: 'defaultAsset',
      currency_code: 'INR',
      opening_balance: '0',
      account_number: '',
      notes: '',
      active: true
    });
    setDialogOpen(true);
  };

  const handleEditAccount = (account: Account) => {
    setEditingAccount(account);
    setFormData({
      name: account.name,
      type: account.type,
      account_role: account.account_role || 'defaultAsset',
      currency_code: account.currency_code,
      opening_balance: account.current_balance,
      account_number: account.account_number || '',
      notes: account.notes || '',
      active: account.active
    });
    setDialogOpen(true);
  };

  const handleSaveAccount = async () => {
    try {
      const url = editingAccount 
        ? `/api/firefly/accounts/${editingAccount.id}`
        : '/api/firefly/accounts';
      
      const method = editingAccount ? 'PUT' : 'POST';
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      const data = await response.json();
      
      if (data.success) {
        setDialogOpen(false);
        loadAccounts();
        if (onAccountsChange) onAccountsChange();
        setError(null);
      } else {
        setError(data.error || 'Failed to save account');
      }
    } catch (error) {
      setError('Error saving account');
    }
  };

  const handleDeleteAccount = async (accountId: string) => {
    if (!confirm('Are you sure you want to delete this account?')) return;

    try {
      const response = await fetch(`/api/firefly/accounts/${accountId}`, {
        method: 'DELETE',
      });

      const data = await response.json();
      
      if (data.success) {
        loadAccounts();
        if (onAccountsChange) onAccountsChange();
        setError(null);
      } else {
        setError(data.error || 'Failed to delete account');
      }
    } catch (error) {
      setError('Error deleting account');
    }
  };

  const formatCurrency = (amount: string, currency: string = 'INR') => {
    const numAmount = parseFloat(amount);
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: currency,
    }).format(numAmount);
  };

  const getAccountTypeColor = (type: string) => {
    switch (type) {
      case 'asset': return 'success';
      case 'expense': return 'error';
      case 'revenue': return 'primary';
      case 'liability': return 'warning';
      default: return 'default';
    }
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <AccountIcon />
          Account Management
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleCreateAccount}
        >
          Create Account
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
              <TableCell>Account Name</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Account Number</TableCell>
              <TableCell>Status</TableCell>
              <TableCell align="right">Balance</TableCell>
              <TableCell align="center">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {accounts.map((account) => (
              <TableRow key={account.id}>
                <TableCell>
                  <Box>
                    <Typography variant="body1" fontWeight="medium">
                      {account.name}
                    </Typography>
                    {account.notes && (
                      <Typography variant="caption" color="text.secondary">
                        {account.notes}
                      </Typography>
                    )}
                  </Box>
                </TableCell>
                <TableCell>
                  <Chip 
                    label={account.type} 
                    size="small" 
                    color={getAccountTypeColor(account.type) as any}
                    variant="outlined"
                  />
                </TableCell>
                <TableCell>{account.account_number || '-'}</TableCell>
                <TableCell>
                  <Chip 
                    label={account.active ? 'Active' : 'Inactive'} 
                    size="small"
                    color={account.active ? 'success' : 'default'}
                  />
                </TableCell>
                <TableCell align="right">
                  <Typography fontWeight="bold">
                    {formatCurrency(account.current_balance, account.currency_code)}
                  </Typography>
                </TableCell>
                <TableCell align="center">
                  <IconButton
                    size="small"
                    onClick={() => handleEditAccount(account)}
                    color="primary"
                  >
                    <EditIcon />
                  </IconButton>
                  <IconButton
                    size="small"
                    onClick={() => handleDeleteAccount(account.id)}
                    color="error"
                  >
                    <DeleteIcon />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Create/Edit Account Dialog */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingAccount ? 'Edit Account' : 'Create New Account'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Account Name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Account Type</InputLabel>
                <Select
                  value={formData.type}
                  label="Account Type"
                  onChange={(e) => setFormData({ 
                    ...formData, 
                    type: e.target.value,
                    account_role: accountRoles[e.target.value as keyof typeof accountRoles][0]?.value || null
                  })}
                >
                  {accountTypes.map((type) => (
                    <MenuItem key={type.value} value={type.value}>
                      {type.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Account Number"
                value={formData.account_number}
                onChange={(e) => setFormData({ ...formData, account_number: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Opening Balance"
                type="number"
                value={formData.opening_balance}
                onChange={(e) => setFormData({ ...formData, opening_balance: e.target.value })}
              />
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
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={formData.active}
                    onChange={(e) => setFormData({ ...formData, active: e.target.checked })}
                  />
                }
                label="Active Account"
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleSaveAccount} variant="contained">
            {editingAccount ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AccountManager;
