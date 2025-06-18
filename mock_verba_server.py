#!/usr/bin/env python3
"""
Mock Verba Server for testing the RAG document upload functionality.
This simulates the Verba API endpoints without requiring actual OpenAI or Weaviate services.
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS, cross_origin
import os
import json
import uuid
import datetime
import shutil
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configure CORS more explicitly
CORS(app, 
     resources={r"/*": {"origins": ["http://localhost:5174", "*"]}},
     allow_headers=["Content-Type", "Authorization", "Accept"],
     supports_credentials=True,
     methods=["GET", "POST", "OPTIONS", "DELETE"])

# Storage directories
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mock_verba_data')
UPLOADS_DIR = os.path.join(DATA_DIR, 'uploads')
COLLECTIONS_FILE = os.path.join(DATA_DIR, 'collections.json')
DOCUMENTS_FILE = os.path.join(DATA_DIR, 'documents.json')

# Create directories if they don't exist
os.makedirs(UPLOADS_DIR, exist_ok=True)

# Initialize collections and documents data
def init_data():
    if not os.path.exists(COLLECTIONS_FILE):
        with open(COLLECTIONS_FILE, 'w') as f:
            json.dump(['apartment_documents'], f)
    
    if not os.path.exists(DOCUMENTS_FILE):
        with open(DOCUMENTS_FILE, 'w') as f:
            json.dump({}, f)

# Load collections
def get_collections():
    with open(COLLECTIONS_FILE, 'r') as f:
        return json.load(f)

# Load documents
def get_documents():
    with open(DOCUMENTS_FILE, 'r') as f:
        return json.load(f)

# Save documents
def save_documents(documents):
    with open(DOCUMENTS_FILE, 'w') as f:
        json.dump(documents, f)

# Initialize data
init_data()

@app.route('/api/verba/status', methods=['GET'])
def status():
    """Check if the Verba service is initialized"""
    return jsonify({"initialized": True, "version": "mock-1.0.0"})

@app.route('/api/verba/collections', methods=['GET'])
def collections():
    """Get all available collections"""
    return jsonify({"collections": get_collections()})

@app.route('/api/verba/documents', methods=['GET'])
def documents():
    """Get all documents in a collection"""
    collection = request.args.get('collection', 'apartment_documents')
    all_documents = get_documents()
    
    # Filter documents by collection
    collection_docs = [doc for doc in all_documents.values() if doc.get('collection') == collection]
    
    return jsonify({"documents": collection_docs})

@app.route('/api/verba/upload', methods=['POST'])
def upload_document():
    """Upload a document to a collection"""
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        
        # Get form data
        collection = request.form.get('collection', 'apartment_documents')
        title = request.form.get('title', file.filename)
        category = request.form.get('category', 'General')
        doc_type = request.form.get('type', 'Document')
        tags = request.form.get('tags', '')
        
        # Split tags if they're comma-separated
        if isinstance(tags, str):
            tags = [tag.strip() for tag in tags.split(',') if tag.strip()]
        
        # Generate a unique ID
        doc_id = str(uuid.uuid4())
        
        # Save the file
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOADS_DIR, f"{doc_id}_{filename}")
        file.save(file_path)
        
        # Create document metadata
        document = {
            "id": doc_id,
            "collection": collection,
            "file_path": file_path,
            "metadata": {
                "title": title,
                "category": category,
                "type": doc_type,
                "tags": tags,
                "file_name": filename,
                "uploaded_at": datetime.datetime.now().isoformat()
            }
        }
        
        # Save document metadata
        all_documents = get_documents()
        all_documents[doc_id] = document
        save_documents(all_documents)
        
        return jsonify({
            "success": True,
            "message": "Document uploaded successfully",
            "document_id": doc_id
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/verba/query', methods=['POST'])
def query_documents():
    """Query documents using RAG"""
    data = request.json
    query = data.get('query', '')
    collection = data.get('collection', 'apartment_documents')
    limit = data.get('limit', 3)
    
    # In a real system, this would query the vector database
    # For mock purposes, we'll return a static response
    
    all_documents = get_documents()
    collection_docs = [doc for doc in all_documents.values() if doc.get('collection') == collection]
    
    # Limit the number of documents
    sample_docs = collection_docs[:limit] if collection_docs else []
    
    sources = []
    for doc in sample_docs:
        sources.append({
            "content": f"This is a mock content snippet from document {doc['metadata']['title']}.",
            "document": doc['metadata']['title'],
            "metadata": doc['metadata'],
            "score": 0.95  # Mock relevance score
        })
    
    return jsonify({
        "answer": f"This is a mock answer to your question: '{query}'. I found {len(sources)} relevant documents.",
        "sources": sources
    })

@app.route('/api/verba/document/<doc_id>', methods=['DELETE'])
def delete_document(doc_id):
    """Delete a document from a collection"""
    all_documents = get_documents()
    
    if doc_id not in all_documents:
        return jsonify({"error": "Document not found"}), 404
    
    # Remove the file
    file_path = all_documents[doc_id]['file_path']
    if os.path.exists(file_path):
        os.remove(file_path)
    
    # Remove from documents
    del all_documents[doc_id]
    save_documents(all_documents)
    
    return jsonify({
        "success": True,
        "message": "Document deleted successfully"
    })

@app.route('/api/verba/collection', methods=['POST'])
def create_collection():
    """Create a new collection"""
    data = request.json
    collection_name = data.get('name')
    
    if not collection_name:
        return jsonify({"error": "Collection name is required"}), 400
    
    collections = get_collections()
    if collection_name in collections:
        return jsonify({"error": "Collection already exists"}), 400
    
    collections.append(collection_name)
    
    with open(COLLECTIONS_FILE, 'w') as f:
        json.dump(collections, f)
    
    return jsonify({
        "success": True,
        "message": f"Collection '{collection_name}' created successfully"
    })

if __name__ == '__main__':
    print("Starting Mock Verba Server...")
    print(f"Data directory: {DATA_DIR}")
    app.run(host='0.0.0.0', port=5001)
