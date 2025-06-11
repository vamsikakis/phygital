import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
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
  CircularProgress,
  Alert,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

interface PaymentMethod {
  id: number;
  name: string;
  type: string;
  icon: React.ReactNode;
}

const paymentMethods: PaymentMethod[] = [
  {
    id: 1,
    name: 'Credit Card',
    type: 'card',
    icon: <img src="/icons/credit-card.svg" alt="Credit Card" style={{ width: 24, height: 24 }} />,
  },
  {
    id: 2,
    name: 'UPI',
    type: 'upi',
    icon: <img src="/icons/upi.svg" alt="UPI" style={{ width: 24, height: 24 }} />,
  },
  {
    id: 3,
    name: 'Net Banking',
    type: 'netbanking',
    icon: <img src="/icons/netbanking.svg" alt="Net Banking" style={{ width: 24, height: 24 }} />,
  },
];

interface PaymentDetails {
  amount: number;
  method: string;
  referenceId: string;
  description: string;
}

const PaymentGateway: React.FC = () => {
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState<PaymentDetails>({
    amount: 0,
    method: '',
    referenceId: '',
    description: '',
  });

  const handleOpen = () => {
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
    setError(null);
    setFormData({
      amount: 0,
      method: '',
      referenceId: '',
      description: '',
    });
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
      setLoading(true);
      setError(null);

      const response = await axios.post('/api/payments/initiate', {
        ...formData,
        amount: Number(formData.amount),
      });

      // Handle payment gateway redirection
      window.location.href = response.data.redirectUrl;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Payment processing failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Paper sx={{ p: 2 }}>
        <Typography variant="h6" gutterBottom>
          Payment Gateway Integration
        </Typography>
        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
          {paymentMethods.map((method) => (
            <Button
              key={method.id}
              variant="outlined"
              startIcon={method.icon}
              onClick={handleOpen}
              sx={{ flex: 1, minWidth: 200 }}
            >
              {method.name}
            </Button>
          ))}
        </Box>
      </Paper>

      <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
        <DialogTitle>Payment Details</DialogTitle>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
        <DialogContent>
          <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1 }}>
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

            <FormControl fullWidth margin="normal">
              <InputLabel>Payment Method</InputLabel>
              <Select
                value={formData.method}
                onChange={handleSelectChange}
                name="method"
                label="Payment Method"
                required
              >
                {paymentMethods.map((method) => (
                  <MenuItem key={method.id} value={method.type}>
                    {method.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <TextField
              fullWidth
              margin="normal"
              label="Reference ID"
              name="referenceId"
              value={formData.referenceId}
              onChange={handleInputChange}
            />

            <TextField
              fullWidth
              margin="normal"
              label="Description"
              name="description"
              multiline
              rows={2}
              value={formData.description}
              onChange={handleInputChange}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Cancel</Button>
          <Button
            type="submit"
            variant="contained"
            color="primary"
            onClick={handleSubmit}
            disabled={loading}
          >
            {loading ? <CircularProgress size={24} /> : 'Pay Now'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default PaymentGateway;
