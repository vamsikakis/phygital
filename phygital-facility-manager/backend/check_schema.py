#!/usr/bin/env python3
"""
Check existing database schema
"""

import os
import sys
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_existing_schema():
    """Check what tables and columns already exist"""
    print("🔍 Checking Existing Database Schema")
    print("=" * 50)
    
    # Get database connection details
    db_host = os.getenv('DB_HOST')
    db_name = os.getenv('DB_NAME')
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_port = os.getenv('DB_PORT', '5432')
    
    try:
        # Connect to the database
        connection = psycopg2.connect(
            host=db_host,
            database=db_name,
            user=db_user,
            password=db_password,
            port=db_port,
            sslmode='require'
        )
        
        cursor = connection.cursor()
        
        # Get all tables
        print("\n📋 Existing Tables:")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        for table in tables:
            table_name = table[0]
            print(f"\n🔸 Table: {table_name}")
            
            # Get columns for this table
            cursor.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = %s AND table_schema = 'public'
                ORDER BY ordinal_position;
            """, (table_name,))
            
            columns = cursor.fetchall()
            for col in columns:
                nullable = "NULL" if col[2] == "YES" else "NOT NULL"
                default = f" DEFAULT {col[3]}" if col[3] else ""
                print(f"   - {col[0]}: {col[1]} {nullable}{default}")
        
        # Check for vector extension tables
        print("\n🔍 Vector Extension Tables:")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_name LIKE '%vector%' OR table_name LIKE '%embedding%'
            ORDER BY table_name;
        """)
        
        vector_tables = cursor.fetchall()
        if vector_tables:
            for table in vector_tables:
                print(f"   - {table[0]}")
        else:
            print("   No vector-specific tables found")
        
        # Check for indexes
        print("\n📊 Indexes:")
        cursor.execute("""
            SELECT indexname, tablename, indexdef
            FROM pg_indexes 
            WHERE schemaname = 'public'
            ORDER BY tablename, indexname;
        """)
        
        indexes = cursor.fetchall()
        current_table = None
        for idx in indexes:
            if idx[1] != current_table:
                current_table = idx[1]
                print(f"\n🔸 Table: {current_table}")
            print(f"   - {idx[0]}")
        
        cursor.close()
        connection.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking schema: {e}")
        return False

def main():
    """Main function"""
    if check_existing_schema():
        print("\n✅ Schema check completed successfully!")
    else:
        print("\n❌ Schema check failed!")

if __name__ == "__main__":
    main()
