import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Paper,
  Typography,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Button,
  IconButton,
  Tooltip,
  Chip,
} from '@mui/material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as ChartTooltip,
  Legend,
  LineChart,
  Line,
  ResponsiveContainer,
} from 'recharts';
import { useFinancialData } from '../../hooks/useFinancialData';
import { format } from 'date-fns';
import RefreshIcon from '@mui/icons-material/Refresh';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';

const ExpenseAnalytics: React.FC = () => {
  const { expenses, loading, error } = useFinancialData();
  const [timeRange, setTimeRange] = useState('month');
  const [selectedCategory, setSelectedCategory] = useState('all');

  const categories = [
    'all',
    'maintenance',
    'utilities',
    'security',
    'cleaning',
    'administration',
    'other',
  ];

  const timeRanges = [
    { label: 'Monthly', value: 'month' },
    { label: 'Quarterly', value: 'quarter' },
    { label: 'Yearly', value: 'year' },
  ];

  const getExpenseTrend = (expenses: any[]) => {
    const groupedExpenses = expenses.reduce((acc, expense) => {
      const date = new Date(expense.date);
      const key = timeRange === 'month'
        ? format(date, 'MMM yyyy')
        : timeRange === 'quarter'
        ? `Q${Math.floor(date.getMonth() / 3) + 1} ${date.getFullYear()}`
        : date.getFullYear().toString();

      if (!acc[key]) {
        acc[key] = {
          total: 0,
          categories: {} as Record<string, number>,
        };
      }

      acc[key].total += expense.amount;
      if (expense.category in acc[key].categories) {
        acc[key].categories[expense.category] += expense.amount;
      } else {
        acc[key].categories[expense.category] = expense.amount;
      }

      return acc;
    }, {} as Record<string, { total: number; categories: Record<string, number> }>);

    return Object.entries(groupedExpenses).map(([key, value]) => ({
      date: key,
      ...value,
    }));
  };

  const getExpenseStats = (expenses: any[]) => {
    const total = expenses.reduce((acc, exp) => acc + exp.amount, 0);
    const average = expenses.length > 0 ? total / expenses.length : 0;
    const max = Math.max(...expenses.map((exp) => exp.amount));
    const min = Math.min(...expenses.map((exp) => exp.amount));

    return {
      total,
      average,
      max,
      min,
    };
  };

  if (loading) {
    return <Box sx={{ p: 3 }}>Loading...</Box>;
  }

  if (error) {
    return <Box sx={{ p: 3 }}>Error: {error.message}</Box>;
  }

  const filteredExpenses = selectedCategory === 'all'
    ? expenses
    : expenses.filter((exp) => exp.category === selectedCategory);

  const trendData = getExpenseTrend(filteredExpenses);
  const stats = getExpenseStats(filteredExpenses);

  return (
    <Box sx={{ p: 3 }}>
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Paper sx={{ p: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h6">Expense Analytics</Typography>
            <Box sx={{ display: 'flex', gap: 2 }}>
              <FormControl sx={{ minWidth: 120 }}>
                <InputLabel>Time Range</InputLabel>
                <Select
                  value={timeRange}
                  onChange={(e) => setTimeRange(e.target.value)}
                  label="Time Range"
                >
                  {timeRanges.map((range) => (
                    <MenuItem key={range.value} value={range.value}>
                      {range.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
              <FormControl sx={{ minWidth: 120 }}>
                <InputLabel>Category</InputLabel>
                <Select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  label="Category"
                >
                  {categories.map((cat) => (
                    <MenuItem key={cat} value={cat}>
                      {cat.charAt(0).toUpperCase() + cat.slice(1)}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
              <Tooltip title="Refresh Data">
                <IconButton>
                  <RefreshIcon />
                </IconButton>
              </Tooltip>
            </Box>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, height: 400 }}>
            <Typography variant="h6" gutterBottom>
              Expense Trend Analysis
            </Typography>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={trendData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="total"
                  stroke="#8884d8"
                  name="Total Expenses"
                />
                {Object.entries(trendData[0]?.categories || {}).map(([category]) => (
                  <Line
                    key={category}
                    type="monotone"
                    dataKey={`categories.${category}`}
                    stroke={`#${Math.floor(Math.random() * 16777215).toString(16)}`}
                    name={category.charAt(0).toUpperCase() + category.slice(1)}
                  />
                ))}
              </LineChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, height: 400 }}>
            <Typography variant="h6" gutterBottom>
              Category Distribution
            </Typography>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={trendData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                {Object.entries(trendData[0]?.categories || {}).map(([category]) => (
                  <Bar
                    key={category}
                    dataKey={`categories.${category}`}
                    fill={`#${Math.floor(Math.random() * 16777215).toString(16)}`}
                    name={category.charAt(0).toUpperCase() + category.slice(1)}
                  />
                ))}
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Expense Statistics
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <TrendingUpIcon color="success" />
                <Typography>Total: ₹{stats.total.toLocaleString()}</Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <TrendingUpIcon color="primary" />
                <Typography>Average: ₹{stats.average.toLocaleString()}</Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <TrendingUpIcon color="warning" />
                <Typography>Highest: ₹{stats.max.toLocaleString()}</Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <TrendingDownIcon color="error" />
                <Typography>Lowest: ₹{stats.min.toLocaleString()}</Typography>
              </Box>
            </Box>
          </Paper>
        </Grid>

        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Top Categories
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {Object.entries(trendData.reduce((acc, data) => {
                Object.entries(data.categories).forEach(([category, amount]) => {
                  acc[category] = (acc[category] || 0) + amount;
                });
                return acc;
              }, {} as Record<string, number>))
                .sort((a, b) => b[1] - a[1])
                .slice(0, 5)
                .map(([category, amount]) => (
                  <Chip
                    key={category}
                    label={`${category.charAt(0).toUpperCase() + category.slice(1)}: ₹${amount.toLocaleString()}`}
                    variant="outlined"
                    sx={{
                      bgcolor: `#${Math.floor(Math.random() * 16777215).toString(16)}`,
                      color: 'white',
                    }}
                  />
                ))}
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default ExpenseAnalytics;
