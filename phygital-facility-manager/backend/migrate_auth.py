"""
Database migration script to add authentication fields to users table
"""

import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_database_url():
    """Get database URL from environment variables"""
    return os.getenv('DATABASE_URL') or os.getenv('POSTGRES_CONNECTION_STRING')

def migrate_users_table():
    """Add new authentication fields to users table"""
    
    database_url = get_database_url()
    if not database_url:
        print("Error: No database URL found in environment variables")
        return False
    
    try:
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Start transaction
            trans = conn.begin()
            
            try:
                print("Adding new columns to users table...")
                
                # Add new columns if they don't exist
                migration_queries = [
                    """
                    ALTER TABLE users 
                    ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255);
                    """,
                    """
                    ALTER TABLE users 
                    ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;
                    """,
                    """
                    ALTER TABLE users 
                    ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT FALSE;
                    """,
                    """
                    ALTER TABLE users 
                    ADD COLUMN IF NOT EXISTS reset_token VARCHAR(255);
                    """,
                    """
                    ALTER TABLE users 
                    ADD COLUMN IF NOT EXISTS reset_token_expires TIMESTAMPTZ;
                    """,
                    """
                    ALTER TABLE users 
                    ADD COLUMN IF NOT EXISTS last_login TIMESTAMPTZ;
                    """,
                    """
                    ALTER TABLE users 
                    ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT NOW();
                    """
                ]
                
                for query in migration_queries:
                    conn.execute(text(query))
                    print(f"Executed: {query.strip()}")
                
                # Update existing users to have default values
                print("Updating existing users with default values...")
                
                update_queries = [
                    """
                    UPDATE users 
                    SET is_active = TRUE 
                    WHERE is_active IS NULL;
                    """,
                    """
                    UPDATE users 
                    SET email_verified = FALSE 
                    WHERE email_verified IS NULL;
                    """,
                    """
                    UPDATE users 
                    SET updated_at = created_at 
                    WHERE updated_at IS NULL;
                    """,
                    """
                    UPDATE users 
                    SET role = 'owners' 
                    WHERE role = 'resident';
                    """
                ]
                
                for query in update_queries:
                    result = conn.execute(text(query))
                    print(f"Updated {result.rowcount} rows: {query.strip()}")
                
                # Create indexes for better performance
                print("Creating indexes...")
                
                index_queries = [
                    """
                    CREATE INDEX IF NOT EXISTS idx_users_email 
                    ON users(email);
                    """,
                    """
                    CREATE INDEX IF NOT EXISTS idx_users_reset_token 
                    ON users(reset_token);
                    """,
                    """
                    CREATE INDEX IF NOT EXISTS idx_users_role 
                    ON users(role);
                    """,
                    """
                    CREATE INDEX IF NOT EXISTS idx_users_is_active 
                    ON users(is_active);
                    """
                ]
                
                for query in index_queries:
                    conn.execute(text(query))
                    print(f"Created index: {query.strip()}")
                
                # Commit transaction
                trans.commit()
                print("Migration completed successfully!")
                return True
                
            except Exception as e:
                trans.rollback()
                print(f"Error during migration: {str(e)}")
                return False
                
    except Exception as e:
        print(f"Error connecting to database: {str(e)}")
        return False

def verify_migration():
    """Verify that the migration was successful"""
    
    database_url = get_database_url()
    if not database_url:
        print("Error: No database URL found in environment variables")
        return False
    
    try:
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Check if new columns exist
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'users' 
                AND column_name IN ('password_hash', 'is_active', 'email_verified', 'reset_token', 'reset_token_expires', 'last_login', 'updated_at')
                ORDER BY column_name;
            """))
            
            columns = [row[0] for row in result]
            expected_columns = ['email_verified', 'is_active', 'last_login', 'password_hash', 'reset_token', 'reset_token_expires', 'updated_at']
            
            print(f"Found columns: {columns}")
            print(f"Expected columns: {expected_columns}")
            
            if set(columns) == set(expected_columns):
                print("✓ All new columns are present")
                
                # Check user count and roles
                result = conn.execute(text("SELECT COUNT(*), role FROM users GROUP BY role ORDER BY role;"))
                role_counts = list(result)
                print(f"User role distribution: {role_counts}")
                
                return True
            else:
                missing = set(expected_columns) - set(columns)
                print(f"✗ Missing columns: {missing}")
                return False
                
    except Exception as e:
        print(f"Error verifying migration: {str(e)}")
        return False

if __name__ == "__main__":
    print("Starting authentication migration...")
    print("=" * 50)
    
    if migrate_users_table():
        print("\nVerifying migration...")
        if verify_migration():
            print("\n✓ Migration completed and verified successfully!")
            sys.exit(0)
        else:
            print("\n✗ Migration verification failed!")
            sys.exit(1)
    else:
        print("\n✗ Migration failed!")
        sys.exit(1)
