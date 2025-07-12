"""
Firefly III API Routes
Provides REST endpoints for financial management through Firefly III
"""

from flask import Blueprint, request, jsonify, current_app
from services.firefly_service import firefly_service
from datetime import datetime

# Create blueprint
firefly_bp = Blueprint('firefly', __name__)

@firefly_bp.route('/test', methods=['GET'])
def test_firefly_connection():
    """Test connection to Firefly III"""
    try:
        result = firefly_service.test_connection()
        # Always return 200 for successful API calls, even if Firefly connection fails
        # The success/failure is indicated in the JSON response
        return jsonify(result), 200
    except Exception as e:
        current_app.logger.error(f"Error testing Firefly connection: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@firefly_bp.route('/accounts', methods=['GET'])
def get_accounts():
    """Get all accounts or accounts of specific type"""
    try:
        account_type = request.args.get('type')
        accounts = firefly_service.get_accounts(account_type)
        
        return jsonify({
            'success': True,
            'accounts': accounts,
            'count': len(accounts)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting accounts: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@firefly_bp.route('/accounts', methods=['POST'])
def create_account():
    """Create a new account"""
    try:
        account_data = request.get_json()

        if not account_data:
            return jsonify({
                'success': False,
                'error': 'No account data provided'
            }), 400

        # Validate required fields
        required_fields = ['name', 'type']
        for field in required_fields:
            if field not in account_data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400

        result = firefly_service.create_account(account_data)
        status_code = 201 if result.get('success') else 400

        return jsonify(result), status_code

    except Exception as e:
        current_app.logger.error(f"Error creating account: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@firefly_bp.route('/accounts/<account_id>', methods=['PUT'])
def update_account(account_id):
    """Update an existing account"""
    try:
        account_data = request.get_json()

        if not account_data:
            return jsonify({
                'success': False,
                'error': 'No account data provided'
            }), 400

        result = firefly_service.update_account(account_id, account_data)
        status_code = 200 if result.get('success') else 400

        return jsonify(result), status_code

    except Exception as e:
        current_app.logger.error(f"Error updating account: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@firefly_bp.route('/accounts/<account_id>', methods=['DELETE'])
def delete_account(account_id):
    """Delete an account"""
    try:
        result = firefly_service.delete_account(account_id)
        status_code = 200 if result.get('success') else 400

        return jsonify(result), status_code

    except Exception as e:
        current_app.logger.error(f"Error deleting account: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@firefly_bp.route('/transactions', methods=['GET'])
def get_transactions():
    """Get transactions within date range"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        limit = int(request.args.get('limit', 50))
        
        transactions = firefly_service.get_transactions(start_date, end_date, limit)
        
        return jsonify({
            'success': True,
            'transactions': transactions,
            'count': len(transactions)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting transactions: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@firefly_bp.route('/transactions', methods=['POST'])
def create_transaction():
    """Create a new transaction"""
    try:
        transaction_data = request.get_json()
        
        if not transaction_data:
            return jsonify({
                'success': False,
                'error': 'No transaction data provided'
            }), 400
        
        result = firefly_service.create_transaction(transaction_data)
        status_code = 201 if result.get('success') else 400
        
        return jsonify(result), status_code
        
    except Exception as e:
        current_app.logger.error(f"Error creating transaction: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@firefly_bp.route('/budgets', methods=['GET'])
def get_budgets():
    """Get all budgets"""
    try:
        budgets = firefly_service.get_budgets()
        
        return jsonify({
            'success': True,
            'budgets': budgets,
            'count': len(budgets)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting budgets: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@firefly_bp.route('/budgets', methods=['POST'])
def create_budget():
    """Create a new budget"""
    try:
        budget_data = request.get_json()

        if not budget_data:
            return jsonify({
                'success': False,
                'error': 'No budget data provided'
            }), 400

        # Validate required fields
        required_fields = ['name']
        for field in required_fields:
            if field not in budget_data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400

        result = firefly_service.create_budget(budget_data)
        status_code = 201 if result.get('success') else 400

        return jsonify(result), status_code

    except Exception as e:
        current_app.logger.error(f"Error creating budget: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@firefly_bp.route('/budgets/<budget_id>', methods=['PUT'])
def update_budget(budget_id):
    """Update an existing budget"""
    try:
        budget_data = request.get_json()

        if not budget_data:
            return jsonify({
                'success': False,
                'error': 'No budget data provided'
            }), 400

        result = firefly_service.update_budget(budget_id, budget_data)
        status_code = 200 if result.get('success') else 400

        return jsonify(result), status_code

    except Exception as e:
        current_app.logger.error(f"Error updating budget: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@firefly_bp.route('/budgets/<budget_id>', methods=['DELETE'])
def delete_budget(budget_id):
    """Delete a budget"""
    try:
        result = firefly_service.delete_budget(budget_id)
        status_code = 200 if result.get('success') else 400

        return jsonify(result), status_code

    except Exception as e:
        current_app.logger.error(f"Error deleting budget: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@firefly_bp.route('/categories', methods=['GET'])
def get_categories():
    """Get all categories"""
    try:
        categories = firefly_service.get_categories()
        
        return jsonify({
            'success': True,
            'categories': categories,
            'count': len(categories)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting categories: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@firefly_bp.route('/summary', methods=['GET'])
def get_financial_summary():
    """Get financial summary and dashboard data"""
    try:
        summary = firefly_service.get_summary()
        
        return jsonify({
            'success': True,
            'summary': summary
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting financial summary: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@firefly_bp.route('/reports/monthly', methods=['GET'])
def get_monthly_report():
    """Get monthly financial report"""
    try:
        year = request.args.get('year', datetime.now().year)
        month = request.args.get('month', datetime.now().month)
        
        # Calculate date range for the month
        from datetime import datetime, timedelta
        start_date = f"{year}-{month:02d}-01"
        
        # Get last day of month
        if month == 12:
            next_month = datetime(int(year) + 1, 1, 1)
        else:
            next_month = datetime(int(year), int(month) + 1, 1)
        
        last_day = next_month - timedelta(days=1)
        end_date = last_day.strftime('%Y-%m-%d')
        
        # Get transactions for the month
        transactions = firefly_service.get_transactions(start_date, end_date, 1000)
        
        # Calculate monthly statistics
        income = sum(float(t.get('amount', 0)) for t in transactions if float(t.get('amount', 0)) > 0)
        expenses = sum(abs(float(t.get('amount', 0))) for t in transactions if float(t.get('amount', 0)) < 0)
        
        # Group by category
        categories = {}
        for transaction in transactions:
            category = transaction.get('category_name', 'Uncategorized')
            amount = float(transaction.get('amount', 0))
            
            if category not in categories:
                categories[category] = {'income': 0, 'expenses': 0, 'count': 0}
            
            if amount > 0:
                categories[category]['income'] += amount
            else:
                categories[category]['expenses'] += abs(amount)
            
            categories[category]['count'] += 1
        
        return jsonify({
            'success': True,
            'report': {
                'period': f"{year}-{month:02d}",
                'start_date': start_date,
                'end_date': end_date,
                'total_income': income,
                'total_expenses': expenses,
                'net_income': income - expenses,
                'transaction_count': len(transactions),
                'categories': categories,
                'transactions': transactions[:20]  # Latest 20 transactions
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting monthly report: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@firefly_bp.route('/analytics/spending', methods=['GET'])
def get_spending_analytics():
    """Get spending analytics and trends"""
    try:
        days = int(request.args.get('days', 30))
        
        from datetime import datetime, timedelta
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        transactions = firefly_service.get_transactions(
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d'),
            1000
        )
        
        # Analyze spending patterns
        daily_spending = {}
        category_spending = {}
        
        for transaction in transactions:
            amount = float(transaction.get('amount', 0))
            if amount < 0:  # Only expenses
                date = transaction.get('date', '')[:10]  # Get date part only
                category = transaction.get('category_name', 'Uncategorized')
                
                # Daily spending
                if date not in daily_spending:
                    daily_spending[date] = 0
                daily_spending[date] += abs(amount)
                
                # Category spending
                if category not in category_spending:
                    category_spending[category] = 0
                category_spending[category] += abs(amount)
        
        # Calculate averages
        total_spending = sum(daily_spending.values())
        avg_daily_spending = total_spending / max(len(daily_spending), 1)
        
        return jsonify({
            'success': True,
            'analytics': {
                'period_days': days,
                'total_spending': total_spending,
                'average_daily_spending': avg_daily_spending,
                'daily_spending': daily_spending,
                'category_spending': category_spending,
                'top_categories': sorted(
                    category_spending.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:10]
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting spending analytics: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
