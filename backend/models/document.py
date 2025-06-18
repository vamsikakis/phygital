from database import db
import json
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime

class Document(db.Model):
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    file_url = db.Column(db.String(255), nullable=False)
    uploaded_by = db.Column(db.String(100), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default='Active')
    # Store tags as JSON array in PostgreSQL
    _tags = db.Column('tags', db.Text, default='[]')
    # Store metadata as JSON object in PostgreSQL
    _metadata = db.Column('metadata', db.Text, default='{}')
    
    @property
    def tags(self):
        return json.loads(self._tags) if self._tags else []
    
    @tags.setter
    def tags(self, value):
        self._tags = json.dumps(value)
    
    @property
    def metadata(self):
        return json.loads(self._metadata) if self._metadata else {}
    
    @metadata.setter
    def metadata(self, value):
        self._metadata = json.dumps(value)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'type': self.type,
            'category': self.category,
            'fileUrl': self.file_url,
            'uploadedBy': self.uploaded_by,
            'uploadedAt': self.uploaded_at.isoformat(),
            'status': self.status,
            'tags': self.tags,
            'metadata': self.metadata
        }

class DocumentType(db.Model):
    __tablename__ = 'document_types'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(255))
    icon = db.Column(db.String(50))
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'icon': self.icon
        }
