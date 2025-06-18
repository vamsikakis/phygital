-- Schema creation SQL for Gopalan Atlantis Facility Manager
-- This script creates the tables for document operations, notifications, AI queries, and exports

-- Create extension for UUID generation if not exists
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Notification Log table for tracking all email notifications
CREATE TABLE IF NOT EXISTS notification_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    notification_type TEXT NOT NULL, -- announcement, event, ticket, document
    recipients JSONB NOT NULL, -- array of recipient emails
    subject TEXT,
    source_id UUID, -- ID of the related entity (announcement, event, etc.)
    content TEXT,
    status TEXT NOT NULL DEFAULT 'pending', -- pending, sent, failed, processed
    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id),
    metadata JSONB -- Additional metadata
);

-- Document Operations table for tracking operations performed on documents
CREATE TABLE IF NOT EXISTS document_operations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    operation TEXT NOT NULL, -- extract_text, generate_summary, optimize_pdf, convert_to_pdf
    status TEXT NOT NULL DEFAULT 'processing', -- processing, success, failed
    metadata JSONB, -- Additional metadata including errors, completion time, etc.
    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id)
);

-- Download tracking table
CREATE TABLE IF NOT EXISTS downloads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id),
    file_id UUID NOT NULL,
    file_type TEXT NOT NULL, -- document, ticket_attachment, event_material
    file_name TEXT,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- AI Query Log table for tracking AI queries and responses
CREATE TABLE IF NOT EXISTS ai_query_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id),
    query TEXT NOT NULL,
    context_type TEXT, -- all, documents, tickets, amenities
    response_text TEXT,
    context_sources JSONB, -- JSON array of source references
    created_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB -- Additional metadata
);

-- Export Log table for tracking document exports and PDF generation
CREATE TABLE IF NOT EXISTS export_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_type TEXT NOT NULL, -- document, ticket, event, announcement, financial
    source_id UUID NOT NULL,
    export_type TEXT NOT NULL, -- pdf, csv, excel
    filename TEXT,
    storage_path TEXT,
    created_by UUID REFERENCES auth.users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    status TEXT NOT NULL DEFAULT 'processing', -- processing, success, failed
    metadata JSONB -- Additional metadata
);

-- FAQ table for common questions and answers
CREATE TABLE IF NOT EXISTS faqs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    category TEXT,
    order_index INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Financial Reports table
CREATE TABLE IF NOT EXISTS financial_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    report_type TEXT NOT NULL, -- monthly, quarterly, annual, special
    period_start DATE,
    period_end DATE,
    description TEXT,
    document_id UUID REFERENCES documents(id),
    status TEXT NOT NULL DEFAULT 'draft', -- draft, published, archived
    created_by UUID REFERENCES auth.users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Financial Details table for storing report line items
CREATE TABLE IF NOT EXISTS financial_details (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    report_id UUID REFERENCES financial_reports(id) ON DELETE CASCADE,
    category TEXT NOT NULL, -- income, expense, asset, liability
    subcategory TEXT,
    description TEXT,
    amount DECIMAL(12,2) NOT NULL,
    transaction_date DATE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add Row Level Security (RLS) policies

-- Notification logs - only administrators can see all notification logs
ALTER TABLE notification_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY notification_logs_admin ON notification_logs
    USING (auth.uid() IN (SELECT id FROM users WHERE role = 'admin'));

-- Document operations - users can see operations on documents they have access to
ALTER TABLE document_operations ENABLE ROW LEVEL SECURITY;

CREATE POLICY document_operations_admin ON document_operations
    USING (auth.uid() IN (SELECT id FROM users WHERE role = 'admin'));
    
CREATE POLICY document_operations_user ON document_operations
    USING (document_id IN (
        SELECT d.id FROM documents d
        WHERE d.visibility = 'public' OR 
              auth.uid() = d.created_by OR
              auth.uid() IN (SELECT id FROM users WHERE role = 'admin')
    ));

-- Downloads - users can see their own downloads, admins can see all
ALTER TABLE downloads ENABLE ROW LEVEL SECURITY;

CREATE POLICY downloads_user ON downloads
    USING (auth.uid() = user_id OR
           auth.uid() IN (SELECT id FROM users WHERE role = 'admin'));

-- AI query logs - users can see their own queries, admins can see all
ALTER TABLE ai_query_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY ai_query_logs_user ON ai_query_logs
    USING (auth.uid() = user_id OR
           auth.uid() IN (SELECT id FROM users WHERE role = 'admin'));

-- Export logs - users can see exports they created, admins can see all
ALTER TABLE export_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY export_logs_user ON export_logs
    USING (auth.uid() = created_by OR
           auth.uid() IN (SELECT id FROM users WHERE role = 'admin'));

-- FAQs - everyone can read, only admins can write
ALTER TABLE faqs ENABLE ROW LEVEL SECURITY;

CREATE POLICY faqs_read ON faqs FOR SELECT
    USING (true);
    
CREATE POLICY faqs_write ON faqs FOR INSERT
    WITH CHECK (auth.uid() IN (SELECT id FROM users WHERE role = 'admin'));
    
CREATE POLICY faqs_update ON faqs FOR UPDATE
    USING (auth.uid() IN (SELECT id FROM users WHERE role = 'admin'));
    
CREATE POLICY faqs_delete ON faqs FOR DELETE
    USING (auth.uid() IN (SELECT id FROM users WHERE role = 'admin'));

-- Financial reports - only admins can write, residents can read published reports
ALTER TABLE financial_reports ENABLE ROW LEVEL SECURITY;

CREATE POLICY financial_reports_read ON financial_reports FOR SELECT
    USING (status = 'published' OR 
           auth.uid() IN (SELECT id FROM users WHERE role IN ('admin', 'staff')));
    
CREATE POLICY financial_reports_write ON financial_reports FOR INSERT
    WITH CHECK (auth.uid() IN (SELECT id FROM users WHERE role IN ('admin', 'staff')));
    
CREATE POLICY financial_reports_update ON financial_reports FOR UPDATE
    USING (auth.uid() IN (SELECT id FROM users WHERE role IN ('admin', 'staff')));
    
CREATE POLICY financial_reports_delete ON financial_reports FOR DELETE
    USING (auth.uid() IN (SELECT id FROM users WHERE role = 'admin'));

-- Financial details - follow same access as the parent report
ALTER TABLE financial_details ENABLE ROW LEVEL SECURITY;

CREATE POLICY financial_details_read ON financial_details FOR SELECT
    USING (report_id IN (
        SELECT id FROM financial_reports
        WHERE status = 'published' OR
              auth.uid() IN (SELECT id FROM users WHERE role IN ('admin', 'staff'))
    ));
    
CREATE POLICY financial_details_write ON financial_details FOR INSERT
    WITH CHECK (auth.uid() IN (SELECT id FROM users WHERE role IN ('admin', 'staff')));
    
CREATE POLICY financial_details_update ON financial_details FOR UPDATE
    USING (auth.uid() IN (SELECT id FROM users WHERE role IN ('admin', 'staff')));
    
CREATE POLICY financial_details_delete ON financial_details FOR DELETE
    USING (auth.uid() IN (SELECT id FROM users WHERE role = 'admin'));

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_notification_logs_type ON notification_logs(notification_type);
CREATE INDEX IF NOT EXISTS idx_notification_logs_status ON notification_logs(status);
CREATE INDEX IF NOT EXISTS idx_document_operations_doc_id ON document_operations(document_id);
CREATE INDEX IF NOT EXISTS idx_document_operations_status ON document_operations(status);
CREATE INDEX IF NOT EXISTS idx_downloads_user_id ON downloads(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_query_logs_user_id ON ai_query_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_export_logs_source ON export_logs(source_type, source_id);
CREATE INDEX IF NOT EXISTS idx_export_logs_status ON export_logs(status);
CREATE INDEX IF NOT EXISTS idx_financial_reports_status ON financial_reports(status);
CREATE INDEX IF NOT EXISTS idx_financial_reports_date ON financial_reports(period_start, period_end);
CREATE INDEX IF NOT EXISTS idx_financial_details_report_id ON financial_details(report_id);
