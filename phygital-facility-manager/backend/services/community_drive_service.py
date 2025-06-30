"""
Community Drive Service
Manages local file storage for downloadable documents
"""

import os
import shutil
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
import json
import hashlib
from flask import current_app
from werkzeug.utils import secure_filename

class CommunityDriveService:
    def __init__(self):
        self.base_path = os.path.join(os.getcwd(), 'storage', 'community_drive')
        self.metadata_file = os.path.join(self.base_path, 'metadata.json')
        self.ensure_directories()
    
    def ensure_directories(self):
        """Ensure all necessary directories exist"""
        directories = [
            self.base_path,
            os.path.join(self.base_path, 'documents'),
            os.path.join(self.base_path, 'bylaws'),
            os.path.join(self.base_path, 'security'),
            os.path.join(self.base_path, 'facilities'),
            os.path.join(self.base_path, 'official'),
            os.path.join(self.base_path, 'general')
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def load_metadata(self) -> Dict[str, Any]:
        """Load document metadata from JSON file"""
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                current_app.logger.error(f"Error loading metadata: {e}")
                return {}
        return {}
    
    def save_metadata(self, metadata: Dict[str, Any]):
        """Save document metadata to JSON file"""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
        except Exception as e:
            current_app.logger.error(f"Error saving metadata: {e}")
    
    def get_file_hash(self, file_path: str) -> str:
        """Generate MD5 hash of file for deduplication"""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception:
            return str(uuid.uuid4())
    
    def categorize_file(self, filename: str) -> str:
        """Automatically categorize file based on filename"""
        filename_lower = filename.lower()
        
        if any(word in filename_lower for word in ['bylaw', 'bye-law', 'constitution']):
            return 'bylaws'
        elif any(word in filename_lower for word in ['security', 'entrance', 'access']):
            return 'security'
        elif any(word in filename_lower for word in ['gym', 'pool', 'club', 'amenity', 'facility']):
            return 'facilities'
        elif any(word in filename_lower for word in ['oc', 'certificate', 'approval', 'registration']):
            return 'official'
        elif any(word in filename_lower for word in ['rule', 'policy', 'guideline', 'procedure']):
            return 'general'
        else:
            return 'general'
    
    def store_document(self, file_path: str, original_filename: str, 
                      category: str = None, description: str = None,
                      openai_file_id: str = None) -> Dict[str, Any]:
        """Store a document in the community drive"""
        try:
            # Auto-categorize if not provided
            if not category:
                category = self.categorize_file(original_filename)
            
            # Generate unique ID and secure filename
            doc_id = str(uuid.uuid4())
            secure_name = secure_filename(original_filename)
            file_hash = self.get_file_hash(file_path)
            
            # Create destination path
            category_path = os.path.join(self.base_path, category)
            destination_path = os.path.join(category_path, f"{doc_id}_{secure_name}")
            
            # Copy file to community drive
            shutil.copy2(file_path, destination_path)
            
            # Get file stats
            file_stats = os.stat(destination_path)
            
            # Create document metadata
            document_info = {
                'id': doc_id,
                'title': original_filename.replace('.txt', '').replace('_', ' ').title(),
                'filename': original_filename,
                'secure_filename': f"{doc_id}_{secure_name}",
                'category': category,
                'description': description or f"Community document: {original_filename}",
                'file_path': destination_path,
                'file_size': file_stats.st_size,
                'file_hash': file_hash,
                'openai_file_id': openai_file_id,
                'uploaded_at': datetime.now().isoformat(),
                'mime_type': self.get_mime_type(original_filename),
                'downloadable': True
            }
            
            # Load existing metadata and add new document
            metadata = self.load_metadata()
            metadata[doc_id] = document_info
            self.save_metadata(metadata)
            
            current_app.logger.info(f"Document stored in community drive: {original_filename}")
            return document_info
            
        except Exception as e:
            current_app.logger.error(f"Error storing document: {e}")
            raise
    
    def get_mime_type(self, filename: str) -> str:
        """Get MIME type based on file extension"""
        ext = filename.lower().split('.')[-1] if '.' in filename else ''
        mime_types = {
            'pdf': 'application/pdf',
            'doc': 'application/msword',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'txt': 'text/plain',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png'
        }
        return mime_types.get(ext, 'application/octet-stream')
    
    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get document metadata by ID"""
        metadata = self.load_metadata()
        return metadata.get(doc_id)
    
    def list_documents(self, category: str = None) -> List[Dict[str, Any]]:
        """List all documents, optionally filtered by category"""
        metadata = self.load_metadata()
        documents = list(metadata.values())
        
        if category:
            documents = [doc for doc in documents if doc.get('category') == category]
        
        # Sort by upload date (newest first)
        documents.sort(key=lambda x: x.get('uploaded_at', ''), reverse=True)
        return documents
    
    def get_file_path(self, doc_id: str) -> Optional[str]:
        """Get the file path for a document"""
        document = self.get_document(doc_id)
        if document and os.path.exists(document.get('file_path', '')):
            return document['file_path']
        return None
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete a document from the community drive"""
        try:
            document = self.get_document(doc_id)
            if not document:
                return False
            
            # Delete physical file
            file_path = document.get('file_path')
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
            
            # Remove from metadata
            metadata = self.load_metadata()
            if doc_id in metadata:
                del metadata[doc_id]
                self.save_metadata(metadata)
            
            current_app.logger.info(f"Document deleted from community drive: {doc_id}")
            return True
            
        except Exception as e:
            current_app.logger.error(f"Error deleting document: {e}")
            return False
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        metadata = self.load_metadata()
        documents = list(metadata.values())
        
        total_size = sum(doc.get('file_size', 0) for doc in documents)
        categories = {}
        
        for doc in documents:
            category = doc.get('category', 'unknown')
            if category not in categories:
                categories[category] = {'count': 0, 'size': 0}
            categories[category]['count'] += 1
            categories[category]['size'] += doc.get('file_size', 0)
        
        return {
            'total_documents': len(documents),
            'total_size': total_size,
            'categories': categories,
            'storage_path': self.base_path
        }

# Create singleton instance
community_drive_service = CommunityDriveService()
