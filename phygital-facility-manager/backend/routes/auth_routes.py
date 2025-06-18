from flask import Blueprint, request, jsonify, current_app
import os
import json
import uuid
from datetime import datetime
from dotenv import load_dotenv

from db import get_db_session, User
from auth import (
    generate_token, 
    decode_token, 
    get_current_user, 
    login_required,
    admin_required,
    validate_google_token,
    get_or_create_google_user
)

# Load environment variables
load_dotenv()

# Create blueprint
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user
    """
    try:
        data = request.json
        
        if not data or 'email' not in data:
            return jsonify({'error': 'Missing required fields'}), 400
            
        email = data.get('email')
        name = data.get('name', '')
        apartment = data.get('apartment', '')
        role = data.get('role', 'resident')
        
        # Check if user already exists
        session = get_db_session()
        existing_user = session.query(User).filter(User.email == email).first()
        
        if existing_user:
            return jsonify({'error': 'User with this email already exists'}), 400
            
        # Create new user
        new_user = User(
            id=str(uuid.uuid4()),
            email=email,
            name=name,
            full_name=name,
            apartment=apartment,
            role=role,
            created_at=datetime.utcnow()
        )
        
        session.add(new_user)
        session.commit()
        
        # Generate token
        token = generate_token(new_user.id, new_user.role)
        
        return jsonify({
            'token': token,
            'user': {
                'id': new_user.id,
                'email': new_user.email,
                'name': new_user.name,
                'apartment': new_user.apartment,
                'role': new_user.role
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error registering user: {str(e)}")
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login with email
    """
    try:
        data = request.json
        
        if not data or 'email' not in data:
            return jsonify({'error': 'Missing required fields'}), 400
            
        email = data.get('email')
        
        # Find user
        session = get_db_session()
        user = session.query(User).filter(User.email == email).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        # Generate token
        token = generate_token(user.id, user.role)
        
        return jsonify({
            'token': token,
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'apartment': user.apartment,
                'role': user.role
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error logging in: {str(e)}")
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/google-auth', methods=['POST'])
def google_auth():
    """
    Login with Google OAuth
    """
    try:
        data = request.json
        
        if not data or 'token' not in data:
            return jsonify({'error': 'Missing Google token'}), 400
            
        google_token = data.get('token')
        
        # Validate Google token
        google_user_info = validate_google_token(google_token)
        
        if not google_user_info:
            return jsonify({'error': 'Invalid Google token'}), 400
            
        # Get or create user
        user = get_or_create_google_user(google_user_info)
        
        if not user:
            return jsonify({'error': 'Failed to create user'}), 500
            
        # Generate token
        token = generate_token(user.id, user.role)
        
        return jsonify({
            'token': token,
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'apartment': user.apartment,
                'role': user.role
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error with Google authentication: {str(e)}")
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/verify', methods=['GET'])
def verify_token():
    """
    Verify a token and get user info
    """
    try:
        current_user = get_current_user()
        
        if not current_user:
            return jsonify({'valid': False}), 401
            
        return jsonify({
            'valid': True,
            'user': {
                'id': current_user.id,
                'email': current_user.email,
                'name': current_user.name,
                'apartment': current_user.apartment,
                'role': current_user.role
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error verifying token: {str(e)}")
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/refresh', methods=['POST'])
def refresh_token():
    """
    Refresh an authentication token
    """
    try:
        current_user = get_current_user()
        
        if not current_user:
            return jsonify({'error': 'Invalid or expired token'}), 401
            
        # Generate new token
        token = generate_token(current_user.id, current_user.role)
        
        return jsonify({
            'token': token,
            'user': {
                'id': current_user.id,
                'email': current_user.email,
                'name': current_user.name,
                'apartment': current_user.apartment,
                'role': current_user.role
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error refreshing token: {str(e)}")
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/user', methods=['GET'])
@login_required
def get_user_info():
    """
    Get current user information
    """
    try:
        current_user = get_current_user()
        
        return jsonify({
            'user': {
                'id': current_user.id,
                'email': current_user.email,
                'name': current_user.name,
                'apartment': current_user.apartment,
                'role': current_user.role
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting user info: {str(e)}")
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/user', methods=['PUT'])
@login_required
def update_user_info():
    """
    Update user information
    """
    try:
        data = request.json
        current_user = get_current_user()
        
        if not data:
            return jsonify({'error': 'No update data provided'}), 400
            
        session = get_db_session()
        user = session.query(User).filter(User.id == current_user.id).first()
        
        # Update fields
        if 'name' in data:
            user.name = data['name']
            user.full_name = data['name']
        if 'apartment' in data:
            user.apartment = data['apartment']
        
        session.commit()
        
        return jsonify({
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'apartment': user.apartment,
                'role': user.role
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error updating user info: {str(e)}")
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/users', methods=['GET'])
@admin_required
def get_users():
    """
    Get all users (admin only)
    """
    try:
        session = get_db_session()
        users = session.query(User).all()
        
        result = []
        for user in users:
            result.append({
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'apartment': user.apartment,
                'role': user.role,
                'created_at': user.created_at.isoformat() if user.created_at else None
            })
            
        return jsonify({
            'users': result
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting users: {str(e)}")
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/users/<user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    """
    Update user information (admin only)
    """
    try:
        data = request.json
        
        if not data:
            return jsonify({'error': 'No update data provided'}), 400
            
        session = get_db_session()
        user = session.query(User).filter(User.id == user_id).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        # Update fields
        if 'name' in data:
            user.name = data['name']
            user.full_name = data['name']
        if 'apartment' in data:
            user.apartment = data['apartment']
        if 'role' in data:
            user.role = data['role']
        
        session.commit()
        
        return jsonify({
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'apartment': user.apartment,
                'role': user.role
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error updating user: {str(e)}")
        return jsonify({'error': str(e)}), 500
