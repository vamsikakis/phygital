"""
Phygital Facility Management API
"""

import os
from flask import Flask, jsonify, request
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__)

# Configure CORS to allow requests from frontend
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

# Auth endpoints
@app.route('/api/auth/register', methods=['POST'])
def register():
    """User registration endpoint"""
    try:
        data = request.get_json()

        # Basic validation
        if not data:
            return jsonify({"error": "No data provided"}), 400

        email = data.get('email')
        name = data.get('name')
        role = data.get('role', 'Owner')  # Default role

        if not email or not name:
            return jsonify({"error": "Email and name are required"}), 400

        # For now, just return success (we'll implement actual registration later)
        return jsonify({
            "message": "Registration successful",
            "user": {
                "email": email,
                "name": name,
                "role": role
            }
        }), 201

    except Exception as e:
        return jsonify({"error": "Registration failed", "details": str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        email = data.get('email')

        if not email:
            return jsonify({"error": "Email is required"}), 400

        # For now, just return success (we'll implement actual authentication later)
        return jsonify({
            "message": "Login successful",
            "user": {
                "email": email,
                "name": "Test User",
                "role": "Owner"
            },
            "token": "dummy_token_for_testing"
        }), 200

    except Exception as e:
        return jsonify({"error": "Login failed", "details": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
