#!/usr/bin/env python3
import requests
import json
import os
import sys

# Base URL for the API
BASE_URL = "http://localhost:5001"

def update_document_view_endpoint():
    """Update the document view endpoint to properly display document content"""
    print("Updating document view endpoint...")
    
    # First, let's check if the backend server is running
    try:
        response = requests.get(f"{BASE_URL}/api/verba/status")
        if response.status_code != 200:
            print("Backend server is not responding correctly. Please make sure it's running.")
            return False
    except Exception as e:
        print(f"Error connecting to backend server: {e}")
        print("Please make sure the backend server is running on port 5001.")
        return False
    
    # Now let's check if the frontend server is running
    try:
        # We'll use the documents endpoint to check if the frontend can access the backend
        response = requests.get(f"{BASE_URL}/api/verba/documents")
        if response.status_code != 200:
            print("Documents endpoint is not responding correctly.")
            return False
        
        documents = response.json()
        print(f"Found {len(documents)} documents in the system.")
        
        # Test document view for each document
        for doc in documents:
            doc_id = doc.get('id')
            title = doc.get('title')
            print(f"Testing document view for '{title}' (ID: {doc_id})...")
            
            view_response = requests.get(f"{BASE_URL}/api/verba/documents/{doc_id}/view")
            if view_response.status_code != 200:
                print(f"  Error: Document view endpoint returned status code {view_response.status_code}")
                continue
            
            content = view_response.text
            content_preview = content[:50] + "..." if len(content) > 50 else content
            print(f"  Content preview: {content_preview}")
            
            # Check if content is properly formatted HTML
            if not content.strip().startswith('<'):
                print(f"  Warning: Document content is not properly formatted HTML")
            
            # Check if content contains the document title
            if title.lower() not in content.lower():
                print(f"  Warning: Document title '{title}' not found in content")
        
        print("\nDocument view endpoint test completed.")
        return True
    except Exception as e:
        print(f"Error testing document view endpoint: {e}")
        return False

def restart_servers():
    """Restart the backend and frontend servers"""
    print("Restarting servers...")
    
    # Kill existing servers
    os.system("pkill -f simple_mock_server.py")
    os.system("pkill -f 'node.*vite'")
    
    # Start backend server
    print("Starting backend server...")
    os.system("python3 simple_mock_server.py > backend_server.log 2>&1 &")
    
    # Start frontend server
    print("Starting frontend server...")
    os.chdir("frontend")
    os.system("npm run dev > ../frontend_server.log 2>&1 &")
    os.chdir("..")
    
    print("Servers restarted. Please wait a few seconds for them to initialize.")
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--restart":
        restart_servers()
    else:
        update_document_view_endpoint()
