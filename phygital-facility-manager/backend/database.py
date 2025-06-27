"""
Neon PostgreSQL Database Configuration and Models
Replaces Supabase with direct PostgreSQL connection using SQLAlchemy
"""

import os
import psycopg2
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, scoped_session
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_PORT = os.getenv('DB_PORT', '5432')

# Create database URL
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    echo=False  # Set to True for SQL debugging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Session = scoped_session(SessionLocal)

# Create declarative base
Base = declarative_base()

# Database Models
class User(Base):
    __tablename__ = 'users'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False)
    name = Column(String)
    full_name = Column(String)
    phone = Column(String)
    apartment_number = Column(String)
    role = Column(String, default='resident')  # admin, staff, resident
    google_id = Column(String, unique=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Document(Base):
    __tablename__ = 'documents'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    description = Column(Text)
    content = Column(Text)
    category = Column(String)
    file_url = Column(String)
    file_path = Column(String)
    file_size = Column(Integer)
    mime_type = Column(String)
    storage_path = Column(String)
    uploaded_by = Column(String, ForeignKey('users.id'))
    is_public = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    uploader = relationship("User", backref="uploaded_documents")

class Ticket(Base):
    __tablename__ = 'tickets'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    subject = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String)
    priority = Column(String, default='medium')  # low, medium, high, urgent
    status = Column(String, default='open')  # open, in_progress, resolved, closed
    created_by = Column(String, ForeignKey('users.id'))
    assigned_to = Column(String, ForeignKey('users.id'))
    apartment_number = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime)
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by], backref="created_tickets")
    assignee = relationship("User", foreign_keys=[assigned_to], backref="assigned_tickets")

class Announcement(Base):
    __tablename__ = 'announcements'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String)
    priority = Column(String, default='normal')  # low, normal, high, urgent
    is_published = Column(Boolean, default=False)
    published_at = Column(DateTime)
    expires_at = Column(DateTime)
    created_by = Column(String, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    creator = relationship("User", backref="announcements")

class Event(Base):
    __tablename__ = 'events'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    description = Column(Text)
    event_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime)
    location = Column(String)
    category = Column(String)
    max_attendees = Column(Integer)
    registration_required = Column(Boolean, default=False)
    created_by = Column(String, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    creator = relationship("User", backref="events")

class AIQueryLog(Base):
    __tablename__ = 'ai_query_logs'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    query = Column(Text, nullable=False)
    response_text = Column(Text)
    context_type = Column(String)
    context_sources = Column(JSON)
    meta_data = Column(JSON)
    user_id = Column(String, ForeignKey('users.id'))
    processing_time = Column(Integer)  # in milliseconds
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", backref="ai_queries")

class FAQ(Base):
    __tablename__ = 'faqs'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    question = Column(String, nullable=False)
    answer = Column(Text, nullable=False)
    category = Column(String)
    order_index = Column(Integer)
    is_published = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Database helper functions
def get_db_session():
    """Get a database session"""
    return Session()

def close_db_session():
    """Close the database session"""
    Session.remove()

def init_db():
    """Initialize the database by creating all tables"""
    try:
        Base.metadata.create_all(engine)
        print("Database tables created successfully")
        return True
    except Exception as e:
        print(f"Error creating database tables: {e}")
        return False

def test_connection():
    """Test database connection"""
    try:
        connection = engine.connect()
        connection.execute("SELECT 1")
        connection.close()
        print("Database connection successful")
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False

def get_raw_connection():
    """Get a raw psycopg2 connection for direct SQL operations"""
    try:
        return psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT
        )
    except Exception as e:
        print(f"Raw connection failed: {e}")
        return None

# Common database operations
def create_record(model_class, **kwargs):
    """Create a new record"""
    session = get_db_session()
    try:
        record = model_class(**kwargs)
        session.add(record)
        session.commit()
        session.refresh(record)
        return record
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def get_record_by_id(model_class, record_id):
    """Get a record by ID"""
    session = get_db_session()
    try:
        return session.query(model_class).filter(model_class.id == record_id).first()
    finally:
        session.close()

def update_record(model_class, record_id, **kwargs):
    """Update a record"""
    session = get_db_session()
    try:
        record = session.query(model_class).filter(model_class.id == record_id).first()
        if record:
            for key, value in kwargs.items():
                setattr(record, key, value)
            record.updated_at = datetime.utcnow()
            session.commit()
            session.refresh(record)
        return record
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def delete_record(model_class, record_id):
    """Delete a record"""
    session = get_db_session()
    try:
        record = session.query(model_class).filter(model_class.id == record_id).first()
        if record:
            session.delete(record)
            session.commit()
            return True
        return False
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def get_all_records(model_class, limit=None, offset=None):
    """Get all records with optional pagination"""
    session = get_db_session()
    try:
        query = session.query(model_class)
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
        return query.all()
    finally:
        session.close()

# Initialize database on import
if __name__ == "__main__":
    print("Testing database connection...")
    if test_connection():
        print("Initializing database...")
        init_db()
    else:
        print("Database connection failed. Please check your configuration.")
