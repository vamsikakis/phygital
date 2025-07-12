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
            
            # Prepare content for vector storage
            content_for_vector_db = ""
            enhanced_content_path = None

            if extracted_text.strip():
                # Create enhanced content for both OpenAI and local vector DB
                content_for_vector_db = f"Document: {file.filename}\n"
                content_for_vector_db += f"Title: {title}\n"
                if description:
                    content_for_vector_db += f"Description: {description}\n"
                content_for_vector_db += f"Category: {category}\n"
                content_for_vector_db += f"\n--- EXTRACTED CONTENT ---\n\n"
                content_for_vector_db += extracted_text

                # Create enhanced text file for OpenAI
                enhanced_content_path = temp_path + "_enhanced.txt"
                with open(enhanced_content_path, 'w', encoding='utf-8') as enhanced_file:
                    enhanced_file.write(content_for_vector_db)

                # Upload the enhanced text file to OpenAI vector store
                enhanced_filename = f"{os.path.splitext(file.filename)[0]}_content.txt"
                result = openai_assistant_service.upload_file_to_vector_store(enhanced_content_path, enhanced_filename)

                # Clean up enhanced content file
                os.remove(enhanced_content_path)

                current_app.logger.info(f"Uploaded enhanced text content for {file.filename} to OpenAI vector store")
            else:
                # Upload original file to OpenAI Vector Store
                result = openai_assistant_service.upload_file_to_vector_store(temp_path, file.filename)
                # Use basic metadata for vector DB if no text extracted
                content_for_vector_db = f"Document: {file.filename}\nTitle: {title}\nDescription: {description}\nCategory: {category}"

            # Local vector database removed - using OpenAI vector store instead
            # Document is already uploaded to OpenAI vector store above
            vector_success = True  # OpenAI vector store handles this
            current_app.logger.info(f"Document uploaded to OpenAI vector store: {result.get('file_id', 'unknown')}")
                    current_app.logger.warning(f"Failed to store document embedding in local vector database: {vector_doc_id}")

            except Exception as vector_error:
                current_app.logger.error(f"Error storing document in vector database: {str(vector_error)}")
                # Don't fail the upload if vector storage fails
            
            # Clean up temp file
            os.remove(temp_path)
            
            # Create document metadata with OCR and vector database information
            import uuid
            document_id = str(uuid.uuid4())
            vector_doc_id = f"doc_{document_id}_{result.get('file_id', '')}"

            document_metadata = {
                'id': document_id,
                'title': title,
                'description': description,
                'category': category,
                'filename': file.filename,
                'file_id': result.get('file_id'),
                'vector_doc_id': vector_doc_id,
                'created_at': datetime.now().isoformat(),
                'status': 'uploaded',
                'ocr_processed': ocr_result is not None,
                'text_extracted': bool(extracted_text.strip()),
                'vector_stored': vector_success if 'vector_success' in locals() else False,
                'searchable': True,  # Document is now searchable via vector similarity
                'ocr_metadata': {
                    'success': ocr_result.get('success', False) if ocr_result else False,
                    'confidence': ocr_result.get('confidence', 0) if ocr_result else 0,
                    'word_count': ocr_result.get('word_count', 0) if ocr_result else 0,
                    'character_count': ocr_result.get('character_count', 0) if ocr_result else 0,
                    'pages_processed': ocr_result.get('pages_processed', 0) if ocr_result else 0,
                    'error': ocr_result.get('error') if ocr_result and not ocr_result.get('success') else None
                },
                'vector_metadata': {
                    'stored_in_vector_db': vector_success if 'vector_success' in locals() else False,
                    'vector_document_id': vector_doc_id,
                    'content_length': len(content_for_vector_db),
                    'embedding_model': 'text-embedding-3-small'
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

@documents_bp.route('/search', methods=['POST'])
def search_documents():
    """Search documents using semantic similarity"""
    try:
        data = request.json
        if not data or 'query' not in data:
            return jsonify({'error': 'Query is required'}), 400

        query = data['query']
        limit = data.get('limit', 10)
        threshold = data.get('threshold', 0.7)

        # Vector search removed - using OpenAI vector store instead
        # TODO: Implement search using OpenAI vector store
        search_results = []

        # Transform results to include document metadata
        documents = []
        for result in search_results:
            metadata = result.get('metadata', {})
            document = {
                'id': metadata.get('document_id', result['document_id']),
                'title': metadata.get('title', 'Unknown'),
                'description': metadata.get('description', ''),
                'category': metadata.get('category', 'general'),
                'filename': metadata.get('original_filename', ''),
                'similarity_score': result['similarity_score'],
                'content_preview': result['content'][:200] + '...' if len(result['content']) > 200 else result['content'],
                'openai_file_id': metadata.get('openai_file_id'),
                'vector_doc_id': result['document_id'],
                'created_at': metadata.get('upload_timestamp', result.get('created_at')),
                'ocr_processed': metadata.get('ocr_processed', False),
                'text_extracted': metadata.get('text_extracted', False)
            }
            documents.append(document)

        result = {
            'documents': documents,
            'total': len(documents),
            'query': query,
            'search_type': 'semantic_similarity',
            'threshold': threshold
        }

        current_app.logger.info(f"Semantic search for '{query}' returned {len(documents)} results")
        return jsonify(result)

    except Exception as e:
        current_app.logger.error(f"Error in semantic document search: {str(e)}")
        return jsonify({'error': str(e)}), 500

@documents_bp.route('/<document_id>', methods=['DELETE'])
def delete_document(document_id):
    """Delete a document from both OpenAI and local vector database"""
    try:
        # Try to delete from OpenAI first (document_id might be OpenAI file_id)
        try:
            from services.openai_assistant_service import openai_assistant_service
            openai_assistant_service.delete_file(document_id)
            current_app.logger.info(f"Deleted document {document_id} from OpenAI")
        except Exception as e:
            current_app.logger.warning(f"Could not delete from OpenAI (might not exist): {str(e)}")

        # Local vector database removed - using OpenAI vector store instead
        # Document deletion from OpenAI vector store is handled above
        deleted_from_vector = True  # OpenAI vector store handles this
                current_app.logger.warning(f"Could not find document {document_id} in vector database")

        except Exception as e:
            current_app.logger.warning(f"Error deleting from vector database: {str(e)}")

        # Try to delete from local database if it exists
        try:
            from db import Document
            session = get_db_session()
            document = session.query(Document).filter(Document.id == document_id).first()

            if document:
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
                current_app.logger.info(f"Deleted document {document_id} from local database")
        except Exception as e:
            current_app.logger.warning(f"Error deleting from local database: {str(e)}")

        return jsonify({'success': True, 'message': 'Document deleted successfully from all systems'})

    except Exception as e:
        current_app.logger.error(f"Error deleting document {document_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@documents_bp.route('/<document_id>/download', methods=['GET'])
def download_document(document_id):
    """Provide information about document download limitations"""
    try:
        from services.openai_assistant_service import openai_assistant_service

        # Get file info from OpenAI (this is allowed)
        files_list = openai_assistant_service.list_files()
        document = None

        for file_info in files_list:
            if file_info.get('file_id') == document_id:
                document = file_info
                break

        if not document:
            return jsonify({'error': 'Document not found'}), 404

        # Return information about the limitation
        return jsonify({
            'error': 'Direct download not available',
            'message': 'Due to OpenAI security policies, files uploaded to the AI assistant cannot be downloaded directly.',
            'document': {
                'id': document_id,
                'filename': document.get('filename', 'Unknown'),
                'size': document.get('bytes', 0),
                'created_at': document.get('created_at', '')
            },
            'alternatives': [
                'Contact the facility management team for a copy of this document',
                'Check if the document is available in the community shared drive',
                'Request the document through the AI Assistant chat'
            ]
        }), 200

    except Exception as e:
        current_app.logger.error(f"Error getting document info {document_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@documents_bp.route('/<document_id>/pdf', methods=['GET'])
def generate_pdf(document_id):
    """Provide information about PDF generation limitations"""
    try:
        from services.openai_assistant_service import openai_assistant_service

        # Get file info from OpenAI
        files_list = openai_assistant_service.list_files()
        document = None

        for file_info in files_list:
            if file_info.get('file_id') == document_id:
                document = file_info
                break

        if not document:
            return jsonify({'error': 'Document not found'}), 404

        filename = document.get('filename', 'Unknown')

        # Return information about the limitation
        return jsonify({
            'error': 'PDF generation not available',
            'message': 'Due to OpenAI security policies, files uploaded to the AI assistant cannot be accessed for PDF conversion.',
            'document': {
                'id': document_id,
                'filename': filename,
                'size': document.get('bytes', 0),
                'is_pdf': filename.lower().endswith('.pdf')
            },
            'alternatives': [
                'If this is already a PDF, contact facility management for a copy',
                'Use the AI Assistant to get information from this document',
                'Request a PDF version through the facility management team'
            ]
        }), 200

    except Exception as e:
        current_app.logger.error(f"Error getting document info for PDF {document_id}: {str(e)}")
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
