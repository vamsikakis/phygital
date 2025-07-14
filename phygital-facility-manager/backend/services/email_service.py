"""
Email Service for Authentication
Handles password setup, reset, and verification emails
"""

import os
import requests
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Optional
from flask import current_app
from db import get_db_session, User

class EmailService:
    def __init__(self):
        self.api_key = os.getenv('RESEND_API_KEY')
        self.from_email = os.getenv('FROM_EMAIL', 'noreply@thephygital.in')
        self.base_url = os.getenv('FRONTEND_URL', 'https://www.thephygital.in')
        
        if not self.api_key:
            current_app.logger.warning("Resend API key not configured")
    
    def send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        """Send email using Resend API"""
        if not self.api_key:
            current_app.logger.error("Email service not configured")
            return False
        
        try:
            response = requests.post(
                'https://api.resend.com/emails',
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json',
                },
                json={
                    'from': self.from_email,
                    'to': [to_email],
                    'subject': subject,
                    'html': html_content,
                }
            )
            
            if response.status_code == 200:
                current_app.logger.info(f"Email sent successfully to {to_email}")
                return True
            else:
                current_app.logger.error(f"Failed to send email: {response.text}")
                return False
                
        except Exception as e:
            current_app.logger.error(f"Email service error: {e}")
            return False
    
    def generate_secure_token(self) -> str:
        """Generate a secure token for email verification"""
        return secrets.token_urlsafe(32)
    
    def hash_token(self, token: str) -> str:
        """Hash token for secure storage"""
        return hashlib.sha256(token.encode()).hexdigest()
    
    def send_password_setup_email(self, user_email: str, user_name: str, token: str) -> bool:
        """Send password setup email to new users"""
        setup_url = f"{self.base_url}/setup-password?token={token}&email={user_email}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Welcome to Gopalan Atlantis</title>
            <style>
                body {{ font-family: 'Inter', Arial, sans-serif; margin: 0; padding: 0; background-color: #f5f5f7; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; }}
                .header {{ background: linear-gradient(135deg, #5B5CE6 0%, #7C7CE8 100%); padding: 40px 20px; text-align: center; }}
                .header h1 {{ color: white; margin: 0; font-size: 28px; font-weight: 700; }}
                .header p {{ color: rgba(255,255,255,0.9); margin: 10px 0 0 0; font-size: 16px; }}
                .content {{ padding: 40px 20px; }}
                .content h2 {{ color: #1D1D1F; margin: 0 0 20px 0; font-size: 24px; }}
                .content p {{ color: #6E6E73; line-height: 1.6; margin: 0 0 20px 0; }}
                .button {{ display: inline-block; background: linear-gradient(135deg, #5B5CE6 0%, #7C7CE8 100%); 
                          color: white; text-decoration: none; padding: 16px 32px; border-radius: 12px; 
                          font-weight: 600; margin: 20px 0; }}
                .footer {{ background-color: #f5f5f7; padding: 20px; text-align: center; color: #6E6E73; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>GOPALAN ATLANTIS</h1>
                    <p>Facility Management System</p>
                </div>
                <div class="content">
                    <h2>Welcome, {user_name}!</h2>
                    <p>Your account has been created successfully. To complete your registration and secure your account, please set up your password by clicking the button below.</p>
                    
                    <a href="{setup_url}" class="button">Set Up Password</a>
                    
                    <p>This link will expire in 24 hours for security reasons.</p>
                    
                    <p>If you didn't request this account, please ignore this email.</p>
                    
                    <p>Best regards,<br>The Gopalan Atlantis Team</p>
                </div>
                <div class="footer">
                    <p>© 2025 Gopalan Atlantis Facility Management. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(
            to_email=user_email,
            subject="Welcome to Gopalan Atlantis - Set Up Your Password",
            html_content=html_content
        )
    
    def send_password_reset_email(self, user_email: str, user_name: str, token: str) -> bool:
        """Send password reset email"""
        reset_url = f"{self.base_url}/reset-password?token={token}&email={user_email}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Reset Your Password - Gopalan Atlantis</title>
            <style>
                body {{ font-family: 'Inter', Arial, sans-serif; margin: 0; padding: 0; background-color: #f5f5f7; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; }}
                .header {{ background: linear-gradient(135deg, #5B5CE6 0%, #7C7CE8 100%); padding: 40px 20px; text-align: center; }}
                .header h1 {{ color: white; margin: 0; font-size: 28px; font-weight: 700; }}
                .header p {{ color: rgba(255,255,255,0.9); margin: 10px 0 0 0; font-size: 16px; }}
                .content {{ padding: 40px 20px; }}
                .content h2 {{ color: #1D1D1F; margin: 0 0 20px 0; font-size: 24px; }}
                .content p {{ color: #6E6E73; line-height: 1.6; margin: 0 0 20px 0; }}
                .button {{ display: inline-block; background: linear-gradient(135deg, #5B5CE6 0%, #7C7CE8 100%); 
                          color: white; text-decoration: none; padding: 16px 32px; border-radius: 12px; 
                          font-weight: 600; margin: 20px 0; }}
                .footer {{ background-color: #f5f5f7; padding: 20px; text-align: center; color: #6E6E73; font-size: 14px; }}
                .warning {{ background-color: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 8px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>GOPALAN ATLANTIS</h1>
                    <p>Facility Management System</p>
                </div>
                <div class="content">
                    <h2>Password Reset Request</h2>
                    <p>Hello {user_name},</p>
                    <p>We received a request to reset your password for your Gopalan Atlantis account. Click the button below to create a new password.</p>
                    
                    <a href="{reset_url}" class="button">Reset Password</a>
                    
                    <div class="warning">
                        <p><strong>Security Notice:</strong> This link will expire in 1 hour for security reasons. If you didn't request this password reset, please ignore this email and your password will remain unchanged.</p>
                    </div>
                    
                    <p>Best regards,<br>The Gopalan Atlantis Team</p>
                </div>
                <div class="footer">
                    <p>© 2025 Gopalan Atlantis Facility Management. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(
            to_email=user_email,
            subject="Reset Your Password - Gopalan Atlantis",
            html_content=html_content
        )
    
    def store_verification_token(self, user_email: str, token: str, token_type: str = 'password_setup') -> bool:
        """Store verification token in database"""
        try:
            session = get_db_session()
            user = session.query(User).filter(User.email == user_email).first()
            
            if not user:
                return False
            
            # Hash the token for security
            hashed_token = self.hash_token(token)
            
            # Set expiration (24 hours for setup, 1 hour for reset)
            expiration_hours = 24 if token_type == 'password_setup' else 1
            expiration = datetime.utcnow() + timedelta(hours=expiration_hours)
            
            # Store token info (you might want to create a separate tokens table)
            user.verification_token = hashed_token
            user.token_expiration = expiration
            user.token_type = token_type
            
            session.commit()
            return True
            
        except Exception as e:
            current_app.logger.error(f"Error storing verification token: {e}")
            return False
    
    def verify_token(self, user_email: str, token: str) -> Optional[Dict]:
        """Verify token and return user info if valid"""
        try:
            session = get_db_session()
            user = session.query(User).filter(User.email == user_email).first()
            
            if not user or not user.verification_token:
                return None
            
            # Check if token matches
            hashed_token = self.hash_token(token)
            if user.verification_token != hashed_token:
                return None
            
            # Check if token is expired
            if user.token_expiration and user.token_expiration < datetime.utcnow():
                return None
            
            return {
                'user_id': user.id,
                'email': user.email,
                'name': user.name,
                'token_type': getattr(user, 'token_type', 'password_setup')
            }
            
        except Exception as e:
            current_app.logger.error(f"Error verifying token: {e}")
            return None
    
    def clear_verification_token(self, user_email: str) -> bool:
        """Clear verification token after use"""
        try:
            session = get_db_session()
            user = session.query(User).filter(User.email == user_email).first()
            
            if user:
                user.verification_token = None
                user.token_expiration = None
                user.token_type = None
                session.commit()
                return True
            
            return False
            
        except Exception as e:
            current_app.logger.error(f"Error clearing verification token: {e}")
            return False

# Create global instance
email_service = EmailService()
