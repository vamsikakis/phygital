"""
Ultra Minimal Flask App for Deployment Testing
"""

import os
from flask import Flask, jsonify
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__)

# Configure CORS
CORS(app, origins=['*'])

# Basic health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "Backend is running"}), 200

# Basic API endpoint
@app.route('/api/test', methods=['GET'])
def test_endpoint():
    return jsonify({"message": "Test endpoint working", "status": "success"}), 200

# Root endpoint
@app.route('/', methods=['GET'])
def root():
    return jsonify({"message": "Phygital Facility Management API", "status": "running"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
