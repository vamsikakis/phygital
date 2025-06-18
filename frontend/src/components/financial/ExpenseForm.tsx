import React, { useState } from 'react';
import {
  Box,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Autocomplete,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useVendors } from '../../hooks/useVendors';
import { useAddExpense } from '../../hooks/useFinancialData';

interface ExpenseFormProps {
  open: boolean;
  onClose: () => void;
  expense?: {
    id: number;
    category: string;
    amount: number;
    description: string;
    vendorId: number;
    status: string;
  };
}

const ExpenseForm: React.FC<ExpenseFormProps> = ({ open, onClose, expense }) => {
  const navigate = useNavigate();
  const { vendors } = useVendors();
  const { addExpense, loading } = useAddExpense();

  const [formData, setFormData] = useState({
    category: expense?.category || '',
    amount: expense?.amount || 0,
    description: expense?.description || '',
    vendorId: expense?.vendorId || null,
    status: expense?.status || 'pending',
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleVendorChange = (vendor: any) => {
    setFormData((prev) => ({
      ...prev,
      vendorId: vendor?.id,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await addExpense(formData);
      onClose();
      navigate('/financial/dashboard');
    } catch (error) {
      console.error('Error adding expense:', error);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>{expense ? 'Edit Expense' : 'Add New Expense'}</DialogTitle>
      <DialogContent>
        <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1 }}>
          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel>Category</InputLabel>
            <Select
              value={formData.category}
              onChange={handleInputChange}
              name="category"
              label="Category"
              required
            >
              <MenuItem value="maintenance">Maintenance</MenuItem>
              <MenuItem value="utilities">Utilities</MenuItem>
              <MenuItem value="security">Security</MenuItem>
              <MenuItem value="cleaning">Cleaning</MenuItem>
              <MenuItem value="administration">Administration</MenuItem>
              <MenuItem value="other">Other</MenuItem>
            </Select>
          </FormControl>

          <TextField
            margin="normal"
            required
            fullWidth
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
            margin="normal"
            required
            fullWidth
            label="Description"
            name="description"
            value={formData.description}
            onChange={handleInputChange}
          />

          <Autocomplete
            options={vendors}
            getOptionLabel={(vendor) => vendor.name}
            value={vendors.find((v) => v.id === formData.vendorId) || null}
            onChange={(_, vendor) => handleVendorChange(vendor)}
            renderInput={(params) => (
              <TextField
                {...params}
                label="Vendor"
                margin="normal"
                fullWidth
              />
            )}
          />

          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel>Status</InputLabel>
            <Select
              value={formData.status}
              onChange={handleInputChange}
              name="status"
              label="Status"
            >
              <MenuItem value="pending">Pending</MenuItem>
              <MenuItem value="approved">Approved</MenuItem>
              <MenuItem value="rejected">Rejected</MenuItem>
              <MenuItem value="paid">Paid</MenuItem>
            </Select>
          </FormControl>
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button type="submit" variant="contained" disabled={loading}>
          {loading ? 'Saving...' : 'Save'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default ExpenseForm;
