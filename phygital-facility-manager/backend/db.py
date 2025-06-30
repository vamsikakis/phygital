# Import from the new database module
# Import specific items to avoid conflicts
from database import (
    engine, SessionLocal, Session, Base, get_db_session, close_db_session,
    init_db, test_connection, get_raw_connection,
    create_record, get_record_by_id, update_record, delete_record, get_all_records,
    User, Document, Ticket, Announcement, Event, AIQueryLog, FAQ, DocumentEmbedding
)

# For backward compatibility, import everything from database module
# This allows existing code to continue working without changes

# All models are now imported from database.py - no need to redefine them here

# Legacy functions for backward compatibility
# These now use the new database module functions

def get_all(table_name):
    """Get all records from a table"""
    # This is a legacy function - use get_all_records() from database module instead
    from database import get_all_records
    # Map table names to model classes
    model_map = {
        'users': User,
        'documents': Document,
        'tickets': Ticket,
        'announcements': Announcement,
        'events': Event,
        'faqs': FAQ,
        'ai_query_logs': AIQueryLog
    }
    model_class = model_map.get(table_name)
    if model_class:
        return [record.__dict__ for record in get_all_records(model_class)]
    return []

def get_by_id(table_name, id):
    """Get a record by ID"""
    # This is a legacy function - use get_record_by_id() from database module instead
    from database import get_record_by_id
    model_map = {
        'users': User,
        'documents': Document,
        'tickets': Ticket,
        'announcements': Announcement,
        'events': Event,
        'faqs': FAQ,
        'ai_query_logs': AIQueryLog
    }
    model_class = model_map.get(table_name)
    if model_class:
        record = get_record_by_id(model_class, id)
        return record.__dict__ if record else None
    return None

def insert(table_name, data):
    """Insert a record"""
    # This is a legacy function - use create_record() from database module instead
    from database import create_record
    model_map = {
        'users': User,
        'documents': Document,
        'tickets': Ticket,
        'announcements': Announcement,
        'events': Event,
        'faqs': FAQ,
        'ai_query_logs': AIQueryLog
    }
    model_class = model_map.get(table_name)
    if model_class:
        record = create_record(model_class, **data)
        return [record.__dict__] if record else []
    return []

def update(table_name, id, data):
    """Update a record"""
    # This is a legacy function - use update_record() from database module instead
    from database import update_record
    model_map = {
        'users': User,
        'documents': Document,
        'tickets': Ticket,
        'announcements': Announcement,
        'events': Event,
        'faqs': FAQ,
        'ai_query_logs': AIQueryLog
    }
    model_class = model_map.get(table_name)
    if model_class:
        record = update_record(model_class, id, **data)
        return [record.__dict__] if record else []
    return []

def delete(table_name, id):
    """Delete a record"""
    # This is a legacy function - use delete_record() from database module instead
    from database import delete_record
    model_map = {
        'users': User,
        'documents': Document,
        'tickets': Ticket,
        'announcements': Announcement,
        'events': Event,
        'faqs': FAQ,
        'ai_query_logs': AIQueryLog
    }
    model_class = model_map.get(table_name)
    if model_class:
        success = delete_record(model_class, id)
        return [{'deleted': success}] if success else []
    return []
