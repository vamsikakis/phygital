#!/usr/bin/env python3
"""Test Knowledge Base functionality"""

import requests
import json
import io
from datetime import datetime

def test_get_documents():
    """Test fetching documents"""
    print("📚 Testing Document Retrieval")
    print("=" * 40)
    
    url = "http://localhost:5000/api/documents"
    
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        result = response.json()
        
        if response.status_code == 200:
            documents = result.get('documents', [])
            print(f"✅ Found {len(documents)} documents")
            
            for doc in documents:
                print(f"  - {doc.get('title')} ({doc.get('filename')})")
                print(f"    Category: {doc.get('category')}")
                print(f"    Size: {doc.get('meta_data', {}).get('size', 0)} bytes")
                print(f"    Created: {doc.get('created_at')}")
                print()
            
            return documents
        else:
            print("❌ Failed to fetch documents")
            print(f"Error: {result}")
            return []
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def test_upload_document():
    """Test uploading a document"""
    print("📤 Testing Document Upload")
    print("=" * 40)
    
    url = "http://localhost:5000/api/documents/upload"
    
    # Create a test PDF content
    test_content = f"""
    GOPALAN ATLANTIS COMMUNITY BYLAWS
    
    Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    
    1. COMMUNITY RULES
    - Residents must maintain quiet hours between 10 PM and 6 AM
    - Common areas must be kept clean and tidy
    - Pets are allowed with proper registration
    
    2. MAINTENANCE PROCEDURES
    - Submit requests through the facility management system
    - Emergency repairs will be addressed within 24 hours
    - Routine maintenance scheduled weekly
    
    3. AMENITIES USAGE
    - Swimming pool hours: 6 AM to 10 PM
    - Gym facilities available 24/7 with access card
    - Community hall bookings require advance notice
    
    This is a test document for the Knowledge Base system.
    """
    
    # Create file-like object
    files = {
        'file': ('test_bylaws.txt', io.StringIO(test_content), 'text/plain')
    }
    
    data = {
        'category': 'bylaws',
        'description': 'Test community bylaws document for Knowledge Base testing'
    }
    
    try:
        response = requests.post(url, files=files, data=data)
        print(f"Status Code: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        
        if response.status_code == 201:
            print("✅ Document uploaded successfully!")
            return result.get('document', {})
        else:
            print("❌ Document upload failed")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_download_document(document_id):
    """Test downloading a document"""
    print(f"📥 Testing Document Download for ID: {document_id}")
    print("=" * 40)
    
    url = f"http://localhost:5000/api/documents/{document_id}/download"
    
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        result = response.json()
        
        if response.status_code == 200 and result.get('download_url'):
            print("✅ Download URL generated successfully!")
            print(f"Download URL: {result['download_url']}")
            return result['download_url']
        else:
            print("❌ Failed to generate download URL")
            print(f"Error: {result}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_generate_pdf(document_id):
    """Test PDF generation"""
    print(f"📄 Testing PDF Generation for ID: {document_id}")
    print("=" * 40)
    
    url = f"http://localhost:5000/api/documents/{document_id}/pdf"
    
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        result = response.json()
        
        if response.status_code == 200 and result.get('download_url'):
            print("✅ PDF generated successfully!")
            print(f"PDF URL: {result['download_url']}")
            return result['download_url']
        else:
            print("❌ Failed to generate PDF")
            print(f"Error: {result}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    print("🎯 Knowledge Base Functionality Test")
    print("=" * 50)
    
    # Test document retrieval
    documents = test_get_documents()
    
    # Test document upload
    uploaded_doc = test_upload_document()
    
    # Test download functionality
    if documents and len(documents) > 0:
        doc_id = documents[0].get('id')
        if doc_id:
            download_url = test_download_document(doc_id)
            pdf_url = test_generate_pdf(doc_id)
    
    # Test with uploaded document if available
    if uploaded_doc and uploaded_doc.get('id'):
        doc_id = uploaded_doc.get('id')
        download_url = test_download_document(doc_id)
        pdf_url = test_generate_pdf(doc_id)
    
    print("\n" + "=" * 50)
    print("🎉 Knowledge Base Test Complete!")
    
    if documents or uploaded_doc:
        print("✅ Knowledge Base functionality is working!")
    else:
        print("⚠️ Some features may need attention")
