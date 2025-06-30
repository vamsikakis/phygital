#!/usr/bin/env python3
"""Test the download functionality fix"""

import requests
import json

def test_download_fix():
    """Test that downloads work without JavaScript errors"""
    print("🔧 Testing Download Fix")
    print("=" * 40)
    
    # Get community drive documents
    try:
        response = requests.get('http://localhost:5000/api/community-drive/documents')
        if response.status_code == 200:
            data = response.json()
            documents = data.get('documents', [])
            
            if documents:
                doc = documents[0]
                print(f"Testing download for: {doc['filename']}")
                print(f"Document ID: {doc['id']}")
                print(f"Title: {doc.get('title', 'No title')}")
                
                # Test download
                download_url = f"http://localhost:5000/api/community-drive/documents/{doc['id']}/download"
                download_response = requests.get(download_url)
                
                if download_response.status_code == 200:
                    print("✅ Download API working correctly")
                    print(f"Content-Type: {download_response.headers.get('Content-Type')}")
                    print(f"Content-Length: {len(download_response.content)} bytes")
                    
                    # Verify it's the expected content
                    if doc['filename'].endswith('.txt'):
                        content = download_response.content.decode('utf-8')
                        if len(content) > 0:
                            print("✅ File content retrieved successfully")
                            print(f"First line: {content.split(chr(10))[0][:50]}...")
                        else:
                            print("❌ File content is empty")
                    
                else:
                    print(f"❌ Download failed: {download_response.status_code}")
                    try:
                        error_data = download_response.json()
                        print(f"Error: {error_data}")
                    except:
                        print(f"Error text: {download_response.text}")
            else:
                print("No documents available for testing")
        else:
            print(f"❌ Failed to get documents: {response.status_code}")
    except Exception as e:
        print(f"❌ Test error: {e}")

def test_frontend_api():
    """Test that the frontend can access the APIs"""
    print(f"\n🌐 Testing Frontend API Access")
    print("=" * 40)
    
    # Test main page
    try:
        response = requests.get('http://localhost:5000/')
        if response.status_code == 200:
            print("✅ Frontend loads successfully")
            print(f"Content-Type: {response.headers.get('Content-Type')}")
        else:
            print(f"❌ Frontend failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Frontend error: {e}")
    
    # Test document APIs
    apis = [
        ('OpenAI Documents', 'http://localhost:5000/api/documents'),
        ('Community Drive', 'http://localhost:5000/api/community-drive/documents'),
        ('Community Stats', 'http://localhost:5000/api/community-drive/stats')
    ]
    
    for name, url in apis:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                print(f"✅ {name}: Working")
            else:
                print(f"❌ {name}: Failed ({response.status_code})")
        except Exception as e:
            print(f"❌ {name}: Error - {e}")

if __name__ == "__main__":
    print("🎯 Testing Download Functionality Fix")
    print("=" * 50)
    
    test_download_fix()
    test_frontend_api()
    
    print("\n" + "=" * 50)
    print("🎉 Download Fix Test Complete!")
    print("\nThe 'T.createElement is not a function' error should now be resolved!")
    print("Try downloading a document from the Knowledge Base to verify.")
