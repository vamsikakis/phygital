#!/usr/bin/env python3
"""
Test script for Verba RAG integration.
This script verifies that the Verba service is properly configured and can process documents.
"""

import os
import sys
import json
from services.verba_service import VerbaService

def print_section(title):
    """Print a section header for better readability"""
    print("\n" + "=" * 50)
    print(f"  {title}")
    print("=" * 50)

def main():
    print_section("VERBA RAG INTEGRATION TEST")
    
    # Step 1: Check Environment Variables
    print("Checking environment variables...")
    required_vars = ["OPENAI_API_KEY", "WEAVIATE_URL"]
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these variables before proceeding.")
        sys.exit(1)
    else:
        print("✅ All required environment variables are set.")
    
    # Step 2: Initialize Verba Service
    print("\nInitializing Verba service...")
    try:
        verba = VerbaService()
        print("✅ Verba service initialized successfully.")
    except Exception as e:
        print(f"❌ Failed to initialize Verba service: {str(e)}")
        sys.exit(1)
    
    # Step 3: Check if Verba client is properly initialized
    if not verba.initialized:
        print("❌ Verba client is not properly initialized.")
        sys.exit(1)
    
    # Step 4: List available collections
    print("\nListing available collections...")
    try:
        collections = verba.get_collections()
        print(f"✅ Found {len(collections)} collections: {collections}")
    except Exception as e:
        print(f"❌ Failed to list collections: {str(e)}")
    
    # Step 5: Create a test collection if it doesn't exist
    test_collection = "test_collection"
    if test_collection not in collections:
        print(f"\nCreating test collection '{test_collection}'...")
        try:
            verba.create_collection(test_collection)
            print(f"✅ Test collection '{test_collection}' created successfully.")
        except Exception as e:
            print(f"❌ Failed to create test collection: {str(e)}")
    else:
        print(f"\n✅ Test collection '{test_collection}' already exists.")
    
    # Step 6: Create a simple test document
    print("\nCreating test document...")
    test_doc_path = "/tmp/test_document.txt"
    with open(test_doc_path, "w") as f:
        f.write("This is a test document for the Verba RAG system.\n")
        f.write("It contains information about the Gopalan Atlantis Facility.\n")
        f.write("The facility has multiple buildings and amenities.\n")
    print(f"✅ Created test document at {test_doc_path}")
    
    # Step 7: Upload test document
    print("\nUploading test document to Verba...")
    metadata = {
        "title": "Test Document",
        "category": "Testing",
        "type": "Text",
        "tags": ["test", "verba", "rag"]
    }
    
    try:
        result = verba.upload_document(test_doc_path, test_collection, metadata)
        print(f"✅ Document uploaded successfully: {result}")
    except Exception as e:
        print(f"❌ Failed to upload document: {str(e)}")
    
    # Step 8: Check documents in the collection
    print("\nRetrieving documents from collection...")
    try:
        documents = verba.get_documents_metadata(test_collection)
        print(f"✅ Found {len(documents)} documents in the collection.")
        for doc in documents:
            print(f"  - {doc.get('id')}: {doc.get('metadata', {}).get('title', 'No title')}")
    except Exception as e:
        print(f"❌ Failed to retrieve documents: {str(e)}")
    
    # Step 9: Perform a test query
    print("\nTesting RAG query...")
    test_query = "What is this document about?"
    try:
        response = verba.query_documents(test_query, test_collection, 3)
        print("✅ Query successful. Response:")
        print(f"Answer: {response.get('answer', 'No answer')}")
        print("Sources:")
        for i, source in enumerate(response.get('sources', [])):
            print(f"  {i+1}. {source.get('document')} (score: {source.get('score')})")
            print(f"     Content: {source.get('content')[:100]}...")
    except Exception as e:
        print(f"❌ Failed to query documents: {str(e)}")
    
    print_section("TEST COMPLETED")
    print("The Verba RAG integration test has completed.")
    print("If all steps show '✅', the integration is working correctly.")

if __name__ == "__main__":
    main()
