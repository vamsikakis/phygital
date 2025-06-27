#!/usr/bin/env python3
"""
Simple Flask Application for AI-Powered Document Management
Simplified version without Supabase dependencies
"""

import os
import sys
from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
from datetime import datetime
import openai
import json

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import configuration
from config import config

# Create Flask app
app = Flask(__name__)
app.config.from_object(config)
CORS(app)

# Initialize OpenAI
openai.api_key = app.config['OPENAI_API_KEY']

# Import services
try:
    from services.vector_service import vector_service
    VECTOR_SERVICE_AVAILABLE = True
    app.logger.info("Vector service loaded successfully")
except Exception as e:
    VECTOR_SERVICE_AVAILABLE = False
    app.logger.warning(f"Vector service not available: {e}")

try:
    from services.openai_assistant_service import openai_assistant_service
    OPENAI_SERVICE_AVAILABLE = True
    app.logger.info("OpenAI assistant service loaded successfully")
except Exception as e:
    OPENAI_SERVICE_AVAILABLE = False
    app.logger.warning(f"OpenAI assistant service not available: {e}")

# Health check endpoint
@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'services': {
            'vector_service': VECTOR_SERVICE_AVAILABLE,
            'openai_service': OPENAI_SERVICE_AVAILABLE
        }
    })

# API info endpoint
@app.route('/api')
def api_info():
    """API information endpoint"""
    return jsonify({
        'message': 'Gopalan Atlantis AI-Powered Document Management API',
        'version': '1.0.0',
        'endpoints': {
            'health': '/health',
            'api_info': '/api',
            'query': '/api/query',
            'documents_search': '/api/documents/search',
            'documents_upload': '/api/documents'
        },
        'services_available': {
            'vector_search': VECTOR_SERVICE_AVAILABLE,
            'openai_assistant': OPENAI_SERVICE_AVAILABLE
        }
    })

# AI Query endpoint
@app.route('/api/query', methods=['POST'])
def ai_query():
    """Process AI queries with vector context"""
    try:
        data = request.json
        if not data or 'query' not in data:
            return jsonify({'error': 'Query is required'}), 400
        
        query = data['query']
        
        # Get context from vector database if available
        vector_context = ""
        vector_sources = []
        
        if VECTOR_SERVICE_AVAILABLE:
            try:
                similar_docs = vector_service.similarity_search(
                    query=query,
                    limit=3,
                    threshold=0.6
                )
                
                if similar_docs:
                    context_parts = []
                    for doc in similar_docs:
                        metadata = doc.get('metadata', {})
                        title = metadata.get('title', 'Unknown Document')
                        context_parts.append(f"Document: {title}")
                        context_parts.append(f"Content: {doc['content'][:300]}...")
                        context_parts.append("---")
                        
                        vector_sources.append({
                            'title': title,
                            'similarity_score': doc['similarity_score']
                        })
                    
                    vector_context = "\n".join(context_parts)
                    
            except Exception as e:
                app.logger.warning(f"Vector search failed: {e}")
        
        # Use OpenAI for response
        try:
            client = openai.OpenAI(api_key=app.config['OPENAI_API_KEY'])
            
            # Enhance query with context
            enhanced_query = query
            if vector_context:
                enhanced_query = f"""Based on this relevant information:

{vector_context}

Please answer: {query}"""
            
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant for Gopalan Atlantis apartment residents. Provide helpful, accurate information about facility management, amenities, and services."},
                    {"role": "user", "content": enhanced_query}
                ],
                max_tokens=500
            )
            
            answer = response.choices[0].message.content
            
            return jsonify({
                'response': answer,
                'vector_context_used': bool(vector_context),
                'sources': vector_sources,
                'query': query
            })
            
        except Exception as e:
            app.logger.error(f"OpenAI query failed: {e}")
            return jsonify({'error': 'AI service temporarily unavailable'}), 500
            
    except Exception as e:
        app.logger.error(f"Query processing failed: {e}")
        return jsonify({'error': str(e)}), 500

# Document search endpoint
@app.route('/api/documents/search', methods=['POST'])
def search_documents():
    """Search documents using semantic similarity"""
    if not VECTOR_SERVICE_AVAILABLE:
        return jsonify({'error': 'Vector search service not available'}), 503
    
    try:
        data = request.json
        if not data or 'query' not in data:
            return jsonify({'error': 'Query is required'}), 400
        
        query = data['query']
        limit = data.get('limit', 10)
        threshold = data.get('threshold', 0.7)
        
        search_results = vector_service.similarity_search(
            query=query,
            limit=limit,
            threshold=threshold
        )
        
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
                'vector_doc_id': result['document_id'],
                'created_at': metadata.get('upload_timestamp', result.get('created_at'))
            }
            documents.append(document)
        
        return jsonify({
            'documents': documents,
            'total': len(documents),
            'query': query,
            'search_type': 'semantic_similarity'
        })
        
    except Exception as e:
        app.logger.error(f"Document search failed: {e}")
        return jsonify({'error': str(e)}), 500

# Simple document upload endpoint
@app.route('/api/documents', methods=['POST'])
def upload_document():
    """Simple document upload with vector storage"""
    if not VECTOR_SERVICE_AVAILABLE:
        return jsonify({'error': 'Vector storage service not available'}), 503
    
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        title = request.form.get('title', file.filename)
        description = request.form.get('description', '')
        category = request.form.get('category', 'general')
        
        # Read file content
        content = file.read().decode('utf-8', errors='ignore')
        
        # Create document ID
        import uuid
        document_id = str(uuid.uuid4())
        
        # Store in vector database
        success = vector_service.store_document_embedding(
            document_id=document_id,
            content=f"Title: {title}\nDescription: {description}\nCategory: {category}\n\nContent:\n{content}",
            metadata={
                'title': title,
                'description': description,
                'category': category,
                'original_filename': file.filename,
                'document_id': document_id,
                'upload_timestamp': datetime.now().isoformat()
            }
        )
        
        if success:
            return jsonify({
                'id': document_id,
                'title': title,
                'description': description,
                'category': category,
                'filename': file.filename,
                'vector_stored': True,
                'status': 'uploaded',
                'created_at': datetime.now().isoformat()
            })
        else:
            return jsonify({'error': 'Failed to store document'}), 500
            
    except Exception as e:
        app.logger.error(f"Document upload failed: {e}")
        return jsonify({'error': str(e)}), 500

# Serve frontend static files
@app.route('/assets/<path:filename>')
def serve_assets(filename):
    """Serve assets from frontend build"""
    frontend_build_path = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'dist', 'assets')
    if os.path.exists(os.path.join(frontend_build_path, filename)):
        return send_from_directory(frontend_build_path, filename)
    else:
        return jsonify({"error": "Asset not found"}), 404

# Serve other static files
@app.route('/<path:filename>')
def serve_static_files(filename):
    """Serve static files from frontend build root"""
    if '.' in filename:  # Has file extension
        frontend_build_path = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'dist')
        file_path = os.path.join(frontend_build_path, filename)
        if os.path.exists(file_path):
            return send_from_directory(frontend_build_path, filename)
    
    # If not a static file, fall through to SPA routing
    return serve_frontend_root()

# Serve frontend for SPA routes
@app.route('/')
def serve_frontend_root():
    """Serve the React frontend for root route"""
    frontend_build_path = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'dist')
    index_path = os.path.join(frontend_build_path, 'index.html')
    
    if os.path.exists(index_path):
        return send_file(index_path)
    else:
        return jsonify({
            "message": "Frontend not available",
            "note": "Please build the frontend first with 'npm run build' in the frontend directory",
            "api_available": True,
            "api_docs": "/api"
        }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
