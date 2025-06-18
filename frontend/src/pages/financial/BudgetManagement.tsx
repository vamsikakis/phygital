import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  FormControl,
  InputLabel,
  Select,
} from '@mui/material';
import { format } from 'date-fns';
import { useNavigate } from 'react-router-dom';
import { useBudgets } from '../../hooks/useFinancialData';

interface Budget {
  id: number;
  year: number;
  month: number;
  category: string;
  allocatedAmount: number;
  actualAmount: number;
  notes: string;
}

const BudgetManagement: React.FC = () => {
  const navigate = useNavigate();
  const { budgets, loading, error, addBudget, updateBudget } = useBudgets();
  const [open, setOpen] = useState(false);
  const [selectedBudget, setSelectedBudget] = useState<Budget | null>(null);
  const [formData, setFormData] = useState({
    year: format(new Date(), 'yyyy'),
    month: format(new Date(), 'MM'),
    category: '',
    allocatedAmount: 0,
    actualAmount: 0,
    notes: '',
  });

  const months = [
    '01',
    '02',
    '03',
    '04',
    '05',
    '06',
    '07',
    '08',
    '09',
    '10',
    '11',
    '12',
  ];

  const categories = [
    'maintenance',
    'utilities',
    'security',
    'cleaning',
    'administration',
    'other',
  ];

  const handleOpen = (budget?: Budget) => {
    if (budget) {
      setSelectedBudget(budget);
      setFormData({
        year: budget.year.toString(),
        month: budget.month.toString(),
        category: budget.category,
        allocatedAmount: budget.allocatedAmount,
        actualAmount: budget.actualAmount,
        notes: budget.notes,
      });
    } else {
      setSelectedBudget(null);
      setFormData({
        year: format(new Date(), 'yyyy'),
        month: format(new Date(), 'MM'),
        category: '',
        allocatedAmount: 0,
        actualAmount: 0,
        notes: '',
      });
    }
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
    setSelectedBudget(null);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSelectChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async () => {
    try {
      if (selectedBudget) {
        await updateBudget(selectedBudget.id, formData);
      } else {
        await addBudget(formData);
      }
      handleClose();
    } catch (error) {
      console.error('Error saving budget:', error);
    }
  };

  const getBudgetStatus = (budget: Budget) => {
    const percentage = (budget.actualAmount / budget.allocatedAmount) * 100;
    if (percentage < 80) return 'success';
    if (percentage < 100) return 'warning';
    return 'error';
  };

  if (loading) {
    return <Box sx={{ p: 3 }}>Loading...</Box>;
  }

  if (error) {
    return <Box sx={{ p: 3 }}>Error: {error.message}</Box>;
  }

  return (
    <Box sx={{ p: 3 }}>
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Paper sx={{ p: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h6">Budget Management</Typography>
            <Button
              variant="contained"
              color="primary"
              onClick={() => handleOpen()}
            >
              Add New Budget
            </Button>
          </Paper>
        </Grid>

        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Month</TableCell>
                    <TableCell>Category</TableCell>
                    <TableCell>Allocated Amount</TableCell>
                    <TableCell>Actual Amount</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {budgets.map((budget) => (
                    <TableRow key={budget.id}>
                      <TableCell>
                        {format(new Date(budget.year, budget.month - 1), 'MMM yyyy')}
                      </TableCell>
                      <TableCell>
                        {budget.category.charAt(0).toUpperCase() + budget.category.slice(1)}
                      </TableCell>
                      <TableCell>₹{budget.allocatedAmount.toLocaleString()}</TableCell>
                      <TableCell>₹{budget.actualAmount.toLocaleString()}</TableCell>
                      <TableCell>
                        <Box
                          sx={{
                            bgcolor: getBudgetStatus(budget),
                            color: 'white',
                            p: 1,
                            borderRadius: 1,
                            minWidth: 80,
                            textAlign: 'center',
                          }}
                        >
                          {getBudgetStatus(budget) === 'success' ? 'Under Budget' :
                          getBudgetStatus(budget) === 'warning' ? 'On Track' : 'Over Budget'}
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Button
                          variant="outlined"
                          size="small"
                          onClick={() => handleOpen(budget)}
                        >
                          Edit
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        </Grid>
      </Grid>

      <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
        <DialogTitle>
          {selectedBudget ? 'Edit Budget' : 'Add New Budget'}
        </DialogTitle>
        <DialogContent>
          <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1 }}>
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Year</InputLabel>
              <Select
                value={formData.year}
                onChange={handleSelectChange}
                name="year"
                label="Year"
              >
                {Array.from({ length: 5 }, (_, i) => {
                  const year = new Date().getFullYear() - i;
                  return (
                    <MenuItem key={year} value={year.toString()}>
                      {year}
                    </MenuItem>
                  );
                })}
              </Select>
            </FormControl>

            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Month</InputLabel>
              <Select
                value={formData.month}
                onChange={handleSelectChange}
                name="month"
                label="Month"
              >
                {months.map((month) => (
                  <MenuItem key={month} value={month}>
                    {format(new Date(2023, parseInt(month) - 1), 'MMMM')}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Category</InputLabel>
              <Select
                value={formData.category}
                onChange={handleSelectChange}
                name="category"
                label="Category"
                required
              >
                {categories.map((cat) => (
                  <MenuItem key={cat} value={cat}>
                    {cat.charAt(0).toUpperCase() + cat.slice(1)}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <TextField
              margin="normal"
              required
              fullWidth
              label="Allocated Amount"
              name="allocatedAmount"
              type="number"
              value={formData.allocatedAmount}
              onChange={handleInputChange}
              InputProps={{
                inputProps: { min: 0, step: 0.01 },
              }}
            />

            <TextField
              margin="normal"
              fullWidth
              label="Actual Amount"
              name="actualAmount"
              type="number"
              value={formData.actualAmount}
              onChange={handleInputChange}
              InputProps={{
                inputProps: { min: 0, step: 0.01 },
              }}
            />

            <TextField
              margin="normal"
              fullWidth
              label="Notes"
              name="notes"
              multiline
              rows={4}
              value={formData.notes}
              onChange={handleInputChange}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Cancel</Button>
          <Button type="submit" variant="contained" color="primary">
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default BudgetManagement;
