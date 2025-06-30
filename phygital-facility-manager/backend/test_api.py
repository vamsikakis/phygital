#!/usr/bin/env python3
"""Test API endpoints"""

import requests
import json

def test_document_search():
    """Test document search endpoint"""
    print("🔍 Testing Document Search API")
    print("=" * 40)
    
    url = "http://localhost:5000/api/documents/search"
    data = {
        "query": "pool timings",
        "limit": 5,
        "threshold": 0.7
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Document search API working!")
        else:
            print("❌ Document search API failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_health():
    """Test health endpoint"""
    print("\n❤️ Testing Health API")
    print("=" * 40)
    
    try:
        response = requests.get("http://localhost:5000/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Health API working!")
        else:
            print("❌ Health API failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_ai_query():
    """Test AI query endpoint"""
    print("\n🤖 Testing AI Query API")
    print("=" * 40)
    
    url = "http://localhost:5000/api/query"
    data = {
        "query": "What are the pool timings at Gopalan Atlantis?"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ AI Query API working!")
        else:
            print("❌ AI Query API failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Testing Enhanced Document Management APIs")
    print("=" * 60)
    
    test_health()
    test_document_search()
    test_ai_query()
    
    print("\n" + "=" * 60)
    print("🎉 API Testing Complete!")
