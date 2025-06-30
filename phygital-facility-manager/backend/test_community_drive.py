#!/usr/bin/env python3
"""Test Community Drive functionality"""

import requests
import json

def test_community_drive():
    """Test the community drive functionality"""
    print("🏗️ Testing Community Drive")
    print("=" * 40)
    
    # Test listing documents
    print("📋 Testing document listing...")
    response = requests.get('http://localhost:5000/api/community-drive/documents')
    
    if response.status_code == 200:
        data = response.json()
        documents = data.get('documents', [])
        print(f"✅ Found {len(documents)} documents in community drive")
        
        if documents:
            # Test downloading the first document
            doc = documents[0]
            print(f"\n📥 Testing download for: {doc['filename']}")
            print(f"Document ID: {doc['id']}")
            print(f"Category: {doc['category']}")
            print(f"Size: {doc['file_size']} bytes")
            
            download_url = f"http://localhost:5000/api/community-drive/documents/{doc['id']}/download"
            download_response = requests.get(download_url)
            
            if download_response.status_code == 200:
                print("✅ Download successful!")
                print(f"Content-Type: {download_response.headers.get('Content-Type')}")
                print(f"Content-Length: {len(download_response.content)} bytes")
                
                # Save to test file
                with open(f"test_{doc['filename']}", 'wb') as f:
                    f.write(download_response.content)
                print(f"Saved to: test_{doc['filename']}")
                
                # Show first few lines if it's text
                if doc['filename'].endswith('.txt'):
                    content = download_response.content.decode('utf-8')
                    lines = content.split('\n')[:5]
                    print("\nFirst 5 lines:")
                    for line in lines:
                        print(f"  {line}")
                
            else:
                print(f"❌ Download failed: {download_response.status_code}")
                try:
                    error_data = download_response.json()
                    print(f"Error: {error_data}")
                except:
                    print(f"Error text: {download_response.text}")
        
        # Show all documents
        print(f"\n📚 All documents in community drive:")
        for doc in documents:
            downloadable = "✅" if doc.get('downloadable', False) else "❌"
            print(f"  {downloadable} {doc['filename']} ({doc['category']}) - {doc['file_size']} bytes")
    
    else:
        print(f"❌ Failed to list documents: {response.status_code}")
        try:
            error_data = response.json()
            print(f"Error: {error_data}")
        except:
            print(f"Error text: {response.text}")

def test_stats():
    """Test community drive statistics"""
    print(f"\n📊 Testing storage statistics...")
    response = requests.get('http://localhost:5000/api/community-drive/stats')
    
    if response.status_code == 200:
        data = response.json()
        stats = data.get('stats', {})
        print("✅ Storage Statistics:")
        print(f"  Total documents: {stats.get('total_documents', 0)}")
        print(f"  Total size: {stats.get('total_size', 0)} bytes")
        print(f"  Categories: {list(stats.get('categories', {}).keys())}")
        
        for category, info in stats.get('categories', {}).items():
            print(f"    {category}: {info['count']} docs, {info['size']} bytes")
    else:
        print(f"❌ Failed to get stats: {response.status_code}")

if __name__ == "__main__":
    print("🎯 Community Drive Test")
    print("=" * 50)
    
    test_community_drive()
    test_stats()
    
    print("\n" + "=" * 50)
    print("🎉 Community Drive Test Complete!")
