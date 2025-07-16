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

# --- MOVE THIS BLOCK UP ---
# Register Assistant routes FIRST, so they are available when the app starts and receives requests
from routes.assistant_routes import assistant_bp
app.register_blueprint(assistant_bp, url_prefix='/api/assistant')
app.logger.info("Registered Assistant routes")

# Register Authentication routes
from routes.auth_routes import auth_bp
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.logger.info("Registered Authentication routes")
# --- END MOVE ---

# Initialize OpenAI Assistant on startup
def initialize_assistant():
    try:
        # This call will now correctly use the service, and if the frontend
        # also calls /api/assistant/init, that route will be available.
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

@app.route('/', methods=['GET'])
def root():
    """Root endpoint"""
    return jsonify({
        "message": "Phygital Facility Manager API",
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "assistant": "/api/assistant/*",
            "documents": "/api/documents/*",
            "clickup": "/api/clickup/*",
            "firefly": "/api/firefly/*"
        }
    }), 200

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/api/query', methods=['POST'])
def process_query():
    from auth import get_current_user

    # Check authentication
    current_user = get_current_user()
    if not current_user:
        return jsonify({"error": "Authentication required"}), 401

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
        from auth import get_current_user

        # Check authentication
        current_user = get_current_user()
        if not current_user:
            return jsonify({"error": "Authentication required"}), 401

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

# Help Desk functionality removed as per requirements

# Additional API endpoints for frontend compatibility
@app.route('/api/financial/budgets', methods=['GET'])
def get_budgets():
    """Get financial budgets"""
    try:
        status = request.args.get('status', 'all')
        # Mock data for now - replace with actual database queries
        budgets = [
            {
                "id": "1",
                "name": "Maintenance Budget 2024",
                "total_amount": 500000,
                "spent_amount": 250000,
                "status": "active",
                "created_at": "2024-01-01T00:00:00Z"
            }
        ]
        return jsonify({"budgets": budgets}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/tickets', methods=['GET'])
def get_tickets():
    """Get tickets"""
    try:
        status = request.args.get('status', 'all')
        # Mock data for now - replace with actual database queries
        tickets = [
            {
                "id": "1",
                "subject": "Pool maintenance required",
                "status": "pending",
                "priority": "medium",
                "created_at": "2024-06-29T00:00:00Z"
            }
        ]
        return jsonify({"tickets": tickets}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/events', methods=['GET'])
def get_events():
    """Get events"""
    try:
        upcoming = request.args.get('upcoming', 'false')
        # Mock data for now - replace with actual database queries
        events = [
            {
                "id": "1",
                "title": "Community Meeting",
                "date": "2024-07-15T18:00:00Z",
                "location": "Clubhouse",
                "description": "Monthly community meeting"
            }
        ]
        return jsonify({"events": events}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/financial/maintenance-fees', methods=['GET'])
def get_maintenance_fees():
    """Get maintenance fees"""
    try:
        status = request.args.get('status', 'all')
        # Mock data for now - replace with actual database queries
        fees = [
            {
                "id": "1",
                "apartment_number": "A-101",
                "amount": 5000,
                "status": "pending",
                "due_date": "2024-07-01T00:00:00Z"
            }
        ]
        return jsonify({"maintenance_fees": fees}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/activities/recent', methods=['GET'])
def get_recent_activities():
    """Get recent activities"""
    try:
        # Mock data for now - replace with actual database queries
        activities = [
            {
                "id": "1",
                "type": "ticket_created",
                "description": "New maintenance ticket created",
                "timestamp": "2024-06-29T10:00:00Z",
                "user": "John Doe"
            }
        ]
        return jsonify({"activities": activities}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/documents/categories', methods=['GET'])
def get_document_categories():
    """Get document categories"""
    try:
        categories = [
            "Community Rules",
            "Maintenance",
            "Amenities",
            "Security",
            "Billing",
            "General",
            "Emergency",
            "Policies"
        ]
        return jsonify({"categories": categories}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Static file endpoints
@app.route('/favicon.ico')
def favicon():
    """Serve favicon"""
    # Return a simple 1x1 transparent PNG
    from flask import Response
    import base64

    # 1x1 transparent PNG in base64
    transparent_png = base64.b64decode(
        'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=='
    )
    return Response(transparent_png, mimetype='image/png')

# PWA icons will be served from frontend dist folder

@app.route('/logo192.png')
def logo():
    """Serve logo"""
    # Return a simple colored square PNG
    from flask import Response
    import base64

    # Simple logo PNG in base64
    logo_png = base64.b64decode(
        'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=='
    )
    return Response(logo_png, mimetype='image/png')

# OpenAI Assistant routes
@app.route('/api/openai-assistant', methods=['GET'])
def get_openai_assistant_info():
    """Get OpenAI assistant information"""
    try:
        return jsonify({
            "status": "available",
            "assistant_id": os.getenv('OPENAI_ASSISTANT_ID', 'default'),
            "model": "gpt-4",
            "capabilities": [
                "document_search",
                "facility_management",
                "natural_language_queries"
            ]
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/openai-assistant/files', methods=['GET'])
def get_assistant_files():
    """Get files uploaded to OpenAI assistant"""
    try:
        # Mock response for now
        files = [
            {
                "id": "file_1",
                "filename": "facility_rules.pdf",
                "purpose": "assistants",
                "created_at": "2024-06-29T00:00:00Z"
            }
        ]
        return jsonify({"files": files}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/openai-assistant/vector-store', methods=['GET'])
def get_vector_store_info():
    """Get vector store information"""
    try:
        return jsonify({
            "status": "available",
            "vector_store_id": "vs_default",
            "file_count": 0,
            "embedding_model": "text-embedding-3-small"
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# User and authentication endpoints
@app.route('/api/user', methods=['GET'])
def get_user_info():
    """Get current user information"""
    try:
        from auth import get_current_user

        current_user = get_current_user()
        if not current_user:
            return jsonify({"error": "Not authenticated"}), 401

        # Return user data with role-based permissions
        permissions = []
        if current_user.role == 'admin':
            permissions = ["all"]
        elif current_user.role == 'management':
            permissions = ["read_documents", "write_documents", "manage_communication", "manage_financial", "manage_tasks", "ai_assistant"]
        elif current_user.role == 'fm':
            permissions = ["read_documents", "write_documents", "manage_communication", "manage_tasks", "ai_assistant"]
        else:  # owners
            permissions = ["read_documents", "view_announcements", "view_financial", "view_tasks", "ai_assistant"]

        user_data = {
            "id": current_user.id,
            "email": current_user.email,
            "name": current_user.name,
            "full_name": current_user.full_name,
            "apartment": current_user.apartment,
            "apartment_number": current_user.apartment,  # For backward compatibility
            "role": current_user.role,
            "roles": [current_user.role],
            "permissions": permissions,
            "access_level": current_user.role,
            "is_admin": current_user.role == 'admin',
            "is_staff": current_user.role in ['admin', 'management', 'fm'],
            "is_resident": current_user.role == 'owners',
            "is_active": current_user.is_active,
            "email_verified": current_user.email_verified,
            "last_login": current_user.last_login.isoformat() if current_user.last_login else None,
            "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
            "preferences": {
                "notifications": True,
                "theme": "light",
                "language": "en"
            },
            "profile": {
                "avatar": None,
                "bio": f"{current_user.role.title()} at Gopalan Atlantis",
                "interests": []
            }
        }
        return jsonify(user_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/auth/status', methods=['GET'])
def get_auth_status():
    """Get authentication status"""
    try:
        return jsonify({
            "authenticated": True,
            "user_id": "user_1",
            "session_valid": True,
            "expires_at": "2024-12-31T23:59:59Z"
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Additional announcements endpoint (backup)
@app.route('/api/announcements/all', methods=['GET'])
def get_all_announcements():
    """Get all announcements (backup endpoint)"""
    try:
        announcements = [
            {
                "id": "1",
                "title": "Pool Maintenance Schedule",
                "content": "The swimming pool will be closed for maintenance on July 1st from 8 AM to 12 PM.",
                "priority": "high",
                "date": "2024-06-29T00:00:00Z",
                "created_by": "Management"
            }
        ]
        return jsonify({"announcements": announcements}), 200
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

# Register ClickUp routes
try:
    from routes.clickup_routes import clickup_bp
    app.register_blueprint(clickup_bp, url_prefix='/api/clickup')
    app.logger.info("Registered ClickUp routes")
except ImportError:
    app.logger.warning("ClickUp routes not found")

# Register Community Drive routes
try:
    from routes.community_drive_routes import community_drive_bp
    app.register_blueprint(community_drive_bp, url_prefix='/api/community-drive')
    app.logger.info("Registered Community Drive routes")
except ImportError:
    app.logger.warning("Community Drive routes not found")

# Register Firefly III routes
try:
    from routes.firefly_routes import firefly_bp
    app.register_blueprint(firefly_bp, url_prefix='/api/firefly')
    app.logger.info("Registered Firefly III routes")
except ImportError:
    app.logger.warning("Firefly III routes not found")

# Serve React frontend (catch-all route, must be last)
@app.route('/')
@app.route('/<path:path>')
def serve_frontend(path=''):
    """Serve the React frontend"""
    import os
    from flask import send_from_directory, send_file

    # Path to the built frontend
    frontend_dist = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'dist')

    # If path is empty or doesn't exist, serve index.html
    if path == '' or not os.path.exists(os.path.join(frontend_dist, path)):
        # If index.html does not exist, return a simple message
        index_path = os.path.join(frontend_dist, 'index.html')
        if os.path.exists(index_path):
            return send_file(index_path)
        else:
            return 'Frontend not built. Please deploy frontend separately.', 404

    # Serve the requested file
    return send_from_directory(frontend_dist, path)

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    # Force deployment to pick up new environment variables
    app.run(host='0.0.0.0', port=port)
