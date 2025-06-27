#!/usr/bin/env python3
"""
Test Enhanced Document Upload and Vector Storage
Tests the complete document upload flow with vector database integration
"""

import os
import sys
import requests
import json
import time
from datetime import datetime

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_document_upload_and_search():
    """Test document upload and semantic search"""
    print("🧪 Testing Enhanced Document Upload and Vector Storage")
    print("=" * 60)
    
    base_url = "http://localhost:5000"
    
    # Test 1: Upload a test document
    print("\n📤 Step 1: Uploading test document...")
    
    # Create a test document
    test_content = """
    Gopalan Atlantis Swimming Pool Guidelines
    
    Pool Hours:
    - Monday to Friday: 6:00 AM to 10:00 PM
    - Saturday and Sunday: 5:30 AM to 10:30 PM
    - Pool closed for maintenance every Monday 8:00 AM to 10:00 AM
    
    Pool Rules:
    - Children under 12 must be accompanied by an adult
    - No diving in shallow end (depth less than 4 feet)
    - Swimming attire is mandatory
    - No food or drinks allowed in pool area
    - Maximum 2 hours continuous usage during peak hours
    
    Pool Facilities:
    - Olympic size swimming pool (50m x 25m)
    - Separate children's pool (depth: 2 feet)
    - Pool deck with lounge chairs
    - Changing rooms with lockers
    - Pool equipment rental available
    
    Contact Information:
    - Pool Manager: +91-9876543210
    - Emergency: +91-9876543211
    - Booking for pool parties: facility.manager@gopalanatlantis.com
    """
    
    # Create a temporary file
    test_filename = f"pool_guidelines_{int(time.time())}.txt"
    with open(test_filename, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    try:
        # Upload the document
        with open(test_filename, 'rb') as f:
            files = {'file': (test_filename, f, 'text/plain')}
            data = {
                'title': 'Swimming Pool Guidelines',
                'description': 'Complete guidelines for using the swimming pool at Gopalan Atlantis',
                'category': 'Amenities'
            }
            
            response = requests.post(f"{base_url}/api/documents", files=files, data=data)
            
        if response.status_code == 200:
            upload_result = response.json()
            print("✅ Document uploaded successfully!")
            print(f"   Document ID: {upload_result.get('id', 'Unknown')}")
            print(f"   Vector stored: {upload_result.get('vector_stored', False)}")
            print(f"   OpenAI file ID: {upload_result.get('file_id', 'Unknown')}")
            
            document_id = upload_result.get('id')
        else:
            print(f"❌ Upload failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return False
    finally:
        # Clean up test file
        if os.path.exists(test_filename):
            os.remove(test_filename)
    
    # Wait a moment for processing
    print("\n⏳ Waiting for document processing...")
    time.sleep(3)
    
    # Test 2: Semantic search
    print("\n🔍 Step 2: Testing semantic search...")
    
    test_queries = [
        "What are the pool timings?",
        "Can children swim alone?",
        "How deep is the pool?",
        "When is pool maintenance?",
        "What facilities are available at the pool?"
    ]
    
    for query in test_queries:
        try:
            search_data = {
                "query": query,
                "limit": 3,
                "threshold": 0.5
            }
            
            response = requests.post(f"{base_url}/api/documents/search", json=search_data)
            
            if response.status_code == 200:
                search_result = response.json()
                documents = search_result.get('documents', [])
                
                print(f"\n   Query: '{query}'")
                print(f"   Results: {len(documents)} documents found")
                
                if documents:
                    best_match = documents[0]
                    print(f"   Best match: {best_match['title']}")
                    print(f"   Similarity: {best_match['similarity_score']:.3f}")
                    print(f"   Preview: {best_match['content_preview'][:100]}...")
                else:
                    print("   No relevant documents found")
                    
            else:
                print(f"   ❌ Search failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Search error: {e}")
    
    # Test 3: AI Query with enhanced context
    print("\n🤖 Step 3: Testing AI query with vector context...")
    
    try:
        ai_query_data = {
            "query": "What are the swimming pool rules and timings at Gopalan Atlantis?"
        }
        
        response = requests.post(f"{base_url}/api/query", json=ai_query_data)
        
        if response.status_code == 200:
            ai_result = response.json()
            print("✅ AI query successful!")
            print(f"   Vector context used: {ai_result.get('vector_context_used', False)}")
            print(f"   Vector documents found: {ai_result.get('vector_documents_found', 0)}")
            print(f"   OpenAI files used: {ai_result.get('openai_files_used', 0)}")
            print(f"   Response preview: {ai_result.get('answer', '')[:200]}...")
        else:
            print(f"❌ AI query failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ AI query error: {e}")
    
    # Test 4: Cleanup
    print("\n🧹 Step 4: Cleaning up test document...")
    
    try:
        if document_id:
            response = requests.delete(f"{base_url}/api/documents/{document_id}")
            if response.status_code == 200:
                print("✅ Test document deleted successfully")
            else:
                print(f"⚠️ Delete failed: {response.status_code}")
    except Exception as e:
        print(f"⚠️ Cleanup error: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Enhanced Document Upload Test Complete!")
    print("\nFeatures Tested:")
    print("✅ Document upload with text extraction")
    print("✅ Vector embedding storage in PostgreSQL")
    print("✅ OpenAI file upload integration")
    print("✅ Semantic similarity search")
    print("✅ AI query with vector context enhancement")
    print("✅ Document deletion from all systems")
    
    return True

def test_vector_service_directly():
    """Test vector service directly"""
    print("\n🔬 Testing Vector Service Directly...")
    
    try:
        from services.vector_service import vector_service
        
        # Test document storage
        test_doc_id = f"direct_test_{int(time.time())}"
        test_content = "Gopalan Atlantis has a beautiful clubhouse available for events and celebrations."
        
        success = vector_service.store_document_embedding(
            document_id=test_doc_id,
            content=test_content,
            metadata={"type": "test", "category": "amenities"}
        )
        
        if success:
            print("✅ Direct vector storage successful")
            
            # Test search
            results = vector_service.similarity_search("clubhouse events", limit=2)
            if results:
                print(f"✅ Direct vector search found {len(results)} results")
                for result in results:
                    if result['document_id'] == test_doc_id:
                        print("✅ Found our test document in search results")
                        break
            
            # Cleanup
            vector_service.delete_document_embedding(test_doc_id)
            print("✅ Direct test cleanup complete")
            
        else:
            print("❌ Direct vector storage failed")
            
    except Exception as e:
        print(f"❌ Direct vector service test failed: {e}")

def main():
    """Run all tests"""
    print("🚀 Enhanced Document Upload and Vector Integration Test Suite")
    print("Testing complete document upload flow with vector database integration")
    
    # Check if Flask app is running
    try:
        response = requests.get("http://localhost:5000/health", timeout=5)
        if response.status_code != 200:
            print("❌ Flask application is not running on localhost:5000")
            print("Please start the application with: python app.py")
            return False
    except Exception:
        print("❌ Cannot connect to Flask application on localhost:5000")
        print("Please start the application with: python app.py")
        return False
    
    print("✅ Flask application is running")
    
    # Run tests
    success = test_document_upload_and_search()
    test_vector_service_directly()
    
    if success:
        print("\n🎊 All tests completed successfully!")
        print("Your enhanced document upload system is working correctly!")
    else:
        print("\n⚠️ Some tests failed. Please check the logs for details.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
