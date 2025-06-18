import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Paper,
  Typography,
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
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Tooltip,
  Divider,
} from '@mui/material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as ChartTooltip,
  ResponsiveContainer,
} from 'recharts';
import { useReports } from '../../hooks/useReports';
import { useNavigate } from 'react-router-dom';
import { format } from 'date-fns';
import FileDownloadIcon from '@mui/icons-material/FileDownload';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import ViewIcon from '@mui/icons-material/Visibility';

const FinancialReports: React.FC = () => {
  const navigate = useNavigate();
  const { reports, loading, error, generateReport, deleteReport } = useReports();
  const [openGenerateDialog, setOpenGenerateDialog] = useState(false);
  const [selectedReport, setSelectedReport] = useState<number | null>(null);
  const [selectedStartDate, setSelectedStartDate] = useState('');
  const [selectedEndDate, setSelectedEndDate] = useState('');

  const handleOpenGenerateDialog = () => {
    setOpenGenerateDialog(true);
  };

  const handleCloseGenerateDialog = () => {
    setOpenGenerateDialog(false);
  };

  const handleGenerateReport = async () => {
    if (!selectedStartDate || !selectedEndDate) return;

    try {
      await generateReport(selectedStartDate, selectedEndDate);
      handleCloseGenerateDialog();
    } catch (error) {
      console.error('Error generating report:', error);
    }
  };

  const handleDeleteReport = async (reportId: number) => {
    try {
      await deleteReport(reportId);
    } catch (error) {
      console.error('Error deleting report:', error);
    }
  };

  const getReportStatusColor = (status: string) => {
    switch (status) {
      case 'draft':
        return 'warning';
      case 'published':
        return 'success';
      case 'archived':
        return 'disabled';
      default:
        return 'default';
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
            <Typography variant="h6">Financial Reports</Typography>
            <Button
              variant="contained"
              color="primary"
              onClick={handleOpenGenerateDialog}
            >
              Generate New Report
            </Button>
          </Paper>
        </Grid>

        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Title</TableCell>
                    <TableCell>Period</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Created At</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {reports.map((report) => (
                    <TableRow key={report.id}>
                      <TableCell>{report.title}</TableCell>
                      <TableCell>
                        {format(new Date(report.periodStart), 'MMM dd, yyyy')} -
                        {format(new Date(report.periodEnd), 'MMM dd, yyyy')}
                      </TableCell>
                      <TableCell>
                        <Box
                          sx={{
                            bgcolor: getReportStatusColor(report.status),
                            color: 'white',
                            p: 1,
                            borderRadius: 1,
                            minWidth: 80,
                            textAlign: 'center',
                          }}
                        >
                          {report.status.charAt(0).toUpperCase() + report.status.slice(1)}
                        </Box>
                      </TableCell>
                      <TableCell>
                        {format(new Date(report.createdAt), 'MMM dd, yyyy')}
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', gap: 1 }}>
                          <Tooltip title="View Report">
                            <IconButton
                              onClick={() => navigate(`/financial/reports/${report.id}`)}
                            >
                              <ViewIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Download Report">
                            <IconButton>
                              <FileDownloadIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Edit Report">
                            <IconButton>
                              <EditIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Delete Report">
                            <IconButton
                              onClick={() => handleDeleteReport(report.id)}
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

      <Dialog open={openGenerateDialog} onClose={handleCloseGenerateDialog} maxWidth="sm" fullWidth>
        <DialogTitle>Generate New Report</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <TextField
              fullWidth
              type="date"
              label="Start Date"
              value={selectedStartDate}
              onChange={(e) => setSelectedStartDate(e.target.value)}
              sx={{ mb: 2 }}
              InputLabelProps={{ shrink: true }}
            />
            <TextField
              fullWidth
              type="date"
              label="End Date"
              value={selectedEndDate}
              onChange={(e) => setSelectedEndDate(e.target.value)}
              sx={{ mb: 2 }}
              InputLabelProps={{ shrink: true }}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseGenerateDialog}>Cancel</Button>
          <Button onClick={handleGenerateReport} variant="contained" color="primary">
            Generate
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default FinancialReports;
