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
  Chip,
  CircularProgress,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as ChartTooltip,
  ResponsiveContainer,
} from 'recharts';
import { useSLA } from '../../hooks/useSLA';
import { useVendors } from '../../hooks/useFinancialData';
import { format } from 'date-fns';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import VisibilityIcon from '@mui/icons-material/Visibility';

const SLATracking: React.FC = () => {
  const { slas, loading, error, addSLA, updateSLA, deleteSLA, getSLACompliance, getSLAStatus } = useSLA();
  const { vendors } = useVendors();
  const [open, setOpen] = useState(false);
  const [selectedSLA, setSelectedSLA] = useState<any | null>(null);
  const [formData, setFormData] = useState({
    vendorId: '',
    serviceType: '',
    responseTime: 0,
    resolutionTime: 0,
    status: 'active',
    startDate: format(new Date(), 'yyyy-MM-dd'),
    endDate: format(new Date(), 'yyyy-MM-dd'),
    metrics: [] as any[],
  });

  const serviceTypes = [
    'maintenance',
    'security',
    'cleaning',
    'facility',
    'emergency',
  ];

  const statusTypes = [
    'active',
    'expired',
    'suspended',
    'terminated',
  ];

  const metricTypes = [
    'response_time',
    'resolution_time',
    'first_contact_resolution',
    'customer_satisfaction',
  ];

  const handleOpen = (sla?: any) => {
    if (sla) {
      setSelectedSLA(sla);
      setFormData({
        vendorId: sla.vendorId,
        serviceType: sla.serviceType,
        responseTime: sla.responseTime,
        resolutionTime: sla.resolutionTime,
        status: sla.status,
        startDate: sla.startDate,
        endDate: sla.endDate,
        metrics: sla.metrics || [],
      });
    } else {
      setSelectedSLA(null);
      setFormData({
        vendorId: '',
        serviceType: '',
        responseTime: 0,
        resolutionTime: 0,
        status: 'active',
        startDate: format(new Date(), 'yyyy-MM-dd'),
        endDate: format(new Date(), 'yyyy-MM-dd'),
        metrics: [],
      });
    }
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
    setSelectedSLA(null);
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

  const handleAddMetric = () => {
    setFormData((prev) => ({
      ...prev,
      metrics: [...prev.metrics, { type: '', target: 0, actual: 0 }],
    }));
  };

  const handleRemoveMetric = (index: number) => {
    setFormData((prev) => ({
      ...prev,
      metrics: prev.metrics.filter((_, i) => i !== index),
    }));
  };

  const handleSubmit = async () => {
    try {
      if (selectedSLA) {
        await updateSLA(selectedSLA.id, formData);
      } else {
        await addSLA(formData);
      }
      handleClose();
    } catch (error) {
      console.error('Error saving SLA:', error);
    }
  };

  const handleDelete = async (slaId: number) => {
    try {
      await deleteSLA(slaId);
    } catch (error) {
      console.error('Error deleting SLA:', error);
    }
  };

  if (loading) {
    return <Box sx={{ p: 3, display: 'flex', justifyContent: 'center', alignItems: 'center', height: '200px' }}>
      <CircularProgress />
    </Box>;
  }

  if (error) {
    return <Box sx={{ p: 3 }}>Error: {error.message}</Box>;
  }

  return (
    <Box sx={{ p: 3 }}>
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Paper sx={{ p: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h6">SLA Tracking</Typography>
            <Button
              variant="contained"
              color="primary"
              onClick={() => handleOpen()}
            >
              Add New SLA
            </Button>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, height: 400 }}>
            <Typography variant="h6" gutterBottom>
              SLA Compliance Overview
            </Typography>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={slas.map((sla) => ({
                date: format(new Date(sla.startDate), 'MMM yyyy'),
                compliance: getSLACompliance(sla),
              }))}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis domain={[0, 100]} />
                <Tooltip />
                <Line
                  type="monotone"
                  dataKey="compliance"
                  stroke="#8884d8"
                  name="Compliance Rate (%)"
                />
              </LineChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              SLA Status Summary
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {statusTypes.map((status) => {
                const count = slas.filter((sla) => sla.status === status).length;
                return (
                  <Chip
                    key={status}
                    label={`${status.charAt(0).toUpperCase() + status.slice(1)}: ${count}`}
                    variant="outlined"
                    color={status === 'active' ? 'success' :
                          status === 'expired' ? 'error' :
                          status === 'suspended' ? 'warning' : 'default'}
                  />
                );
              })}
            </Box>
          </Paper>
        </Grid>

        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Vendor</TableCell>
                    <TableCell>Service Type</TableCell>
                    <TableCell>Compliance Rate</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Metrics</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {slas.map((sla) => {
                    const vendor = vendors.find((v) => v.id === sla.vendorId);
                    return (
                      <TableRow key={sla.id}>
                        <TableCell>{vendor?.name || 'N/A'}</TableCell>
                        <TableCell>
                          {sla.serviceType.charAt(0).toUpperCase() + sla.serviceType.slice(1)}
                        </TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Typography>
                              {getSLACompliance(sla).toFixed(1)}%
                            </Typography>
                            <Chip
                              label={getSLAStatus(sla)}
                              size="small"
                              color={getSLAStatus(sla) === 'excellent' ? 'success' :
                                    getSLAStatus(sla) === 'good' ? 'primary' :
                                    getSLAStatus(sla) === 'warning' ? 'warning' : 'error'}
                            />
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={sla.status}
                            size="small"
                            color={sla.status === 'active' ? 'success' :
                                  sla.status === 'expired' ? 'error' :
                                  sla.status === 'suspended' ? 'warning' : 'default'}
                          />
                        </TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                            {sla.metrics?.slice(0, 3).map((metric: any) => (
                              <Chip
                                key={metric.id}
                                label={`${metric.type}: ${metric.actual}/${metric.target}`}
                                size="small"
                                color={metric.compliance ? 'success' : 'error'}
                              />
                            ))}
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', gap: 1 }}>
                            <Tooltip title="View SLA">
                              <IconButton
                                onClick={() => navigate(`/sla/${sla.id}`)}
                              >
                                <VisibilityIcon />
                              </IconButton>
                            </Tooltip>
                            <Tooltip title="Edit SLA">
                              <IconButton onClick={() => handleOpen(sla)}>
                                <EditIcon />
                              </IconButton>
                            </Tooltip>
                            <Tooltip title="Delete SLA">
                              <IconButton
                                onClick={() => handleDelete(sla.id)}
                                color="error"
                              >
                                <DeleteIcon />
                              </IconButton>
                            </Tooltip>
                          </Box>
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        </Grid>
      </Grid>

      <Dialog open={open} onClose={handleClose} maxWidth="lg" fullWidth>
        <DialogTitle>
          {selectedSLA ? 'Edit SLA' : 'Add New SLA'}
        </DialogTitle>
        <DialogContent>
          <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1 }}>
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Vendor</InputLabel>
              <Select
                value={formData.vendorId}
                onChange={handleSelectChange}
                name="vendorId"
                label="Vendor"
                required
              >
                {vendors.map((vendor) => (
                  <MenuItem key={vendor.id} value={vendor.id}>
                    {vendor.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Service Type</InputLabel>
              <Select
                value={formData.serviceType}
                onChange={handleSelectChange}
                name="serviceType"
                label="Service Type"
                required
              >
                {serviceTypes.map((type) => (
                  <MenuItem key={type} value={type}>
                    {type.charAt(0).toUpperCase() + type.slice(1)}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <TextField
              fullWidth
              margin="normal"
              label="Response Time (hours)"
              name="responseTime"
              type="number"
              value={formData.responseTime}
              onChange={handleInputChange}
              InputProps={{
                inputProps: { min: 0 },
              }}
            />

            <TextField
              fullWidth
              margin="normal"
              label="Resolution Time (hours)"
              name="resolutionTime"
              type="number"
              value={formData.resolutionTime}
              onChange={handleInputChange}
              InputProps={{
                inputProps: { min: 0 },
              }}
            />

            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Status</InputLabel>
              <Select
                value={formData.status}
                onChange={handleSelectChange}
                name="status"
                label="Status"
              >
                {statusTypes.map((status) => (
                  <MenuItem key={status} value={status}>
                    {status.charAt(0).toUpperCase() + status.slice(1)}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <TextField
              fullWidth
              margin="normal"
              label="Start Date"
              name="startDate"
              type="date"
              value={formData.startDate}
              onChange={handleInputChange}
              InputLabelProps={{ shrink: true }}
            />

            <TextField
              fullWidth
              margin="normal"
              label="End Date"
              name="endDate"
              type="date"
              value={formData.endDate}
              onChange={handleInputChange}
              InputLabelProps={{ shrink: true }}
            />

            <Box sx={{ mt: 2 }}>
              <Typography variant="h6" gutterBottom>
                SLA Metrics
              </Typography>
              {formData.metrics.map((metric: any, index: number) => (
                <Box key={index} sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                  <FormControl sx={{ minWidth: 120 }}>
                    <InputLabel>Metric Type</InputLabel>
                    <Select
                      value={metric.type}
                      onChange={(e) => {
                        const newMetrics = [...formData.metrics];
                        newMetrics[index].type = e.target.value;
                        setFormData((prev) => ({ ...prev, metrics: newMetrics }));
                      }}
                      label="Metric Type"
                    >
                      {metricTypes.map((type) => (
                        <MenuItem key={type} value={type}>
                          {type.replace('_', ' ')}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                  <TextField
                    label="Target Value"
                    type="number"
                    value={metric.target}
                    onChange={(e) => {
                      const newMetrics = [...formData.metrics];
                      newMetrics[index].target = Number(e.target.value);
                      setFormData((prev) => ({ ...prev, metrics: newMetrics }));
                    }}
                  />
                  <TextField
                    label="Actual Value"
                    type="number"
                    value={metric.actual}
                    onChange={(e) => {
                      const newMetrics = [...formData.metrics];
                      newMetrics[index].actual = Number(e.target.value);
                      setFormData((prev) => ({ ...prev, metrics: newMetrics }));
                    }}
                  />
                  <IconButton
                    onClick={() => handleRemoveMetric(index)}
                    color="error"
                  >
                    <DeleteIcon />
                  </IconButton>
                </Box>
              ))}
              <Button
                variant="outlined"
                onClick={handleAddMetric}
                sx={{ mt: 2 }}
              >
                Add Metric
              </Button>
            </Box>
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

export default SLATracking;
