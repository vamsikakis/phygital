#!/usr/bin/env python3
import requests
import os
import json
import mimetypes
from pathlib import Path

# Base URL for the API
BASE_URL = "http://localhost:5001"
MOCK_DOCS_DIR = "mock_docs"

def get_document_category(filename):
    """Determine document category based on filename"""
    filename_lower = filename.lower()
    
    if any(term in filename_lower for term in ["policy", "rule", "guideline"]):
        return "Apartment Policies"
    elif any(term in filename_lower for term in ["notice", "announcement"]):
        return "Notices"
    elif any(term in filename_lower for term in ["form", "application"]):
        return "Forms"
    elif any(term in filename_lower for term in ["schedule", "calendar"]):
        return "Schedules"
    else:
        return "General Documents"

def get_document_title(filename):
    """Generate a readable title from filename"""
    # Remove extension
    name = os.path.splitext(filename)[0]
    
    # Replace underscores and hyphens with spaces
    name = name.replace('_', ' ').replace('-', ' ')
    
    # Capitalize words
    title = ' '.join(word.capitalize() for word in name.split())
    
    return title

def upload_document(file_path):
    """Upload a document using the API"""
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return False
    
    filename = os.path.basename(file_path)
    title = get_document_title(filename)
    category = get_document_category(filename)
    
    # Determine mime type
    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type:
        mime_type = 'application/octet-stream'
    
    print(f"Uploading {filename} as '{title}' in category '{category}'...")
    
    url = f"{BASE_URL}/api/verba/upload"
    
    # Prepare form data
    files = {
        'file': (filename, open(file_path, 'rb'), mime_type)
    }
    
    data = {
        'collection': 'apartment_documents',
        'title': title,
        'category': category
    }
    
    try:
        response = requests.post(url, files=files, data=data)
        if response.status_code == 200:
            result = response.json()
            print(f"Successfully uploaded document: {title}")
            print(f"Document ID: {result.get('id')}")
            return True
        else:
            print(f"Failed to upload document {filename}: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Error uploading document {filename}: {e}")
        return False

def upload_all_documents():
    """Upload all documents in the mock_docs directory"""
    if not os.path.exists(MOCK_DOCS_DIR):
        print(f"Directory not found: {MOCK_DOCS_DIR}")
        return
    
    files = [f for f in os.listdir(MOCK_DOCS_DIR) if os.path.isfile(os.path.join(MOCK_DOCS_DIR, f))]
    
    if not files:
        print(f"No files found in {MOCK_DOCS_DIR}")
        return
    
    print(f"Found {len(files)} files to upload.")
    
    success_count = 0
    for filename in files:
        file_path = os.path.join(MOCK_DOCS_DIR, filename)
        if upload_document(file_path):
            success_count += 1
    
    print(f"Uploaded {success_count} out of {len(files)} documents.")

if __name__ == "__main__":
    print("Starting document upload process...")
    upload_all_documents()
    print("Document upload process completed.")
