#!/usr/bin/env python3
"""
Database Setup Script for AI Integration
Sets up PostgreSQL database with pgvector extension and required tables
"""

import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import config

def create_database_if_not_exists():
    """Create database if it doesn't exist"""
    print("🗄️ Checking database existence...")
    
    try:
        # Connect to postgres database to create our target database
        conn = psycopg2.connect(
            host=config.DB_HOST,
            database='postgres',  # Connect to default postgres database
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            port=getattr(config, 'DB_PORT', 5432)
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{config.DB_NAME}'")
        exists = cursor.fetchone()
        
        if not exists:
            print(f"Creating database: {config.DB_NAME}")
            cursor.execute(f"CREATE DATABASE {config.DB_NAME}")
            print("✅ Database created successfully")
        else:
            print("✅ Database already exists")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return False

def setup_pgvector_extension():
    """Set up pgvector extension"""
    print("\n🔧 Setting up pgvector extension...")
    
    try:
        conn = psycopg2.connect(
            host=config.DB_HOST,
            database=config.DB_NAME,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            port=getattr(config, 'DB_PORT', 5432)
        )
        cursor = conn.cursor()
        
        # Create pgvector extension
        cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        conn.commit()
        
        # Verify extension
        cursor.execute("SELECT * FROM pg_extension WHERE extname = 'vector';")
        extension = cursor.fetchone()
        
        if extension:
            print("✅ pgvector extension installed successfully")
        else:
            print("❌ pgvector extension installation failed")
            return False
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error setting up pgvector: {e}")
        return False

def create_tables():
    """Create required tables for AI integration"""
    print("\n📋 Creating database tables...")
    
    try:
        conn = psycopg2.connect(
            host=config.DB_HOST,
            database=config.DB_NAME,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            port=getattr(config, 'DB_PORT', 5432)
        )
        cursor = conn.cursor()
        
        # Create document_embeddings table
        create_embeddings_table = """
        CREATE TABLE IF NOT EXISTS document_embeddings (
            id SERIAL PRIMARY KEY,
            document_id VARCHAR(255) UNIQUE NOT NULL,
            content TEXT NOT NULL,
            embedding vector(1536),
            metadata JSONB DEFAULT '{}',
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );
        """
        
        cursor.execute(create_embeddings_table)
        print("✅ Created document_embeddings table")
        
        # Create index for vector similarity search
        create_vector_index = """
        CREATE INDEX IF NOT EXISTS idx_document_embeddings_embedding 
        ON document_embeddings USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 100);
        """
        
        cursor.execute(create_vector_index)
        print("✅ Created vector similarity index")
        
        # Create assistant_threads table
        create_threads_table = """
        CREATE TABLE IF NOT EXISTS assistant_threads (
            id SERIAL PRIMARY KEY,
            thread_id VARCHAR(255) UNIQUE NOT NULL,
            user_id VARCHAR(255),
            created_at TIMESTAMP DEFAULT NOW(),
            last_activity TIMESTAMP DEFAULT NOW(),
            metadata JSONB DEFAULT '{}'
        );
        """
        
        cursor.execute(create_threads_table)
        print("✅ Created assistant_threads table")
        
        # Create query_logs table for analytics
        create_logs_table = """
        CREATE TABLE IF NOT EXISTS query_logs (
            id SERIAL PRIMARY KEY,
            thread_id VARCHAR(255),
            query TEXT NOT NULL,
            response TEXT,
            module VARCHAR(50),
            processing_time FLOAT,
            created_at TIMESTAMP DEFAULT NOW(),
            metadata JSONB DEFAULT '{}'
        );
        """
        
        cursor.execute(create_logs_table)
        print("✅ Created query_logs table")
        
        # Create documents table for file management
        create_documents_table = """
        CREATE TABLE IF NOT EXISTS documents (
            id SERIAL PRIMARY KEY,
            document_id VARCHAR(255) UNIQUE NOT NULL,
            filename VARCHAR(255) NOT NULL,
            file_path TEXT,
            file_size INTEGER,
            mime_type VARCHAR(100),
            category VARCHAR(100),
            uploaded_by VARCHAR(255),
            processed BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT NOW(),
            metadata JSONB DEFAULT '{}'
        );
        """
        
        cursor.execute(create_documents_table)
        print("✅ Created documents table")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ All tables created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

def insert_sample_data():
    """Insert sample data for testing"""
    print("\n📝 Inserting sample data...")
    
    try:
        conn = psycopg2.connect(
            host=config.DB_HOST,
            database=config.DB_NAME,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            port=getattr(config, 'DB_PORT', 5432)
        )
        cursor = conn.cursor()
        
        # Sample documents
        sample_docs = [
            {
                'document_id': 'sample_amenities_001',
                'filename': 'amenities_guide.txt',
                'category': 'amenities',
                'metadata': {'type': 'guide', 'priority': 'high'}
            },
            {
                'document_id': 'sample_rules_001',
                'filename': 'facility_rules.txt',
                'category': 'rules',
                'metadata': {'type': 'policy', 'priority': 'high'}
            },
            {
                'document_id': 'sample_contact_001',
                'filename': 'contact_info.txt',
                'category': 'contact',
                'metadata': {'type': 'directory', 'priority': 'medium'}
            }
        ]
        
        for doc in sample_docs:
            insert_query = """
            INSERT INTO documents (document_id, filename, category, metadata)
            VALUES (%(document_id)s, %(filename)s, %(category)s, %(metadata)s)
            ON CONFLICT (document_id) DO NOTHING
            """
            cursor.execute(insert_query, doc)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ Sample data inserted successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error inserting sample data: {e}")
        return False

def verify_setup():
    """Verify the database setup"""
    print("\n🔍 Verifying database setup...")
    
    try:
        conn = psycopg2.connect(
            host=config.DB_HOST,
            database=config.DB_NAME,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            port=getattr(config, 'DB_PORT', 5432)
        )
        cursor = conn.cursor()
        
        # Check tables
        tables_to_check = [
            'document_embeddings',
            'assistant_threads',
            'query_logs',
            'documents'
        ]
        
        for table in tables_to_check:
            cursor.execute(f"""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = '{table}'
                );
            """)
            exists = cursor.fetchone()[0]
            
            if exists:
                cursor.execute(f"SELECT COUNT(*) FROM {table};")
                count = cursor.fetchone()[0]
                print(f"✅ Table '{table}' exists with {count} records")
            else:
                print(f"❌ Table '{table}' not found")
                return False
        
        # Check pgvector extension
        cursor.execute("SELECT * FROM pg_extension WHERE extname = 'vector';")
        vector_ext = cursor.fetchone()
        
        if vector_ext:
            print("✅ pgvector extension is active")
        else:
            print("❌ pgvector extension not found")
            return False
        
        cursor.close()
        conn.close()
        
        print("✅ Database setup verification completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error verifying setup: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 AI Integration Database Setup")
    print("=" * 50)
    
    steps = [
        ("Create Database", create_database_if_not_exists),
        ("Setup pgvector Extension", setup_pgvector_extension),
        ("Create Tables", create_tables),
        ("Insert Sample Data", insert_sample_data),
        ("Verify Setup", verify_setup)
    ]
    
    for step_name, step_func in steps:
        print(f"\n📍 {step_name}...")
        if not step_func():
            print(f"❌ {step_name} failed. Stopping setup.")
            return False
    
    print("\n" + "=" * 50)
    print("🎉 Database setup completed successfully!")
    print("✅ Your AI integration database is ready to use.")
    print("\nNext steps:")
    print("1. Run 'python simple_ai_test.py' to test basic connectivity")
    print("2. Run 'python test_ai_integration.py' for comprehensive testing")
    print("3. Start your Flask application with 'python app.py'")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
