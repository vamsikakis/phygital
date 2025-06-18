from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime
from models.document import Document, DocumentType
from database import db

document_routes = Blueprint('document_routes', __name__)

UPLOAD_FOLDER = 'uploads/documents'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'csv'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@document_routes.route('/api/documents', methods=['GET'])
def get_documents():
    try:
        documents = Document.query.all()
        return jsonify([doc.to_dict() for doc in documents]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@document_routes.route('/api/documents/types', methods=['GET'])
def get_document_types():
    try:
        types = DocumentType.query.all()
        return jsonify([t.to_dict() for t in types]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@document_routes.route('/api/documents/upload', methods=['POST'])
def upload_document():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
            file.save(file_path)
            
            new_document = Document(
                title=request.form.get('title'),
                type=request.form.get('type'),
                category=request.form.get('category'),
                file_url=f"/uploads/documents/{unique_filename}",
                uploaded_by=request.form.get('uploadedBy', 'System User'),
                uploaded_at=datetime.now(),
                status='Active',
                tags=request.form.get('tags', '').split(',') if request.form.get('tags') else [],
                metadata={
                    'size': os.path.getsize(file_path),
                    'pages': 0,  # This would need a library to determine
                    'language': 'en'  # This would need analysis to determine
                }
            )
            
            db.session.add(new_document)
            db.session.commit()
            
            return jsonify(new_document.to_dict()), 201
        
        return jsonify({"error": "File type not allowed"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@document_routes.route('/api/documents/<int:document_id>', methods=['GET'])
def get_document(document_id):
    try:
        document = Document.query.get(document_id)
        if not document:
            return jsonify({"error": "Document not found"}), 404
        
        return jsonify(document.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@document_routes.route('/api/documents/<int:document_id>', methods=['PUT'])
def update_document(document_id):
    try:
        document = Document.query.get(document_id)
        if not document:
            return jsonify({"error": "Document not found"}), 404
        
        data = request.get_json()
        
        if 'title' in data:
            document.title = data['title']
        if 'type' in data:
            document.type = data['type']
        if 'category' in data:
            document.category = data['category']
        if 'tags' in data:
            document.tags = data['tags']
        if 'status' in data:
            document.status = data['status']
        
        db.session.commit()
        
        return jsonify(document.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@document_routes.route('/api/documents/<int:document_id>', methods=['DELETE'])
def delete_document(document_id):
    try:
        document = Document.query.get(document_id)
        if not document:
            return jsonify({"error": "Document not found"}), 404
        
        # Delete the file if it exists
        if document.file_url and os.path.exists(document.file_url.replace('/uploads', 'uploads')):
            os.remove(document.file_url.replace('/uploads', 'uploads'))
        
        db.session.delete(document)
        db.session.commit()
        
        return jsonify({"message": "Document deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@document_routes.route('/api/documents/search', methods=['GET'])
def search_documents():
    try:
        query = request.args.get('query', '')
        if not query:
            return jsonify({"error": "Search query is required"}), 400
        
        # Perform search using a like query
        documents = Document.query.filter(
            (Document.title.like(f'%{query}%')) | 
            (Document.category.like(f'%{query}%')) | 
            (Document.type.like(f'%{query}%'))
        ).all()
        
        return jsonify([doc.to_dict() for doc in documents]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
