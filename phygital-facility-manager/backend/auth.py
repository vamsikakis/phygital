from flask import request, jsonify, g, current_app
from functools import wraps
import os
import jwt
import bcrypt
import secrets
from datetime import datetime, timedelta
from dotenv import load_dotenv
from db import get_db_session, User

# Load environment variables
load_dotenv()

# JWT configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_EXPIRATION = int(os.getenv("JWT_EXPIRATION", 86400))  # Default to 24 hours

def hash_password(password):
    """
    Hash a password using bcrypt

    Args:
        password: Plain text password

    Returns:
        Hashed password string
    """
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password, hashed_password):
    """
    Verify a password against its hash

    Args:
        password: Plain text password
        hashed_password: Hashed password from database

    Returns:
        bool: True if password matches, False otherwise
    """
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def generate_reset_token():
    """
    Generate a secure random token for password reset

    Returns:
        Random token string
    """
    return secrets.token_urlsafe(32)

def generate_token(user_id, role="owners", expiration=None):
    """
    Generate a JWT token for authentication

    Args:
        user_id: User ID for the token
        role: User role (admin, management, fm, owners)
        expiration: Token expiration in seconds

    Returns:
        JWT token string
    """
    if expiration is None:
        expiration = JWT_EXPIRATION

    payload = {
        'sub': user_id,
        'role': role,
        'exp': datetime.utcnow() + timedelta(seconds=expiration),
        'iat': datetime.utcnow()
    }

    return jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')

def decode_token(token):
    """
    Decode and validate a JWT token
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded token payload or None if invalid
    """
    try:
        return jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
    except jwt.PyJWTError as e:
        current_app.logger.error(f"Token validation error: {str(e)}")
        return None

def get_current_user():
    """
    Get the current authenticated user from the request
    
    Returns:
        User object or None if not authenticated
    """
    # Check if user already loaded in the request context
    if hasattr(g, 'current_user'):
        return g.current_user
        
    # Get token from header or query parameter
    auth_header = request.headers.get('Authorization')
    token = None
    
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
    else:
        token = request.args.get('token')
        
    if not token:
        return None
        
    # Decode and validate token
    payload = decode_token(token)
    if not payload:
        return None
        
    # Get user from database
    try:
        session = get_db_session()
        user = session.query(User).filter(User.id == payload['sub']).first()
        
        # Cache user in request context
        g.current_user = user
        return user
    except Exception as e:
        current_app.logger.error(f"Error fetching current user: {str(e)}")
        return None

def login_required(f):
    """Decorator for routes that require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user = get_current_user()
        
        if not current_user:
            return jsonify({
                'error': 'Unauthorized',
                'message': 'Authentication is required for this resource'
            }), 401
            
        return f(*args, **kwargs)
        
    return decorated_function

def admin_required(f):
    """Decorator for routes that require admin privileges"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user = get_current_user()

        if not current_user:
            return jsonify({
                'error': 'Unauthorized',
                'message': 'Authentication is required for this resource'
            }), 401

        if current_user.role != 'admin':
            return jsonify({
                'error': 'Forbidden',
                'message': 'Admin privileges are required for this resource'
            }), 403

        return f(*args, **kwargs)

    return decorated_function

def management_required(f):
    """Decorator for routes that require management or admin privileges"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user = get_current_user()

        if not current_user:
            return jsonify({
                'error': 'Unauthorized',
                'message': 'Authentication is required for this resource'
            }), 401

        if current_user.role not in ['admin', 'management']:
            return jsonify({
                'error': 'Forbidden',
                'message': 'Management privileges are required for this resource'
            }), 403

        return f(*args, **kwargs)

    return decorated_function

def fm_required(f):
    """Decorator for routes that require FM, management, or admin privileges"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user = get_current_user()

        if not current_user:
            return jsonify({
                'error': 'Unauthorized',
                'message': 'Authentication is required for this resource'
            }), 401

        if current_user.role not in ['admin', 'management', 'fm']:
            return jsonify({
                'error': 'Forbidden',
                'message': 'Facility Manager privileges are required for this resource'
            }), 403

        return f(*args, **kwargs)

    return decorated_function

def staff_required(f):
    """Decorator for routes that require staff privileges (management or fm) or admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user = get_current_user()

        if not current_user:
            return jsonify({
                'error': 'Unauthorized',
                'message': 'Authentication is required for this resource'
            }), 401

        if current_user.role not in ['admin', 'management', 'fm']:
            return jsonify({
                'error': 'Forbidden',
                'message': 'Staff privileges are required for this resource'
            }), 403

        return f(*args, **kwargs)

    return decorated_function

def validate_google_token(token):
    """
    Validate a Google OAuth token and get user info
    
    Args:
        token: Google ID token
        
    Returns:
        User info dictionary or None if invalid
    """
    try:
        from google.oauth2 import id_token
        from google.auth.transport import requests
        
        # Google OAuth client ID
        client_id = os.getenv("GOOGLE_CLIENT_ID")
        
        # Verify the token
        id_info = id_token.verify_oauth2_token(token, requests.Request(), client_id)
        
        # Check issuer
        if id_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            return None
            
        return id_info
    except Exception as e:
        current_app.logger.error(f"Google token validation error: {str(e)}")
        return None

def get_or_create_google_user(google_user_info):
    """
    Get or create a user from Google OAuth user info
    
    Args:
        google_user_info: User info from Google OAuth
        
    Returns:
        User object for the Google user
    """
    try:
        session = get_db_session()
        
        # Check if user exists by Google ID
        user = session.query(User).filter(User.google_id == google_user_info['sub']).first()
        
        if user:
            return user
            
        # Check if user exists by email
        user = session.query(User).filter(User.email == google_user_info['email']).first()
        
        if user:
            # Link Google ID to existing user
            user.google_id = google_user_info['sub']
            session.commit()
            return user
            
        # Create new user
        user = User(
            email=google_user_info['email'],
            name=google_user_info.get('name', ''),
            full_name=google_user_info.get('name', ''),
            google_id=google_user_info['sub'],
            role='resident',  # Default role
            created_at=datetime.utcnow()
        )
        
        session.add(user)
        session.commit()
        
        return user
    except Exception as e:
        current_app.logger.error(f"Error creating Google user: {str(e)}")
        return None
