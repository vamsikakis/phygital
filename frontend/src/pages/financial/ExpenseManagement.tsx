import React, { useState } from 'react';
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
  IconButton,
  Tooltip,
} from '@mui/material';
import { useFinancialData } from '../../hooks/useFinancialData';
import { useNavigate } from 'react-router-dom';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import AddIcon from '@mui/icons-material/Add';

interface Expense {
  id: number;
  category: string;
  amount: number;
  description: string;
  vendorId: number;
  status: string;
  date: string;
}

const ExpenseManagement: React.FC = () => {
  const navigate = useNavigate();
  const { expenses, loading, error, addExpense, updateExpense, deleteExpense } = useFinancialData();
  const [open, setOpen] = useState(false);
  const [selectedExpense, setSelectedExpense] = useState<Expense | null>(null);
  const [formData, setFormData] = useState({
    category: '',
    amount: 0,
    description: '',
    vendorId: null,
    status: 'pending',
  });

  const categories = [
    'maintenance',
    'utilities',
    'security',
    'cleaning',
    'administration',
    'other',
  ];

  const statuses = [
    'pending',
    'approved',
    'rejected',
    'paid',
  ];

  const handleOpen = (expense?: Expense) => {
    if (expense) {
      setSelectedExpense(expense);
      setFormData({
        category: expense.category,
        amount: expense.amount,
        description: expense.description,
        vendorId: expense.vendorId,
        status: expense.status,
      });
    } else {
      setSelectedExpense(null);
      setFormData({
        category: '',
        amount: 0,
        description: '',
        vendorId: null,
        status: 'pending',
      });
    }
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
    setSelectedExpense(null);
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
      if (selectedExpense) {
        await updateExpense(selectedExpense.id, formData);
      } else {
        await addExpense(formData);
      }
      handleClose();
    } catch (error) {
      console.error('Error saving expense:', error);
    }
  };

  const handleDelete = async (expenseId: number) => {
    try {
      await deleteExpense(expenseId);
    } catch (error) {
      console.error('Error deleting expense:', error);
    }
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
            <Typography variant="h6">Expense Management</Typography>
            <Button
              variant="contained"
              color="primary"
              onClick={() => handleOpen()}
              startIcon={<AddIcon />}
            >
              Add Expense
            </Button>
          </Paper>
        </Grid>

        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Category</TableCell>
                    <TableCell>Amount</TableCell>
                    <TableCell>Description</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Date</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {expenses.map((expense) => (
                    <TableRow key={expense.id}>
                      <TableCell>
                        {expense.category.charAt(0).toUpperCase() + expense.category.slice(1)}
                      </TableCell>
                      <TableCell>₹{expense.amount.toLocaleString()}</TableCell>
                      <TableCell>{expense.description}</TableCell>
                      <TableCell>
                        <Box
                          sx={{
                            bgcolor: expense.status === 'pending' ? 'warning.light' :
                                    expense.status === 'approved' ? 'success.light' :
                                    expense.status === 'rejected' ? 'error.light' :
                                    'primary.light',
                            color: expense.status === 'pending' ? 'warning.main' :
                                    expense.status === 'approved' ? 'success.main' :
                                    expense.status === 'rejected' ? 'error.main' :
                                    'primary.main',
                            p: 1,
                            borderRadius: 1,
                            minWidth: 80,
                            textAlign: 'center',
                          }}
                        >
                          {expense.status.charAt(0).toUpperCase() + expense.status.slice(1)}
                        </Box>
                      </TableCell>
                      <TableCell>
                        {new Date(expense.date).toLocaleDateString()}
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', gap: 1 }}>
                          <Tooltip title="Edit Expense">
                            <IconButton onClick={() => handleOpen(expense)}>
                              <EditIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Delete Expense">
                            <IconButton
                              onClick={() => handleDelete(expense.id)}
                              color="error"
                            >
                              <DeleteIcon />
                            </IconButton>
                          </Tooltip>
                        </Box>
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
          {selectedExpense ? 'Edit Expense' : 'Add New Expense'}
        </DialogTitle>
        <DialogContent>
          <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1 }}>
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
              fullWidth
              margin="normal"
              label="Amount"
              name="amount"
              type="number"
              value={formData.amount}
              onChange={handleInputChange}
              InputProps={{
                inputProps: { min: 0, step: 0.01 },
              }}
            />

            <TextField
              fullWidth
              margin="normal"
              label="Description"
              name="description"
              value={formData.description}
              onChange={handleInputChange}
            />

            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Status</InputLabel>
              <Select
                value={formData.status}
                onChange={handleSelectChange}
                name="status"
                label="Status"
                required
              >
                {statuses.map((status) => (
                  <MenuItem key={status} value={status}>
                    {status.charAt(0).toUpperCase() + status.slice(1)}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
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

export default ExpenseManagement;
