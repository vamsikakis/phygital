from flask import Blueprint, request, jsonify, current_app
import os
import json
from datetime import datetime
import werkzeug

from services.openai_assistant_service import openai_assistant_service
from auth import get_current_user, admin_required

# Create blueprint
assistant_bp = Blueprint('assistant', __name__)

@assistant_bp.route('/init', methods=['GET'])
def initialize_assistant_route():
    """Initialize or retrieve the OpenAI Assistant and Vector Store"""
    try:
        result = openai_assistant_service.initialize()
        
        # Store IDs in environment for future use
        current_assistant_id = result.get('assistant_id')
        current_vector_store_id = result.get('vector_store_id')
        
        return jsonify({
            "assistant_id": current_assistant_id,
            "vector_store_id": current_vector_store_id,
            "message": "Assistant and Vector Store initialized/re-initialized via /init route."
        })
    except Exception as e:
        current_app.logger.error(f"Error initializing assistant: {str(e)}")
        return jsonify({'error': str(e)}), 500

@assistant_bp.route('/threads', methods=['POST'])
def create_thread_route():
    """Create a new conversation thread"""
    try:
        result = openai_assistant_service.create_thread()
        return jsonify(result), 201
    except Exception as e:
        current_app.logger.error(f"Error creating thread: {str(e)}")
        return jsonify({'error': str(e)}), 500

@assistant_bp.route('/threads', methods=['GET'])
def list_threads_route():
    """List available threads"""
    try:
        limit = int(request.args.get('limit', 10))
        threads = openai_assistant_service.list_threads(limit)
        return jsonify({"threads": threads})
    except Exception as e:
        current_app.logger.error(f"Error listing threads: {str(e)}")
        return jsonify({'error': str(e)}), 500

@assistant_bp.route('/threads/<thread_id>', methods=['GET'])
def get_thread_route(thread_id):
    """Get a thread by ID"""
    try:
        thread = openai_assistant_service.get_thread(thread_id)
        return jsonify(thread)
    except Exception as e:
        current_app.logger.error(f"Error retrieving thread {thread_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@assistant_bp.route('/threads/<thread_id>', methods=['DELETE'])
def delete_thread_route(thread_id):
    """Delete a thread"""
    try:
        result = openai_assistant_service.delete_thread(thread_id)
        return jsonify(result)
    except Exception as e:
        current_app.logger.error(f"Error deleting thread {thread_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@assistant_bp.route('/threads/<thread_id>/messages', methods=['POST'])
def add_message_route(thread_id):
    """Add a message to a thread"""
    try:
        data = request.json
        if not data or 'content' not in data:
            return jsonify({'error': 'No message content provided'}), 400
            
        content = data['content']
        role = data.get('role', 'user')
        
        result = openai_assistant_service.add_message(thread_id, content, role)
        return jsonify(result), 201
    except Exception as e:
        current_app.logger.error(f"Error adding message to thread {thread_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@assistant_bp.route('/threads/<thread_id>/messages', methods=['GET'])
def get_messages_route(thread_id):
    """Get messages from a thread"""
    try:
        limit = int(request.args.get('limit', 100))
        messages = openai_assistant_service.get_thread_messages(thread_id, limit)
        return jsonify({"messages": messages})
    except Exception as e:
        current_app.logger.error(f"Error getting messages from thread {thread_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@assistant_bp.route('/threads/<thread_id>/run', methods=['POST'])
def run_assistant_route(thread_id):
    """Run the assistant on a thread"""
    try:
        data = request.json
        instructions = data.get('instructions') if data else None
        
        result = openai_assistant_service.run_assistant_on_thread(thread_id, instructions)
        return jsonify(result)
    except Exception as e:
        current_app.logger.error(f"Error running assistant on thread {thread_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@assistant_bp.route('/files', methods=['POST'])
def upload_file_route():
    """Upload a file to the vector store"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
            
        # Save file temporarily
        temp_path = f"/tmp/{werkzeug.utils.secure_filename(file.filename)}"
        file.save(temp_path)
        
        # Upload to vector store
        result = openai_assistant_service.upload_file_to_vector_store(temp_path, file.filename)
        
        # Clean up temp file
        os.remove(temp_path)
        
        return jsonify(result), 201
    except Exception as e:
        current_app.logger.error(f"Error uploading file: {str(e)}")
        return jsonify({'error': str(e)}), 500

@assistant_bp.route('/files', methods=['GET'])
def list_files_route():
    """List files in the vector store"""
    try:
        files = openai_assistant_service.list_files()
        return jsonify({"files": files})
    except Exception as e:
        current_app.logger.error(f"Error listing files: {str(e)}")
        return jsonify({'error': str(e)}), 500

@assistant_bp.route('/files/<file_id>', methods=['DELETE'])
@admin_required
def delete_file_route(file_id):
    """Delete a file from the vector store"""
    try:
        result = openai_assistant_service.delete_file(file_id)
        return jsonify(result)
    except Exception as e:
        current_app.logger.error(f"Error deleting file {file_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500
