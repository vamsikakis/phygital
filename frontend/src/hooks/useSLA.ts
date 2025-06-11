import { useState, useEffect } from 'react';
import axios from 'axios';

interface SLA {
  id: number;
  vendorId: number;
  serviceType: string;
  responseTime: number;
  resolutionTime: number;
  status: string;
  startDate: string;
  endDate: string;
  metrics: SLAMetric[];
}

interface SLAMetric {
  id: number;
  slaId: number;
  metricType: string;
  targetValue: number;
  actualValue: number;
  compliance: boolean;
}

export const useSLA = () => {
  const [slas, setSLAs] = useState<SLA[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const fetchSLAs = async () => {
      try {
        const response = await axios.get('/api/sla');
        setSLAs(response.data);
      } catch (err) {
        setError(err instanceof Error ? err : new Error('Failed to fetch SLAs'));
      } finally {
        setLoading(false);
      }
    };

    fetchSLAs();
  }, []);

  const addSLA = async (slaData: Omit<SLA, 'id'>) => {
    try {
      const response = await axios.post('/api/sla', slaData);
      setSLAs((prev) => [...prev, response.data]);
      return response.data;
    } catch (err) {
      throw err instanceof Error ? err : new Error('Failed to add SLA');
    }
  };

  const updateSLA = async (slaId: number, slaData: Partial<SLA>) => {
    try {
      const response = await axios.put(`/api/sla/${slaId}`, slaData);
      setSLAs((prev) =>
        prev.map((sla) =>
          sla.id === slaId ? { ...sla, ...response.data } : sla
        )
      );
      return response.data;
    } catch (err) {
      throw err instanceof Error ? err : new Error('Failed to update SLA');
    }
  };

  const deleteSLA = async (slaId: number) => {
    try {
      await axios.delete(`/api/sla/${slaId}`);
      setSLAs((prev) => prev.filter((sla) => sla.id !== slaId));
    } catch (err) {
      throw err instanceof Error ? err : new Error('Failed to delete SLA');
    }
  };

  const getSLACompliance = (sla: SLA) => {
    const metrics = sla.metrics || [];
    const compliantMetrics = metrics.filter((metric) => metric.compliance);
    return (compliantMetrics.length / metrics.length) * 100;
  };

  const getSLAStatus = (sla: SLA) => {
    const compliance = getSLACompliance(sla);
    if (compliance >= 90) return 'excellent';
    if (compliance >= 80) return 'good';
    if (compliance >= 70) return 'warning';
    return 'critical';
  };

  return {
    slas,
    loading,
    error,
    addSLA,
    updateSLA,
    deleteSLA,
    getSLACompliance,
    getSLAStatus,
  };
};
