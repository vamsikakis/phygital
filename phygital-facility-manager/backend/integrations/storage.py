import os
import uuid
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client
import mimetypes
import base64
from pathlib import Path

# Load environment variables
load_dotenv()

# Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# Create supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Storage bucket names
DOCUMENTS_BUCKET = 'documents'
TICKETS_BUCKET = 'tickets'
EVENTS_BUCKET = 'events'
PROFILES_BUCKET = 'profiles'
TEMP_BUCKET = 'temp'

# Ensure all expected buckets exist
REQUIRED_BUCKETS = [
    DOCUMENTS_BUCKET,
    TICKETS_BUCKET, 
    EVENTS_BUCKET, 
    PROFILES_BUCKET,
    TEMP_BUCKET
]

def ensure_buckets_exist():
    """
    Check if required storage buckets exist and create them if they don't.
    This requires admin/service role privileges.
    """
    try:
        # Use service role key for admin operations
        admin_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        existing_buckets = [bucket['name'] for bucket in admin_client.storage.list_buckets()]
        
        for bucket_name in REQUIRED_BUCKETS:
            if bucket_name not in existing_buckets:
                admin_client.storage.create_bucket(bucket_name, {'public': bucket_name == DOCUMENTS_BUCKET})
                print(f"Created bucket: {bucket_name}")
    except Exception as e:
        print(f"Error ensuring buckets exist: {e}")
        # Continue even if bucket creation fails, as they might exist already

def get_download_url(bucket_name, file_path, expiration_seconds=3600):
    """
    Get a signed URL for downloading a file.
    
    Args:
        bucket_name: Name of the storage bucket
        file_path: Path to the file within the bucket
        expiration_seconds: Number of seconds until the URL expires
        
    Returns:
        Signed URL for downloading the file
    """
    try:
        # Generate signed URL with expiration time
        response = supabase.storage.from_(bucket_name).create_signed_url(
            file_path, expiration_seconds
        )
        return response['signedURL']
    except Exception as e:
        print(f"Error getting download URL: {e}")
        return None

def upload_file(bucket_name, file_path, file_content, content_type=None):
    """
    Upload a file to a storage bucket.
    
    Args:
        bucket_name: Name of the storage bucket
        file_path: Path where file should be stored
        file_content: File data (bytes or file-like object)
        content_type: MIME type of the file (optional)
    
    Returns:
        File metadata on success, None on failure
    """
    try:
        # If content_type not provided, guess from file extension
        if not content_type:
            content_type, _ = mimetypes.guess_type(file_path)
        
        # Upload the file
        response = supabase.storage.from_(bucket_name).upload(
            file_path, file_content, {"content-type": content_type}
        )
        
        # Get and return file metadata
        file_info = {
            'bucket': bucket_name,
            'path': file_path,
            'content_type': content_type,
            'size': len(file_content) if isinstance(file_content, bytes) else None,
            'uploaded_at': datetime.now().isoformat()
        }
        
        return file_info
    except Exception as e:
        print(f"Error uploading file: {e}")
        return None

def download_file(bucket_name, file_path):
    """
    Download a file from a storage bucket.
    
    Args:
        bucket_name: Name of the storage bucket
        file_path: Path to the file within the bucket
        
    Returns:
        File data as bytes on success, None on failure
    """
    try:
        response = supabase.storage.from_(bucket_name).download(file_path)
        return response
    except Exception as e:
        print(f"Error downloading file: {e}")
        return None

def delete_file(bucket_name, file_path):
    """
    Delete a file from a storage bucket.
    
    Args:
        bucket_name: Name of the storage bucket
        file_path: Path to the file within the bucket
        
    Returns:
        True on success, False on failure
    """
    try:
        supabase.storage.from_(bucket_name).remove([file_path])
        return True
    except Exception as e:
        print(f"Error deleting file: {e}")
        return False

def list_files(bucket_name, folder_path=None):
    """
    List files in a storage bucket or folder.
    
    Args:
        bucket_name: Name of the storage bucket
        folder_path: Optional path to list within the bucket
        
    Returns:
        List of files on success, empty list on failure
    """
    try:
        if folder_path:
            response = supabase.storage.from_(bucket_name).list(folder_path)
        else:
            response = supabase.storage.from_(bucket_name).list()
        return response
    except Exception as e:
        print(f"Error listing files: {e}")
        return []

def move_file(source_bucket, source_path, dest_bucket, dest_path):
    """
    Move a file from one location to another.
    
    Args:
        source_bucket: Source bucket name
        source_path: Source file path
        dest_bucket: Destination bucket name
        dest_path: Destination file path
        
    Returns:
        True on success, False on failure
    """
    try:
        # Download the file
        file_data = download_file(source_bucket, source_path)
        if not file_data:
            return False
        
        # Upload to new location
        content_type, _ = mimetypes.guess_type(source_path)
        upload_result = upload_file(dest_bucket, dest_path, file_data, content_type)
        if not upload_result:
            return False
        
        # Delete from original location
        return delete_file(source_bucket, source_path)
    except Exception as e:
        print(f"Error moving file: {e}")
        return False

def copy_file(source_bucket, source_path, dest_bucket, dest_path):
    """
    Copy a file from one location to another.
    
    Args:
        source_bucket: Source bucket name
        source_path: Source file path
        dest_bucket: Destination bucket name
        dest_path: Destination file path
        
    Returns:
        True on success, False on failure
    """
    try:
        # Download the file
        file_data = download_file(source_bucket, source_path)
        if not file_data:
            return False
        
        # Upload to new location
        content_type, _ = mimetypes.guess_type(source_path)
        upload_result = upload_file(dest_bucket, dest_path, file_data, content_type)
        return upload_result is not None
    except Exception as e:
        print(f"Error copying file: {e}")
        return False

def create_folder(bucket_name, folder_path):
    """
    Create a folder in a storage bucket.
    
    Args:
        bucket_name: Name of the storage bucket
        folder_path: Path to the folder (ending with /)
        
    Returns:
        True on success, False on failure
    """
    try:
        # Ensure folder path ends with slash
        if not folder_path.endswith('/'):
            folder_path += '/'
            
        # Create empty file to represent folder
        supabase.storage.from_(bucket_name).upload(folder_path + '.folder', b'')
        return True
    except Exception as e:
        print(f"Error creating folder: {e}")
        return False

def generate_unique_filename(original_filename):
    """Generate a unique filename to avoid collisions"""
    file_uuid = uuid.uuid4().hex[:8]
    file_ext = os.path.splitext(original_filename)[1]
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"{timestamp}_{file_uuid}{file_ext}"

def upload_document(file_data, original_filename, category, description=None):
    """
    Upload a document and update the documents table.
    
    Args:
        file_data: Document file data
        original_filename: Original name of the file
        category: Document category
        description: Optional document description
        
    Returns:
        Document metadata on success, None on failure
    """
    try:
        # Generate unique filename
        unique_filename = generate_unique_filename(original_filename)
        
        # Determine file path in bucket
        file_path = f"{category}/{unique_filename}"
        
        # Upload file
        upload_result = upload_file(DOCUMENTS_BUCKET, file_path, file_data)
        if not upload_result:
            return None
            
        # Create document record in database
        doc_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        # Get download URL
        download_url = get_download_url(DOCUMENTS_BUCKET, file_path)
        
        # Add record to documents table
        document_data = {
            'id': doc_id,
            'title': original_filename,
            'description': description or f"Uploaded document {original_filename}",
            'category': category,
            'file_url': download_url,
            'storage_path': file_path,
            'created_at': now,
            'last_updated': now
        }
        
        result = supabase.table('documents').insert(document_data).execute()
        
        if result.data:
            return result.data[0]
        return None
    except Exception as e:
        print(f"Error uploading document: {e}")
        return None

def upload_ticket_attachment(ticket_id, file_data, original_filename, user_id=None):
    """
    Upload an attachment for a support ticket.
    
    Args:
        ticket_id: ID of the ticket
        file_data: Attachment file data
        original_filename: Original name of the file
        user_id: ID of the user uploading the file
        
    Returns:
        Attachment metadata on success, None on failure
    """
    try:
        # Generate unique filename
        unique_filename = generate_unique_filename(original_filename)
        
        # Determine file path in bucket
        file_path = f"{ticket_id}/{unique_filename}"
        
        # Upload file
        upload_result = upload_file(TICKETS_BUCKET, file_path, file_data)
        if not upload_result:
            return None
        
        # Get download URL
        download_url = get_download_url(TICKETS_BUCKET, file_path)
        
        # Add record to ticket_attachments table
        attachment_data = {
            'id': str(uuid.uuid4()),
            'ticket_id': ticket_id,
            'filename': original_filename,
            'storage_path': file_path,
            'download_url': download_url,
            'uploaded_by': user_id,
            'uploaded_at': datetime.now().isoformat()
        }
        
        result = supabase.table('ticket_attachments').insert(attachment_data).execute()
        
        if result.data:
            return result.data[0]
        return None
    except Exception as e:
        print(f"Error uploading ticket attachment: {e}")
        return None

def upload_event_material(event_id, file_data, original_filename, description=None, user_id=None):
    """
    Upload materials for an event.
    
    Args:
        event_id: ID of the event
        file_data: File data
        original_filename: Original name of the file
        description: Optional file description
        user_id: ID of the user uploading the file
        
    Returns:
        Material metadata on success, None on failure
    """
    try:
        # Generate unique filename
        unique_filename = generate_unique_filename(original_filename)
        
        # Determine file path in bucket
        file_path = f"{event_id}/{unique_filename}"
        
        # Upload file
        upload_result = upload_file(EVENTS_BUCKET, file_path, file_data)
        if not upload_result:
            return None
            
        # Get download URL
        download_url = get_download_url(EVENTS_BUCKET, file_path)
        
        # Add record to event_materials table
        material_data = {
            'id': str(uuid.uuid4()),
            'event_id': event_id,
            'filename': original_filename,
            'description': description or f"Event material: {original_filename}",
            'storage_path': file_path,
            'download_url': download_url,
            'uploaded_by': user_id,
            'uploaded_at': datetime.now().isoformat()
        }
        
        result = supabase.table('event_materials').insert(material_data).execute()
        
        if result.data:
            return result.data[0]
        return None
    except Exception as e:
        print(f"Error uploading event material: {e}")
        return None

def upload_profile_photo(user_id, file_data, original_filename):
    """
    Upload or update a user's profile photo.
    
    Args:
        user_id: ID of the user
        file_data: Photo file data
        original_filename: Original name of the file
        
    Returns:
        Photo URL on success, None on failure
    """
    try:
        # Get file extension and check it's an image
        file_ext = os.path.splitext(original_filename)[1].lower()
        if file_ext not in ['.jpg', '.jpeg', '.png', '.gif']:
            print("Invalid image format")
            return None
        
        # Determine file path in bucket
        file_path = f"{user_id}/profile{file_ext}"
        
        # Delete existing profile photo if it exists
        existing_files = list_files(PROFILES_BUCKET, user_id)
        for file in existing_files:
            if 'profile' in file['name']:
                delete_file(PROFILES_BUCKET, f"{user_id}/{file['name']}")
        
        # Upload new photo
        content_type = f"image/{file_ext[1:]}" if file_ext != '.jpg' else 'image/jpeg'
        upload_result = upload_file(PROFILES_BUCKET, file_path, file_data, content_type)
        if not upload_result:
            return None
            
        # Get public URL
        download_url = get_download_url(PROFILES_BUCKET, file_path, 86400 * 30)  # 30 days
        
        # Update user profile
        result = supabase.table('users').update({'avatar_url': download_url}).eq('id', user_id).execute()
        
        return download_url
    except Exception as e:
        print(f"Error uploading profile photo: {e}")
        return None

def record_download(user_id, file_id, file_type, file_name):
    """
    Record a file download event for analytics.
    
    Args:
        user_id: ID of the user who downloaded the file
        file_id: ID of the file that was downloaded
        file_type: Type of file (document, ticket_attachment, event_material)
        file_name: Name of the downloaded file
    
    Returns:
        Download record on success, None on failure
    """
    try:
        download_data = {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'file_id': file_id,
            'file_type': file_type,
            'file_name': file_name,
            'timestamp': datetime.now().isoformat()
        }
        
        result = supabase.table('downloads').insert(download_data).execute()
        
        if result.data:
            return result.data[0]
        return None
    except Exception as e:
        print(f"Error recording download: {e}")
        return None
