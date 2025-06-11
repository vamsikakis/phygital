import { useState, useEffect } from 'react';
import axios from 'axios';

interface Report {
  id: number;
  title: string;
  periodStart: string;
  periodEnd: string;
  status: string;
  sections: ReportSection[];
  createdAt: string;
}

interface ReportSection {
  id: number;
  title: string;
  content: string;
  chartData: string;
  reportId: number;
}

export const useReports = () => {
  const [reports, setReports] = useState<Report[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const fetchReports = async () => {
      try {
        const response = await axios.get('/api/financial/reports');
        setReports(response.data);
      } catch (err) {
        setError(err instanceof Error ? err : new Error('Failed to fetch reports'));
      } finally {
        setLoading(false);
      }
    };

    fetchReports();
  }, []);

  const addReport = async (reportData: Omit<Report, 'id' | 'createdAt'>) => {
    try {
      const response = await axios.post('/api/financial/reports/', reportData);
      setReports((prev) => [...prev, response.data]);
      return response.data;
    } catch (err) {
      throw err instanceof Error ? err : new Error('Failed to add report');
    }
  };

  const updateReport = async (reportId: number, reportData: Partial<Report>) => {
    try {
      const response = await axios.put(`/api/financial/reports/${reportId}`, reportData);
      setReports((prev) =>
        prev.map((report) =>
          report.id === reportId ? { ...report, ...response.data } : report
        )
      );
      return response.data;
    } catch (err) {
      throw err instanceof Error ? err : new Error('Failed to update report');
    }
  };

  const deleteReport = async (reportId: number) => {
    try {
      await axios.delete(`/api/financial/reports/${reportId}`);
      setReports((prev) => prev.filter((report) => report.id !== reportId));
    } catch (err) {
      throw err instanceof Error ? err : new Error('Failed to delete report');
    }
  };

  const generateReport = async (startDate: string, endDate: string) => {
    try {
      const response = await axios.post('/api/financial/reports/generate', {
        startDate,
        endDate,
      });
      return response.data;
    } catch (err) {
      throw err instanceof Error ? err : new Error('Failed to generate report');
    }
  };

  return {
    reports,
    loading,
    error,
    addReport,
    updateReport,
    deleteReport,
    generateReport,
  };
};
