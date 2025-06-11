from flask import Blueprint, request, jsonify, current_app
from services.verba_service import verba_service
import os
from werkzeug.utils import secure_filename
import uuid
from datetime import datetime

verba_bp = Blueprint('verba_routes', __name__)
UPLOAD_FOLDER = 'uploads/documents'

@verba_bp.route('/api/verba/status', methods=['GET'])
def get_status():
    """Check if Verba service is properly initialized"""
    initialized = verba_service.is_initialized()
    return jsonify({
        "status": "ok" if initialized else "error",
        "initialized": initialized
    })

@verba_bp.route('/api/verba/collections', methods=['GET'])
def get_collections():
    """Get all available collections"""
    collections = verba_service.get_collections()
    return jsonify({
        "collections": collections
    })

@verba_bp.route('/api/verba/documents', methods=['GET'])
def get_documents():
    """Get all indexed documents metadata"""
    collection = request.args.get('collection', 'apartment_documents')
    documents = verba_service.get_document_metadata(collection)
    return jsonify({
        "documents": documents
    })

@verba_bp.route('/api/verba/upload', methods=['POST'])
def upload_document():
    """Upload document to Verba collection"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400
        
        file = request.files['file']
        title = request.form.get('title', '')
        category = request.form.get('category', '')
        doc_type = request.form.get('type', '')
        collection = request.form.get('collection', 'apartment_documents')
        
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        
        # Save file temporarily
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)
            
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(file_path)
        
        # Generate metadata
        metadata = {
            "title": title,
            "category": category,
            "type": doc_type,
            "uploaded_at": datetime.now().isoformat(),
            "file_name": filename
        }
        
        # Upload to Verba
        result = verba_service.upload_document(
            file_path=file_path,
            collection_name=collection,
            metadata=metadata
        )
        
        if not result:
            return jsonify({
                "error": "Failed to upload document to Verba"
            }), 500
        
        return jsonify({
            "success": True,
            "message": "Document uploaded and indexed successfully",
            "metadata": metadata
        })
        
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

@verba_bp.route('/api/verba/query', methods=['POST'])
def query_documents():
    """Query documents using Verba RAG"""
    try:
        data = request.json
        if not data or 'query' not in data:
            return jsonify({"error": "No query provided"}), 400
        
        query = data.get('query')
        collection = data.get('collection', 'apartment_documents')
        limit = data.get('limit', 5)
        
        result = verba_service.query_documents(
            query_text=query,
            collection_name=collection,
            limit=limit
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500
