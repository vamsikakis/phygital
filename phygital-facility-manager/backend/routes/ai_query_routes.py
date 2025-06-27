from flask import Blueprint, request, jsonify, current_app
import os
import json
import uuid
from datetime import datetime
import requests

from db import get_db_session
from auth import get_current_user

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# Create blueprint
ai_query_bp = Blueprint('ai_query', __name__)

@ai_query_bp.route('/ask', methods=['POST'])
def ask_ai():
    """
    Send a query to the AI and get a response
    """
    try:
        data = request.json
        
        if not data or 'query' not in data:
            return jsonify({'error': 'No query provided'}), 400
            
        query = data['query']
        context_type = data.get('context_type', 'all')  # all, documents, tickets, amenities, etc.
        
        # Get current user for context and logging
        current_user = get_current_user()
        user_id = current_user.id if current_user else None
        
        # Additional options
        options = data.get('options', {})
        if user_id:
            options['user_id'] = user_id
            
        # Construct payload for edge function
        payload = {
            'query': query,
            'context_type': context_type,
            'options': options
        }
        
        # Use both OpenAI Assistant service and local vector database for enhanced context
        try:
            from services.openai_assistant_service import openai_assistant_service
            from services.vector_service import vector_service

            # First, get relevant context from local vector database
            vector_context = ""
            vector_sources = []
            try:
                # Perform semantic search on local vector database
                similar_docs = vector_service.similarity_search(
                    query=query,
                    limit=5,
                    threshold=0.6
                )

                if similar_docs:
                    current_app.logger.info(f"Found {len(similar_docs)} relevant documents in vector database")

                    # Build context from similar documents
                    context_parts = []
                    for doc in similar_docs:
                        metadata = doc.get('metadata', {})
                        title = metadata.get('title', 'Unknown Document')
                        category = metadata.get('category', 'General')

                        context_parts.append(f"Document: {title} (Category: {category})")
                        context_parts.append(f"Content: {doc['content'][:500]}...")
                        context_parts.append("---")

                        vector_sources.append({
                            'type': 'vector_document',
                            'title': title,
                            'category': category,
                            'similarity_score': doc['similarity_score'],
                            'document_id': doc['document_id']
                        })

                    vector_context = "\n".join(context_parts)
                    current_app.logger.info(f"Built vector context with {len(vector_context)} characters")
                else:
                    current_app.logger.info("No relevant documents found in vector database")

            except Exception as vector_error:
                current_app.logger.warning(f"Error querying vector database: {str(vector_error)}")
                # Continue without vector context if it fails

            # Get all uploaded files to provide context to OpenAI Assistant
            uploaded_files = openai_assistant_service.list_files()

            # Filter files to only include supported formats for OpenAI Assistant file search
            # Supported formats: txt, pdf, docx, doc, rtf, md, json, csv, xml, html
            supported_extensions = {'.txt', '.pdf', '.docx', '.doc', '.rtf', '.md', '.json', '.csv', '.xml', '.html'}

            supported_files = []
            if uploaded_files:
                for file_info in uploaded_files:
                    filename = file_info.get("filename", "")
                    file_extension = os.path.splitext(filename.lower())[1]
                    if file_extension in supported_extensions:
                        supported_files.append(file_info["file_id"])
                    else:
                        current_app.logger.info(f"Skipping unsupported file format: {filename} ({file_extension})")

            file_ids = supported_files
            current_app.logger.info(f"Found {len(file_ids)} supported files to attach to query")
            
            # Create a thread for this query
            thread_response = openai_assistant_service.create_thread()
            thread_id = thread_response["thread_id"]

            # Enhance the query with vector context if available
            enhanced_query = query
            if vector_context:
                enhanced_query = f"""Based on the following relevant information from our knowledge base:

{vector_context}

Please answer this question: {query}

If the information above is relevant, use it to provide a comprehensive answer. If not, please answer based on your general knowledge about apartment/facility management."""

            # Add the enhanced message to the thread with file attachments
            openai_assistant_service.add_message(thread_id, enhanced_query, role="user", file_ids=file_ids)

            # Run the assistant on the thread
            run = openai_assistant_service.run_assistant_on_thread(thread_id)

            # Get the messages from the thread
            messages = openai_assistant_service.get_thread_messages(thread_id)

            # Extract the assistant's response
            assistant_messages = [msg for msg in messages if msg["role"] == "assistant"]
            answer = assistant_messages[0]["content"] if assistant_messages else "No response from assistant"

            # Combine sources from both OpenAI files and vector database
            all_sources = []
            all_sources.extend([f"openai_file_{fid}" for fid in file_ids])
            all_sources.extend(vector_sources)

            # Format the result
            result = {
                "answer": answer,
                "sources": all_sources,
                "vector_context_used": bool(vector_context),
                "vector_documents_found": len(vector_sources),
                "openai_files_used": len(file_ids),
                "suggestions": []  # We'll implement suggestions later
            }
            
            # Log query to database for analytics
            try:
                from db import AIQueryLog
                session = get_db_session()
                query_log = AIQueryLog(
                    query=query,
                    response_text=answer,
                    context_type="assistant",
                    context_sources=json.dumps(result.get("sources", [])),
                    meta_data=json.dumps({
                        "sources": result.get("sources", []),
                        "suggestions": result.get("suggestions", [])
                    }),
                    user_id=user_id
                )
                session.add(query_log)
                session.commit()
                current_app.logger.info(f"Successfully logged AI query")
            except Exception as e:
                # Don't fail the request if logging fails
                current_app.logger.warning(f"Error logging AI query: {str(e)}")
                # Continue with the response even if logging fails
            
            return jsonify(result)
                
        except Exception as e:
            current_app.logger.error(f"Error calling AI query function: {str(e)}")
            return jsonify({'error': str(e)}), 500
        
    except Exception as e:
        current_app.logger.error(f"Error processing AI query: {str(e)}")
        return jsonify({'error': str(e)}), 500

@ai_query_bp.route('/history', methods=['GET'])
def get_query_history():
    """
    Get query history for the current user
    """
    try:
        # Get current user
        current_user = get_current_user()
        
        if not current_user:
            return jsonify({'error': 'Unauthorized'}), 401
            
        limit = int(request.args.get('limit', 20))
        offset = int(request.args.get('offset', 0))
        
        # Query the database
        from db import AIQueryLog
        session = get_db_session()
        query = session.query(AIQueryLog).filter(AIQueryLog.user_id == current_user.id)
        
        # Get total count
        total_count = query.count()
        
        # Apply pagination
        query_logs = query.order_by(AIQueryLog.created_at.desc()).offset(offset).limit(limit).all()
        
        # Format response
        result = []
        for log in query_logs:
            result.append({
                'id': log.id,
                'query': log.query,
                'response': log.response_text,
                'context_type': log.context_type,
                'sources': json.loads(log.context_sources) if log.context_sources else [],
                'created_at': log.created_at.isoformat() if log.created_at else None
            })
            
        return jsonify({
            'history': result,
            'total': total_count,
            'limit': limit,
            'offset': offset
        })
        
    except Exception as e:
        current_app.logger.error(f"Error fetching query history: {str(e)}")
        return jsonify({'error': str(e)}), 500

@ai_query_bp.route('/history/<query_id>', methods=['DELETE'])
def delete_query_history(query_id):
    """
    Delete a query from history
    """
    try:
        # Get current user
        current_user = get_current_user()
        
        if not current_user:
            return jsonify({'error': 'Unauthorized'}), 401
            
        # Find and delete the query log
        from db import AIQueryLog
        session = get_db_session()
        query_log = session.query(AIQueryLog).filter(
            AIQueryLog.id == query_id,
            AIQueryLog.user_id == current_user.id
        ).first()
        
        if not query_log:
            return jsonify({'error': 'Query log not found'}), 404
            
        # Delete the query log
        session.delete(query_log)
        session.commit()
        
        return jsonify({'success': True, 'message': 'Query log deleted successfully'})
        
    except Exception as e:
        current_app.logger.error(f"Error deleting query log {query_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500
        
@ai_query_bp.route('/faq', methods=['GET'])
def get_faq():
    """
    Get a list of frequently asked questions
    """
    try:
        # Query the database
        from db import FAQ
        session = get_db_session()
        faqs = session.query(FAQ).order_by(FAQ.order_index).all()
        
        # Format response
        result = []
        for faq in faqs:
            result.append({
                'id': faq.id,
                'question': faq.question,
                'answer': faq.answer,
                'category': faq.category,
                'order_index': faq.order_index
            })
            
        return jsonify({
            'faqs': result
        })
        
    except Exception as e:
        current_app.logger.error(f"Error fetching FAQs: {str(e)}")
        return jsonify({'error': str(e)}), 500
