from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize database
from database import db, init_app
app = init_app(app)

# Import routes
from routes.ai_query_routes import ai_query_bp
from routes.document_routes import document_routes
from routes.financial_routes import financial_routes
from routes.verba_routes import verba_bp

# Register blueprints
app.register_blueprint(ai_query_bp, url_prefix='/api')
app.register_blueprint(document_routes, url_prefix='')
app.register_blueprint(financial_routes, url_prefix='/api')
app.register_blueprint(verba_bp, url_prefix='')

@app.route('/')
def index():
    return jsonify({"message": "Gopalan Atlantis Facility Manager API"})

@app.route('/uploads/<path:filename>')
def serve_uploads(filename):
    """Serve uploaded files"""
    upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    return send_from_directory(upload_dir, filename)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
