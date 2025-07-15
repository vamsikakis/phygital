#!/usr/bin/env python3
"""
Minimal Flask app for testing Render deployment
This helps isolate deployment issues from application complexity
"""

import os
from flask import Flask, jsonify
from flask_cors import CORS

# Create Flask app
app = Flask(__name__)
CORS(app)

# Basic configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'test-secret-key')

@app.route('/', methods=['GET'])
def root():
    """Root endpoint"""
    return jsonify({
        "message": "Phygital Facility Manager API - Minimal Test",
        "status": "running",
        "environment": os.getenv('FLASK_ENV', 'unknown'),
        "port": os.getenv('PORT', '5000')
    })

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "phygital-backend-minimal",
        "environment": os.getenv('FLASK_ENV', 'unknown')
    })

@app.route('/api/test', methods=['GET'])
def api_test():
    """Test API endpoint"""
    return jsonify({
        "message": "API is working",
        "endpoints": [
            "/health",
            "/api/test",
            "/api/assistant/init"
        ]
    })

@app.route('/api/assistant/init', methods=['GET'])
def assistant_init_test():
    """Test assistant initialization endpoint"""
    try:
        # Check if OpenAI API key is available
        openai_key = os.getenv('OPENAI_API_KEY')
        if not openai_key:
            return jsonify({
                "error": "OPENAI_API_KEY not configured",
                "status": "failed"
            }), 500
        
        # Check if database URL is available
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            return jsonify({
                "error": "DATABASE_URL not configured", 
                "status": "failed"
            }), 500
        
        return jsonify({
            "message": "Assistant initialization test successful",
            "status": "ready",
            "openai_configured": bool(openai_key),
            "database_configured": bool(db_url),
            "assistant_id": "test-mode",
            "vector_store_id": "test-mode"
        })
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "status": "failed"
        }), 500

@app.route('/api/env-check', methods=['GET'])
def env_check():
    """Check environment variables (for debugging)"""
    env_vars = {
        'FLASK_ENV': os.getenv('FLASK_ENV'),
        'PORT': os.getenv('PORT'),
        'DATABASE_URL': 'SET' if os.getenv('DATABASE_URL') else 'NOT SET',
        'OPENAI_API_KEY': 'SET' if os.getenv('OPENAI_API_KEY') else 'NOT SET',
        'SECRET_KEY': 'SET' if os.getenv('SECRET_KEY') else 'NOT SET'
    }
    
    return jsonify({
        "environment_variables": env_vars,
        "status": "checked"
    })

if __name__ == '__main__':
    # Get port from environment variable (Render sets this)
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    print(f"Starting minimal Flask app on port {port}")
    print(f"Debug mode: {debug}")
    print(f"Environment: {os.getenv('FLASK_ENV', 'unknown')}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
