"""
Mock Firefly III Service for Demo Purposes
This provides sample financial data when Firefly III is not available
"""

import os
from datetime import datetime, timedelta
from typing import Dict, List, Any
import random

class MockFireflyService:
    def __init__(self):
        self.enabled = os.getenv('ENABLE_MOCK_FIREFLY', 'false').lower() == 'true'
    
    def test_connection(self) -> Dict[str, Any]:
        """Mock connection test"""
        if not self.enabled:
            return {
                'success': False,
                'error': 'Mock service not enabled',
                'message': 'Set ENABLE_MOCK_FIREFLY=true to use demo data'
            }
        
        return {
            'success': True,
            'version': 'Mock v1.0.0',
            'api_version': 'Demo API',
            'message': 'Connected to Mock Firefly III (Demo Mode)'
        }
    
    def get_accounts(self, account_type: str = None) -> List[Dict[str, Any]]:
        """Mock accounts data"""
        if not self.enabled:
            return []
        
        accounts = [
            {
                'id': '1',
                'name': 'Gopalan Atlantis Maintenance Fund',
                'type': 'asset',
                'account_role': 'defaultAsset',
                'currency_code': 'INR',
                'current_balance': '2850000.00',
                'current_balance_date': datetime.now().strftime('%Y-%m-%d'),
                'active': True,
                'account_number': 'MAINT001',
                'iban': None,
                'notes': 'Main maintenance fund for facility operations'
            },
            {
                'id': '2',
                'name': 'Reserve Fund Account',
                'type': 'asset',
                'account_role': 'savingAsset',
                'currency_code': 'INR',
                'current_balance': '1250000.00',
                'current_balance_date': datetime.now().strftime('%Y-%m-%d'),
                'active': True,
                'account_number': 'RESV001',
                'iban': None,
                'notes': 'Emergency reserve fund'
            },
            {
                'id': '3',
                'name': 'Operating Expenses Account',
                'type': 'asset',
                'account_role': 'defaultAsset',
                'currency_code': 'INR',
                'current_balance': '485000.00',
                'current_balance_date': datetime.now().strftime('%Y-%m-%d'),
                'active': True,
                'account_number': 'OPER001',
                'iban': None,
                'notes': 'Day-to-day operational expenses'
            },
            {
                'id': '4',
                'name': 'Utility Payments',
                'type': 'expense',
                'account_role': None,
                'currency_code': 'INR',
                'current_balance': '0.00',
                'current_balance_date': datetime.now().strftime('%Y-%m-%d'),
                'active': True,
                'account_number': None,
                'iban': None,
                'notes': 'Electricity, water, gas payments'
            }
        ]
        
        if account_type:
            accounts = [acc for acc in accounts if acc['type'] == account_type]
        
        return accounts
    
    def get_transactions(self, start_date: str = None, end_date: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Mock transactions data"""
        if not self.enabled:
            return []
        
        # Generate sample transactions for the last 30 days
        transactions = []
        base_date = datetime.now()
        
        sample_transactions = [
            {
                'description': 'Monthly Maintenance Fee Collection',
                'amount': '125000.00',
                'source_name': 'Maintenance Fee Collection',
                'destination_name': 'Gopalan Atlantis Maintenance Fund',
                'category_name': 'Maintenance Fees',
                'type': 'deposit'
            },
            {
                'description': 'Electricity Bill Payment - BESCOM',
                'amount': '-45000.00',
                'source_name': 'Operating Expenses Account',
                'destination_name': 'BESCOM',
                'category_name': 'Utilities',
                'type': 'withdrawal'
            },
            {
                'description': 'Security Service Payment',
                'amount': '-35000.00',
                'source_name': 'Operating Expenses Account',
                'destination_name': 'SecureGuard Services',
                'category_name': 'Security',
                'type': 'withdrawal'
            },
            {
                'description': 'Cleaning Service Payment',
                'amount': '-18000.00',
                'source_name': 'Operating Expenses Account',
                'destination_name': 'CleanPro Services',
                'category_name': 'Cleaning',
                'type': 'withdrawal'
            },
            {
                'description': 'Elevator Maintenance',
                'amount': '-25000.00',
                'source_name': 'Maintenance Fund',
                'destination_name': 'Otis Elevator Service',
                'category_name': 'Maintenance',
                'type': 'withdrawal'
            },
            {
                'description': 'Water Bill Payment - BWSSB',
                'amount': '-12000.00',
                'source_name': 'Operating Expenses Account',
                'destination_name': 'BWSSB',
                'category_name': 'Utilities',
                'type': 'withdrawal'
            },
            {
                'description': 'Parking Fee Collection',
                'amount': '15000.00',
                'source_name': 'Parking Fees',
                'destination_name': 'Operating Expenses Account',
                'category_name': 'Parking Revenue',
                'type': 'deposit'
            },
            {
                'description': 'Landscaping Service',
                'amount': '-8000.00',
                'source_name': 'Operating Expenses Account',
                'destination_name': 'GreenThumb Landscaping',
                'category_name': 'Landscaping',
                'type': 'withdrawal'
            }
        ]
        
        for i in range(min(limit, 20)):
            transaction_template = random.choice(sample_transactions)
            transaction_date = base_date - timedelta(days=random.randint(0, 30))
            
            transactions.append({
                'id': f'mock_{i+1}',
                'date': transaction_date.strftime('%Y-%m-%d'),
                'description': transaction_template['description'],
                'amount': transaction_template['amount'],
                'currency_code': 'INR',
                'source_name': transaction_template['source_name'],
                'destination_name': transaction_template['destination_name'],
                'category_name': transaction_template['category_name'],
                'type': transaction_template['type'],
                'notes': f'Demo transaction #{i+1}'
            })
        
        # Sort by date (newest first)
        transactions.sort(key=lambda x: x['date'], reverse=True)
        return transactions
    
    def get_budgets(self) -> List[Dict[str, Any]]:
        """Mock budgets data"""
        if not self.enabled:
            return []
        
        return [
            {
                'id': '1',
                'name': 'Monthly Utilities Budget',
                'active': True,
                'auto_budget_type': 'monthly',
                'auto_budget_amount': '60000.00',
                'auto_budget_period': 'monthly',
                'notes': 'Budget for electricity, water, gas'
            },
            {
                'id': '2',
                'name': 'Security Services Budget',
                'active': True,
                'auto_budget_type': 'monthly',
                'auto_budget_amount': '40000.00',
                'auto_budget_period': 'monthly',
                'notes': 'Monthly security service costs'
            },
            {
                'id': '3',
                'name': 'Maintenance & Repairs Budget',
                'active': True,
                'auto_budget_type': 'monthly',
                'auto_budget_amount': '50000.00',
                'auto_budget_period': 'monthly',
                'notes': 'Regular maintenance and emergency repairs'
            },
            {
                'id': '4',
                'name': 'Cleaning Services Budget',
                'active': True,
                'auto_budget_type': 'monthly',
                'auto_budget_amount': '20000.00',
                'auto_budget_period': 'monthly',
                'notes': 'Common area cleaning services'
            }
        ]
    
    def get_categories(self) -> List[Dict[str, Any]]:
        """Mock categories data"""
        if not self.enabled:
            return []
        
        return [
            {'id': '1', 'name': 'Utilities', 'notes': 'Electricity, water, gas'},
            {'id': '2', 'name': 'Security', 'notes': 'Security services and equipment'},
            {'id': '3', 'name': 'Maintenance', 'notes': 'Building maintenance and repairs'},
            {'id': '4', 'name': 'Cleaning', 'notes': 'Cleaning services'},
            {'id': '5', 'name': 'Landscaping', 'notes': 'Garden and landscape maintenance'},
            {'id': '6', 'name': 'Maintenance Fees', 'notes': 'Monthly maintenance fee collection'},
            {'id': '7', 'name': 'Parking Revenue', 'notes': 'Parking fee collection'}
        ]
    
    def get_summary(self) -> Dict[str, Any]:
        """Mock financial summary"""
        if not self.enabled:
            return {
                'total_assets': 0,
                'total_liabilities': 0,
                'net_worth': 0,
                'accounts_count': 0,
                'recent_transactions_count': 0,
                'recent_transactions': [],
                'error': 'Mock service not enabled'
            }
        
        accounts = self.get_accounts()
        transactions = self.get_transactions(limit=5)
        
        total_assets = sum(float(acc.get('current_balance', 0)) for acc in accounts if acc.get('type') == 'asset')
        total_liabilities = sum(float(acc.get('current_balance', 0)) for acc in accounts if acc.get('type') == 'liability')
        
        return {
            'total_assets': total_assets,
            'total_liabilities': abs(total_liabilities),
            'net_worth': total_assets - abs(total_liabilities),
            'accounts_count': len(accounts),
            'recent_transactions_count': len(transactions),
            'recent_transactions': transactions,
            'summary_data': {
                'demo_mode': True,
                'message': 'This is demo data. Install Firefly III for real financial management.'
            }
        }

# Create singleton instance
mock_firefly_service = MockFireflyService()
