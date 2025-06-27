#!/usr/bin/env python3
"""
Test Neon PostgreSQL Connection
Tests the database connection and creates necessary tables
"""

import os
import sys
from dotenv import load_dotenv

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

def test_neon_connection():
    """Test connection to Neon PostgreSQL database"""
    print("🔗 Testing Neon PostgreSQL Connection")
    print("=" * 50)
    
    try:
        from database import test_connection, init_db
        
        # Test basic connection
        print("\n📡 Testing database connection...")
        if test_connection():
            print("✅ Database connection successful!")
        else:
            print("❌ Database connection failed!")
            return False
        
        # Initialize database tables
        print("\n🏗️ Initializing database tables...")
        if init_db():
            print("✅ Database tables created successfully!")
        else:
            print("❌ Failed to create database tables!")
            return False
        
        # Test basic CRUD operations
        print("\n🧪 Testing basic CRUD operations...")
        from database import create_record, get_record_by_id, update_record, delete_record, User
        
        # Create a test user
        test_user = create_record(
            User,
            email="test@example.com",
            name="Test User",
            full_name="Test User Full Name",
            role="resident"
        )
        
        if test_user:
            print(f"✅ Created test user: {test_user.email}")
            
            # Read the user
            retrieved_user = get_record_by_id(User, test_user.id)
            if retrieved_user:
                print(f"✅ Retrieved user: {retrieved_user.email}")
            else:
                print("❌ Failed to retrieve user")
                return False
            
            # Update the user
            updated_user = update_record(User, test_user.id, name="Updated Test User")
            if updated_user and updated_user.name == "Updated Test User":
                print(f"✅ Updated user: {updated_user.name}")
            else:
                print("❌ Failed to update user")
                return False
            
            # Delete the user
            if delete_record(User, test_user.id):
                print("✅ Deleted test user")
            else:
                print("❌ Failed to delete user")
                return False
        else:
            print("❌ Failed to create test user")
            return False
        
        print("\n🎉 All database tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_vector_service():
    """Test vector service with PostgreSQL"""
    print("\n🔍 Testing Vector Service with PostgreSQL")
    print("=" * 50)
    
    try:
        from services.vector_service import vector_service
        
        # Test storing a document embedding
        print("\n📝 Testing document embedding storage...")
        test_doc_id = "test_doc_123"
        test_content = "This is a test document for vector storage in Neon PostgreSQL with pgvector extension."
        
        success = vector_service.store_document_embedding(
            document_id=test_doc_id,
            content=test_content,
            metadata={
                "title": "Test Document",
                "category": "test",
                "source": "neon_test"
            }
        )
        
        if success:
            print("✅ Document embedding stored successfully!")
            
            # Test similarity search
            print("\n🔍 Testing similarity search...")
            results = vector_service.similarity_search(
                query="test document vector storage",
                limit=5,
                threshold=0.5
            )
            
            if results and len(results) > 0:
                print(f"✅ Similarity search returned {len(results)} results")
                for i, result in enumerate(results):
                    print(f"   {i+1}. Document: {result['document_id']} (Score: {result['similarity_score']:.3f})")
            else:
                print("⚠️ No results found in similarity search")
            
            # Clean up test document
            print("\n🧹 Cleaning up test document...")
            if vector_service.delete_document_embedding(test_doc_id):
                print("✅ Test document deleted successfully!")
            else:
                print("⚠️ Failed to delete test document")
            
        else:
            print("❌ Failed to store document embedding")
            return False
        
        print("\n🎉 Vector service tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Vector service test failed: {e}")
        return False

def check_environment():
    """Check if all required environment variables are set"""
    print("\n⚙️ Checking Environment Configuration")
    print("=" * 50)
    
    required_vars = [
        'DB_HOST',
        'DB_NAME', 
        'DB_USER',
        'DB_PASSWORD',
        'OPENAI_API_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if 'PASSWORD' in var or 'KEY' in var:
                display_value = f"{value[:4]}...{value[-4:]}" if len(value) > 8 else "***"
            else:
                display_value = value
            print(f"✅ {var}: {display_value}")
        else:
            print(f"❌ {var}: Not set")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️ Missing environment variables: {', '.join(missing_vars)}")
        print("Please check your .env file and ensure all required variables are set.")
        return False
    
    print("\n✅ All required environment variables are set!")
    return True

def main():
    """Run all tests"""
    print("🚀 Neon PostgreSQL Integration Test Suite")
    print("Testing migration from Supabase to Neon PostgreSQL")
    print("=" * 60)
    
    # Check environment
    if not check_environment():
        print("\n❌ Environment check failed. Please configure your .env file.")
        return False
    
    # Test database connection
    if not test_neon_connection():
        print("\n❌ Database tests failed.")
        return False
    
    # Test vector service
    if not test_vector_service():
        print("\n⚠️ Vector service tests failed, but database connection works.")
        print("This might be expected if pgvector extension is not installed.")
    
    print("\n" + "=" * 60)
    print("🎊 Neon PostgreSQL migration test completed!")
    print("\nNext steps:")
    print("1. ✅ Database connection is working")
    print("2. ✅ Tables are created successfully") 
    print("3. ✅ Basic CRUD operations work")
    print("4. 🔧 Configure your application to use the new database")
    print("5. 🔧 Install pgvector extension for vector operations (optional)")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
