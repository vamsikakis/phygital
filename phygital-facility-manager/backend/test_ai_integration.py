#!/usr/bin/env python3
"""
Comprehensive AI Integration Test Suite
Tests OpenAI integration, vector embeddings, and database connectivity
"""

import os
import sys
import json
import time
import asyncio
from datetime import datetime

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.vector_service import vector_service
from services.openai_assistant_service import openai_assistant_service
from config import config
import openai
import psycopg2

def test_environment_setup():
    """Test if all required environment variables are set"""
    print("🔧 Testing Environment Setup...")
    
    required_vars = [
        'OPENAI_API_KEY',
        'DB_HOST',
        'DB_NAME',
        'DB_USER',
        'DB_PASSWORD'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not hasattr(config, var) or not getattr(config, var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        return False
    
    print("✅ All environment variables are set")
    return True

def test_database_connection():
    """Test database connectivity and pgvector extension"""
    print("\n🗄️ Testing Database Connection...")
    
    try:
        conn = psycopg2.connect(
            host=config.DB_HOST,
            database=config.DB_NAME,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            port=getattr(config, 'DB_PORT', 5432)
        )
        
        cursor = conn.cursor()
        
        # Test basic connection
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"✅ Connected to PostgreSQL: {version[:50]}...")
        
        # Test pgvector extension
        cursor.execute("SELECT * FROM pg_extension WHERE extname = 'vector';")
        vector_ext = cursor.fetchone()
        
        if vector_ext:
            print("✅ pgvector extension is installed")
        else:
            print("❌ pgvector extension not found")
            return False
        
        # Test document_embeddings table
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'document_embeddings'
            );
        """)
        
        table_exists = cursor.fetchone()[0]
        if table_exists:
            print("✅ document_embeddings table exists")
        else:
            print("⚠️ document_embeddings table not found, creating...")
            create_table_sql = """
                CREATE TABLE IF NOT EXISTS document_embeddings (
                    id SERIAL PRIMARY KEY,
                    document_id VARCHAR(255) UNIQUE NOT NULL,
                    content TEXT NOT NULL,
                    embedding vector(1536),
                    metadata JSONB DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                );
                
                CREATE INDEX IF NOT EXISTS idx_document_embeddings_embedding 
                ON document_embeddings USING ivfflat (embedding vector_cosine_ops);
            """
            cursor.execute(create_table_sql)
            conn.commit()
            print("✅ Created document_embeddings table")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_openai_connection():
    """Test OpenAI API connectivity"""
    print("\n🤖 Testing OpenAI Connection...")
    
    try:
        client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
        
        # Test embeddings
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input="Test embedding for Gopalan Atlantis facility management"
        )
        
        embedding = response.data[0].embedding
        print(f"✅ OpenAI Embeddings API working (dimension: {len(embedding)})")
        
        # Test chat completion
        chat_response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant for apartment management."},
                {"role": "user", "content": "What are the key features of a good apartment management system?"}
            ],
            max_tokens=100
        )
        
        print(f"✅ OpenAI Chat API working")
        print(f"   Response: {chat_response.choices[0].message.content[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ OpenAI connection failed: {e}")
        return False

def test_vector_service():
    """Test vector service functionality"""
    print("\n🔍 Testing Vector Service...")
    
    try:
        # Test document storage
        test_doc_id = f"test_doc_{int(time.time())}"
        test_content = """
        Gopalan Atlantis is a premium apartment complex with modern amenities.
        It features a swimming pool, gym, clubhouse, and 24/7 security.
        The apartments are spacious with balconies and modern fittings.
        """
        
        # Store document
        success = vector_service.store_document_embedding(
            document_id=test_doc_id,
            content=test_content,
            metadata={"type": "test", "category": "amenities"}
        )
        
        if success:
            print("✅ Document embedding stored successfully")
        else:
            print("❌ Failed to store document embedding")
            return False
        
        # Test similarity search
        search_results = vector_service.similarity_search(
            query="What amenities are available in the apartment?",
            limit=3,
            threshold=0.5
        )
        
        if search_results:
            print(f"✅ Similarity search working ({len(search_results)} results)")
            for i, result in enumerate(search_results[:2]):
                print(f"   Result {i+1}: Score {result['similarity_score']:.3f}")
        else:
            print("❌ Similarity search returned no results")
        
        # Test document retrieval
        retrieved_doc = vector_service.get_document_embedding(test_doc_id)
        if retrieved_doc:
            print("✅ Document retrieval working")
        else:
            print("❌ Document retrieval failed")
        
        # Cleanup test document
        vector_service.delete_document_embedding(test_doc_id)
        print("✅ Test document cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Vector service test failed: {e}")
        return False

def test_assistant_service():
    """Test OpenAI Assistant service"""
    print("\n🎯 Testing Assistant Service...")
    
    try:
        # Test assistant initialization
        assistant_info = openai_assistant_service.get_assistant_info()
        if assistant_info:
            print(f"✅ Assistant service initialized: {assistant_info.get('name', 'Unknown')}")
        else:
            print("❌ Assistant service not initialized")
            return False
        
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
            query="What are the office hours for the facility management?"
        )
        
        if response and response.get('response'):
            print("✅ Query processing working")
            print(f"   Response: {response['response'][:100]}...")
        else:
            print("❌ Query processing failed")
        
        return True
        
    except Exception as e:
        print(f"❌ Assistant service test failed: {e}")
        return False

def test_integration_flow():
    """Test complete integration flow"""
    print("\n🔄 Testing Complete Integration Flow...")
    
    try:
        # 1. Store sample documents
        sample_docs = [
            {
                "id": f"integration_test_1_{int(time.time())}",
                "content": "Gopalan Atlantis has a beautiful swimming pool open from 6 AM to 10 PM daily.",
                "metadata": {"type": "amenity", "category": "recreation"}
            },
            {
                "id": f"integration_test_2_{int(time.time())}",
                "content": "The gym at Gopalan Atlantis is equipped with modern equipment and is open 24/7.",
                "metadata": {"type": "amenity", "category": "fitness"}
            }
        ]
        
        stored_docs = []
        for doc in sample_docs:
            success = vector_service.store_document_embedding(
                document_id=doc["id"],
                content=doc["content"],
                metadata=doc["metadata"]
            )
            if success:
                stored_docs.append(doc["id"])
        
        print(f"✅ Stored {len(stored_docs)} sample documents")
        
        # 2. Test semantic search
        search_query = "What are the pool timings?"
        results = vector_service.similarity_search(search_query, limit=2)
        
        if results:
            print(f"✅ Semantic search found {len(results)} relevant documents")
            best_match = results[0]
            print(f"   Best match (score: {best_match['similarity_score']:.3f}): {best_match['content'][:80]}...")
        
        # 3. Test AI-powered response
        thread_id = openai_assistant_service.create_thread()
        if thread_id:
            # Add context from search results
            context = "\n".join([r['content'] for r in results[:2]])
            enhanced_query = f"Based on this information: {context}\n\nQuestion: {search_query}"
            
            ai_response = openai_assistant_service.process_query(
                thread_id=thread_id,
                query=enhanced_query
            )
            
            if ai_response:
                print("✅ AI-powered response generated")
                print(f"   Response: {ai_response.get('response', '')[:100]}...")
        
        # Cleanup
        for doc_id in stored_docs:
            vector_service.delete_document_embedding(doc_id)
        print("✅ Integration test completed and cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration flow test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting AI Integration Test Suite")
    print("=" * 50)
    
    tests = [
        ("Environment Setup", test_environment_setup),
        ("Database Connection", test_database_connection),
        ("OpenAI Connection", test_openai_connection),
        ("Vector Service", test_vector_service),
        ("Assistant Service", test_assistant_service),
        ("Integration Flow", test_integration_flow)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"{test_name:<20} {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! AI integration is working correctly.")
        return True
    else:
        print("⚠️ Some tests failed. Please check the configuration and try again.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
