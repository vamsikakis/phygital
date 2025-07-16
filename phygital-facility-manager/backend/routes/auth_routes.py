from flask import Blueprint, request, jsonify, current_app
import os
import json
import uuid
from datetime import datetime, timedelta
from dotenv import load_dotenv

from db import get_db_session, User
from auth import (
    generate_token,
    decode_token,
    get_current_user,
    login_required,
    admin_required,
    management_required,
    fm_required,
    staff_required,
    hash_password,
    verify_password,
    generate_reset_token,
    validate_google_token,
    get_or_create_google_user
)
from email_service import send_password_setup_email, send_password_reset_email, send_welcome_email

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
    Login with email and password
    """
    try:
        data = request.json

        if not data or 'email' not in data or 'password' not in data:
            return jsonify({'error': 'Email and password are required'}), 400

        email = data.get('email')
        password = data.get('password')

        # Find user
        session = get_db_session()
        user = session.query(User).filter(User.email == email).first()

        if not user:
            return jsonify({'error': 'Invalid email or password'}), 401

        # Check if user has a password set
        if not user.password_hash:
            return jsonify({'error': 'Password not set. Please check your email for setup instructions.'}), 401

        # Verify password
        if not verify_password(password, user.password_hash):
            return jsonify({'error': 'Invalid email or password'}), 401

        # Check if user is active
        if not user.is_active:
            return jsonify({'error': 'Account is deactivated. Please contact administrator.'}), 401

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
                'is_active': user.is_active,
                'email_verified': user.email_verified
            }
        })

    except Exception as e:
        current_app.logger.error(f"Error logging in: {str(e)}")
        return jsonify({'error': 'Login failed. Please try again.'}), 500

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
    Set up password for new users using setup token
    """
    try:
        data = request.json

        if not data or 'token' not in data or 'password' not in data:
            return jsonify({'error': 'Token and password are required'}), 400

        token = data.get('token')
        password = data.get('password')

        # Validate password strength
        if len(password) < 8:
            return jsonify({'error': 'Password must be at least 8 characters long'}), 400

        # Find user by reset token
        session = get_db_session()
        user = session.query(User).filter(
            User.reset_token == token,
            User.reset_token_expires > datetime.utcnow()
        ).first()

        if not user:
            return jsonify({'error': 'Invalid or expired setup token'}), 400

        # Set password
        user.password_hash = hash_password(password)
        user.reset_token = None
        user.reset_token_expires = None
        user.email_verified = True
        user.is_active = True
        user.updated_at = datetime.utcnow()

        session.commit()

        # Send welcome email
        send_welcome_email(user.email, user.name, user.role)

        return jsonify({
            'message': 'Password set successfully',
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'role': user.role
            }
        })

    except Exception as e:
        current_app.logger.error(f"Error setting up password: {str(e)}")
        return jsonify({'error': 'Failed to set up password. Please try again.'}), 500

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
        if user and user.is_active:
            # Generate reset token
            reset_token = generate_reset_token()
            user.reset_token = reset_token
            user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
            user.updated_at = datetime.utcnow()

            session.commit()

            # Send reset email
            send_password_reset_email(user.email, user.name, reset_token)

        return jsonify({
            'message': 'If an account with that email exists, a password reset link has been sent.'
        })

    except Exception as e:
        current_app.logger.error(f"Error sending password reset: {str(e)}")
        return jsonify({'error': 'Failed to send password reset email. Please try again.'}), 500

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """
    Reset password using reset token
    """
    try:
        data = request.json

        if not data or 'token' not in data or 'password' not in data:
            return jsonify({'error': 'Token and password are required'}), 400

        token = data.get('token')
        password = data.get('password')

        # Validate password strength
        if len(password) < 8:
            return jsonify({'error': 'Password must be at least 8 characters long'}), 400

        # Find user by reset token
        session = get_db_session()
        user = session.query(User).filter(
            User.reset_token == token,
            User.reset_token_expires > datetime.utcnow()
        ).first()

        if not user:
            return jsonify({'error': 'Invalid or expired reset token'}), 400

        # Update password
        user.password_hash = hash_password(password)
        user.reset_token = None
        user.reset_token_expires = None
        user.updated_at = datetime.utcnow()

        session.commit()

        return jsonify({'message': 'Password reset successfully'})

    except Exception as e:
        current_app.logger.error(f"Error resetting password: {str(e)}")
        return jsonify({'error': 'Failed to reset password. Please try again.'}), 500

@auth_bp.route('/register', methods=['POST'])
def register_user():
    """
    Public user registration endpoint
    """
    try:
        data = request.json

        if not data or 'email' not in data or 'name' not in data:
            return jsonify({'error': 'Email and name are required'}), 400

        email = data.get('email')
        name = data.get('name')
        role = data.get('role', 'owners')  # Default to owners
        apartment = data.get('apartment', '')

        # Validate role - only allow certain roles for public registration
        allowed_roles = ['owners', 'tenant']  # Management, FM and admin must be created by admin
        if role not in allowed_roles:
            role = 'owners'  # Default to owners if invalid role

        # Check if user already exists
        session = get_db_session()
        existing_user = session.query(User).filter(User.email == email).first()

        if existing_user:
            return jsonify({'error': 'User with this email already exists'}), 400

        # Generate setup token
        setup_token = generate_reset_token()

        # Create new user
        new_user = User(
            id=str(uuid.uuid4()),
            email=email,
            name=name,
            full_name=name,
            apartment=apartment,
            role=role,
            is_active=True,
            email_verified=False,
            reset_token=setup_token,
            reset_token_expires=datetime.utcnow() + timedelta(hours=24),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        session.add(new_user)
        session.commit()

        # Send password setup email
        print(f"Calling send_password_setup_email for {email}")
        email_sent = send_password_setup_email(email, name, setup_token)
        print(f"Email sent result: {email_sent}")

        return jsonify({
            'message': 'Registration successful! Please check your email to set up your password.',
            'user': {
                'id': new_user.id,
                'email': new_user.email,
                'name': new_user.name,
                'apartment': new_user.apartment,
                'role': new_user.role
            }
        }), 201

    except Exception as e:
        current_app.logger.error(f"Error during registration: {str(e)}")
        return jsonify({'error': 'Registration failed. Please try again.'}), 500

@auth_bp.route('/resend-setup', methods=['POST'])
def resend_setup_email():
    """
    Resend password setup email for users who haven't set their password
    """
    try:
        data = request.json

        if not data or 'email' not in data:
            return jsonify({'error': 'Email is required'}), 400

        email = data.get('email')

        # Find user
        session = get_db_session()
        user = session.query(User).filter(User.email == email).first()

        if not user:
            return jsonify({'error': 'User not found'}), 404

        if user.password_hash:
            return jsonify({'error': 'User already has a password set'}), 400

        # Generate new setup token
        setup_token = generate_reset_token()
        user.reset_token = setup_token
        user.reset_token_expires = datetime.utcnow() + timedelta(hours=24)
        user.updated_at = datetime.utcnow()

        session.commit()

        # Send password setup email
        print(f"Resending setup email to {email}")
        email_sent = send_password_setup_email(email, user.name, setup_token)
        print(f"Email sent result: {email_sent}")

        return jsonify({
            'message': 'Password setup email sent successfully!'
        })

    except Exception as e:
        current_app.logger.error(f"Error resending setup email: {str(e)}")
        return jsonify({'error': 'Failed to resend setup email. Please try again.'}), 500

@auth_bp.route('/test-email', methods=['POST'])
def test_email():
    """
    Test email service - for debugging only
    """
    try:
        data = request.json
        email = data.get('email', 'test@example.com')

        print(f"Testing email service with email: {email}")
        result = send_password_setup_email(email, "Test User", "test-token-123")
        print(f"Email test result: {result}")

        return jsonify({
            'message': f'Email test completed. Result: {result}',
            'email': email
        })

    except Exception as e:
        print(f"Email test error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/create-test-user', methods=['POST'])
def create_test_user():
    """
    Create a test user with password - for development only
    """
    try:
        data = request.json

        email = data.get('email', 'admin@gopalanatlantis.in')
        password = data.get('password', 'password123')
        name = data.get('name', 'Test Admin')
        role = data.get('role', 'admin')

        # Check if user already exists
        session = get_db_session()
        existing_user = session.query(User).filter(User.email == email).first()

        if existing_user:
            # Update existing user with password
            existing_user.password_hash = hash_password(password)
            existing_user.is_active = True
            existing_user.email_verified = True
            existing_user.reset_token = None
            existing_user.reset_token_expires = None
            existing_user.updated_at = datetime.utcnow()
            session.commit()

            return jsonify({
                'message': f'Updated existing user {email} with password',
                'user': {
                    'email': existing_user.email,
                    'name': existing_user.name,
                    'role': existing_user.role
                }
            })
        else:
            # Create new user with password
            new_user = User(
                id=str(uuid.uuid4()),
                email=email,
                password_hash=hash_password(password),
                name=name,
                full_name=name,
                apartment='',
                role=role,
                is_active=True,
                email_verified=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            session.add(new_user)
            session.commit()

            return jsonify({
                'message': f'Created test user {email} with password',
                'user': {
                    'email': new_user.email,
                    'name': new_user.name,
                    'role': new_user.role
                },
                'credentials': {
                    'email': email,
                    'password': password
                }
            })

    except Exception as e:
        print(f"Error creating test user: {str(e)}")
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

        users_data = []
        for user in users:
            users_data.append({
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'full_name': user.full_name,
                'apartment': user.apartment,
                'role': user.role,
                'is_active': user.is_active,
                'email_verified': user.email_verified,
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'created_at': user.created_at.isoformat() if user.created_at else None
            })

        return jsonify({'users': users_data})

    except Exception as e:
        current_app.logger.error(f"Error fetching users: {str(e)}")
        return jsonify({'error': 'Failed to fetch users'}), 500

@auth_bp.route('/users', methods=['POST'])
@admin_required
def create_user():
    """
    Create a new user (admin only)
    """
    try:
        data = request.json

        if not data or 'email' not in data or 'name' not in data or 'role' not in data:
            return jsonify({'error': 'Email, name, and role are required'}), 400

        email = data.get('email')
        name = data.get('name')
        role = data.get('role')
        apartment = data.get('apartment', '')

        # Validate role
        valid_roles = ['admin', 'management', 'fm', 'owners']
        if role not in valid_roles:
            return jsonify({'error': f'Invalid role. Must be one of: {", ".join(valid_roles)}'}), 400

        # Check if user already exists
        session = get_db_session()
        existing_user = session.query(User).filter(User.email == email).first()

        if existing_user:
            return jsonify({'error': 'User with this email already exists'}), 400

        # Generate setup token
        setup_token = generate_reset_token()

        # Create new user
        new_user = User(
            id=str(uuid.uuid4()),
            email=email,
            name=name,
            full_name=name,
            apartment=apartment,
            role=role,
            is_active=True,
            email_verified=False,
            reset_token=setup_token,
            reset_token_expires=datetime.utcnow() + timedelta(hours=24),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        session.add(new_user)
        session.commit()

        # Send password setup email
        send_password_setup_email(email, name, setup_token)

        return jsonify({
            'message': 'User created successfully. Password setup email sent.',
            'user': {
                'id': new_user.id,
                'email': new_user.email,
                'name': new_user.name,
                'apartment': new_user.apartment,
                'role': new_user.role
            }
        }), 201

    except Exception as e:
        current_app.logger.error(f"Error creating user: {str(e)}")
        return jsonify({'error': 'Failed to create user'}), 500

@auth_bp.route('/users/<user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    """
    Update a user (admin only)
    """
    try:
        data = request.json

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        session = get_db_session()
        user = session.query(User).filter(User.id == user_id).first()

        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Update allowed fields
        if 'name' in data:
            user.name = data['name']
            user.full_name = data['name']
        if 'apartment' in data:
            user.apartment = data['apartment']
        if 'role' in data:
            valid_roles = ['admin', 'management', 'fm', 'owners']
            if data['role'] not in valid_roles:
                return jsonify({'error': f'Invalid role. Must be one of: {", ".join(valid_roles)}'}), 400
            user.role = data['role']
        if 'is_active' in data:
            user.is_active = data['is_active']

        user.updated_at = datetime.utcnow()
        session.commit()

        return jsonify({
            'message': 'User updated successfully',
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'apartment': user.apartment,
                'role': user.role,
                'is_active': user.is_active
            }
        })

    except Exception as e:
        current_app.logger.error(f"Error updating user: {str(e)}")
        return jsonify({'error': 'Failed to update user'}), 500

@auth_bp.route('/users/<user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """
    Delete a user (admin only)
    """
    try:
        session = get_db_session()
        user = session.query(User).filter(User.id == user_id).first()

        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Don't allow deleting the current user
        current_user = get_current_user()
        if current_user.id == user_id:
            return jsonify({'error': 'Cannot delete your own account'}), 400

        session.delete(user)
        session.commit()

        return jsonify({'message': 'User deleted successfully'})

    except Exception as e:
        current_app.logger.error(f"Error deleting user: {str(e)}")
        return jsonify({'error': 'Failed to delete user'}), 500

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """
    Logout user (invalidate token on client side)
    """
    try:
        # In a stateless JWT system, logout is handled client-side
        # by removing the token from storage
        return jsonify({'message': 'Logged out successfully'})

    except Exception as e:
        current_app.logger.error(f"Error logging out: {str(e)}")
        return jsonify({'error': 'Logout failed'}), 500

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




