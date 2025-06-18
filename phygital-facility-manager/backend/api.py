from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler
import json
from datetime import datetime, date

# Load environment variables
load_dotenv()

# Import routes
from routes.document_routes import documents_bp
from routes.ai_query_routes import ai_query_bp
from routes.notification_routes import notification_bp
from routes.auth_routes import auth_bp
from routes.financial_routes import financial_bp
from routes.document_operations_routes import doc_operations_bp
from routes.ticket_routes import ticket_bp

# Create Flask app
app = Flask(__name__)

# Configure CORS
CORS(app, resources={r"/*": {"origins": "*"}})

# Configure logging
if not os.path.exists('logs'):
    os.mkdir('logs')
    
file_handler = RotatingFileHandler('logs/api.log', maxBytes=10485760, backupCount=10)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)

app.logger.setLevel(logging.INFO)
app.logger.info('Facility Manager API startup')

# JSON encoder for datetime objects
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            if isinstance(obj, datetime):
                return obj.isoformat()
            elif isinstance(obj, date):
                return obj.isoformat()
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return json.JSONEncoder.default(self, obj)

app.json_encoder = CustomJSONEncoder

# Register blueprints
app.register_blueprint(documents_bp, url_prefix='/api/documents')
app.register_blueprint(ai_query_bp, url_prefix='/api/ai-query')
app.register_blueprint(notification_bp, url_prefix='/api/notifications')
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(financial_bp, url_prefix='/api/financial')
app.register_blueprint(doc_operations_bp, url_prefix='/api/document-operations')
app.register_blueprint(ticket_bp, url_prefix='/api/tickets')

# Root routes
@app.route('/')
def index():
    return jsonify({
        'name': 'Gopalan Atlantis Facility Manager API',
        'version': '1.0.0',
        'status': 'online'
    })

@app.route('/api/health')
def health():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'environment': os.getenv('FLASK_ENV', 'development')
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Not Found',
        'message': 'The requested resource was not found'
    }), 404

@app.errorhandler(500)
def server_error(error):
    app.logger.error(f"Server error: {str(error)}")
    return jsonify({
        'error': 'Internal Server Error',
        'message': 'An unexpected error occurred'
    }), 500

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        'error': 'Bad Request',
        'message': str(error)
    }), 400

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        'error': 'Unauthorized',
        'message': 'Authentication is required'
    }), 401

@app.errorhandler(403)
def forbidden(error):
    return jsonify({
        'error': 'Forbidden',
        'message': 'You do not have permission to access this resource'
    }), 403

if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_ENV') == 'development', 
            host=os.getenv('FLASK_HOST', '0.0.0.0'), 
            port=int(os.getenv('FLASK_PORT', 5000)))
