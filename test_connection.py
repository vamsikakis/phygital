#!/usr/bin/env python3
import requests
import json

# Base URL for the API
BASE_URL = "http://localhost:5001"

def test_backend_connection():
    """Test if the backend server is responding"""
    try:
        response = requests.get(f"{BASE_URL}/api/verba/status")
        print(f"Backend status: {response.status_code}")
        print(response.json())
        return response.status_code == 200
    except Exception as e:
        print(f"Error connecting to backend: {e}")
        return False

def test_documents_endpoint():
    """Test if the documents endpoint is working"""
    try:
        response = requests.get(f"{BASE_URL}/api/verba/documents")
        print(f"Documents endpoint status: {response.status_code}")
        if response.status_code == 200:
            documents = response.json()
            print(f"Found {len(documents)} documents")
            for doc in documents:
                print(f"- {doc.get('title', 'Untitled')} (ID: {doc.get('id', 'Unknown')})")
        return response.status_code == 200
    except Exception as e:
        print(f"Error accessing documents endpoint: {e}")
        return False

def test_document_view():
    """Test if a document can be viewed"""
    try:
        # First get a document ID
        response = requests.get(f"{BASE_URL}/api/verba/documents")
        if response.status_code == 200:
            documents = response.json()
            if documents:
                doc_id = documents[0].get('id')
                print(f"Testing document view for ID: {doc_id}")
                
                view_response = requests.get(f"{BASE_URL}/api/verba/documents/{doc_id}/view")
                print(f"Document view status: {view_response.status_code}")
                if view_response.status_code == 200:
                    content_preview = view_response.text[:100] + "..." if len(view_response.text) > 100 else view_response.text
                    print(f"Document content preview: {content_preview}")
                return view_response.status_code == 200
        return False
    except Exception as e:
        print(f"Error testing document view: {e}")
        return False

def test_document_assistant():
    """Test if the document assistant is working"""
    try:
        query = "What are the clubhouse usage rules?"
        print(f"Testing document assistant with query: '{query}'")
        
        response = requests.post(
            f"{BASE_URL}/api/verba/query",
            json={"query": query}
        )
        
        print(f"Document assistant status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Answer: {result.get('answer', 'No answer provided')}")
            print(f"Sources: {len(result.get('sources', []))} sources found")
            return True
        return False
    except Exception as e:
        print(f"Error testing document assistant: {e}")
        return False

if __name__ == "__main__":
    print("Testing backend connection...")
    backend_ok = test_backend_connection()
    
    if backend_ok:
        print("\nTesting documents endpoint...")
        test_documents_endpoint()
        
        print("\nTesting document view...")
        test_document_view()
        
        print("\nTesting document assistant...")
        test_document_assistant()
    else:
        print("Backend connection failed. Please check if the server is running.")
