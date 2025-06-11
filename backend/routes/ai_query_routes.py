from flask import Blueprint, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

ai_query_bp = Blueprint('ai_query', __name__)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

@ai_query_bp.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        messages = data.get('messages', [])
        
        if not messages:
            return jsonify({"error": "No messages provided"}), 400

        # Add system prompt
        messages.insert(0, {
            "role": "system",
            "content": "You are a helpful facility manager assistant. Provide clear and concise answers about apartment facilities and management."
        })

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )

        return jsonify({
            "response": response.choices[0].message.content,
            "usage": response.usage
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@ai_query_bp.route('/document-summary/<int:document_id>', methods=['GET'])
def get_document_summary(document_id):
    try:
        # TODO: Implement actual document fetching and summary generation
        # For now, return a mock response
        return jsonify({
            "summary": "This is a summary of the document. The AI will analyze the document and provide a concise summary of its contents."
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@ai_query_bp.route('/announcements', methods=['GET'])
def get_community_announcements():
    try:
        # TODO: Implement actual announcement fetching
        # For now, return mock announcements
        return jsonify({
            "announcements": [
                "Monthly maintenance schedule has been updated",
                "Community meeting scheduled for next Friday",
                "New parking regulations effective from next month"
            ]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
