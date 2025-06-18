import os
from supabase import create_client, Client
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase_service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# Create supabase client
def get_supabase_client():
    """Get a Supabase client using the API key from environment variables."""
    if not supabase_url or not supabase_key:
        raise ValueError("Supabase URL and API key must be set in environment variables")
    return create_client(supabase_url, supabase_key)

def get_admin_client():
    """Get a Supabase client with admin privileges using the service key."""
    if not supabase_url or not supabase_service_key:
        raise ValueError("Supabase URL and service role key must be set in environment variables")
    return create_client(supabase_url, supabase_service_key)

# SQLAlchemy connection for more complex operations
def get_sqlalchemy_engine():
    """Get an SQLAlchemy engine connected to the Supabase PostgreSQL database."""
    connection_string = os.getenv("POSTGRES_CONNECTION_STRING")
    if not connection_string:
        raise ValueError("PostgreSQL connection string must be set in environment variables")
    return create_engine(connection_string)

# Database initialization
def init_database():
    """Initialize the database by creating necessary tables if they don't exist."""
    engine = get_sqlalchemy_engine()
    
    # Create tables using raw SQL - this gives more control than SQLAlchemy models
    # for complex Supabase-specific operations
    with engine.connect() as conn:
        # Documents table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS documents (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                title VARCHAR NOT NULL,
                description TEXT,
                content TEXT,
                category VARCHAR,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                file_url VARCHAR
            );
        """))
        
        # Announcements table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS announcements (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                title VARCHAR NOT NULL,
                content TEXT,
                date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                priority VARCHAR,
                created_by UUID,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """))
        
        # Events table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS events (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                title VARCHAR NOT NULL,
                description TEXT,
                date DATE NOT NULL,
                time_start TIME,
                time_end TIME,
                location VARCHAR,
                created_by UUID,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """))
        
        # Polls table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS polls (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                title VARCHAR NOT NULL,
                description TEXT,
                closing_date TIMESTAMP WITH TIME ZONE,
                created_by UUID,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """))
        
        # Poll options table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS poll_options (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                poll_id UUID REFERENCES polls(id) ON DELETE CASCADE,
                text VARCHAR NOT NULL
            );
        """))
        
        # Poll votes table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS poll_votes (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                option_id UUID REFERENCES poll_options(id) ON DELETE CASCADE,
                user_id UUID,
                timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """))
        
        # Tickets table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS tickets (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                subject VARCHAR NOT NULL,
                description TEXT,
                status VARCHAR DEFAULT 'open',
                category VARCHAR,
                created_by UUID,
                assigned_to UUID,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """))
        
        # Ticket comments table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS ticket_comments (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                ticket_id UUID REFERENCES tickets(id) ON DELETE CASCADE,
                content TEXT NOT NULL,
                created_by UUID,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """))
        
        # Users table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                email VARCHAR UNIQUE NOT NULL,
                name VARCHAR,
                apartment VARCHAR,
                role VARCHAR DEFAULT 'resident',
                google_id VARCHAR,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """))
        
        # Create necessary indexes
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_documents_category ON documents(category);
            CREATE INDEX IF NOT EXISTS idx_announcements_date ON announcements(date);
            CREATE INDEX IF NOT EXISTS idx_events_date ON events(date);
            CREATE INDEX IF NOT EXISTS idx_tickets_status ON tickets(status);
            CREATE INDEX IF NOT EXISTS idx_tickets_category ON tickets(category);
        """))
        
        # Setup RLS (Row Level Security) policies if you're using Supabase Auth
        # This is very important for security when using Supabase
        
        # Example RLS policy for documents - users can read all documents but only admins can edit
        conn.execute(text("""
            ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
            
            DROP POLICY IF EXISTS "Documents are viewable by all authenticated users" ON documents;
            CREATE POLICY "Documents are viewable by all authenticated users" 
                ON documents FOR SELECT 
                USING (true);
                
            DROP POLICY IF EXISTS "Documents are editable by admins" ON documents;
            CREATE POLICY "Documents are editable by admins" 
                ON documents FOR ALL 
                USING (
                    EXISTS (
                        SELECT 1 FROM users 
                        WHERE users.id = auth.uid() AND users.role = 'admin'
                    )
                );
        """))
        
        # Commit transaction
        conn.commit()

# Supabase CRUD operations using the client
def create_record(table, data):
    """Insert a new record into the specified table."""
    client = get_supabase_client()
    result = client.table(table).insert(data).execute()
    return result.data[0] if result.data else None

def get_record(table, id):
    """Get a single record by its ID."""
    client = get_supabase_client()
    result = client.table(table).select("*").eq("id", id).execute()
    return result.data[0] if result.data else None

def update_record(table, id, data):
    """Update a record by its ID."""
    client = get_supabase_client()
    result = client.table(table).update(data).eq("id", id).execute()
    return result.data[0] if result.data else None

def delete_record(table, id):
    """Delete a record by its ID."""
    client = get_supabase_client()
    result = client.table(table).delete().eq("id", id).execute()
    return result.data[0] if result.data else None

def query_records(table, query_func):
    """
    Query records using a function that applies filters to the Supabase query.
    
    Example usage:
    query_records('documents', lambda q: q.eq('category', 'bylaws').order('created_at', desc=True))
    """
    client = get_supabase_client()
    base_query = client.table(table).select("*")
    result = query_func(base_query).execute()
    return result.data

# Function to execute raw SQL queries for complex operations
def execute_raw_query(sql, params=None):
    """Execute a raw SQL query and return the results."""
    engine = get_sqlalchemy_engine()
    with engine.connect() as conn:
        result = conn.execute(text(sql), params or {})
        return [dict(row) for row in result]
