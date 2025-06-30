#!/usr/bin/env python3
"""Test the fixes for console errors"""

import requests
import json

def test_knowledge_base_apis():
    """Test both knowledge base APIs"""
    print("🔍 Testing Knowledge Base APIs")
    print("=" * 40)
    
    # Test OpenAI documents
    try:
        response = requests.get('http://localhost:5000/api/documents')
        if response.status_code == 200:
            data = response.json()
            openai_docs = data.get('documents', [])
            print(f"✅ OpenAI Documents: {len(openai_docs)} found")
            
            # Check for potential undefined fields
            for doc in openai_docs[:3]:  # Check first 3
                title = doc.get('title', 'UNDEFINED')
                filename = doc.get('filename', 'UNDEFINED')
                category = doc.get('category', 'UNDEFINED')
                print(f"  - Title: {title[:30]}...")
                print(f"    Filename: {filename}")
                print(f"    Category: {category}")
        else:
            print(f"❌ OpenAI API failed: {response.status_code}")
    except Exception as e:
        print(f"❌ OpenAI API error: {e}")
    
    # Test Community Drive documents
    try:
        response = requests.get('http://localhost:5000/api/community-drive/documents')
        if response.status_code == 200:
            data = response.json()
            community_docs = data.get('documents', [])
            print(f"✅ Community Drive Documents: {len(community_docs)} found")
            
            # Check for potential undefined fields
            for doc in community_docs[:3]:  # Check first 3
                title = doc.get('title', 'UNDEFINED')
                filename = doc.get('filename', 'UNDEFINED')
                category = doc.get('category', 'UNDEFINED')
                downloadable = doc.get('downloadable', False)
                print(f"  - Title: {title}")
                print(f"    Filename: {filename}")
                print(f"    Category: {category}")
                print(f"    Downloadable: {downloadable}")
        else:
            print(f"❌ Community Drive API failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Community Drive API error: {e}")

def test_pwa_icons():
    """Test PWA icon accessibility"""
    print(f"\n🎨 Testing PWA Icons")
    print("=" * 40)
    
    icons = [
        'http://localhost:5000/pwa-192x192.png',
        'http://localhost:5000/pwa-512x512.png',
        'http://localhost:5000/favicon.ico'
    ]
    
    for icon_url in icons:
        try:
            response = requests.get(icon_url)
            if response.status_code == 200:
                size = len(response.content)
                content_type = response.headers.get('Content-Type', 'unknown')
                print(f"✅ {icon_url.split('/')[-1]}: {size} bytes, {content_type}")
            else:
                print(f"❌ {icon_url.split('/')[-1]}: {response.status_code}")
        except Exception as e:
            print(f"❌ {icon_url.split('/')[-1]}: {e}")

def test_download_functionality():
    """Test download functionality"""
    print(f"\n📥 Testing Download Functionality")
    print("=" * 40)
    
    # Get a community drive document
    try:
        response = requests.get('http://localhost:5000/api/community-drive/documents')
        if response.status_code == 200:
            data = response.json()
            docs = data.get('documents', [])
            
            if docs:
                doc = docs[0]
                doc_id = doc['id']
                filename = doc['filename']
                
                print(f"Testing download for: {filename}")
                
                download_url = f"http://localhost:5000/api/community-drive/documents/{doc_id}/download"
                download_response = requests.get(download_url)
                
                if download_response.status_code == 200:
                    print(f"✅ Download successful: {len(download_response.content)} bytes")
                else:
                    print(f"❌ Download failed: {download_response.status_code}")
            else:
                print("No documents available for download test")
        else:
            print(f"Failed to get documents: {response.status_code}")
    except Exception as e:
        print(f"❌ Download test error: {e}")

if __name__ == "__main__":
    print("🎯 Testing Console Error Fixes")
    print("=" * 50)
    
    test_knowledge_base_apis()
    test_pwa_icons()
    test_download_functionality()
    
    print("\n" + "=" * 50)
    print("🎉 Fix Testing Complete!")
    print("\nIf all tests show ✅, the console errors should be resolved!")
