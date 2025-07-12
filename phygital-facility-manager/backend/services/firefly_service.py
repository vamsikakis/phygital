"""
Firefly III Integration Service
Provides financial analysis and management through Firefly III API
"""

import os
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from flask import current_app

# Import mock service for demo purposes
try:
    from .mock_firefly_service import mock_firefly_service
except ImportError:
    mock_firefly_service = None

class FireflyService:
    def __init__(self):
        self.base_url = os.getenv('FIREFLY_BASE_URL', 'http://localhost:8080')
        self.api_token = os.getenv('FIREFLY_API_TOKEN')
        self.api_base = f"{self.base_url}/api/v1"
        
        if not self.api_token:
            # Use print instead of current_app.logger during initialization
            print("Warning: Firefly III API token not configured")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for Firefly III API requests"""
        return {
            'Authorization': f'Bearer {self.api_token}',
            'Accept': 'application/vnd.api+json',
            'Content-Type': 'application/json'
        }
    
    def _make_request(self, method: str, endpoint: str, data: Dict = None) -> Dict[str, Any]:
        """Make a request to Firefly III API"""
        if not self.api_token:
            raise ValueError("Firefly III API token not configured")
        
        url = f"{self.api_base}/{endpoint}"
        headers = self._get_headers()
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, params=data)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers, json=data)
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=headers, json=data)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Firefly III API error: {e}")
            raise
    
    def test_connection(self) -> Dict[str, Any]:
        """Test connection to Firefly III"""
        try:
            response = self._make_request('GET', 'about')
            return {
                'success': True,
                'version': response.get('data', {}).get('version', 'Unknown'),
                'api_version': response.get('data', {}).get('api_version', 'Unknown'),
                'message': 'Connected to Firefly III successfully'
            }
        except Exception as e:
            current_app.logger.error(f"Failed to connect to Firefly III: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to connect to Firefly III. Please check your configuration.'
            }
    
    def get_accounts(self, account_type: str = None) -> List[Dict[str, Any]]:
        """Get all accounts or accounts of specific type"""
        try:
            params = {}
            if account_type:
                params['type'] = account_type
            
            response = self._make_request('GET', 'accounts', params)
            accounts = response.get('data', [])
            
            formatted_accounts = []
            for account in accounts:
                attrs = account.get('attributes', {})
                formatted_accounts.append({
                    'id': account.get('id'),
                    'name': attrs.get('name'),
                    'type': attrs.get('type'),
                    'account_role': attrs.get('account_role'),
                    'currency_code': attrs.get('currency_code'),
                    'current_balance': attrs.get('current_balance'),
                    'current_balance_date': attrs.get('current_balance_date'),
                    'active': attrs.get('active', True),
                    'account_number': attrs.get('account_number'),
                    'iban': attrs.get('iban'),
                    'notes': attrs.get('notes')
                })
            
            return formatted_accounts
            
        except Exception as e:
            current_app.logger.error(f"Error getting accounts: {e}")
            # Fall back to mock service if available
            if mock_firefly_service:
                current_app.logger.info("Using mock service for accounts")
                # Temporarily enable mock service for fallback
                original_enabled = mock_firefly_service.enabled
                mock_firefly_service.enabled = True
                result = mock_firefly_service.get_accounts(account_type)
                mock_firefly_service.enabled = original_enabled
                return result
            return []
    
    def get_transactions(self, start_date: str = None, end_date: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get transactions within date range"""
        try:
            params = {'limit': limit}
            
            if not start_date:
                start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            if not end_date:
                end_date = datetime.now().strftime('%Y-%m-%d')
            
            params['start'] = start_date
            params['end'] = end_date
            
            response = self._make_request('GET', 'transactions', params)
            transactions = response.get('data', [])
            
            formatted_transactions = []
            for transaction in transactions:
                attrs = transaction.get('attributes', {})
                transactions_data = attrs.get('transactions', [])
                
                for trans in transactions_data:
                    formatted_transactions.append({
                        'id': transaction.get('id'),
                        'date': attrs.get('date'),
                        'description': trans.get('description'),
                        'amount': trans.get('amount'),
                        'currency_code': trans.get('currency_code'),
                        'source_name': trans.get('source_name'),
                        'destination_name': trans.get('destination_name'),
                        'category_name': trans.get('category_name'),
                        'budget_name': trans.get('budget_name'),
                        'type': trans.get('type'),
                        'notes': trans.get('notes')
                    })
            
            return formatted_transactions
            
        except Exception as e:
            current_app.logger.error(f"Error getting transactions: {e}")
            return []
    
    def get_budgets(self) -> List[Dict[str, Any]]:
        """Get all budgets"""
        try:
            response = self._make_request('GET', 'budgets')
            budgets = response.get('data', [])
            
            formatted_budgets = []
            for budget in budgets:
                attrs = budget.get('attributes', {})
                formatted_budgets.append({
                    'id': budget.get('id'),
                    'name': attrs.get('name'),
                    'active': attrs.get('active'),
                    'auto_budget_type': attrs.get('auto_budget_type'),
                    'auto_budget_amount': attrs.get('auto_budget_amount'),
                    'auto_budget_period': attrs.get('auto_budget_period'),
                    'notes': attrs.get('notes')
                })
            
            return formatted_budgets
            
        except Exception as e:
            current_app.logger.error(f"Error getting budgets: {e}")
            # Fall back to mock service if available
            if mock_firefly_service:
                current_app.logger.info("Using mock service for budgets")
                # Temporarily enable mock service for fallback
                original_enabled = mock_firefly_service.enabled
                mock_firefly_service.enabled = True
                result = mock_firefly_service.get_budgets()
                mock_firefly_service.enabled = original_enabled
                return result
            return []
    
    def get_categories(self) -> List[Dict[str, Any]]:
        """Get all categories"""
        try:
            response = self._make_request('GET', 'categories')
            categories = response.get('data', [])
            
            formatted_categories = []
            for category in categories:
                attrs = category.get('attributes', {})
                formatted_categories.append({
                    'id': category.get('id'),
                    'name': attrs.get('name'),
                    'notes': attrs.get('notes'),
                    'spent': attrs.get('spent', []),
                    'earned': attrs.get('earned', [])
                })
            
            return formatted_categories
            
        except Exception as e:
            current_app.logger.error(f"Error getting categories: {e}")
            return []
    
    def get_summary(self) -> Dict[str, Any]:
        """Get financial summary"""
        try:
            # Get basic summary from Firefly III
            response = self._make_request('GET', 'summary/basic')
            summary_data = response.get('data', {})
            
            # Get accounts for balance calculation
            accounts = self.get_accounts()
            
            # Calculate totals
            total_assets = sum(float(acc.get('current_balance', 0)) for acc in accounts if acc.get('type') == 'asset')
            total_liabilities = sum(float(acc.get('current_balance', 0)) for acc in accounts if acc.get('type') == 'liability')
            
            # Get recent transactions
            recent_transactions = self.get_transactions(limit=10)
            
            return {
                'total_assets': total_assets,
                'total_liabilities': abs(total_liabilities),
                'net_worth': total_assets - abs(total_liabilities),
                'accounts_count': len(accounts),
                'recent_transactions_count': len(recent_transactions),
                'recent_transactions': recent_transactions[:5],  # Last 5 transactions
                'summary_data': summary_data
            }
            
        except Exception as e:
            current_app.logger.error(f"Error getting summary: {e}")
            # Fall back to mock service if available
            if mock_firefly_service:
                current_app.logger.info("Using mock service for summary")
                # Temporarily enable mock service for fallback
                original_enabled = mock_firefly_service.enabled
                mock_firefly_service.enabled = True
                result = mock_firefly_service.get_summary()
                mock_firefly_service.enabled = original_enabled
                return result
            return {
                'total_assets': 0,
                'total_liabilities': 0,
                'net_worth': 0,
                'accounts_count': 0,
                'recent_transactions_count': 0,
                'recent_transactions': [],
                'error': str(e)
            }
    
    def create_transaction(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new transaction"""
        try:
            # Format transaction data for Firefly III API
            firefly_data = {
                'error_if_duplicate_hash': False,
                'apply_rules': True,
                'fire_webhooks': True,
                'transactions': [transaction_data]
            }
            
            response = self._make_request('POST', 'transactions', firefly_data)
            return {
                'success': True,
                'transaction': response.get('data', {})
            }
            
        except Exception as e:
            current_app.logger.error(f"Error creating transaction: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def create_account(self, account_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new account"""
        try:
            # Format account data for Firefly III API
            firefly_data = {
                'name': account_data.get('name'),
                'type': account_data.get('type'),
                'account_role': account_data.get('account_role'),
                'currency_code': account_data.get('currency_code', 'INR'),
                'opening_balance': account_data.get('opening_balance', '0'),
                'opening_balance_date': account_data.get('opening_balance_date', datetime.now().strftime('%Y-%m-%d')),
                'account_number': account_data.get('account_number'),
                'iban': account_data.get('iban'),
                'bic': account_data.get('bic'),
                'notes': account_data.get('notes'),
                'active': account_data.get('active', True)
            }

            response = self._make_request('POST', 'accounts', firefly_data)
            return {
                'success': True,
                'account': response.get('data', {})
            }

        except Exception as e:
            current_app.logger.error(f"Error creating account: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def update_account(self, account_id: str, account_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing account"""
        try:
            response = self._make_request('PUT', f'accounts/{account_id}', account_data)
            return {
                'success': True,
                'account': response.get('data', {})
            }

        except Exception as e:
            current_app.logger.error(f"Error updating account: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def delete_account(self, account_id: str) -> Dict[str, Any]:
        """Delete an account"""
        try:
            self._make_request('DELETE', f'accounts/{account_id}')
            return {
                'success': True,
                'message': 'Account deleted successfully'
            }

        except Exception as e:
            current_app.logger.error(f"Error deleting account: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def create_budget(self, budget_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new budget"""
        try:
            # Format budget data for Firefly III API
            firefly_data = {
                'name': budget_data.get('name'),
                'active': budget_data.get('active', True),
                'auto_budget_type': budget_data.get('auto_budget_type'),
                'auto_budget_amount': budget_data.get('auto_budget_amount'),
                'auto_budget_period': budget_data.get('auto_budget_period'),
                'notes': budget_data.get('notes')
            }

            response = self._make_request('POST', 'budgets', firefly_data)
            return {
                'success': True,
                'budget': response.get('data', {})
            }

        except Exception as e:
            current_app.logger.error(f"Error creating budget: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def update_budget(self, budget_id: str, budget_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing budget"""
        try:
            response = self._make_request('PUT', f'budgets/{budget_id}', budget_data)
            return {
                'success': True,
                'budget': response.get('data', {})
            }

        except Exception as e:
            current_app.logger.error(f"Error updating budget: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def delete_budget(self, budget_id: str) -> Dict[str, Any]:
        """Delete a budget"""
        try:
            self._make_request('DELETE', f'budgets/{budget_id}')
            return {
                'success': True,
                'message': 'Budget deleted successfully'
            }

        except Exception as e:
            current_app.logger.error(f"Error deleting budget: {e}")
            return {
                'success': False,
                'error': str(e)
            }

# Create singleton instance
firefly_service = FireflyService()
