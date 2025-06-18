from app import app
from database import db
from models.document import Document, DocumentType
from datetime import datetime
import json
import os

def init_db():
    """Initialize database with schema and seed data"""
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Create document types if they don't exist
        doc_types = [
            {"name": "Manual", "description": "User guides and instruction manuals", "icon": "book"},
            {"name": "Invoice", "description": "Payment invoices", "icon": "receipt"},
            {"name": "Contract", "description": "Legal agreements", "icon": "gavel"},
            {"name": "Report", "description": "Statistical reports", "icon": "assessment"},
            {"name": "Form", "description": "Forms and applications", "icon": "description"}
        ]
        
        for doc_type in doc_types:
            existing = DocumentType.query.filter_by(name=doc_type["name"]).first()
            if not existing:
                new_type = DocumentType(
                    name=doc_type["name"],
                    description=doc_type["description"],
                    icon=doc_type["icon"]
                )
                db.session.add(new_type)
        
        # Create sample documents if none exist
        if Document.query.count() == 0:
            sample_docs = [
                {
                    "title": "Atlantis Facility User Guide",
                    "type": "Manual",
                    "category": "Guides",
                    "file_url": "/uploads/documents/sample_user_guide.pdf",
                    "uploaded_by": "System Admin",
                    "tags": ["guide", "manual", "facility"],
                    "metadata": {
                        "size": 1024,
                        "pages": 10,
                        "language": "en"
                    }
                },
                {
                    "title": "Maintenance Contract 2025",
                    "type": "Contract",
                    "category": "Legal",
                    "file_url": "/uploads/documents/sample_contract.pdf",
                    "uploaded_by": "Legal Department",
                    "tags": ["contract", "maintenance", "2025"],
                    "metadata": {
                        "size": 2048,
                        "pages": 5,
                        "language": "en"
                    }
                },
                {
                    "title": "Q1 Financial Report",
                    "type": "Report",
                    "category": "Finance",
                    "file_url": "/uploads/documents/sample_report.pdf",
                    "uploaded_by": "Finance Team",
                    "tags": ["finance", "report", "Q1"],
                    "metadata": {
                        "size": 1536,
                        "pages": 8,
                        "language": "en"
                    }
                }
            ]
            
            for doc in sample_docs:
                # Create sample document file if it doesn't exist
                upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads/documents")
                os.makedirs(upload_dir, exist_ok=True)
                
                file_path = os.path.join(upload_dir, doc["file_url"].split("/")[-1])
                if not os.path.exists(file_path):
                    with open(file_path, "w") as f:
                        f.write(f"Sample content for {doc['title']}")
                
                new_doc = Document(
                    title=doc["title"],
                    type=doc["type"],
                    category=doc["category"],
                    file_url=doc["file_url"],
                    uploaded_by=doc["uploaded_by"],
                    uploaded_at=datetime.utcnow(),
                    status="Active",
                    _tags=json.dumps(doc["tags"]),
                    _metadata=json.dumps(doc["metadata"])
                )
                db.session.add(new_doc)
        
        db.session.commit()
        print("Database initialized successfully!")

if __name__ == "__main__":
    init_db()
