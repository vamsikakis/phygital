import os
import pickle
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from dotenv import load_dotenv
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from cryptography.fernet import Fernet
import time

# Load environment variables
load_dotenv()

# Google API credentials
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
GOOGLE_REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI')
GMAIL_SCOPES = os.getenv('GMAIL_SCOPES', '').split(' ')
GDRIVE_SCOPES = os.getenv('GDRIVE_SCOPES', '').split(' ')

# Combined scopes for a single OAuth flow
ALL_SCOPES = list(set(GMAIL_SCOPES + GDRIVE_SCOPES))

# For token encryption
TOKEN_ENCRYPTION_KEY = os.getenv('TOKEN_ENCRYPTION_KEY')
cipher_suite = Fernet(base64.b64encode(TOKEN_ENCRYPTION_KEY.encode()[:32]))

# Directory for storing tokens
TOKENS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tokens')
os.makedirs(TOKENS_DIR, exist_ok=True)

def create_oauth_flow():
    """Create a OAuth2 flow instance to manage the OAuth 2.0 Authorization Grant Flow."""
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [GOOGLE_REDIRECT_URI]
            }
        },
        scopes=ALL_SCOPES
    )
    flow.redirect_uri = GOOGLE_REDIRECT_URI
    return flow

def get_authorization_url():
    """Get the authorization URL to redirect users to."""
    flow = create_oauth_flow()
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    return authorization_url, state

def exchange_code_for_token(code, state):
    """Exchange authorization code for refresh and access tokens."""
    flow = create_oauth_flow()
    flow.fetch_token(code=code)
    credentials = flow.credentials
    
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes,
        'expiry': credentials.expiry.isoformat() if credentials.expiry else None
    }

def save_token(user_id, token_data):
    """Save token data for a user, encrypted."""
    token_path = os.path.join(TOKENS_DIR, f"{user_id}.enc")
    encrypted_token = cipher_suite.encrypt(json.dumps(token_data).encode())
    with open(token_path, 'wb') as token_file:
        token_file.write(encrypted_token)

def load_token(user_id):
    """Load and decrypt token data for a user."""
    token_path = os.path.join(TOKENS_DIR, f"{user_id}.enc")
    if not os.path.exists(token_path):
        return None
    
    with open(token_path, 'rb') as token_file:
        encrypted_token = token_file.read()
    
    try:
        decrypted_token = cipher_suite.decrypt(encrypted_token).decode()
        return json.loads(decrypted_token)
    except Exception as e:
        print(f"Error decrypting token: {e}")
        return None

def get_credentials(user_id):
    """Get valid credentials for the given user."""
    token_data = load_token(user_id)
    if not token_data:
        return None
    
    credentials = Credentials(
        token=token_data.get('token'),
        refresh_token=token_data.get('refresh_token'),
        token_uri=token_data.get('token_uri'),
        client_id=token_data.get('client_id'),
        client_secret=token_data.get('client_secret'),
        scopes=token_data.get('scopes')
    )
    
    # If the token is expired, refresh it
    if credentials.expired:
        try:
            credentials.refresh(Request())
            # Update the stored token
            token_data['token'] = credentials.token
            token_data['expiry'] = credentials.expiry.isoformat() if credentials.expiry else None
            save_token(user_id, token_data)
        except Exception as e:
            print(f"Error refreshing token: {e}")
            return None
    
    return credentials

# Gmail integration functions
def get_gmail_service(user_id):
    """Get a Gmail service instance for the user."""
    credentials = get_credentials(user_id)
    if not credentials:
        return None
    
    return build('gmail', 'v1', credentials=credentials)

def send_email(user_id, to, subject, body_text=None, body_html=None, attachments=None):
    """
    Send an email using the Gmail API.
    
    Args:
        user_id: User ID for credentials
        to: Email address of the recipient
        subject: Subject of the email
        body_text: Plain text email body
        body_html: HTML email body (optional)
        attachments: List of file paths to attach
    
    Returns:
        The sent message ID if successful, None otherwise
    """
    service = get_gmail_service(user_id)
    if not service:
        return None
    
    message = MIMEMultipart('alternative') if body_html else MIMEMultipart()
    message['to'] = to
    message['subject'] = subject
    
    if body_text:
        message.attach(MIMEText(body_text, 'plain'))
    
    if body_html:
        message.attach(MIMEText(body_html, 'html'))
    
    # Add attachments if any
    if attachments:
        for file_path in attachments:
            if os.path.isfile(file_path):
                with open(file_path, 'rb') as file:
                    part = MIMEApplication(file.read(), Name=os.path.basename(file_path))
                part['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
                message.attach(part)
    
    # Encode the message
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    
    try:
        message = service.users().messages().send(userId='me', body={'raw': raw_message}).execute()
        return message.get('id')
    except Exception as e:
        print(f"Error sending email: {e}")
        return None

def list_emails(user_id, query='', max_results=10):
    """
    List emails from the user's Gmail account.
    
    Args:
        user_id: User ID for credentials
        query: Gmail search query
        max_results: Maximum number of emails to return
        
    Returns:
        List of emails if successful, empty list otherwise
    """
    service = get_gmail_service(user_id)
    if not service:
        return []
    
    try:
        results = service.users().messages().list(userId='me', q=query, maxResults=max_results).execute()
        messages = results.get('messages', [])
        
        if not messages:
            return []
        
        emails = []
        for msg in messages:
            message = service.users().messages().get(userId='me', id=msg['id']).execute()
            
            # Extract header data
            headers = message['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
            date = next((h['value'] for h in headers if h['name'] == 'Date'), '')
            
            # Get snippet
            snippet = message.get('snippet', '')
            
            emails.append({
                'id': message['id'],
                'sender': sender,
                'subject': subject,
                'date': date,
                'snippet': snippet
            })
        
        return emails
    except Exception as e:
        print(f"Error listing emails: {e}")
        return []

# Google Drive integration functions
def get_drive_service(user_id):
    """Get a Google Drive service instance for the user."""
    credentials = get_credentials(user_id)
    if not credentials:
        return None
    
    return build('drive', 'v3', credentials=credentials)

def list_drive_files(user_id, query='', max_results=10):
    """
    List files from the user's Google Drive.
    
    Args:
        user_id: User ID for credentials
        query: Drive search query
        max_results: Maximum number of files to return
        
    Returns:
        List of files if successful, empty list otherwise
    """
    service = get_drive_service(user_id)
    if not service:
        return []
    
    try:
        results = service.files().list(
            q=query,
            pageSize=max_results,
            fields="nextPageToken, files(id, name, mimeType, createdTime, modifiedTime, size, webViewLink)"
        ).execute()
        
        return results.get('files', [])
    except Exception as e:
        print(f"Error listing Drive files: {e}")
        return []

def upload_to_drive(user_id, file_path, folder_id=None):
    """
    Upload a file to Google Drive.
    
    Args:
        user_id: User ID for credentials
        file_path: Path to the file to upload
        folder_id: ID of the folder to upload to (optional)
        
    Returns:
        File metadata if successful, None otherwise
    """
    from googleapiclient.http import MediaFileUpload
    
    service = get_drive_service(user_id)
    if not service:
        return None
    
    try:
        file_metadata = {
            'name': os.path.basename(file_path)
        }
        
        if folder_id:
            file_metadata['parents'] = [folder_id]
        
        media = MediaFileUpload(file_path, resumable=True)
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name, webViewLink'
        ).execute()
        
        return file
    except Exception as e:
        print(f"Error uploading to Drive: {e}")
        return None

def create_drive_folder(user_id, folder_name, parent_folder_id=None):
    """
    Create a folder in Google Drive.
    
    Args:
        user_id: User ID for credentials
        folder_name: Name of the folder
        parent_folder_id: ID of the parent folder (optional)
        
    Returns:
        Folder metadata if successful, None otherwise
    """
    service = get_drive_service(user_id)
    if not service:
        return None
    
    try:
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        
        if parent_folder_id:
            file_metadata['parents'] = [parent_folder_id]
        
        folder = service.files().create(
            body=file_metadata,
            fields='id, name, webViewLink'
        ).execute()
        
        return folder
    except Exception as e:
        print(f"Error creating Drive folder: {e}")
        return None

def share_drive_file(user_id, file_id, email, role='reader'):
    """
    Share a Drive file with a user.
    
    Args:
        user_id: User ID for credentials
        file_id: ID of the file to share
        email: Email address to share with
        role: Permission role (reader, writer, commenter)
        
    Returns:
        True if successful, False otherwise
    """
    service = get_drive_service(user_id)
    if not service:
        return False
    
    try:
        permission = {
            'type': 'user',
            'role': role,
            'emailAddress': email
        }
        
        service.permissions().create(
            fileId=file_id,
            body=permission,
            sendNotificationEmail=True
        ).execute()
        
        return True
    except Exception as e:
        print(f"Error sharing Drive file: {e}")
        return False
