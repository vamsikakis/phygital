import { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

interface Expense {
  id: number;
  category: string;
  amount: number;
  description: string;
  vendorId: number | null;
  status: string;
  date: string;
}

interface Vendor {
  id: number;
  name: string;
  contactPerson: string;
  email: string;
  phone: string;
  address: string;
  rating: number;
}

interface Budget {
  id: number;
  year: number;
  month: number;
  category: string;
  allocatedAmount: number;
  actualAmount: number;
  notes: string;
}

export const useFinancialData = (month: string) => {
  const [expenses, setExpenses] = useState<Expense[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const fetchExpenses = async () => {
      try {
        const response = await axios.get(`/api/financial/expenses?month=${month}`);
        setExpenses(response.data);
      } catch (err) {
        setError(err instanceof Error ? err : new Error('Failed to fetch expenses'));
      } finally {
        setLoading(false);
      }
    };

    fetchExpenses();
  }, [month]);

  const addExpense = async (expenseData: Omit<Expense, 'id' | 'date'>) => {
    try {
      const response = await axios.post('/api/financial/expenses/', expenseData);
      setExpenses((prev) => [...prev, response.data]);
      return response.data;
    } catch (err) {
      throw err instanceof Error ? err : new Error('Failed to add expense');
    }
  };

  const updateExpense = async (expenseId: number, expenseData: Partial<Expense>) => {
    try {
      const response = await axios.put(`/api/financial/expenses/${expenseId}`, expenseData);
      setExpenses((prev) =>
        prev.map((expense) =>
          expense.id === expenseId ? { ...expense, ...response.data } : expense
        )
      );
      return response.data;
    } catch (err) {
      throw err instanceof Error ? err : new Error('Failed to update expense');
    }
  };

  const deleteExpense = async (expenseId: number) => {
    try {
      await axios.delete(`/api/financial/expenses/${expenseId}`);
      setExpenses((prev) => prev.filter((expense) => expense.id !== expenseId));
    } catch (err) {
      throw err instanceof Error ? err : new Error('Failed to delete expense');
    }
  };

  return { expenses, loading, error, addExpense, updateExpense, deleteExpense };
};

export const useVendors = () => {
  const [vendors, setVendors] = useState<Vendor[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const fetchVendors = async () => {
      try {
        const response = await axios.get('/api/financial/vendors');
        setVendors(response.data);
      } catch (err) {
        setError(err instanceof Error ? err : new Error('Failed to fetch vendors'));
      } finally {
        setLoading(false);
      }
    };

    fetchVendors();
  }, []);

  const addVendor = async (vendorData: Omit<Vendor, 'id'>) => {
    try {
      const response = await axios.post('/api/financial/vendors/', vendorData);
      setVendors((prev) => [...prev, response.data]);
      return response.data;
    } catch (err) {
      throw err instanceof Error ? err : new Error('Failed to add vendor');
    }
  };

  const updateVendor = async (vendorId: number, vendorData: Partial<Vendor>) => {
    try {
      const response = await axios.put(`/api/financial/vendors/${vendorId}`, vendorData);
      setVendors((prev) =>
        prev.map((vendor) =>
          vendor.id === vendorId ? { ...vendor, ...response.data } : vendor
        )
      );
      return response.data;
    } catch (err) {
      throw err instanceof Error ? err : new Error('Failed to update vendor');
    }
  };

  const deleteVendor = async (vendorId: number) => {
    try {
      await axios.delete(`/api/financial/vendors/${vendorId}`);
      setVendors((prev) => prev.filter((vendor) => vendor.id !== vendorId));
    } catch (err) {
      throw err instanceof Error ? err : new Error('Failed to delete vendor');
    }
  };

  return { vendors, loading, error, addVendor, updateVendor, deleteVendor };
};

export const useBudgets = () => {
  const [budgets, setBudgets] = useState<Budget[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const fetchBudgets = async () => {
      try {
        const response = await axios.get('/api/financial/budgets');
        setBudgets(response.data);
      } catch (err) {
        setError(err instanceof Error ? err : new Error('Failed to fetch budgets'));
      } finally {
        setLoading(false);
      }
    };

    fetchBudgets();
  }, []);

  const addBudget = async (budgetData: Omit<Budget, 'id'>) => {
    try {
      const response = await axios.post('/api/financial/budgets/', budgetData);
      setBudgets((prev) => [...prev, response.data]);
      return response.data;
    } catch (err) {
      throw err instanceof Error ? err : new Error('Failed to add budget');
    }
  };

  const updateBudget = async (budgetId: number, budgetData: Partial<Budget>) => {
    try {
      const response = await axios.put(`/api/financial/budgets/${budgetId}`, budgetData);
      setBudgets((prev) =>
        prev.map((budget) =>
          budget.id === budgetId ? { ...budget, ...response.data } : budget
        )
      );
      return response.data;
    } catch (err) {
      throw err instanceof Error ? err : new Error('Failed to update budget');
    }
  };

  const deleteBudget = async (budgetId: number) => {
    try {
      await axios.delete(`/api/financial/budgets/${budgetId}`);
      setBudgets((prev) => prev.filter((budget) => budget.id !== budgetId));
    } catch (err) {
      throw err instanceof Error ? err : new Error('Failed to delete budget');
    }
  };

  return { budgets, loading, error, addBudget, updateBudget, deleteBudget };
};
