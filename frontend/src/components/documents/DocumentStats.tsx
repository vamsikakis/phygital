import React from 'react';
import { Box, Card, CardContent, Grid, Typography, LinearProgress, Paper } from '@mui/material';
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  Legend
} from 'recharts';

interface DocumentStatsProps {
  documents: any[];
}

const DocumentStats: React.FC<DocumentStatsProps> = ({ documents }) => {
  // Count documents by type
  const documentsByType = documents.reduce((acc: Record<string, number>, doc: any) => {
    const type = doc.type || 'Unknown';
    acc[type] = (acc[type] || 0) + 1;
    return acc;
  }, {});

  // Format data for pie chart
  const chartData = Object.entries(documentsByType).map(([name, value]) => ({ name, value }));
  
  // Colors for the pie chart
  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d'];

  // Count total documents
  const totalDocuments = documents.length;
  
  // Count documents by status
  const activeDocuments = documents.filter(doc => doc.status === 'Active').length;
  const archivedDocuments = documents.filter(doc => doc.status === 'Archived').length;
  const draftDocuments = documents.filter(doc => doc.status === 'Draft').length;

  return (
    <Paper sx={{ p: 2, mb: 3 }}>
      <Typography variant="h6" gutterBottom>Document Analytics</Typography>
      
      <Grid container spacing={3}>
        {/* Document count stats */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="subtitle2" color="textSecondary">Total Documents</Typography>
              <Typography variant="h4">{totalDocuments}</Typography>
              
              <Box sx={{ mt: 2 }}>
                <Typography variant="body2">
                  Active: {activeDocuments} ({totalDocuments ? Math.round((activeDocuments / totalDocuments) * 100) : 0}%)
                </Typography>
                <LinearProgress 
                  variant="determinate" 
                  value={totalDocuments ? (activeDocuments / totalDocuments) * 100 : 0} 
                  color="primary" 
                  sx={{ mt: 0.5, mb: 1.5 }} 
                />
                
                <Typography variant="body2">
                  Archived: {archivedDocuments} ({totalDocuments ? Math.round((archivedDocuments / totalDocuments) * 100) : 0}%)
                </Typography>
                <LinearProgress 
                  variant="determinate" 
                  value={totalDocuments ? (archivedDocuments / totalDocuments) * 100 : 0} 
                  color="secondary" 
                  sx={{ mt: 0.5, mb: 1.5 }} 
                />
                
                <Typography variant="body2">
                  Draft: {draftDocuments} ({totalDocuments ? Math.round((draftDocuments / totalDocuments) * 100) : 0}%)
                </Typography>
                <LinearProgress 
                  variant="determinate" 
                  value={totalDocuments ? (draftDocuments / totalDocuments) * 100 : 0} 
                  color="info" 
                  sx={{ mt: 0.5 }} 
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        {/* Document type distribution chart */}
        <Grid item xs={12} md={8}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="subtitle2" color="textSecondary">Document Type Distribution</Typography>
              <Box sx={{ height: 250 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={chartData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {chartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => [`${value} documents`, 'Count']} />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Paper>
  );
};

export default DocumentStats;
