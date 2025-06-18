import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from config import config
import openai
from dotenv import load_dotenv
from services.openai_assistant_service import openai_assistant_service

# Create the modules files
from modules.akc.knowledge_base import ApartmentKnowledgeBase
from modules.oce.communication import OwnersCommunication
from modules.hdc.helpdesk import HelpDesk

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(config[os.getenv('FLASK_ENV', 'default')])
CORS(app)

# Register blueprints
from routes.assistant_routes import assistant_bp
app.register_blueprint(assistant_bp, url_prefix='/api/assistant')

# Initialize OpenAI Assistant on startup
def initialize_assistant():
    try:
        result = openai_assistant_service.initialize()
        app.logger.info(f"OpenAI Assistant initialized: {result}")
    except Exception as e:
        app.logger.error(f"Failed to initialize OpenAI Assistant: {str(e)}")

# Call initialize_assistant at startup
with app.app_context():
    initialize_assistant()

# Set up OpenAI client
client = openai.OpenAI(api_key=app.config['OPENAI_API_KEY'])

# Initialize modules
akc = ApartmentKnowledgeBase(client)
oce = OwnersCommunication(client)
hdc = HelpDesk(client)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/api/query', methods=['POST'])
def process_query():
    data = request.json
    if not data or 'query' not in data:
        return jsonify({"error": "Missing query parameter"}), 400
    
    query = data['query']
    module = data.get('module', 'auto')  # If no module specified, auto-detect
    
    # Auto-detect which module should handle this query
    if module == 'auto':
        if any(keyword in query.lower() for keyword in ['document', 'rule', 'policy', 'knowledge', 'information']):
            module = 'akc'
        elif any(keyword in query.lower() for keyword in ['announcement', 'communication', 'event', 'feedback', 'poll']):
            module = 'oce'
        else:
            module = 'hdc'  # Default to help desk for general questions
    
    # Route to appropriate module
    try:
        if module == 'akc':
            response = akc.process_query(query)
        elif module == 'oce':
            response = oce.process_query(query)
        else:  # hdc
            response = hdc.process_query(query)
        
        return jsonify({"response": response, "module": module}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/akc/documents', methods=['GET'])
def get_documents():
    try:
        documents = akc.get_documents()
        return jsonify({"documents": documents}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/oce/announcements', methods=['GET'])
def get_announcements():
    try:
        announcements = oce.get_announcements()
        return jsonify({"announcements": announcements}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/hdc/create-ticket', methods=['POST'])
def create_ticket():
    data = request.json
    if not data or 'description' not in data:
        return jsonify({"error": "Missing ticket description"}), 400
    
    try:
        ticket_id = hdc.create_ticket(data['description'], data.get('category', 'General'))
        return jsonify({"ticket_id": ticket_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Register existing routes if they exist
try:
    from routes.ai_query_routes import ai_query_bp
    app.register_blueprint(ai_query_bp, url_prefix='/api/ai_query')
    app.logger.info("Registered AI query routes")
except ImportError:
    app.logger.warning("AI query routes not found")

try:
    from routes.document_routes import documents_bp
    app.register_blueprint(documents_bp, url_prefix='/api/documents')
    app.logger.info("Registered document routes")
except ImportError:
    app.logger.warning("Document routes not found")

# Register migration routes
try:
    from routes.migration_routes import migration_bp
    app.register_blueprint(migration_bp, url_prefix='/api/migration')
    app.logger.info("Registered migration routes")
except ImportError:
    app.logger.warning("Migration routes not found")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
