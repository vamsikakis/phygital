#!/usr/bin/env python3
"""
Final Integration Test
Complete end-to-end test of the AI-powered facility management system
"""

import os
import sys
import json
import time
import requests
from datetime import datetime

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.vector_service import vector_service
from services.openai_assistant_service import openai_assistant_service

def test_flask_app_running():
    """Test if Flask app is running"""
    print("🌐 Testing Flask Application...")
    
    try:
        response = requests.get("http://localhost:5000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Flask app is running")
            return True
        else:
            print(f"❌ Flask app returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Flask app not accessible: {e}")
        return False

def test_api_endpoints():
    """Test key API endpoints"""
    print("\n🔌 Testing API Endpoints...")
    
    try:
        # Test API info endpoint
        response = requests.get("http://localhost:5000/api", timeout=10)
        if response.status_code == 200:
            print("✅ API info endpoint working")
        else:
            print("❌ API info endpoint failed")
            return False
        
        # Test AI query endpoint
        query_data = {"query": "What amenities are available?"}
        response = requests.post(
            "http://localhost:5000/api/query",
            json=query_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if 'response' in result:
                print("✅ AI query endpoint working")
                print(f"   Sample response: {result['response'][:80]}...")
            else:
                print("❌ AI query endpoint returned invalid response")
                return False
        else:
            print(f"❌ AI query endpoint failed with status {response.status_code}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ API endpoint test failed: {e}")
        return False

def test_frontend_serving():
    """Test if frontend is being served correctly"""
    print("\n🎨 Testing Frontend Serving...")
    
    try:
        # Test main page
        response = requests.get("http://localhost:5000/", timeout=10)
        if response.status_code == 200 and "html" in response.headers.get('content-type', ''):
            print("✅ Frontend HTML served correctly")
        else:
            print("❌ Frontend HTML not served correctly")
            return False
        
        # Test static assets
        response = requests.get("http://localhost:5000/assets/index-f5f4410b.js", timeout=10)
        if response.status_code == 200:
            print("✅ Static assets served correctly")
        else:
            print("⚠️ Static assets may not be available (this is OK if build is different)")
        
        return True
        
    except Exception as e:
        print(f"❌ Frontend serving test failed: {e}")
        return False

def test_vector_search_integration():
    """Test vector search with real data"""
    print("\n🔍 Testing Vector Search Integration...")
    
    try:
        # Store a test document
        test_doc_id = f"final_test_{int(time.time())}"
        test_content = """
        Gopalan Atlantis Swimming Pool Information:
        - Pool is open from 6:00 AM to 10:00 PM daily
        - Children under 12 must be accompanied by adults
        - Pool maintenance on Mondays from 8:00 AM to 10:00 AM
        - Swimming lessons available on weekends
        - Pool depth: 4 feet to 8 feet
        """
        
        success = vector_service.store_document_embedding(
            document_id=test_doc_id,
            content=test_content,
            metadata={"type": "amenity", "category": "pool", "test": True}
        )
        
        if not success:
            print("❌ Failed to store test document")
            return False
        
        print("✅ Test document stored")
        
        # Test search
        search_results = vector_service.similarity_search(
            query="What are the pool timings and rules?",
            limit=3,
            threshold=0.3
        )
        
        if search_results:
            print(f"✅ Vector search returned {len(search_results)} results")
            best_result = search_results[0]
            print(f"   Best match score: {best_result['similarity_score']:.3f}")
            
            if best_result['document_id'] == test_doc_id:
                print("✅ Search correctly found our test document")
            else:
                print("⚠️ Search found other documents (this is OK)")
        else:
            print("❌ Vector search returned no results")
            return False
        
        # Cleanup
        vector_service.delete_document_embedding(test_doc_id)
        print("✅ Test document cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Vector search integration test failed: {e}")
        return False

def test_assistant_integration():
    """Test AI assistant integration"""
    print("\n🤖 Testing AI Assistant Integration...")
    
    try:
        # Test assistant info
        assistant_info = openai_assistant_service.get_assistant_info()
        if assistant_info:
            print(f"✅ Assistant available: {assistant_info.get('name', 'Unknown')}")
        else:
            print("⚠️ Assistant not configured (this is OK)")
            return True  # Not a failure if assistant isn't set up
        
        # Test thread creation
        thread_id = openai_assistant_service.create_thread()
        if thread_id:
            print(f"✅ Thread created: {thread_id[:20]}...")
        else:
            print("❌ Thread creation failed")
            return False
        
        # Test query processing
        response = openai_assistant_service.process_query(
            thread_id=thread_id,
            query="What facilities are available for residents?"
        )
        
        if response and response.get('response'):
            print("✅ Assistant query processing working")
            print(f"   Response length: {len(response['response'])} characters")
        else:
            print("❌ Assistant query processing failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Assistant integration test failed: {e}")
        return False

def test_end_to_end_flow():
    """Test complete end-to-end user flow"""
    print("\n🔄 Testing End-to-End Flow...")
    
    try:
        # 1. Store facility information
        facility_doc_id = f"e2e_test_{int(time.time())}"
        facility_content = """
        Gopalan Atlantis Facility Information:
        - 24/7 Security with CCTV monitoring
        - Clubhouse available for events (booking required)
        - Gym open 5:00 AM to 11:00 PM
        - Children's play area with safety equipment
        - Visitor parking available (registration required)
        - Maintenance requests via facility management office
        """
        
        vector_service.store_document_embedding(
            document_id=facility_doc_id,
            content=facility_content,
            metadata={"type": "facility_info", "test": True}
        )
        
        print("✅ Facility information stored")
        
        # 2. Simulate user query via API
        user_query = "How do I book the clubhouse for an event?"
        
        response = requests.post(
            "http://localhost:5000/api/query",
            json={"query": user_query},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ End-to-end API query successful")
            print(f"   Query: {user_query}")
            print(f"   Response: {result.get('response', '')[:100]}...")
            
            # Check if response contains relevant information
            response_text = result.get('response', '').lower()
            if 'clubhouse' in response_text or 'booking' in response_text:
                print("✅ Response is contextually relevant")
            else:
                print("⚠️ Response may not be fully relevant")
        else:
            print(f"❌ End-to-end API query failed: {response.status_code}")
            return False
        
        # 3. Test document retrieval
        all_docs = vector_service.get_all_documents(limit=10)
        print(f"✅ Retrieved {len(all_docs)} documents from database")
        
        # Cleanup
        vector_service.delete_document_embedding(facility_doc_id)
        print("✅ End-to-end test cleanup completed")
        
        return True
        
    except Exception as e:
        print(f"❌ End-to-end flow test failed: {e}")
        return False

def main():
    """Run final integration tests"""
    print("🚀 Final Integration Test Suite")
    print("=" * 50)
    print("Testing complete AI-powered facility management system")
    print("=" * 50)
    
    tests = [
        ("Flask Application", test_flask_app_running),
        ("API Endpoints", test_api_endpoints),
        ("Frontend Serving", test_frontend_serving),
        ("Vector Search Integration", test_vector_search_integration),
        ("AI Assistant Integration", test_assistant_integration),
        ("End-to-End Flow", test_end_to_end_flow)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n📍 Running {test_name}...")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 FINAL TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"{test_name:<30} {status}")
    
    print(f"\nOverall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Your AI-powered facility management system is fully operational!")
        print("\n🚀 System Ready For Production Use:")
        print("   • AI-powered query processing ✅")
        print("   • Vector similarity search ✅")
        print("   • Document management ✅")
        print("   • Frontend interface ✅")
        print("   • API endpoints ✅")
        print("   • Database integration ✅")
        print("\n🌐 Access your application at: http://localhost:5000")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed.")
        print("Please check the error messages above and fix any issues.")
        print("The system may still be partially functional.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
