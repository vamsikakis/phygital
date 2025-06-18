from flask import Blueprint, request, jsonify
import os
import json
import requests
from datetime import datetime
import logging
from db import get_db_session, DocumentOperation, Document, ExportLog, Download
from auth import login_required, admin_required, staff_required, get_user_from_token

# Initialize logger
logger = logging.getLogger(__name__)

# Initialize blueprint
doc_operations_bp = Blueprint('document_operations', __name__)

# Supabase function URL 
SUPABASE_URL = os.getenv('SUPABASE_URL')
EDGE_FUNCTION_URL = f"{SUPABASE_URL}/functions/v1"
SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')

# Document operations endpoints
@doc_operations_bp.route('/extract-text', methods=['POST'])
@login_required
def extract_text():
    """Extract text from a document"""
    try:
        data = request.json
        if not data or 'documentId' not in data:
            return jsonify({'error': 'Document ID is required'}), 400

        user = get_user_from_token(request)
        
        # Call Supabase Edge Function
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {SUPABASE_ANON_KEY}'
        }
        
        payload = {
            'operation': 'extract_text',
            'documentId': data['documentId'],
            'userId': user.id,
            'options': data.get('options', {})
        }
        
        response = requests.post(
            f"{EDGE_FUNCTION_URL}/document-operations",
            headers=headers,
            json=payload
        )
        
        if response.status_code != 200:
            logger.error(f"Error extracting text: {response.text}")
            return jsonify({'error': 'Failed to extract text'}), response.status_code
            
        # Log the operation in database
        with get_db_session() as session:
            operation = session.query(DocumentOperation).filter_by(
                document_id=data['documentId'],
                operation='extract_text',
                status='success'
            ).order_by(DocumentOperation.created_at.desc()).first()
            
            if not operation:
                operation = DocumentOperation(
                    document_id=data['documentId'],
                    operation='extract_text',
                    status='completed',
                    created_by=user.id,
                    metadata={'completed_at': datetime.utcnow().isoformat()}
                )
                session.add(operation)
                session.commit()
        
        return jsonify(response.json())
        
    except Exception as e:
        logger.error(f"Error in extract_text: {str(e)}")
        return jsonify({'error': str(e)}), 500

@doc_operations_bp.route('/generate-summary', methods=['POST'])
@login_required
def generate_summary():
    """Generate a summary for a document using OpenAI"""
    try:
        data = request.json
        if not data or 'documentId' not in data:
            return jsonify({'error': 'Document ID is required'}), 400

        user = get_user_from_token(request)
        
        # Call Supabase Edge Function
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {SUPABASE_ANON_KEY}'
        }
        
        payload = {
            'operation': 'generate_summary',
            'documentId': data['documentId'],
            'userId': user.id,
            'options': data.get('options', {})
        }
        
        response = requests.post(
            f"{EDGE_FUNCTION_URL}/document-operations",
            headers=headers,
            json=payload
        )
        
        if response.status_code != 200:
            logger.error(f"Error generating summary: {response.text}")
            return jsonify({'error': 'Failed to generate summary'}), response.status_code
            
        # Log the operation in database
        with get_db_session() as session:
            operation = session.query(DocumentOperation).filter_by(
                document_id=data['documentId'],
                operation='generate_summary',
                status='success'
            ).order_by(DocumentOperation.created_at.desc()).first()
            
            if not operation:
                operation = DocumentOperation(
                    document_id=data['documentId'],
                    operation='generate_summary',
                    status='completed',
                    created_by=user.id,
                    metadata={'completed_at': datetime.utcnow().isoformat()}
                )
                session.add(operation)
                session.commit()
        
        return jsonify(response.json())
        
    except Exception as e:
        logger.error(f"Error in generate_summary: {str(e)}")
        return jsonify({'error': str(e)}), 500

@doc_operations_bp.route('/convert-to-pdf', methods=['POST'])
@login_required
def convert_to_pdf():
    """Convert a document to PDF"""
    try:
        data = request.json
        if not data or 'documentId' not in data:
            return jsonify({'error': 'Document ID is required'}), 400

        user = get_user_from_token(request)
        
        # Call Supabase Edge Function
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {SUPABASE_ANON_KEY}'
        }
        
        payload = {
            'operation': 'convert_to_pdf',
            'documentId': data['documentId'],
            'userId': user.id,
            'options': data.get('options', {})
        }
        
        response = requests.post(
            f"{EDGE_FUNCTION_URL}/document-operations",
            headers=headers,
            json=payload
        )
        
        if response.status_code != 200:
            logger.error(f"Error converting to PDF: {response.text}")
            return jsonify({'error': 'Failed to convert document to PDF'}), response.status_code
            
        # Log the operation in database
        with get_db_session() as session:
            operation = DocumentOperation(
                document_id=data['documentId'],
                operation='convert_to_pdf',
                status='completed',
                created_by=user.id,
                metadata={
                    'completed_at': datetime.utcnow().isoformat(),
                    'result': response.json().get('result', {})
                }
            )
            session.add(operation)
            
            # Also log as an export
            export = ExportLog(
                source_id=data['documentId'],
                source_type='document',
                export_type='pdf',
                status='completed',
                created_by=user.id,
                file_path=response.json().get('result', {}).get('url', '')
            )
            session.add(export)
            session.commit()
        
        return jsonify(response.json())
        
    except Exception as e:
        logger.error(f"Error in convert_to_pdf: {str(e)}")
        return jsonify({'error': str(e)}), 500

@doc_operations_bp.route('/optimize-pdf', methods=['POST'])
@login_required
def optimize_pdf():
    """Optimize a PDF document"""
    try:
        data = request.json
        if not data or 'documentId' not in data:
            return jsonify({'error': 'Document ID is required'}), 400

        user = get_user_from_token(request)
        
        # Call Supabase Edge Function
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {SUPABASE_ANON_KEY}'
        }
        
        payload = {
            'operation': 'optimize_pdf',
            'documentId': data['documentId'],
            'userId': user.id,
            'options': data.get('options', {})
        }
        
        response = requests.post(
            f"{EDGE_FUNCTION_URL}/document-operations",
            headers=headers,
            json=payload
        )
        
        if response.status_code != 200:
            logger.error(f"Error optimizing PDF: {response.text}")
            return jsonify({'error': 'Failed to optimize PDF'}), response.status_code
            
        # Log the operation in database
        with get_db_session() as session:
            operation = DocumentOperation(
                document_id=data['documentId'],
                operation='optimize_pdf',
                status='completed',
                created_by=user.id,
                metadata={
                    'completed_at': datetime.utcnow().isoformat(),
                    'result': response.json().get('result', {})
                }
            )
            session.add(operation)
            session.commit()
        
        return jsonify(response.json())
        
    except Exception as e:
        logger.error(f"Error in optimize_pdf: {str(e)}")
        return jsonify({'error': str(e)}), 500

@doc_operations_bp.route('/export-pdf', methods=['POST'])
@login_required
def export_pdf():
    """Export a document as PDF"""
    try:
        data = request.json
        if not data or 'documentId' not in data:
            return jsonify({'error': 'Document ID is required'}), 400

        user = get_user_from_token(request)
        
        # First check if the document is already in PDF format
        with get_db_session() as session:
            document = session.query(Document).filter_by(id=data['documentId']).first()
            
            if not document:
                return jsonify({'error': 'Document not found'}), 404
                
            # If already PDF, just create an export log entry
            if document.file_type == 'application/pdf':
                export = ExportLog(
                    source_id=data['documentId'],
                    source_type='document',
                    export_type='pdf',
                    status='completed',
                    created_by=user.id,
                    file_path=document.file_path
                )
                session.add(export)
                session.commit()
                
                return jsonify({
                    'success': True,
                    'message': 'Document is already in PDF format',
                    'url': document.file_path
                })
                
        # If not PDF, convert it
        return convert_to_pdf()
        
    except Exception as e:
        logger.error(f"Error in export_pdf: {str(e)}")
        return jsonify({'error': str(e)}), 500

@doc_operations_bp.route('/downloads/<document_id>', methods=['POST'])
@login_required
def log_download(document_id):
    """Log a document download"""
    try:
        user = get_user_from_token(request)
        
        with get_db_session() as session:
            document = session.query(Document).filter_by(id=document_id).first()
            
            if not document:
                return jsonify({'error': 'Document not found'}), 404
                
            # Log the download
            download = Download(
                document_id=document_id,
                downloaded_by=user.id,
                download_date=datetime.utcnow()
            )
            session.add(download)
            session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Download logged successfully',
                'download_id': download.id
            })
            
    except Exception as e:
        logger.error(f"Error logging download: {str(e)}")
        return jsonify({'error': str(e)}), 500

@doc_operations_bp.route('/operations/history/<document_id>', methods=['GET'])
@login_required
def get_operations_history(document_id):
    """Get document operations history"""
    try:
        with get_db_session() as session:
            operations = session.query(DocumentOperation).filter_by(
                document_id=document_id
            ).order_by(DocumentOperation.created_at.desc()).all()
            
            result = [{
                'id': op.id,
                'operation': op.operation,
                'status': op.status,
                'created_at': op.created_at.isoformat(),
                'created_by': op.created_by,
                'metadata': op.metadata
            } for op in operations]
            
            return jsonify({
                'document_id': document_id,
                'operations': result
            })
            
    except Exception as e:
        logger.error(f"Error getting operations history: {str(e)}")
        return jsonify({'error': str(e)}), 500

@doc_operations_bp.route('/operations/statistics', methods=['GET'])
@staff_required
def get_operations_statistics():
    """Get document operations statistics for staff"""
    try:
        with get_db_session() as session:
            # Get count by operation type
            operations_by_type = {}
            for op in session.query(DocumentOperation.operation, 
                                    DocumentOperation.status, 
                                    DocumentOperation.id.count()
                                   ).group_by(DocumentOperation.operation, 
                                             DocumentOperation.status).all():
                op_type = op[0]
                status = op[1]
                count = op[2]
                
                if op_type not in operations_by_type:
                    operations_by_type[op_type] = {}
                    
                operations_by_type[op_type][status] = count
            
            # Get download statistics
            download_count = session.query(Download).count()
            
            # Get export statistics
            exports = session.query(ExportLog.export_type, 
                                   ExportLog.id.count()
                                  ).group_by(ExportLog.export_type).all()
            
            export_stats = {export_type: count for export_type, count in exports}
            
            return jsonify({
                'operations_by_type': operations_by_type,
                'download_count': download_count,
                'export_stats': export_stats
            })
            
    except Exception as e:
        logger.error(f"Error getting operations statistics: {str(e)}")
        return jsonify({'error': str(e)}), 500
