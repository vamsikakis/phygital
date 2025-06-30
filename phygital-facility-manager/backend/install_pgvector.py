#!/usr/bin/env python3
"""
Install pgvector Extension in Neon PostgreSQL
"""

import os
import sys
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def install_pgvector():
    """Install pgvector extension in Neon PostgreSQL"""
    print("🔧 Installing pgvector Extension in Neon PostgreSQL")
    print("=" * 60)
    
    # Get database connection details
    db_host = os.getenv('DB_HOST')
    db_name = os.getenv('DB_NAME')
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_port = os.getenv('DB_PORT', '5432')
    
    if not all([db_host, db_name, db_user, db_password]):
        print("❌ Missing database configuration in .env file")
        print("Please ensure DB_HOST, DB_NAME, DB_USER, and DB_PASSWORD are set")
        return False
    
    try:
        # Connect to the database
        print(f"📡 Connecting to database: {db_name} on {db_host}")
        
        connection = psycopg2.connect(
            host=db_host,
            database=db_name,
            user=db_user,
            password=db_password,
            port=db_port,
            sslmode='require'
        )
        
        cursor = connection.cursor()
        
        # Check if pgvector is already installed
        print("\n🔍 Checking if pgvector extension exists...")
        cursor.execute("SELECT * FROM pg_extension WHERE extname = 'vector';")
        existing = cursor.fetchone()
        
        if existing:
            print("✅ pgvector extension is already installed!")
            
            # Check version
            cursor.execute("SELECT extversion FROM pg_extension WHERE extname = 'vector';")
            version = cursor.fetchone()[0]
            print(f"   Version: {version}")
        else:
            # Install pgvector extension
            print("\n🚀 Installing pgvector extension...")
            cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            connection.commit()
            print("✅ pgvector extension installed successfully!")
        
        # Test the extension
        print("\n🧪 Testing pgvector functionality...")
        
        # Create a test table with vector column
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_vectors (
                id SERIAL PRIMARY KEY,
                content TEXT,
                embedding vector(1536)
            );
        """)
        
        # Insert a test vector
        test_vector = [0.1] * 1536  # Simple test vector
        cursor.execute("""
            INSERT INTO test_vectors (content, embedding)
            VALUES (%s, %s::vector)
            ON CONFLICT DO NOTHING;
        """, ("Test document", test_vector))

        # Test similarity search
        cursor.execute("""
            SELECT content, embedding <-> %s::vector as distance
            FROM test_vectors
            ORDER BY embedding <-> %s::vector
            LIMIT 1;
        """, (test_vector, test_vector))
        
        result = cursor.fetchone()
        if result:
            print(f"✅ Vector similarity search working! Distance: {result[1]}")
        
        # Clean up test table
        cursor.execute("DROP TABLE IF EXISTS test_vectors;")
        connection.commit()
        
        # Show available vector operators
        print("\n📊 Available vector operators:")
        cursor.execute("""
            SELECT oprname, oprleft::regtype, oprright::regtype, oprresult::regtype
            FROM pg_operator 
            WHERE oprname IN ('<->', '<#>', '<=>') 
            ORDER BY oprname;
        """)
        
        operators = cursor.fetchall()
        for op in operators:
            print(f"   {op[0]}: {op[1]} {op[0]} {op[2]} -> {op[3]}")
        
        cursor.close()
        connection.close()
        
        print("\n🎉 pgvector installation and testing completed successfully!")
        print("\nAvailable distance operators:")
        print("   <-> : L2 distance (Euclidean)")
        print("   <#> : Negative inner product")
        print("   <=> : Cosine distance")
        
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def check_prerequisites():
    """Check if all prerequisites are met"""
    print("🔍 Checking Prerequisites")
    print("=" * 30)
    
    # Check if psycopg2 is installed
    try:
        import psycopg2
        print("✅ psycopg2 is installed")
    except ImportError:
        print("❌ psycopg2 is not installed")
        print("   Run: pip install psycopg2-binary")
        return False
    
    # Check environment variables
    required_vars = ['DB_HOST', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
    missing_vars = []
    
    for var in required_vars:
        if os.getenv(var):
            print(f"✅ {var} is set")
        else:
            print(f"❌ {var} is not set")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️ Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    print("✅ All prerequisites met!")
    return True

def main():
    """Main function"""
    print("🚀 Neon PostgreSQL pgvector Installation Script")
    print("=" * 60)
    
    if not check_prerequisites():
        print("\n❌ Prerequisites not met. Please fix the issues above.")
        return False
    
    if install_pgvector():
        print("\n🎊 Installation completed successfully!")
        print("\nNext steps:")
        print("1. ✅ pgvector extension is now available")
        print("2. 🔧 Run: python test_neon_connection.py")
        print("3. 🚀 Start your application: python app.py")
        return True
    else:
        print("\n❌ Installation failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
