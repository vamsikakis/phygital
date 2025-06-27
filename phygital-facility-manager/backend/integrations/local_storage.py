"""
Local File Storage Implementation
Replaces Supabase storage with local file system storage
"""

import os
import uuid
import shutil
from datetime import datetime
from dotenv import load_dotenv
import mimetypes
from pathlib import Path

# Load environment variables
load_dotenv()

# Local storage configuration
STORAGE_ROOT = os.getenv("STORAGE_ROOT", "./storage")

# Storage folder names (replacing buckets)
DOCUMENTS_FOLDER = 'documents'
TICKETS_FOLDER = 'tickets'
EVENTS_FOLDER = 'events'
PROFILES_FOLDER = 'profiles'
TEMP_FOLDER = 'temp'

# Required folders for the application
REQUIRED_FOLDERS = [
    DOCUMENTS_FOLDER,
    TICKETS_FOLDER,
    EVENTS_FOLDER,
    PROFILES_FOLDER,
    TEMP_FOLDER
]

def ensure_folders_exist():
    """
    Ensure all required storage folders exist
    """
    try:
        # Create main storage directory
        os.makedirs(STORAGE_ROOT, exist_ok=True)
        
        for folder_name in REQUIRED_FOLDERS:
            folder_path = os.path.join(STORAGE_ROOT, folder_name)
            os.makedirs(folder_path, exist_ok=True)
            print(f"Ensured folder exists: {folder_path}")
                
        return True
    except Exception as e:
        print(f"Error ensuring folders exist: {str(e)}")
        return False

def get_file_path(folder_name, file_path):
    """
    Get the full file path for a file in storage
    
    Args:
        folder_name: Name of the storage folder
        file_path: Relative path to the file within the folder
        
    Returns:
        Full file path
    """
    return os.path.join(STORAGE_ROOT, folder_name, file_path)

def upload_file(folder_name, file_path, file_content, content_type=None):
    """
    Upload a file to local storage
    
    Args:
        folder_name: Name of the storage folder
        file_path: Path where the file should be stored
        file_content: File content (bytes or file-like object)
        content_type: MIME type of the file
        
    Returns:
        Upload result dictionary
    """
    try:
        # Auto-detect content type if not provided
        if content_type is None:
            content_type, _ = mimetypes.guess_type(file_path)
        
        # Create full file path
        full_path = get_file_path(folder_name, file_path)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        # Write file content
        if isinstance(file_content, bytes):
            with open(full_path, 'wb') as f:
                f.write(file_content)
        else:
            # Assume file-like object
            with open(full_path, 'wb') as f:
                shutil.copyfileobj(file_content, f)
        
        return {
            "success": True,
            "file_path": file_path,
            "folder": folder_name,
            "full_path": full_path,
            "content_type": content_type,
            "size": os.path.getsize(full_path)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "file_path": file_path,
            "folder": folder_name
        }

def download_file(folder_name, file_path):
    """
    Download a file from local storage
    
    Args:
        folder_name: Name of the storage folder
        file_path: Path to the file within the folder
        
    Returns:
        File content as bytes
    """
    try:
        full_path = get_file_path(folder_name, file_path)
        with open(full_path, 'rb') as f:
            return f.read()
    except Exception as e:
        print(f"Error downloading file: {str(e)}")
        return None

def delete_file(folder_name, file_path):
    """
    Delete a file from local storage
    
    Args:
        folder_name: Name of the storage folder
        file_path: Path to the file within the folder
        
    Returns:
        Boolean indicating success
    """
    try:
        full_path = get_file_path(folder_name, file_path)
        if os.path.exists(full_path):
            os.remove(full_path)
            return True
        return False
    except Exception as e:
        print(f"Error deleting file: {str(e)}")
        return False

def list_files(folder_name, subfolder_path=""):
    """
    List files in a storage folder
    
    Args:
        folder_name: Name of the storage folder
        subfolder_path: Optional subfolder path to list files from
        
    Returns:
        List of file information dictionaries
    """
    try:
        folder_path = get_file_path(folder_name, subfolder_path)
        if not os.path.exists(folder_path):
            return []
        
        files = []
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            if os.path.isfile(item_path):
                stat = os.stat(item_path)
                files.append({
                    "name": item,
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "path": os.path.join(subfolder_path, item) if subfolder_path else item
                })
        
        return files
    except Exception as e:
        print(f"Error listing files: {str(e)}")
        return []

def upload_document(file_content, filename, category="general"):
    """
    Upload a document with automatic organization
    
    Args:
        file_content: File content (bytes or file-like object)
        filename: Original filename
        category: Document category for organization
        
    Returns:
        Upload result with file information
    """
    try:
        # Generate unique filename to avoid conflicts
        file_extension = Path(filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        
        # Organize by category and date
        date_folder = datetime.now().strftime("%Y/%m")
        file_path = f"{category}/{date_folder}/{unique_filename}"
        
        # Upload the file
        result = upload_file(DOCUMENTS_FOLDER, file_path, file_content)
        
        if result["success"]:
            result.update({
                "original_filename": filename,
                "category": category,
                "storage_path": file_path,
                "download_url": f"/api/files/{DOCUMENTS_FOLDER}/{file_path}"
            })
        
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "filename": filename
        }

def get_download_url(folder_name, file_path):
    """
    Get a download URL for a file
    
    Args:
        folder_name: Name of the storage folder
        file_path: Path to the file within the folder
        
    Returns:
        Download URL string
    """
    return f"/api/files/{folder_name}/{file_path}"

def record_download(user_id, file_id, file_type, file_name):
    """
    Record a file download for analytics
    
    Args:
        user_id: ID of the user downloading the file
        file_id: ID of the file being downloaded
        file_type: Type of file (document, ticket_attachment, etc.)
        file_name: Name of the file
        
    Returns:
        Boolean indicating success
    """
    try:
        from database import create_record
        from database import Download
        
        download_record = create_record(
            Download,
            id=str(uuid.uuid4()),
            user_id=user_id,
            file_id=file_id,
            file_type=file_type,
            file_name=file_name,
            timestamp=datetime.now()
        )
        
        return download_record is not None
    except Exception as e:
        print(f"Error recording download: {str(e)}")
        return False

# Initialize storage on import
ensure_folders_exist()

# For backward compatibility, create aliases with old names
upload_document = upload_document
download_file = download_file
delete_file = delete_file
list_files = list_files
get_download_url = get_download_url
record_download = record_download
