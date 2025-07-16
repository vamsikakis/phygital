from flask import Blueprint, request, jsonify, current_app
import os
import json
import uuid
from datetime import datetime
from dotenv import load_dotenv

# Temporarily commented out missing models to allow server startup
# from db import get_db_session, User, FinancialReport, FinancialDetail
try:
    from db import get_db_session, User
    # FinancialReport, FinancialDetail models need to be added to db.py
except ImportError as e:
    print(f"Warning: Database models not fully available: {e}")
    get_db_session = None
    User = None
from auth import login_required, admin_required, staff_required, management_required, get_current_user
# Temporarily commented out missing function to allow server startup
# from integrations.document_exports import generate_financial_report_pdf
try:
    from integrations.document_exports import generate_financial_report_pdf
except ImportError as e:
    print(f"Warning: Document export function not available: {e}")
    generate_financial_report_pdf = None

# Create blueprint
financial_bp = Blueprint('financial', __name__)

@financial_bp.route('/reports', methods=['GET'])
@login_required
def get_financial_reports():
    """
    Get all financial reports
    Regular users can only see published reports
    Staff and admins can see all reports
    """
    try:
        session = get_db_session()
        current_user = get_current_user()
        
        query = session.query(FinancialReport)
        
        # Filter reports based on user role
        if current_user.role not in ['admin', 'staff']:
            query = query.filter(FinancialReport.status == 'published')
            
        # Apply filters if provided
        report_type = request.args.get('type')
        if report_type:
            query = query.filter(FinancialReport.report_type == report_type)
            
        start_date = request.args.get('start_date')
        if start_date:
            query = query.filter(FinancialReport.period_end >= start_date)
            
        end_date = request.args.get('end_date')
        if end_date:
            query = query.filter(FinancialReport.period_start <= end_date)
            
        status = request.args.get('status')
        if status and current_user.role in ['admin', 'staff']:
            query = query.filter(FinancialReport.status == status)
            
        # Order by date descending
        query = query.order_by(FinancialReport.period_end.desc())
        
        reports = query.all()
        
        result = []
        for report in reports:
            result.append({
                'id': report.id,
                'title': report.title,
                'report_type': report.report_type,
                'period_start': report.period_start.isoformat() if report.period_start else None,
                'period_end': report.period_end.isoformat() if report.period_end else None,
                'description': report.description,
                'document_id': report.document_id,
                'status': report.status,
                'created_at': report.created_at.isoformat() if report.created_at else None,
                'updated_at': report.updated_at.isoformat() if report.updated_at else None
            })
            
        return jsonify({
            'reports': result
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting financial reports: {str(e)}")
        return jsonify({'error': str(e)}), 500

@financial_bp.route('/reports/<report_id>', methods=['GET'])
@login_required
def get_financial_report(report_id):
    """
    Get a specific financial report with its details
    Regular users can only see published reports
    Staff and admins can see all reports
    """
    try:
        session = get_db_session()
        current_user = get_current_user()
        
        query = session.query(FinancialReport)
        
        # Filter report based on user role and report id
        if current_user.role not in ['admin', 'management', 'fm']:
            query = query.filter(FinancialReport.status == 'published')
            
        report = query.filter(FinancialReport.id == report_id).first()
        
        if not report:
            return jsonify({'error': 'Report not found'}), 404
            
        # Get report details
        details_query = session.query(FinancialDetail).filter(FinancialDetail.report_id == report_id)
        details = details_query.all()
        
        details_data = []
        for detail in details:
            details_data.append({
                'id': detail.id,
                'category': detail.category,
                'subcategory': detail.subcategory,
                'description': detail.description,
                'amount': float(detail.amount),
                'transaction_date': detail.transaction_date.isoformat() if detail.transaction_date else None
            })
            
        report_data = {
            'id': report.id,
            'title': report.title,
            'report_type': report.report_type,
            'period_start': report.period_start.isoformat() if report.period_start else None,
            'period_end': report.period_end.isoformat() if report.period_end else None,
            'description': report.description,
            'document_id': report.document_id,
            'status': report.status,
            'created_at': report.created_at.isoformat() if report.created_at else None,
            'updated_at': report.updated_at.isoformat() if report.updated_at else None,
            'details': details_data
        }
            
        return jsonify({
            'report': report_data
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting financial report: {str(e)}")
        return jsonify({'error': str(e)}), 500

@financial_bp.route('/reports', methods=['POST'])
@staff_required
def create_financial_report():
    """
    Create a new financial report (staff/admin only)
    """
    try:
        data = request.json
        current_user = get_current_user()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        required_fields = ['title', 'report_type']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
                
        session = get_db_session()
        
        # Create new report
        new_report = FinancialReport(
            id=str(uuid.uuid4()),
            title=data['title'],
            report_type=data['report_type'],
            period_start=data.get('period_start'),
            period_end=data.get('period_end'),
            description=data.get('description'),
            status=data.get('status', 'draft'),
            created_by=current_user.id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        session.add(new_report)
        
        # Add report details if provided
        if 'details' in data and isinstance(data['details'], list):
            for detail_data in data['details']:
                new_detail = FinancialDetail(
                    id=str(uuid.uuid4()),
                    report_id=new_report.id,
                    category=detail_data.get('category'),
                    subcategory=detail_data.get('subcategory'),
                    description=detail_data.get('description'),
                    amount=detail_data.get('amount', 0),
                    transaction_date=detail_data.get('transaction_date'),
                    created_at=datetime.utcnow()
                )
                session.add(new_detail)
                
        session.commit()
        
        return jsonify({
            'message': 'Financial report created successfully',
            'report_id': new_report.id
        })
        
    except Exception as e:
        current_app.logger.error(f"Error creating financial report: {str(e)}")
        return jsonify({'error': str(e)}), 500

@financial_bp.route('/reports/<report_id>', methods=['PUT'])
@staff_required
def update_financial_report(report_id):
    """
    Update a financial report (staff/admin only)
    """
    try:
        data = request.json
        current_user = get_current_user()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        session = get_db_session()
        report = session.query(FinancialReport).filter(FinancialReport.id == report_id).first()
        
        if not report:
            return jsonify({'error': 'Report not found'}), 404
            
        # Update report fields
        if 'title' in data:
            report.title = data['title']
        if 'report_type' in data:
            report.report_type = data['report_type']
        if 'period_start' in data:
            report.period_start = data['period_start']
        if 'period_end' in data:
            report.period_end = data['period_end']
        if 'description' in data:
            report.description = data['description']
        if 'status' in data:
            report.status = data['status']
        if 'document_id' in data:
            report.document_id = data['document_id']
            
        report.updated_at = datetime.utcnow()
        
        # Update report details if provided
        if 'details' in data and isinstance(data['details'], list):
            # Handle details - first approach: delete and recreate
            if data.get('replace_details', False):
                session.query(FinancialDetail).filter(FinancialDetail.report_id == report_id).delete()
                
                # Create new details
                for detail_data in data['details']:
                    new_detail = FinancialDetail(
                        id=str(uuid.uuid4()),
                        report_id=report_id,
                        category=detail_data.get('category'),
                        subcategory=detail_data.get('subcategory'),
                        description=detail_data.get('description'),
                        amount=detail_data.get('amount', 0),
                        transaction_date=detail_data.get('transaction_date'),
                        created_at=datetime.utcnow()
                    )
                    session.add(new_detail)
            # Second approach: update existing, add new ones
            else:
                for detail_data in data['details']:
                    if 'id' in detail_data:
                        # Update existing detail
                        detail = session.query(FinancialDetail).filter(
                            FinancialDetail.id == detail_data['id'],
                            FinancialDetail.report_id == report_id
                        ).first()
                        
                        if detail:
                            if 'category' in detail_data:
                                detail.category = detail_data['category']
                            if 'subcategory' in detail_data:
                                detail.subcategory = detail_data['subcategory']
                            if 'description' in detail_data:
                                detail.description = detail_data['description']
                            if 'amount' in detail_data:
                                detail.amount = detail_data['amount']
                            if 'transaction_date' in detail_data:
                                detail.transaction_date = detail_data['transaction_date']
                    else:
                        # Create new detail
                        new_detail = FinancialDetail(
                            id=str(uuid.uuid4()),
                            report_id=report_id,
                            category=detail_data.get('category'),
                            subcategory=detail_data.get('subcategory'),
                            description=detail_data.get('description'),
                            amount=detail_data.get('amount', 0),
                            transaction_date=detail_data.get('transaction_date'),
                            created_at=datetime.utcnow()
                        )
                        session.add(new_detail)
                
        session.commit()
        
        return jsonify({
            'message': 'Financial report updated successfully',
            'report_id': report.id
        })
        
    except Exception as e:
        current_app.logger.error(f"Error updating financial report: {str(e)}")
        return jsonify({'error': str(e)}), 500

@financial_bp.route('/reports/<report_id>/details', methods=['POST'])
@staff_required
def add_financial_detail(report_id):
    """
    Add a detail to a financial report (staff/admin only)
    """
    try:
        data = request.json
        current_user = get_current_user()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        session = get_db_session()
        report = session.query(FinancialReport).filter(FinancialReport.id == report_id).first()
        
        if not report:
            return jsonify({'error': 'Report not found'}), 404
            
        # Create new detail
        new_detail = FinancialDetail(
            id=str(uuid.uuid4()),
            report_id=report_id,
            category=data.get('category'),
            subcategory=data.get('subcategory'),
            description=data.get('description'),
            amount=data.get('amount', 0),
            transaction_date=data.get('transaction_date'),
            created_at=datetime.utcnow()
        )
        
        session.add(new_detail)
        session.commit()
        
        return jsonify({
            'message': 'Financial detail added successfully',
            'detail_id': new_detail.id
        })
        
    except Exception as e:
        current_app.logger.error(f"Error adding financial detail: {str(e)}")
        return jsonify({'error': str(e)}), 500

@financial_bp.route('/reports/details/<detail_id>', methods=['DELETE'])
@staff_required
def delete_financial_detail(detail_id):
    """
    Delete a financial detail (staff/admin only)
    """
    try:
        current_user = get_current_user()
        session = get_db_session()
        
        detail = session.query(FinancialDetail).filter(FinancialDetail.id == detail_id).first()
        
        if not detail:
            return jsonify({'error': 'Detail not found'}), 404
            
        session.delete(detail)
        session.commit()
        
        return jsonify({
            'message': 'Financial detail deleted successfully'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error deleting financial detail: {str(e)}")
        return jsonify({'error': str(e)}), 500

@financial_bp.route('/reports/<report_id>', methods=['DELETE'])
@admin_required
def delete_financial_report(report_id):
    """
    Delete a financial report (admin only)
    """
    try:
        current_user = get_current_user()
        session = get_db_session()
        
        report = session.query(FinancialReport).filter(FinancialReport.id == report_id).first()
        
        if not report:
            return jsonify({'error': 'Report not found'}), 404
            
        # Delete related details first (should be handled by cascade, but being explicit)
        session.query(FinancialDetail).filter(FinancialDetail.report_id == report_id).delete()
        
        # Delete the report
        session.delete(report)
        session.commit()
        
        return jsonify({
            'message': 'Financial report deleted successfully'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error deleting financial report: {str(e)}")
        return jsonify({'error': str(e)}), 500

@financial_bp.route('/reports/<report_id>/publish', methods=['POST'])
@staff_required
def publish_financial_report(report_id):
    """
    Publish a financial report (staff/admin only)
    """
    try:
        current_user = get_current_user()
        session = get_db_session()
        
        report = session.query(FinancialReport).filter(FinancialReport.id == report_id).first()
        
        if not report:
            return jsonify({'error': 'Report not found'}), 404
            
        # Update report status
        report.status = 'published'
        report.updated_at = datetime.utcnow()
        
        session.commit()
        
        return jsonify({
            'message': 'Financial report published successfully'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error publishing financial report: {str(e)}")
        return jsonify({'error': str(e)}), 500

@financial_bp.route('/reports/<report_id>/generate-pdf', methods=['POST'])
@staff_required
def generate_report_pdf(report_id):
    """
    Generate a PDF for a financial report (staff/admin only)
    """
    try:
        current_user = get_current_user()
        session = get_db_session()
        
        report = session.query(FinancialReport).filter(FinancialReport.id == report_id).first()
        
        if not report:
            return jsonify({'error': 'Report not found'}), 404
            
        # Get report details
        details = session.query(FinancialDetail).filter(FinancialDetail.report_id == report_id).all()
        
        # Format data for PDF generation
        report_data = {
            'id': report.id,
            'title': report.title,
            'report_type': report.report_type,
            'period_start': report.period_start.isoformat() if report.period_start else None,
            'period_end': report.period_end.isoformat() if report.period_end else None,
            'description': report.description,
            'details': [
                {
                    'category': detail.category,
                    'subcategory': detail.subcategory,
                    'description': detail.description,
                    'amount': float(detail.amount),
                    'transaction_date': detail.transaction_date.isoformat() if detail.transaction_date else None
                } for detail in details
            ]
        }
        
        # Generate PDF using the document exports module
        result = generate_financial_report_pdf(report_data, current_user.id)
        
        if not result.get('success'):
            return jsonify({'error': result.get('error', 'Failed to generate PDF')}), 500
            
        # Update report with document ID if PDF was created
        if result.get('document_id'):
            report.document_id = result['document_id']
            report.updated_at = datetime.utcnow()
            session.commit()
        
        return jsonify({
            'message': 'Financial report PDF generated successfully',
            'document_id': result.get('document_id'),
            'download_url': result.get('download_url')
        })
        
    except Exception as e:
        current_app.logger.error(f"Error generating financial report PDF: {str(e)}")
        return jsonify({'error': str(e)}), 500

@financial_bp.route('/reports/<report_id>/analytics', methods=['GET'])
@login_required
def get_financial_analytics(report_id):
    """
    Get financial analytics for a report
    """
    try:
        current_user = get_current_user()
        session = get_db_session()
        
        query = session.query(FinancialReport)
        
        # Filter report based on user role and report id
        if current_user.role not in ['admin', 'staff']:
            query = query.filter(FinancialReport.status == 'published')
            
        report = query.filter(FinancialReport.id == report_id).first()
        
        if not report:
            return jsonify({'error': 'Report not found'}), 404
            
        # Get report details
        details = session.query(FinancialDetail).filter(FinancialDetail.report_id == report_id).all()
        
        # Calculate analytics
        total_income = sum(float(detail.amount) for detail in details 
                         if detail.category == 'income')
        total_expense = sum(float(detail.amount) for detail in details 
                          if detail.category == 'expense')
        total_assets = sum(float(detail.amount) for detail in details 
                         if detail.category == 'asset')
        total_liabilities = sum(float(detail.amount) for detail in details 
                              if detail.category == 'liability')
        
        # Category breakdown
        category_breakdown = {}
        for detail in details:
            if detail.category not in category_breakdown:
                category_breakdown[detail.category] = 0
            category_breakdown[detail.category] += float(detail.amount)
        
        # Subcategory breakdown
        subcategory_breakdown = {}
        for detail in details:
            key = f"{detail.category}:{detail.subcategory}" if detail.subcategory else detail.category
            if key not in subcategory_breakdown:
                subcategory_breakdown[key] = 0
            subcategory_breakdown[key] += float(detail.amount)
        
        # Calculate net income/loss
        net_income = total_income - total_expense
        
        return jsonify({
            'analytics': {
                'total_income': total_income,
                'total_expense': total_expense,
                'net_income': net_income,
                'total_assets': total_assets,
                'total_liabilities': total_liabilities,
                'category_breakdown': category_breakdown,
                'subcategory_breakdown': subcategory_breakdown
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting financial analytics: {str(e)}")
        return jsonify({'error': str(e)}), 500
