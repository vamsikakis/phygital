"""
Email service using Resend for authentication-related emails
"""

import os
import resend
from flask import current_app
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Resend
resend.api_key = os.getenv("RESEND_API_KEY")

def send_password_setup_email(email, name, setup_token):
    """
    Send password setup email to new users
    
    Args:
        email: User's email address
        name: User's name
        setup_token: Token for password setup
        
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
        setup_url = f"{frontend_url}/setup-password?token={setup_token}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Welcome to Gopalan Atlantis</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(45deg, #3f51b5 30%, #7986cb 90%); color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background: #f9f9f9; }}
                .button {{ display: inline-block; padding: 12px 24px; background: #3f51b5; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ padding: 20px; text-align: center; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Welcome to Gopalan Atlantis</h1>
                    <p>Your Facility Management Portal</p>
                </div>
                <div class="content">
                    <h2>Hello {name},</h2>
                    <p>Welcome to the Gopalan Atlantis facility management system! Your account has been created and you need to set up your password to get started.</p>
                    
                    <p>Click the button below to set up your password:</p>
                    <a href="{setup_url}" class="button">Set Up Password</a>
                    
                    <p>If the button doesn't work, copy and paste this link into your browser:</p>
                    <p><a href="{setup_url}">{setup_url}</a></p>
                    
                    <p>This link will expire in 24 hours for security reasons.</p>
                    
                    <p>If you didn't expect this email, please contact the facility management team.</p>
                </div>
                <div class="footer">
                    <p>© 2025 Gopalan Atlantis. All rights reserved.</p>
                    <p>This is an automated email. Please do not reply to this message.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Welcome to Gopalan Atlantis!
        
        Hello {name},
        
        Welcome to the Gopalan Atlantis facility management system! Your account has been created and you need to set up your password to get started.
        
        Please visit the following link to set up your password:
        {setup_url}
        
        This link will expire in 24 hours for security reasons.
        
        If you didn't expect this email, please contact the facility management team.
        
        © 2025 Gopalan Atlantis. All rights reserved.
        """
        
        params = {
            "from": os.getenv("FROM_EMAIL", "noreply@gopalanatlantis.in"),
            "to": [email],
            "subject": "Welcome to Gopalan Atlantis - Set Up Your Password",
            "html": html_content,
            "text": text_content
        }
        
        print(f"Attempting to send email to {email} with API key: {os.getenv('RESEND_API_KEY')[:10]}...")
        response = resend.Emails.send(params)
        print(f"Email response: {response}")
        current_app.logger.info(f"Password setup email sent to {email}: {response}")
        return True
        
    except Exception as e:
        current_app.logger.error(f"Failed to send password setup email to {email}: {str(e)}")
        return False

def send_password_reset_email(email, name, reset_token):
    """
    Send password reset email
    
    Args:
        email: User's email address
        name: User's name
        reset_token: Token for password reset
        
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
        reset_url = f"{frontend_url}/reset-password?token={reset_token}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Password Reset - Gopalan Atlantis</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(45deg, #3f51b5 30%, #7986cb 90%); color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background: #f9f9f9; }}
                .button {{ display: inline-block; padding: 12px 24px; background: #3f51b5; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ padding: 20px; text-align: center; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Password Reset</h1>
                    <p>Gopalan Atlantis</p>
                </div>
                <div class="content">
                    <h2>Hello {name},</h2>
                    <p>We received a request to reset your password for your Gopalan Atlantis account.</p>
                    
                    <p>Click the button below to reset your password:</p>
                    <a href="{reset_url}" class="button">Reset Password</a>
                    
                    <p>If the button doesn't work, copy and paste this link into your browser:</p>
                    <p><a href="{reset_url}">{reset_url}</a></p>
                    
                    <p>This link will expire in 1 hour for security reasons.</p>
                    
                    <p>If you didn't request a password reset, please ignore this email or contact the facility management team if you have concerns.</p>
                </div>
                <div class="footer">
                    <p>© 2025 Gopalan Atlantis. All rights reserved.</p>
                    <p>This is an automated email. Please do not reply to this message.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Password Reset - Gopalan Atlantis
        
        Hello {name},
        
        We received a request to reset your password for your Gopalan Atlantis account.
        
        Please visit the following link to reset your password:
        {reset_url}
        
        This link will expire in 1 hour for security reasons.
        
        If you didn't request a password reset, please ignore this email or contact the facility management team if you have concerns.
        
        © 2025 Gopalan Atlantis. All rights reserved.
        """
        
        params = {
            "from": os.getenv("FROM_EMAIL", "noreply@gopalanatlantis.in"),
            "to": [email],
            "subject": "Password Reset - Gopalan Atlantis",
            "html": html_content,
            "text": text_content
        }
        
        response = resend.Emails.send(params)
        current_app.logger.info(f"Password reset email sent to {email}: {response}")
        return True
        
    except Exception as e:
        current_app.logger.error(f"Failed to send password reset email to {email}: {str(e)}")
        return False

def send_welcome_email(email, name, role):
    """
    Send welcome email after successful password setup
    
    Args:
        email: User's email address
        name: User's name
        role: User's role in the system
        
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
        
        role_descriptions = {
            'admin': 'Administrator with full system access',
            'management': 'Management team member with oversight capabilities',
            'fm': 'Facility Manager with operational access',
            'owners': 'Property owner with resident access'
        }
        
        role_description = role_descriptions.get(role, 'System user')
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Welcome to Gopalan Atlantis</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(45deg, #3f51b5 30%, #7986cb 90%); color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background: #f9f9f9; }}
                .button {{ display: inline-block; padding: 12px 24px; background: #3f51b5; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ padding: 20px; text-align: center; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Welcome to Gopalan Atlantis!</h1>
                    <p>Your account is now active</p>
                </div>
                <div class="content">
                    <h2>Hello {name},</h2>
                    <p>Congratulations! Your Gopalan Atlantis account has been successfully set up.</p>
                    
                    <p><strong>Your Role:</strong> {role_description}</p>
                    
                    <p>You can now access the facility management portal using your email and password.</p>
                    
                    <a href="{frontend_url}" class="button">Access Portal</a>
                    
                    <p>If you have any questions or need assistance, please contact the facility management team.</p>
                </div>
                <div class="footer">
                    <p>© 2025 Gopalan Atlantis. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        params = {
            "from": os.getenv("FROM_EMAIL", "noreply@gopalanatlantis.in"),
            "to": [email],
            "subject": "Welcome to Gopalan Atlantis - Account Active",
            "html": html_content
        }
        
        response = resend.Emails.send(params)
        current_app.logger.info(f"Welcome email sent to {email}: {response}")
        return True
        
    except Exception as e:
        current_app.logger.error(f"Failed to send welcome email to {email}: {str(e)}")
        return False
