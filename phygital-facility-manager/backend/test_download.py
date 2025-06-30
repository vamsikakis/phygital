#!/usr/bin/env python3
"""Test document download functionality"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_download_endpoint():
    """Test the download endpoint directly"""
    print("🔍 Testing Document Download")
    print("=" * 40)
    
    # First get the list of documents
    docs_url = "http://localhost:5000/api/documents"
    
    try:
        response = requests.get(docs_url)
        if response.status_code == 200:
            data = response.json()
            documents = data.get('documents', [])
            
            if documents:
                # Test with the first document
                doc = documents[0]
                doc_id = doc['id']
                filename = doc['filename']
                
                print(f"Testing download for: {filename}")
                print(f"Document ID: {doc_id}")
                
                # Test download
                download_url = f"http://localhost:5000/api/documents/{doc_id}/download"
                
                print(f"Requesting: {download_url}")
                
                download_response = requests.get(download_url)
                print(f"Status Code: {download_response.status_code}")
                
                if download_response.status_code == 200:
                    print("✅ Download successful!")
                    print(f"Content-Type: {download_response.headers.get('Content-Type')}")
                    print(f"Content-Length: {download_response.headers.get('Content-Length')}")
                    
                    # Save to a test file
                    test_filename = f"test_download_{filename}"
                    with open(test_filename, 'wb') as f:
                        f.write(download_response.content)
                    
                    print(f"Saved to: {test_filename}")
                    print(f"File size: {len(download_response.content)} bytes")
                    
                else:
                    print("❌ Download failed!")
                    try:
                        error_data = download_response.json()
                        print(f"Error: {error_data}")
                    except:
                        print(f"Error text: {download_response.text}")
            else:
                print("No documents found to test")
        else:
            print(f"Failed to get documents: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_openai_direct():
    """Test OpenAI file access directly"""
    print("\n🤖 Testing OpenAI Direct Access")
    print("=" * 40)
    
    try:
        from services.openai_assistant_service import openai_assistant_service
        
        # Get a file ID from the documents
        docs_url = "http://localhost:5000/api/documents"
        response = requests.get(docs_url)
        
        if response.status_code == 200:
            data = response.json()
            documents = data.get('documents', [])
            
            if documents:
                doc = documents[0]
                file_id = doc['file_id']
                filename = doc['filename']
                
                print(f"Testing OpenAI download for: {filename}")
                print(f"File ID: {file_id}")
                
                # Test the service method directly
                content, downloaded_filename = openai_assistant_service.download_file(file_id)
                
                if content:
                    print("✅ OpenAI download successful!")
                    print(f"Downloaded filename: {downloaded_filename}")
                    print(f"Content size: {len(content)} bytes")
                    print(f"Content type: {type(content)}")
                else:
                    print("❌ OpenAI download failed!")
            else:
                print("No documents found")
        else:
            print("Failed to get documents")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🎯 Document Download Test")
    print("=" * 50)
    
    test_download_endpoint()
    test_openai_direct()
    
    print("\n" + "=" * 50)
    print("🎉 Download Test Complete!")
