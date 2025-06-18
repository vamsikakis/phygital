import os
from supabase import create_client, Client
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase_service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# Create supabase client
supabase: Client = create_client(supabase_url, supabase_key)

# SQLAlchemy setup for more complex operations
Base = declarative_base()
engine = create_engine(os.getenv("POSTGRES_CONNECTION_STRING"))
Session = sessionmaker(bind=engine)

# Define models
class Document(Base):
    __tablename__ = 'documents'
    
    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    content = Column(Text)
    category = Column(String)
    created_at = Column(DateTime)
    last_updated = Column(DateTime)
    file_url = Column(String)  # URL to Google Drive file if applicable
    
class Announcement(Base):
    __tablename__ = 'announcements'
    
    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    content = Column(Text)
    date = Column(DateTime)
    priority = Column(String)
    created_by = Column(String)
    
class Event(Base):
    __tablename__ = 'events'
    
    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    date = Column(DateTime)
    time_start = Column(DateTime)
    time_end = Column(DateTime)
    location = Column(String)
    created_by = Column(String)

class Poll(Base):
    __tablename__ = 'polls'
    
    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    closing_date = Column(DateTime)
    created_by = Column(String)
    options = relationship("PollOption", back_populates="poll")

class PollOption(Base):
    __tablename__ = 'poll_options'
    
    id = Column(String, primary_key=True)
    poll_id = Column(String, ForeignKey('polls.id'))
    text = Column(String, nullable=False)
    poll = relationship("Poll", back_populates="options")
    votes = relationship("PollVote", back_populates="option")

class PollVote(Base):
    __tablename__ = 'poll_votes'
    
    id = Column(String, primary_key=True)
    option_id = Column(String, ForeignKey('poll_options.id'))
    user_id = Column(String)
    timestamp = Column(DateTime)
    option = relationship("PollOption", back_populates="votes")

class Ticket(Base):
    __tablename__ = 'tickets'
    
    id = Column(String, primary_key=True)
    subject = Column(String, nullable=False)
    description = Column(Text)
    status = Column(String)  # new, in_progress, pending, resolved, closed
    category = Column(String)  # maintenance, complaint, request, other
    priority = Column(String)  # low, medium, high, critical
    apartment_unit = Column(String)
    location_details = Column(String)
    created_by = Column(String, ForeignKey('users.id'))
    assigned_to = Column(String, ForeignKey('users.id'))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    comments = relationship("TicketComment", back_populates="ticket")
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    assignee = relationship("User", foreign_keys=[assigned_to])

class TicketComment(Base):
    __tablename__ = 'ticket_comments'
    
    id = Column(String, primary_key=True)
    ticket_id = Column(String, ForeignKey('tickets.id'))
    content = Column(Text)
    created_by = Column(String, ForeignKey('users.id'))
    created_at = Column(DateTime)
    ticket = relationship("Ticket", back_populates="comments")
    
    # Relationship to get author details
    author = relationship("User", foreign_keys=[created_by])

class User(Base):
    __tablename__ = 'users'
    
    id = Column(String, primary_key=True)
    email = Column(String, nullable=False)
    name = Column(String)
    full_name = Column(String)
    apartment = Column(String)
    role = Column(String)  # admin, resident, staff
    google_id = Column(String)  # For Google OAuth
    created_at = Column(DateTime)

class NotificationLog(Base):
    __tablename__ = 'notification_logs'
    
    id = Column(String, primary_key=True)
    notification_type = Column(String, nullable=False)  # announcement, event, ticket, document
    recipients = Column(Text)  # JSON array of recipient emails
    subject = Column(String)
    source_id = Column(String)  # ID of the related entity (announcement, event, etc.)
    content = Column(Text)
    status = Column(String)  # sent, failed, processed
    created_at = Column(DateTime)
    created_by = Column(String, ForeignKey('users.id'))
    meta_data = Column(Text)  # JSON metadata

class DocumentOperation(Base):
    __tablename__ = 'document_operations'
    
    id = Column(String, primary_key=True)
    document_id = Column(String, ForeignKey('documents.id'))
    operation = Column(String, nullable=False)  # extract_text, generate_summary, optimize_pdf, convert_to_pdf
    status = Column(String, nullable=False)  # success, failed, processing
    meta_data = Column(Text)  # JSON metadata
    created_at = Column(DateTime)
    created_by = Column(String, ForeignKey('users.id'))
    
class Download(Base):
    __tablename__ = 'downloads'
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'))
    file_id = Column(String, nullable=False)
    file_type = Column(String, nullable=False)  # document, ticket_attachment, event_material
    file_name = Column(String)
    timestamp = Column(DateTime)

class AIQueryLog(Base):
    __tablename__ = 'ai_query_logs'
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'))
    query = Column(Text, nullable=False)
    context_type = Column(String)  # all, documents, tickets, amenities
    response_text = Column(Text)
    context_sources = Column(Text)  # JSON array of source references
    created_at = Column(DateTime)
    meta_data = Column(Text)  # JSON metadata

class ExportLog(Base):
    __tablename__ = 'export_logs'
    
    id = Column(String, primary_key=True)
    source_type = Column(String, nullable=False)  # document, ticket, event, announcement, financial
    source_id = Column(String, nullable=False)
    export_type = Column(String, nullable=False)  # pdf, csv, excel
    filename = Column(String)
    storage_path = Column(String)
    created_by = Column(String, ForeignKey('users.id'))
    created_at = Column(DateTime)
    status = Column(String, nullable=False)  # success, failed, processing
    meta_data = Column(Text)  # JSON metadata
    
class FAQ(Base):
    __tablename__ = 'faqs'
    
    id = Column(String, primary_key=True)
    question = Column(String, nullable=False)
    answer = Column(Text, nullable=False)
    category = Column(String)
    order_index = Column(Integer)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

# Create tables if they don't exist
def init_db():
    Base.metadata.create_all(engine)

# Database helper functions
def get_db_session():
    return Session()

# Common database operations
def get_all(table_name):
    """Get all records from a table using Supabase"""
    response = supabase.table(table_name).select("*").execute()
    return response.data

def get_by_id(table_name, id):
    """Get a record by ID using Supabase"""
    response = supabase.table(table_name).select("*").eq("id", id).execute()
    if len(response.data) > 0:
        return response.data[0]
    return None

def insert(table_name, data):
    """Insert a record using Supabase"""
    response = supabase.table(table_name).insert(data).execute()
    return response.data

def update(table_name, id, data):
    """Update a record using Supabase"""
    response = supabase.table(table_name).update(data).eq("id", id).execute()
    return response.data

def delete(table_name, id):
    """Delete a record using Supabase"""
    response = supabase.table(table_name).delete().eq("id", id).execute()
    return response.data
