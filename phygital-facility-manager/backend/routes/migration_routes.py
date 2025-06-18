from flask import Blueprint, request, jsonify, current_app
import os
import json
from datetime import datetime

from services.migration_service import migration_service
from services.openai_assistant_service import openai_assistant_service
from auth import get_current_user, admin_required

# Create blueprint
migration_bp = Blueprint('migration', __name__)

@migration_bp.route('/weaviate-to-openai', methods=['POST'])
@admin_required
def migrate_from_weaviate():
    """
    Migrate documents from Weaviate to OpenAI Vector Store
    Expects a JSON array of Weaviate documents
    """
    try:
        data = request.json
        
        if not data or not isinstance(data, list):
            return jsonify({'error': 'Invalid data format. Expected array of documents.'}), 400
            
        # Ensure OpenAI Assistant is initialized
        if not openai_assistant_service.isInitialized:
            openai_assistant_service.initialize()
            
        # Perform migration
        results = migration_service.migrate_documents_from_weaviate(data)
        
        # Count successes and failures
        successes = sum(1 for doc in results if doc['status'] == 'migrated')
        failures = sum(1 for doc in results if doc['status'] == 'failed')
        
        return jsonify({
            'message': f'Migration completed with {successes} successes and {failures} failures',
            'results': results
        })
        
    except Exception as e:
        current_app.logger.error(f"Error during migration: {str(e)}")
        return jsonify({'error': str(e)}), 500

@migration_bp.route('/file', methods=['POST'])
@admin_required
def migrate_file():
    """
    Migrate a single file to OpenAI Vector Store
    """
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
            
        # Get metadata
        metadata = {
            'title': request.form.get('title', file.filename),
            'category': request.form.get('category', 'general'),
            'tags': request.form.get('tags', '').split(',') if request.form.get('tags') else []
        }
        
        # Save file temporarily
        temp_path = f"/tmp/migration_{file.filename}"
        file.save(temp_path)
        
        # Ensure OpenAI Assistant is initialized
        if not openai_assistant_service._is_initialized:
            openai_assistant_service.initialize()
            
        # Perform migration
        result = migration_service.migrate_document_from_file(temp_path, metadata)
        
        # Clean up temp file
        os.remove(temp_path)
        
        if result['status'] == 'migrated':
            return jsonify({
                'message': f'Successfully migrated file {file.filename}',
                'result': result
            })
        else:
            return jsonify({
                'error': f'Failed to migrate file: {result.get("error", "Unknown error")}',
                'result': result
            }), 500
        
    except Exception as e:
        current_app.logger.error(f"Error during file migration: {str(e)}")
        return jsonify({'error': str(e)}), 500

@migration_bp.route('/status', methods=['GET'])
@admin_required
def migration_status():
    """
    Get migration status and document counts
    """
    try:
        # Get document counts
        counts = migration_service.compare_document_counts()
        
        # If weaviate_count is provided as a query parameter, use it
        weaviate_count = request.args.get('weaviate_count')
        if weaviate_count and weaviate_count.isdigit():
            counts['weaviate_count'] = int(weaviate_count)
        
        return jsonify({
            'status': 'Migration service operational',
            'document_counts': counts,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting migration status: {str(e)}")
        return jsonify({'error': str(e)}), 500
