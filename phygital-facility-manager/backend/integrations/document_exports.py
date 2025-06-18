import os
import io
import uuid
import json
from datetime import datetime
import requests
from typing import Dict, Any, Optional, List, Tuple
from dotenv import load_dotenv
import base64

# Import our integration modules
from integrations.supabase import get_supabase_client
from integrations.storage import get_download_url, record_download
from db import get_db_session

# Load environment variables
load_dotenv()

# Supabase and Edge Function configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")


class DocumentExporter:
    """
    Handles document download and export functionality including PDF generation,
    file conversion, and export to various formats.
    """
    
    def __init__(self):
        """Initialize the document exporter with necessary connections"""
        self.supabase = get_supabase_client()
        self.db_session = get_db_session()
    
    def get_document(self, document_id: str) -> Dict[str, Any]:
        """
        Retrieve document details from the database
        
        Args:
            document_id: ID of the document
            
        Returns:
            Document details or None if not found
        """
        response = self.supabase.table('documents').select('*').eq('id', document_id).execute()
        
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None

    def download_original_document(self, document_id: str, user_id: Optional[str] = None) -> Tuple[str, Dict[str, Any]]:
        """
        Generate a download URL for the original document file
        
        Args:
            document_id: ID of the document to download
            user_id: ID of the user downloading the document (for tracking)
            
        Returns:
            Tuple of (download_url, document_data)
        """
        document = self.get_document(document_id)
        
        if not document:
            raise ValueError(f"Document with ID {document_id} not found")
        
        # Get the storage path from the document record
        storage_path = document.get('storage_path')
        
        if not storage_path:
            raise ValueError(f"Document {document_id} has no associated storage path")
        
        # Get bucket name from storage path or use default
        bucket_name = 'documents'  # Default bucket
        
        # Generate a signed download URL
        download_url = get_download_url(bucket_name, storage_path, expiration_seconds=3600)
        
        if not download_url:
            raise ValueError(f"Failed to generate download URL for document {document_id}")
        
        # Record the download if user_id is provided
        if user_id:
            record_download(
                user_id=user_id,
                file_id=document_id,
                file_type='document',
                file_name=document.get('title', 'Unknown')
            )
            
        return download_url, document
    
    def generate_pdf(self, document_id: str, template: str = "default", 
                    user_id: Optional[str] = None, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate a PDF version of a document using the Edge Function
        
        Args:
            document_id: ID of the document to convert
            template: Template name to use for PDF generation
            user_id: ID of the user requesting PDF generation (for tracking)
            options: Additional options for PDF generation
            
        Returns:
            Dictionary with PDF generation results including download URL
        """
        # Call the generate-pdf edge function
        if not options:
            options = {}
            
        if user_id:
            options["user_id"] = user_id
            
        # Construct the payload
        payload = {
            "source_type": "document",
            "source_id": document_id,
            "template": template,
            "options": options
        }
        
        # Call the edge function
        try:
            # Use service role key for edge function access
            headers = {
                "apikey": SUPABASE_SERVICE_KEY,
                "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                f"{SUPABASE_URL}/functions/v1/generate-pdf",
                headers=headers,
                json=payload
            )
            
            if response.status_code != 200:
                raise ValueError(f"PDF generation failed: {response.text}")
            
            result = response.json()
            
            # Record the download if user_id is provided
            if user_id:
                record_download(
                    user_id=user_id,
                    file_id=document_id,
                    file_type='document_pdf',
                    file_name=result.get('filename')
                )
                
            return result
        except Exception as e:
            raise ValueError(f"Error calling PDF generation function: {str(e)}")
    
    def convert_document(self, document_id: str, target_format: str,
                        user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Convert a document to another format (e.g., DOCX to PDF, PDF to TXT)
        Uses the document processing edge function for conversion
        
        Args:
            document_id: ID of the document to convert
            target_format: Target format for conversion (pdf, txt, docx, etc.)
            user_id: ID of the user requesting conversion (for tracking)
            
        Returns:
            Dictionary with conversion results including download URL
        """
        # Call the process-documents edge function
        payload = {
            "document_id": document_id,
            "action": "convert_to_" + target_format.lower()
        }
        
        # Call the edge function
        try:
            # Use service role key for edge function access
            headers = {
                "apikey": SUPABASE_SERVICE_KEY,
                "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                f"{SUPABASE_URL}/functions/v1/process-documents",
                headers=headers,
                json=payload
            )
            
            if response.status_code != 200:
                raise ValueError(f"Document conversion failed: {response.text}")
            
            result = response.json()
            
            # Record the download if user_id is provided
            if user_id:
                record_download(
                    user_id=user_id,
                    file_id=document_id,
                    file_type=f'document_{target_format}',
                    file_name=result.get('pdf_filename', f"document.{target_format}")
                )
                
            return result
        except Exception as e:
            raise ValueError(f"Error calling document conversion function: {str(e)}")
    
    def extract_text(self, document_id: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Extract text content from a document
        Uses the document processing edge function for text extraction
        
        Args:
            document_id: ID of the document to extract text from
            user_id: ID of the user requesting extraction (for tracking)
            
        Returns:
            Dictionary with extraction results including text content
        """
        # Call the process-documents edge function
        payload = {
            "document_id": document_id,
            "action": "extract_text"
        }
        
        # Call the edge function
        try:
            # Use service role key for edge function access
            headers = {
                "apikey": SUPABASE_SERVICE_KEY,
                "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                f"{SUPABASE_URL}/functions/v1/process-documents",
                headers=headers,
                json=payload
            )
            
            if response.status_code != 200:
                raise ValueError(f"Text extraction failed: {response.text}")
            
            return response.json()
        except Exception as e:
            raise ValueError(f"Error calling text extraction function: {str(e)}")
    
    def generate_document_summary(self, document_id: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a summary of a document using AI
        Uses the document processing edge function for summary generation
        
        Args:
            document_id: ID of the document to summarize
            user_id: ID of the user requesting summarization (for tracking)
            
        Returns:
            Dictionary with summary results including summary text
        """
        # Call the process-documents edge function
        payload = {
            "document_id": document_id,
            "action": "generate_summary"
        }
        
        # Call the edge function
        try:
            # Use service role key for edge function access
            headers = {
                "apikey": SUPABASE_SERVICE_KEY,
                "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                f"{SUPABASE_URL}/functions/v1/process-documents",
                headers=headers,
                json=payload
            )
            
            if response.status_code != 200:
                raise ValueError(f"Summary generation failed: {response.text}")
            
            return response.json()
        except Exception as e:
            raise ValueError(f"Error calling summary generation function: {str(e)}")
            

def create_export_database_tables():
    """
    Create database tables for tracking exports and downloads
    This should be run as part of the database initialization
    """
    # Define SQL for creating the necessary tables
    sql = """
    -- Table for tracking document operations
    CREATE TABLE IF NOT EXISTS document_operations (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        document_id UUID NOT NULL REFERENCES documents(id),
        operation VARCHAR(50) NOT NULL,
        status VARCHAR(20) NOT NULL,
        metadata JSONB,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        created_by UUID REFERENCES users(id)
    );

    -- Table for tracking downloads
    CREATE TABLE IF NOT EXISTS downloads (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        user_id UUID REFERENCES users(id),
        file_id UUID NOT NULL,
        file_type VARCHAR(50) NOT NULL,
        file_name TEXT,
        timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );

    -- Table for tracking exports
    CREATE TABLE IF NOT EXISTS export_logs (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        source_type VARCHAR(50) NOT NULL,
        source_id UUID NOT NULL,
        export_type VARCHAR(20) NOT NULL,
        filename TEXT,
        storage_path TEXT,
        created_by UUID REFERENCES users(id),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        status VARCHAR(20) NOT NULL,
        metadata JSONB
    );

    -- Add indexes for common queries
    CREATE INDEX IF NOT EXISTS idx_document_operations_document_id ON document_operations(document_id);
    CREATE INDEX IF NOT EXISTS idx_downloads_user_id ON downloads(user_id);
    CREATE INDEX IF NOT EXISTS idx_downloads_file_id ON downloads(file_id);
    CREATE INDEX IF NOT EXISTS idx_export_logs_source ON export_logs(source_type, source_id);
    """
    
    # Execute the SQL using our supabase client
    supabase = get_supabase_client()
    supabase.rpc('execute_sql', {'sql': sql}).execute()
    
    print("Created export and download tracking tables")


def create_reports_database_tables():
    """
    Create database tables for financial reports and document management
    This should be run as part of the database initialization
    """
    # Define SQL for creating the necessary tables
    sql = """
    -- Table for financial reports
    CREATE TABLE IF NOT EXISTS financial_reports (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        title VARCHAR(255) NOT NULL,
        report_type VARCHAR(50) NOT NULL,
        period_start DATE,
        period_end DATE,
        storage_path TEXT,
        file_url TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        created_by UUID REFERENCES users(id),
        last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        metadata JSONB,
        status VARCHAR(20) DEFAULT 'draft',
        published BOOLEAN DEFAULT FALSE
    );

    -- Table for tracking document versions
    CREATE TABLE IF NOT EXISTS document_versions (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        document_id UUID NOT NULL REFERENCES documents(id),
        version_number INTEGER NOT NULL,
        storage_path TEXT NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        created_by UUID REFERENCES users(id),
        change_summary TEXT,
        file_size INTEGER,
        active BOOLEAN DEFAULT TRUE
    );

    -- Add indexes for common queries
    CREATE INDEX IF NOT EXISTS idx_financial_reports_period ON financial_reports(period_start, period_end);
    CREATE INDEX IF NOT EXISTS idx_document_versions_document_id ON document_versions(document_id);
    
    -- Add unique constraint for document versions
    ALTER TABLE document_versions 
    ADD CONSTRAINT unique_document_version 
    UNIQUE (document_id, version_number);
    """
    
    # Execute the SQL using our supabase client
    supabase = get_supabase_client()
    supabase.rpc('execute_sql', {'sql': sql}).execute()
    
    print("Created report and document version tables")
