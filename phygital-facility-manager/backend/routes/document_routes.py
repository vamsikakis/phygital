from flask import Blueprint, request, jsonify, current_app
import os
import uuid
from datetime import datetime
import io

from integrations.storage import (
    upload_document, 
    download_file, 
    get_download_url,
    list_files,
    record_download
)
from integrations.document_exports import DocumentExporter
from db import get_db_session
from auth import get_current_user, admin_required

# Create blueprint
documents_bp = Blueprint('documents', __name__)
document_exporter = DocumentExporter()

@documents_bp.route('', methods=['GET'])
def get_documents():
    """Get all documents from OpenAI Vector Store"""
    try:
        # Use OpenAI Assistant service to list files
        from services.openai_assistant_service import openai_assistant_service
        
        # Get files from OpenAI Vector Store
        files_list = openai_assistant_service.list_files()
        
        # Transform the files into document format expected by frontend
        documents = []
        for file_info in files_list:
            document = {
                'id': file_info.get('file_id', ''),
                'title': file_info.get('filename', 'Unknown'),
                'filename': file_info.get('filename', ''),
                'category': 'general',  # Default category since OpenAI doesn't store this
                'description': f"Document uploaded to vector store",
                'created_at': file_info.get('created_at', ''),
                'file_id': file_info.get('file_id', ''),
                'status': 'uploaded',
                'meta_data': {
                    'size': file_info.get('bytes', 0),
                    'purpose': file_info.get('purpose', 'assistants')
                }
            }
            documents.append(document)
        
        result = {
            'documents': documents,
            'total': len(documents),
            'page': 1,
            'per_page': len(documents)
        }
        
        current_app.logger.info(f"Retrieved {len(documents)} documents from OpenAI Vector Store")
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"Error fetching documents from OpenAI Vector Store: {str(e)}")
        return jsonify({'error': str(e)}), 500

@documents_bp.route('/<document_id>', methods=['GET'])
def get_document(document_id):
    """Get a single document by ID"""
    try:
        from db import Document
        session = get_db_session()
        document = session.query(Document).filter(Document.id == document_id).first()
        
        if not document:
            return jsonify({'error': 'Document not found'}), 404
            
        result = {
            'id': document.id,
            'title': document.title,
            'description': document.description,
            'category': document.category,
            'file_url': document.file_url,
            'created_at': document.created_at.isoformat() if document.created_at else None,
            'last_updated': document.last_updated.isoformat() if document.last_updated else None,
            'summary': document.summary,
            'metadata': document.metadata
        }
        
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"Error fetching document {document_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@documents_bp.route('', methods=['POST'])
def create_document():
    """Upload a new document to OpenAI Vector Store"""
    try:
        # Check if file is included in the request
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
            
        file = request.files['file']
        title = request.form.get('title', file.filename)
        description = request.form.get('description', '')
        category = request.form.get('category', 'general')
        
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        # Use OpenAI Assistant service to upload file
        try:
            from services.openai_assistant_service import openai_assistant_service
            from services.ocr_service import ocr_service
            import tempfile
            import os
            import uuid
            from datetime import datetime
            
            # Save file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as temp_file:
                file.save(temp_file.name)
                temp_path = temp_file.name
            
            # Initialize OCR result
            ocr_result = None
            extracted_text = ""
            
            # Check if file supports OCR and process it
            if ocr_service.is_ocr_supported_file(temp_path):
                current_app.logger.info(f"Starting OCR processing for file: {file.filename}")
                ocr_result = ocr_service.extract_text_from_file(temp_path)
                
                if ocr_result.get('success', False):
                    extracted_text = ocr_result.get('text', '')
                    current_app.logger.info(f"OCR completed successfully. Extracted {len(extracted_text)} characters from {file.filename}")
                else:
                    current_app.logger.warning(f"OCR failed for {file.filename}: {ocr_result.get('error', 'Unknown error')}")
            else:
                current_app.logger.info(f"File {file.filename} does not support OCR processing")
            
            # If we have extracted text, create an enhanced text file for better vector store indexing
            enhanced_content_path = None
            if extracted_text.strip():
                # Create a text file with the original filename and extracted content
                enhanced_content_path = temp_path + "_enhanced.txt"
                with open(enhanced_content_path, 'w', encoding='utf-8') as enhanced_file:
                    enhanced_file.write(f"Document: {file.filename}\n")
                    enhanced_file.write(f"Title: {title}\n")
                    if description:
                        enhanced_file.write(f"Description: {description}\n")
                    enhanced_file.write(f"Category: {category}\n")
                    enhanced_file.write(f"\n--- EXTRACTED CONTENT ---\n\n")
                    enhanced_file.write(extracted_text)
                
                # Upload the enhanced text file to vector store for better searchability
                enhanced_filename = f"{os.path.splitext(file.filename)[0]}_content.txt"
                result = openai_assistant_service.upload_file_to_vector_store(enhanced_content_path, enhanced_filename)
                
                # Clean up enhanced content file
                os.remove(enhanced_content_path)
                
                current_app.logger.info(f"Uploaded enhanced text content for {file.filename} to vector store")
            else:
                # Upload original file to OpenAI Vector Store
                result = openai_assistant_service.upload_file_to_vector_store(temp_path, file.filename)
            
            # Clean up temp file
            os.remove(temp_path)
            
            # Create document metadata with OCR information
            document_id = str(uuid.uuid4())
            document_metadata = {
                'id': document_id,
                'title': title,
                'description': description,
                'category': category,
                'filename': file.filename,
                'file_id': result.get('file_id'),
                'created_at': datetime.now().isoformat(),
                'status': 'uploaded',
                'ocr_processed': ocr_result is not None,
                'text_extracted': bool(extracted_text.strip()),
                'ocr_metadata': {
                    'success': ocr_result.get('success', False) if ocr_result else False,
                    'confidence': ocr_result.get('confidence', 0) if ocr_result else 0,
                    'word_count': ocr_result.get('word_count', 0) if ocr_result else 0,
                    'character_count': ocr_result.get('character_count', 0) if ocr_result else 0,
                    'pages_processed': ocr_result.get('pages_processed', 0) if ocr_result else 0,
                    'error': ocr_result.get('error') if ocr_result and not ocr_result.get('success') else None
                }
            }
            
            current_app.logger.info(f"Document uploaded successfully with OCR processing: {document_metadata}")
            
            return jsonify(document_metadata), 201
            
        except Exception as e:
            current_app.logger.error(f"Error uploading to OpenAI Vector Store: {str(e)}")
            return jsonify({'error': f'Failed to upload to vector store: {str(e)}'}), 500
        
    except Exception as e:
        current_app.logger.error(f"Error creating document: {str(e)}")
        return jsonify({'error': str(e)}), 500

@documents_bp.route('/<document_id>', methods=['PUT'])
@admin_required
def update_document(document_id):
    """Update document metadata"""
    try:
        data = request.json
        
        if not data:
            return jsonify({'error': 'No update data provided'}), 400
            
        from db import Document
        session = get_db_session()
        document = session.query(Document).filter(Document.id == document_id).first()
        
        if not document:
            return jsonify({'error': 'Document not found'}), 404
            
        # Update fields
        if 'title' in data:
            document.title = data['title']
        if 'description' in data:
            document.description = data['description']
        if 'category' in data:
            document.category = data['category']
        if 'metadata' in data:
            document.metadata = data['metadata']
        
        document.last_updated = datetime.now()
        session.commit()
        
        result = {
            'id': document.id,
            'title': document.title,
            'description': document.description,
            'category': document.category,
            'file_url': document.file_url,
            'created_at': document.created_at.isoformat() if document.created_at else None,
            'last_updated': document.last_updated.isoformat() if document.last_updated else None,
            'summary': document.summary,
            'metadata': document.metadata
        }
        
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"Error updating document {document_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@documents_bp.route('/<document_id>', methods=['DELETE'])
@admin_required
def delete_document(document_id):
    """Delete a document"""
    try:
        from db import Document
        session = get_db_session()
        document = session.query(Document).filter(Document.id == document_id).first()
        
        if not document:
            return jsonify({'error': 'Document not found'}), 404
            
        # Delete file from storage
        try:
            from integrations.storage import delete_file
            storage_path = document.storage_path
            if storage_path:
                delete_file('documents', storage_path)
        except Exception as e:
            current_app.logger.warning(f"Error deleting document file: {str(e)}")
        
        # Delete document record
        session.delete(document)
        session.commit()
        
        return jsonify({'success': True, 'message': 'Document deleted successfully'})
        
    except Exception as e:
        current_app.logger.error(f"Error deleting document {document_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@documents_bp.route('/<document_id>/download', methods=['GET'])
def download_document(document_id):
    """Get a download URL for a document"""
    try:
        # Get current user for tracking
        current_user = get_current_user()
        user_id = current_user.id if current_user else None
        
        # Get download URL
        download_url, document = document_exporter.download_original_document(document_id, user_id)
        
        return jsonify({
            'download_url': download_url,
            'document': {
                'id': document['id'],
                'title': document['title'],
                'category': document['category'],
                'file_url': document['file_url']
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error generating download URL for document {document_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@documents_bp.route('/<document_id>/pdf', methods=['GET'])
def generate_pdf(document_id):
    """Generate a PDF version of a document"""
    try:
        # Get current user for tracking
        current_user = get_current_user()
        user_id = current_user.id if current_user else None
        
        # Get template option
        template = request.args.get('template', 'default')
        
        # Generate PDF
        result = document_exporter.generate_pdf(
            document_id=document_id,
            template=template,
            user_id=user_id
        )
        
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"Error generating PDF for document {document_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500
        
@documents_bp.route('/<document_id>/convert', methods=['GET'])
def convert_document(document_id):
    """Convert a document to another format"""
    try:
        # Get current user for tracking
        current_user = get_current_user()
        user_id = current_user.id if current_user else None
        
        # Get format option
        target_format = request.args.get('format', 'pdf')
        
        # Convert document
        result = document_exporter.convert_document(
            document_id=document_id,
            target_format=target_format,
            user_id=user_id
        )
        
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"Error converting document {document_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500
        
@documents_bp.route('/<document_id>/text', methods=['GET'])
def extract_text(document_id):
    """Extract text from a document"""
    try:
        # Get current user for tracking
        current_user = get_current_user()
        user_id = current_user.id if current_user else None
        
        # Extract text
        result = document_exporter.extract_text(
            document_id=document_id,
            user_id=user_id
        )
        
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"Error extracting text from document {document_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500
        
@documents_bp.route('/<document_id>/summary', methods=['GET'])
def generate_summary(document_id):
    """Generate a summary of a document using AI"""
    try:
        # Get current user for tracking
        current_user = get_current_user()
        user_id = current_user.id if current_user else None
        
        # Generate summary
        result = document_exporter.generate_document_summary(
            document_id=document_id,
            user_id=user_id
        )
        
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"Error generating summary for document {document_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500
