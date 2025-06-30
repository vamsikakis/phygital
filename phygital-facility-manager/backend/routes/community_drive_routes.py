"""
Community Drive API Routes
Provides REST endpoints for community document storage and download
"""

from flask import Blueprint, request, jsonify, send_file, current_app
import os
import tempfile
from services.community_drive_service import community_drive_service
from services.openai_assistant_service import openai_assistant_service

# Create blueprint
community_drive_bp = Blueprint('community_drive', __name__)

@community_drive_bp.route('/documents', methods=['GET'])
def list_community_documents():
    """List all documents in the community drive"""
    try:
        category = request.args.get('category')
        documents = community_drive_service.list_documents(category)
        
        return jsonify({
            'success': True,
            'documents': documents,
            'count': len(documents)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error listing community documents: {e}")
        return jsonify({'error': str(e)}), 500

@community_drive_bp.route('/documents/<doc_id>/download', methods=['GET'])
def download_community_document(doc_id):
    """Download a document from the community drive"""
    try:
        file_path = community_drive_service.get_file_path(doc_id)
        
        if not file_path:
            return jsonify({'error': 'Document not found in community drive'}), 404
        
        document = community_drive_service.get_document(doc_id)
        filename = document.get('filename', 'document')
        mime_type = document.get('mime_type', 'application/octet-stream')
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype=mime_type
        )
        
    except Exception as e:
        current_app.logger.error(f"Error downloading community document {doc_id}: {e}")
        return jsonify({'error': str(e)}), 500

@community_drive_bp.route('/documents/upload', methods=['POST'])
def upload_to_community_drive():
    """Upload a document to the community drive"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Get additional metadata
        category = request.form.get('category', 'general')
        description = request.form.get('description', '')
        
        # Save file temporarily
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        file.save(temp_file.name)
        temp_file.close()
        
        try:
            # Store in community drive
            document_info = community_drive_service.store_document(
                file_path=temp_file.name,
                original_filename=file.filename,
                category=category,
                description=description
            )
            
            # Also upload to OpenAI for AI assistant access
            try:
                openai_result = openai_assistant_service.upload_file_to_vector_store(
                    temp_file.name, 
                    file.filename
                )
                document_info['openai_file_id'] = openai_result.get('file_id')
            except Exception as openai_error:
                current_app.logger.warning(f"OpenAI upload failed: {openai_error}")
                # Continue without OpenAI integration
            
            return jsonify({
                'success': True,
                'message': 'Document uploaded to community drive',
                'document': document_info
            }), 201
            
        finally:
            # Clean up temp file
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)
        
    except Exception as e:
        current_app.logger.error(f"Error uploading to community drive: {e}")
        return jsonify({'error': str(e)}), 500

@community_drive_bp.route('/documents/<doc_id>', methods=['DELETE'])
def delete_community_document(doc_id):
    """Delete a document from the community drive"""
    try:
        success = community_drive_service.delete_document(doc_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Document deleted from community drive'
            }), 200
        else:
            return jsonify({'error': 'Document not found'}), 404
            
    except Exception as e:
        current_app.logger.error(f"Error deleting community document {doc_id}: {e}")
        return jsonify({'error': str(e)}), 500

@community_drive_bp.route('/stats', methods=['GET'])
def get_community_drive_stats():
    """Get community drive storage statistics"""
    try:
        stats = community_drive_service.get_storage_stats()
        return jsonify({
            'success': True,
            'stats': stats
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting community drive stats: {e}")
        return jsonify({'error': str(e)}), 500

@community_drive_bp.route('/sync-from-openai', methods=['POST'])
def sync_from_openai():
    """Sync documents from OpenAI to community drive (admin function)"""
    try:
        # This would require downloading from OpenAI (which we can't do)
        # But we can create placeholder entries for existing OpenAI files
        
        openai_files = openai_assistant_service.list_files()
        synced_count = 0
        
        for file_info in openai_files:
            file_id = file_info.get('file_id')
            filename = file_info.get('filename', 'Unknown')
            
            # Check if already in community drive
            existing_docs = community_drive_service.list_documents()
            already_exists = any(
                doc.get('openai_file_id') == file_id 
                for doc in existing_docs
            )
            
            if not already_exists:
                # Create a placeholder entry (without actual file)
                doc_info = {
                    'id': f"openai_{file_id}",
                    'filename': filename,
                    'category': community_drive_service.categorize_file(filename),
                    'description': f"Document from OpenAI: {filename}",
                    'file_size': file_info.get('bytes', 0),
                    'openai_file_id': file_id,
                    'uploaded_at': file_info.get('created_at', ''),
                    'downloadable': False,  # Can't download from OpenAI
                    'source': 'openai'
                }
                
                metadata = community_drive_service.load_metadata()
                metadata[doc_info['id']] = doc_info
                community_drive_service.save_metadata(metadata)
                synced_count += 1
        
        return jsonify({
            'success': True,
            'message': f'Synced {synced_count} documents from OpenAI',
            'synced_count': synced_count
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error syncing from OpenAI: {e}")
        return jsonify({'error': str(e)}), 500
