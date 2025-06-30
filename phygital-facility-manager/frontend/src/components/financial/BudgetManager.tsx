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
  FormControlLabel,
  LinearProgress,
  Card,
  CardContent
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  AccountBalance as BudgetIcon,
  TrendingUp as IncomeIcon,
  TrendingDown as ExpenseIcon,
  Assessment as ReportIcon
} from '@mui/icons-material';

interface Budget {
  id: string;
  name: string;
  active: boolean;
  auto_budget_type?: string;
  auto_budget_amount?: string;
  auto_budget_period?: string;
  notes?: string;
  spent?: number;
  available?: number;
  percentage_used?: number;
}

interface BudgetManagerProps {
  onBudgetsChange?: () => void;
}

const BudgetManager: React.FC<BudgetManagerProps> = ({ onBudgetsChange }) => {
  const [budgets, setBudgets] = useState<Budget[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingBudget, setEditingBudget] = useState<Budget | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    auto_budget_amount: '',
    auto_budget_period: 'monthly',
    auto_budget_type: 'reset',
    notes: '',
    active: true
  });

  const budgetPeriods = [
    { value: 'daily', label: 'Daily' },
    { value: 'weekly', label: 'Weekly' },
    { value: 'monthly', label: 'Monthly' },
    { value: 'quarterly', label: 'Quarterly' },
    { value: 'half-year', label: 'Half-yearly' },
    { value: 'yearly', label: 'Yearly' }
  ];

  const budgetTypes = [
    { value: 'reset', label: 'Reset (starts fresh each period)' },
    { value: 'rollover', label: 'Rollover (unused amount carries over)' }
  ];

  useEffect(() => {
    loadBudgets();
  }, []);

  const loadBudgets = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/firefly/budgets');
      const data = await response.json();
      if (data.success) {
        // Calculate spending data for each budget
        const budgetsWithSpending = await Promise.all(
          data.budgets.map(async (budget: Budget) => {
            try {
              // Get spending data for this budget (you might need to implement this endpoint)
              const spentAmount = 0; // Placeholder - implement actual spending calculation
              const budgetAmount = parseFloat(budget.auto_budget_amount || '0');
              const available = budgetAmount - spentAmount;
              const percentageUsed = budgetAmount > 0 ? (spentAmount / budgetAmount) * 100 : 0;

              return {
                ...budget,
                spent: spentAmount,
                available: available,
                percentage_used: percentageUsed
              };
            } catch (error) {
              return budget;
            }
          })
        );
        setBudgets(budgetsWithSpending);
      } else {
        setError('Failed to load budgets');
      }
    } catch (error) {
      setError('Error loading budgets');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateBudget = () => {
    setEditingBudget(null);
    setFormData({
      name: '',
      auto_budget_amount: '',
      auto_budget_period: 'monthly',
      auto_budget_type: 'reset',
      notes: '',
      active: true
    });
    setDialogOpen(true);
  };

  const handleEditBudget = (budget: Budget) => {
    setEditingBudget(budget);
    setFormData({
      name: budget.name,
      auto_budget_amount: budget.auto_budget_amount || '',
      auto_budget_period: budget.auto_budget_period || 'monthly',
      auto_budget_type: budget.auto_budget_type || 'reset',
      notes: budget.notes || '',
      active: budget.active
    });
    setDialogOpen(true);
  };

  const handleSaveBudget = async () => {
    try {
      const url = editingBudget 
        ? `/api/firefly/budgets/${editingBudget.id}`
        : '/api/firefly/budgets';
      
      const method = editingBudget ? 'PUT' : 'POST';
      
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
        loadBudgets();
        if (onBudgetsChange) onBudgetsChange();
        setError(null);
      } else {
        setError(data.error || 'Failed to save budget');
      }
    } catch (error) {
      setError('Error saving budget');
    }
  };

  const handleDeleteBudget = async (budgetId: string) => {
    if (!confirm('Are you sure you want to delete this budget?')) return;

    try {
      const response = await fetch(`/api/firefly/budgets/${budgetId}`, {
        method: 'DELETE',
      });

      const data = await response.json();
      
      if (data.success) {
        loadBudgets();
        if (onBudgetsChange) onBudgetsChange();
        setError(null);
      } else {
        setError(data.error || 'Failed to delete budget');
      }
    } catch (error) {
      setError('Error deleting budget');
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
    }).format(amount);
  };

  const getBudgetStatusColor = (percentageUsed: number) => {
    if (percentageUsed <= 50) return 'success';
    if (percentageUsed <= 80) return 'warning';
    return 'error';
  };

  const getBudgetStatusText = (percentageUsed: number) => {
    if (percentageUsed <= 50) return 'On Track';
    if (percentageUsed <= 80) return 'Watch';
    if (percentageUsed <= 100) return 'Near Limit';
    return 'Over Budget';
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <BudgetIcon />
          Budget Management
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleCreateBudget}
        >
          Create Budget
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Budget Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        {budgets.map((budget) => (
          <Grid item xs={12} md={6} lg={4} key={budget.id}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                  <Typography variant="h6" component="div">
                    {budget.name}
                  </Typography>
                  <Chip 
                    label={budget.active ? 'Active' : 'Inactive'} 
                    size="small"
                    color={budget.active ? 'success' : 'default'}
                  />
                </Box>
                
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Budget Amount: {formatCurrency(parseFloat(budget.auto_budget_amount || '0'))}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Period: {budget.auto_budget_period}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Type: {budget.auto_budget_type}
                  </Typography>
                </Box>

                <Box sx={{ mb: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">
                      Spent: {formatCurrency(budget.spent || 0)}
                    </Typography>
                    <Typography variant="body2">
                      {(budget.percentage_used || 0).toFixed(1)}%
                    </Typography>
                  </Box>
                  <LinearProgress 
                    variant="determinate" 
                    value={Math.min(budget.percentage_used || 0, 100)}
                    color={getBudgetStatusColor(budget.percentage_used || 0)}
                    sx={{ height: 8, borderRadius: 4 }}
                  />
                  <Typography variant="caption" color="text.secondary">
                    Available: {formatCurrency(budget.available || 0)}
                  </Typography>
                </Box>

                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Chip 
                    label={getBudgetStatusText(budget.percentage_used || 0)}
                    size="small"
                    color={getBudgetStatusColor(budget.percentage_used || 0)}
                  />
                  <Box>
                    <IconButton
                      size="small"
                      onClick={() => handleEditBudget(budget)}
                      color="primary"
                    >
                      <EditIcon />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={() => handleDeleteBudget(budget.id)}
                      color="error"
                    >
                      <DeleteIcon />
                    </IconButton>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Budget Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Budget Name</TableCell>
              <TableCell>Amount</TableCell>
              <TableCell>Period</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Status</TableCell>
              <TableCell align="right">Spent</TableCell>
              <TableCell align="right">Available</TableCell>
              <TableCell align="center">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {budgets.map((budget) => (
              <TableRow key={budget.id}>
                <TableCell>
                  <Box>
                    <Typography variant="body1" fontWeight="medium">
                      {budget.name}
                    </Typography>
                    {budget.notes && (
                      <Typography variant="caption" color="text.secondary">
                        {budget.notes}
                      </Typography>
                    )}
                  </Box>
                </TableCell>
                <TableCell>
                  <Typography fontWeight="bold">
                    {formatCurrency(parseFloat(budget.auto_budget_amount || '0'))}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Chip label={budget.auto_budget_period} size="small" variant="outlined" />
                </TableCell>
                <TableCell>
                  <Chip label={budget.auto_budget_type} size="small" variant="outlined" />
                </TableCell>
                <TableCell>
                  <Chip 
                    label={getBudgetStatusText(budget.percentage_used || 0)}
                    size="small"
                    color={getBudgetStatusColor(budget.percentage_used || 0)}
                  />
                </TableCell>
                <TableCell align="right">
                  <Typography color="error">
                    {formatCurrency(budget.spent || 0)}
                  </Typography>
                </TableCell>
                <TableCell align="right">
                  <Typography color="success.main">
                    {formatCurrency(budget.available || 0)}
                  </Typography>
                </TableCell>
                <TableCell align="center">
                  <IconButton
                    size="small"
                    onClick={() => handleEditBudget(budget)}
                    color="primary"
                  >
                    <EditIcon />
                  </IconButton>
                  <IconButton
                    size="small"
                    onClick={() => handleDeleteBudget(budget.id)}
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

      {/* Create/Edit Budget Dialog */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingBudget ? 'Edit Budget' : 'Create New Budget'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Budget Name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
                placeholder="e.g., Monthly Utilities, Security Services"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Budget Amount"
                type="number"
                value={formData.auto_budget_amount}
                onChange={(e) => setFormData({ ...formData, auto_budget_amount: e.target.value })}
                required
                InputProps={{
                  startAdornment: '₹'
                }}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Budget Period</InputLabel>
                <Select
                  value={formData.auto_budget_period}
                  label="Budget Period"
                  onChange={(e) => setFormData({ ...formData, auto_budget_period: e.target.value })}
                >
                  {budgetPeriods.map((period) => (
                    <MenuItem key={period.value} value={period.value}>
                      {period.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Budget Type</InputLabel>
                <Select
                  value={formData.auto_budget_type}
                  label="Budget Type"
                  onChange={(e) => setFormData({ ...formData, auto_budget_type: e.target.value })}
                >
                  {budgetTypes.map((type) => (
                    <MenuItem key={type.value} value={type.value}>
                      {type.label}
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
                placeholder="Budget description, purpose, or additional details"
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
                label="Active Budget"
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleSaveBudget} variant="contained">
            {editingBudget ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default BudgetManager;
