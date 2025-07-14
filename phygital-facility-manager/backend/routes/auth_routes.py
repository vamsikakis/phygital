from flask import Blueprint, request, jsonify, current_app
import os
import json
import uuid
import bcrypt
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
from services.email_service import email_service

# Load environment variables
load_dotenv()

# Create blueprint
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user and send password setup email
    """
    try:
        data = request.json

        if not data or 'email' not in data:
            return jsonify({'error': 'Missing required fields'}), 400

        email = data.get('email')
        name = data.get('name', '')
        apartment = data.get('apartment', '')
        role = data.get('role', 'owner')  # Default to 'owner' instead of 'resident'

        # Check if user already exists
        session = get_db_session()
        existing_user = session.query(User).filter(User.email == email).first()

        if existing_user:
            return jsonify({'error': 'User with this email already exists'}), 400

        # Create new user without password
        new_user = User(
            id=str(uuid.uuid4()),
            email=email,
            name=name,
            full_name=name,
            apartment=apartment,
            role=role,
            has_password=False,
            email_verified=False,
            is_active=True,
            created_at=datetime.utcnow()
        )

        session.add(new_user)
        session.commit()

        # Generate password setup token
        setup_token = email_service.generate_secure_token()

        # Store token in database
        if email_service.store_verification_token(email, setup_token, 'password_setup'):
            # Send password setup email
            if email_service.send_password_setup_email(email, name, setup_token):
                return jsonify({
                    'success': True,
                    'message': 'Account created successfully. Please check your email to set up your password.',
                    'user': {
                        'id': new_user.id,
                        'email': new_user.email,
                        'name': new_user.name,
                        'apartment': new_user.apartment,
                        'role': new_user.role,
                        'has_password': False
                    }
                })
            else:
                return jsonify({'error': 'Account created but failed to send setup email. Please contact support.'}), 500
        else:
            return jsonify({'error': 'Failed to generate setup token. Please try again.'}), 500

    except Exception as e:
        current_app.logger.error(f"Error registering user: {str(e)}")
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login with email and password
    """
    try:
        data = request.json

        if not data or 'email' not in data:
            return jsonify({'error': 'Missing required fields'}), 400

        email = data.get('email')
        password = data.get('password')

        # Find user
        session = get_db_session()
        user = session.query(User).filter(User.email == email).first()

        if not user:
            return jsonify({'error': 'Invalid email or password'}), 401

        if not user.is_active:
            return jsonify({'error': 'Account is deactivated. Please contact support.'}), 401

        # Check if user has set up password
        if not user.has_password or not user.password_hash:
            return jsonify({
                'error': 'Password not set up',
                'message': 'Please check your email for password setup instructions.',
                'requires_setup': True
            }), 401

        # Verify password
        if not password:
            return jsonify({'error': 'Password is required'}), 400

        if not bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            return jsonify({'error': 'Invalid email or password'}), 401

        # Update last login
        user.last_login = datetime.utcnow()
        session.commit()

        # Generate token
        token = generate_token(user.id, user.role)

        return jsonify({
            'token': token,
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'apartment': user.apartment,
                'role': user.role,
                'has_password': user.has_password,
                'email_verified': user.email_verified
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

@auth_bp.route('/setup-password', methods=['POST'])
def setup_password():
    """
    Set up password using email token
    """
    try:
        data = request.json

        if not data or 'token' not in data or 'email' not in data or 'password' not in data:
            return jsonify({'error': 'Missing required fields'}), 400

        token = data.get('token')
        email = data.get('email')
        password = data.get('password')

        # Validate password strength
        if len(password) < 8:
            return jsonify({'error': 'Password must be at least 8 characters long'}), 400

        # Verify token
        token_info = email_service.verify_token(email, token)
        if not token_info:
            return jsonify({'error': 'Invalid or expired token'}), 400

        if token_info['token_type'] != 'password_setup':
            return jsonify({'error': 'Invalid token type'}), 400

        # Hash password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Update user
        session = get_db_session()
        user = session.query(User).filter(User.email == email).first()

        if not user:
            return jsonify({'error': 'User not found'}), 404

        user.password_hash = password_hash
        user.has_password = True
        user.email_verified = True
        user.updated_at = datetime.utcnow()
        session.commit()

        # Clear verification token
        email_service.clear_verification_token(email)

        # Generate login token
        token = generate_token(user.id, user.role)

        return jsonify({
            'success': True,
            'message': 'Password set up successfully',
            'token': token,
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'apartment': user.apartment,
                'role': user.role,
                'has_password': True,
                'email_verified': True
            }
        })

    except Exception as e:
        current_app.logger.error(f"Error setting up password: {str(e)}")
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """
    Send password reset email
    """
    try:
        data = request.json

        if not data or 'email' not in data:
            return jsonify({'error': 'Email is required'}), 400

        email = data.get('email')

        # Find user
        session = get_db_session()
        user = session.query(User).filter(User.email == email).first()

        # Always return success to prevent email enumeration
        if not user:
            return jsonify({
                'success': True,
                'message': 'If an account with this email exists, you will receive a password reset email.'
            })

        if not user.has_password:
            return jsonify({
                'success': True,
                'message': 'If an account with this email exists, you will receive a password reset email.'
            })

        # Generate reset token
        reset_token = email_service.generate_secure_token()

        # Store token
        if email_service.store_verification_token(email, reset_token, 'password_reset'):
            # Send reset email
            email_service.send_password_reset_email(email, user.name, reset_token)

        return jsonify({
            'success': True,
            'message': 'If an account with this email exists, you will receive a password reset email.'
        })

    except Exception as e:
        current_app.logger.error(f"Error in forgot password: {str(e)}")
        return jsonify({'error': 'An error occurred. Please try again.'}), 500

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """
    Reset password using email token
    """
    try:
        data = request.json

        if not data or 'token' not in data or 'email' not in data or 'password' not in data:
            return jsonify({'error': 'Missing required fields'}), 400

        token = data.get('token')
        email = data.get('email')
        password = data.get('password')

        # Validate password strength
        if len(password) < 8:
            return jsonify({'error': 'Password must be at least 8 characters long'}), 400

        # Verify token
        token_info = email_service.verify_token(email, token)
        if not token_info:
            return jsonify({'error': 'Invalid or expired token'}), 400

        if token_info['token_type'] != 'password_reset':
            return jsonify({'error': 'Invalid token type'}), 400

        # Hash new password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Update user
        session = get_db_session()
        user = session.query(User).filter(User.email == email).first()

        if not user:
            return jsonify({'error': 'User not found'}), 404

        user.password_hash = password_hash
        user.updated_at = datetime.utcnow()
        session.commit()

        # Clear verification token
        email_service.clear_verification_token(email)

        return jsonify({
            'success': True,
            'message': 'Password reset successfully'
        })

    except Exception as e:
        current_app.logger.error(f"Error resetting password: {str(e)}")
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
