"""
Vector Service for OpenAI Embeddings and Similarity Search
Handles document embeddings, vector storage, and semantic search functionality
"""

import os
import openai
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import psycopg2
from psycopg2.extras import RealDictCursor
import logging
from config import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorService:
    """Service for handling vector embeddings and similarity search"""
    
    def __init__(self):
        """Initialize the vector service with OpenAI and database connections"""
        # Get OpenAI API key from environment or config
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key and hasattr(config, 'OPENAI_API_KEY'):
            api_key = config.OPENAI_API_KEY
        elif not api_key and isinstance(config, dict):
            api_key = config.get('OPENAI_API_KEY')

        if not api_key:
            raise ValueError("OpenAI API key not found in environment or config")

        self.openai_client = openai.OpenAI(api_key=api_key)
        self.embedding_model = "text-embedding-3-small"
        self.embedding_dimension = 1536
        
    def get_db_connection(self):
        """Get database connection"""
        try:
            # Get database configuration from environment or config
            db_config = {
                'host': os.getenv('DB_HOST') or getattr(config, 'DB_HOST', None),
                'database': os.getenv('DB_NAME') or getattr(config, 'DB_NAME', None),
                'user': os.getenv('DB_USER') or getattr(config, 'DB_USER', None),
                'password': os.getenv('DB_PASSWORD') or getattr(config, 'DB_PASSWORD', None),
                'port': os.getenv('DB_PORT', '5432') or getattr(config, 'DB_PORT', '5432')
            }

            # Handle config as dictionary
            if isinstance(config, dict):
                db_config.update({
                    'host': db_config['host'] or config.get('DB_HOST'),
                    'database': db_config['database'] or config.get('DB_NAME'),
                    'user': db_config['user'] or config.get('DB_USER'),
                    'password': db_config['password'] or config.get('DB_PASSWORD'),
                    'port': db_config['port'] or config.get('DB_PORT', '5432')
                })

            conn = psycopg2.connect(**db_config)
            return conn
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            raise
    
    def create_embedding(self, text: str) -> List[float]:
        """
        Create embedding for given text using OpenAI
        
        Args:
            text (str): Text to embed
            
        Returns:
            List[float]: Embedding vector
        """
        try:
            # Clean and prepare text
            text = text.strip().replace('\n', ' ')
            if not text:
                raise ValueError("Text cannot be empty")
            
            # Create embedding
            response = self.openai_client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            
            embedding = response.data[0].embedding
            logger.info(f"Created embedding with dimension: {len(embedding)}")
            return embedding
            
        except Exception as e:
            logger.error(f"Error creating embedding: {e}")
            raise
    
    def store_document_embedding(self, document_id: str, content: str, metadata: Dict[str, Any] = None) -> bool:
        """
        Store document embedding in the database
        
        Args:
            document_id (str): Unique document identifier
            content (str): Document content to embed
            metadata (dict): Additional metadata
            
        Returns:
            bool: Success status
        """
        try:
            # Create embedding
            embedding = self.create_embedding(content)
            
            # Store in database
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # Insert or update document embedding
            query = """
                INSERT INTO document_embeddings (document_id, content, embedding, metadata, created_at)
                VALUES (%s, %s, %s, %s, NOW())
                ON CONFLICT (document_id) 
                DO UPDATE SET 
                    content = EXCLUDED.content,
                    embedding = EXCLUDED.embedding,
                    metadata = EXCLUDED.metadata,
                    updated_at = NOW()
            """
            
            cursor.execute(query, (
                document_id,
                content,
                embedding,
                metadata or {}
            ))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"Stored embedding for document: {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing document embedding: {e}")
            return False
    
    def similarity_search(self, query: str, limit: int = 5, threshold: float = 0.7) -> List[Dict[str, Any]]:
        """
        Perform similarity search for documents
        
        Args:
            query (str): Search query
            limit (int): Maximum number of results
            threshold (float): Similarity threshold (0-1)
            
        Returns:
            List[Dict]: Similar documents with scores
        """
        try:
            # Create query embedding
            query_embedding = self.create_embedding(query)
            
            # Search in database
            conn = self.get_db_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Use cosine similarity for search
            search_query = """
                SELECT 
                    document_id,
                    content,
                    metadata,
                    (1 - (embedding <=> %s::vector)) as similarity_score,
                    created_at
                FROM document_embeddings
                WHERE (1 - (embedding <=> %s::vector)) > %s
                ORDER BY similarity_score DESC
                LIMIT %s
            """
            
            cursor.execute(search_query, (query_embedding, query_embedding, threshold, limit))
            results = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            # Convert to list of dictionaries
            similar_docs = []
            for row in results:
                similar_docs.append({
                    'document_id': row['document_id'],
                    'content': row['content'],
                    'metadata': row['metadata'],
                    'similarity_score': float(row['similarity_score']),
                    'created_at': row['created_at'].isoformat() if row['created_at'] else None
                })
            
            logger.info(f"Found {len(similar_docs)} similar documents for query: {query[:50]}...")
            return similar_docs
            
        except Exception as e:
            logger.error(f"Error in similarity search: {e}")
            return []
    
    def get_document_embedding(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve document embedding by ID
        
        Args:
            document_id (str): Document identifier
            
        Returns:
            Dict: Document data with embedding
        """
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            query = """
                SELECT document_id, content, embedding, metadata, created_at, updated_at
                FROM document_embeddings
                WHERE document_id = %s
            """
            
            cursor.execute(query, (document_id,))
            result = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            if result:
                return dict(result)
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving document embedding: {e}")
            return None
    
    def delete_document_embedding(self, document_id: str) -> bool:
        """
        Delete document embedding
        
        Args:
            document_id (str): Document identifier
            
        Returns:
            bool: Success status
        """
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            query = "DELETE FROM document_embeddings WHERE document_id = %s"
            cursor.execute(query, (document_id,))
            
            deleted_count = cursor.rowcount
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"Deleted embedding for document: {document_id}")
            return deleted_count > 0
            
        except Exception as e:
            logger.error(f"Error deleting document embedding: {e}")
            return False
    
    def get_all_documents(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get all stored documents
        
        Args:
            limit (int): Maximum number of documents to return
            
        Returns:
            List[Dict]: List of documents
        """
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            query = """
                SELECT document_id, content, metadata, created_at, updated_at
                FROM document_embeddings
                ORDER BY created_at DESC
                LIMIT %s
            """
            
            cursor.execute(query, (limit,))
            results = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            return [dict(row) for row in results]
            
        except Exception as e:
            logger.error(f"Error retrieving all documents: {e}")
            return []

# Create global instance
vector_service = VectorService()
