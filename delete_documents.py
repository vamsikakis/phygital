#!/usr/bin/env python3
import requests
import json
import os

# Base URL for the API
BASE_URL = "http://localhost:5001"

def get_all_documents():
    """Get all documents from the metadata file"""
    try:
        with open('mock_verba_data/metadata.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading metadata file: {e}")
        return {}

def delete_document(doc_id):
    """Delete a document using the API"""
    url = f"{BASE_URL}/api/verba/documents/{doc_id}/delete"
    try:
        response = requests.delete(url)
        if response.status_code == 200:
            print(f"Successfully deleted document: {doc_id}")
            return True
        else:
            print(f"Failed to delete document {doc_id}: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Error deleting document {doc_id}: {e}")
        return False

def delete_all_documents():
    """Delete all documents"""
    documents = get_all_documents()
    if not documents:
        print("No documents found to delete.")
        return
    
    print(f"Found {len(documents)} documents to delete.")
    
    success_count = 0
    for doc_id, doc_info in documents.items():
        title = doc_info.get('metadata', {}).get('title', 'Unknown')
        print(f"Deleting document: {title} (ID: {doc_id})...")
        if delete_document(doc_id):
            success_count += 1
    
    print(f"Deleted {success_count} out of {len(documents)} documents.")

def clean_mock_docs_directory():
    """Clean up the mock_docs directory"""
    mock_docs_dir = "mock_verba_data/documents"
    if os.path.exists(mock_docs_dir):
        try:
            for item in os.listdir(mock_docs_dir):
                item_path = os.path.join(mock_docs_dir, item)
                if os.path.isdir(item_path):
                    print(f"Removing directory: {item_path}")
                    os.system(f"rm -rf '{item_path}'")
        except Exception as e:
            print(f"Error cleaning mock_docs directory: {e}")

if __name__ == "__main__":
    print("Starting document deletion process...")
    delete_all_documents()
    clean_mock_docs_directory()
    print("Document deletion process completed.")
