#!/usr/bin/env python3
"""
Simple AI Integration Test
Quick test to verify OpenAI and database connectivity
"""

import os
import sys
import json
from datetime import datetime

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import config
import openai
import psycopg2

def test_openai_simple():
    """Simple OpenAI API test"""
    print("🤖 Testing OpenAI API...")
    
    try:
        client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
        
        # Test simple completion
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Say 'Hello from Gopalan Atlantis AI!'"}
            ],
            max_tokens=50
        )
        
        message = response.choices[0].message.content
        print(f"✅ OpenAI Response: {message}")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI test failed: {e}")
        return False

def test_database_simple():
    """Simple database connectivity test"""
    print("\n🗄️ Testing Database...")
    
    try:
        conn = psycopg2.connect(
            host=config.DB_HOST,
            database=config.DB_NAME,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            port=getattr(config, 'DB_PORT', 5432)
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT NOW();")
        current_time = cursor.fetchone()[0]
        
        print(f"✅ Database connected. Current time: {current_time}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_embedding_simple():
    """Simple embedding test"""
    print("\n🔍 Testing Embeddings...")
    
    try:
        client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
        
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input="Gopalan Atlantis apartment management system"
        )
        
        embedding = response.data[0].embedding
        print(f"✅ Embedding created with {len(embedding)} dimensions")
        print(f"   First 5 values: {embedding[:5]}")
        return True
        
    except Exception as e:
        print(f"❌ Embedding test failed: {e}")
        return False

def main():
    """Run simple tests"""
    print("🚀 Simple AI Integration Test")
    print("=" * 40)
    
    tests = [
        test_openai_simple,
        test_database_simple,
        test_embedding_simple
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All simple tests passed!")
        return True
    else:
        print("⚠️ Some tests failed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
