import os
import json
import logging
from typing import List, Dict, Any, Optional
import openai
from openai import OpenAI

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MigrationService:
    """Service for migrating data from Weaviate to OpenAI Vector Store"""
    
    def __init__(self, client: OpenAI = None):
        """Initialize the Migration Service"""
        self.client = client or OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.assistant_id = os.getenv("OPENAI_ASSISTANT_ID")
        
    def migrate_documents_from_weaviate(self, weaviate_documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Migrate documents from Weaviate to OpenAI Vector Store
        
        Args:
            weaviate_documents: List of documents from Weaviate
            
        Returns:
            List of migrated document IDs and status
        """
        if not self.assistant_id:
            raise ValueError("Assistant ID not set. Initialize the assistant first.")
            
        results = []
        
        for doc in weaviate_documents:
            try:
                # Extract content and metadata from Weaviate document
                content = doc.get('content', '')
                metadata = {
                    'title': doc.get('title', ''),
                    'source': doc.get('source', ''),
                    'weaviate_id': doc.get('id', ''),
                    'category': doc.get('category', ''),
                    'tags': doc.get('tags', [])
                }
                
                # Create a temporary file with the content
                temp_file_path = f"/tmp/migration_{metadata['weaviate_id']}.txt"
                with open(temp_file_path, 'w') as f:
                    f.write(content)
                
                # Upload to OpenAI
                with open(temp_file_path, 'rb') as file:
                    file_obj = self.client.files.create(
                        file=file,
                        purpose="assistants"
                    )
                
                # Attach to assistant
                self.client.beta.assistants.files.create(
                    assistant_id=self.assistant_id,
                    file_id=file_obj.id
                )
                
                # Clean up temp file
                os.remove(temp_file_path)
                
                results.append({
                    'weaviate_id': metadata['weaviate_id'],
                    'openai_file_id': file_obj.id,
                    'title': metadata['title'],
                    'status': 'migrated'
                })
                
                logger.info(f"Successfully migrated document: {metadata['title']}")
                
            except Exception as e:
                logger.error(f"Error migrating document {doc.get('id', 'unknown')}: {str(e)}")
                results.append({
                    'weaviate_id': doc.get('id', 'unknown'),
                    'title': doc.get('title', 'unknown'),
                    'status': 'failed',
                    'error': str(e)
                })
        
        return results
    
    def migrate_document_from_file(self, file_path: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Migrate a document from a file to OpenAI Vector Store
        
        Args:
            file_path: Path to the file
            metadata: Document metadata
            
        Returns:
            Migration result
        """
        if not self.assistant_id:
            raise ValueError("Assistant ID not set. Initialize the assistant first.")
            
        try:
            # Upload to OpenAI
            with open(file_path, 'rb') as file:
                file_obj = self.client.files.create(
                    file=file,
                    purpose="assistants"
                )
            
            # Attach to assistant
            self.client.beta.assistants.files.create(
                assistant_id=self.assistant_id,
                file_id=file_obj.id
            )
            
            result = {
                'file_path': file_path,
                'openai_file_id': file_obj.id,
                'title': metadata.get('title', os.path.basename(file_path)),
                'status': 'migrated'
            }
            
            logger.info(f"Successfully migrated file: {file_path}")
            return result
            
        except Exception as e:
            logger.error(f"Error migrating file {file_path}: {str(e)}")
            return {
                'file_path': file_path,
                'status': 'failed',
                'error': str(e)
            }
    
    def compare_document_counts(self) -> Dict[str, int]:
        """
        Compare document counts between Weaviate and OpenAI Vector Store
        
        Returns:
            Dictionary with document counts
        """
        try:
            # Get OpenAI files count
            openai_files = self.client.beta.assistants.files.list(
                assistant_id=self.assistant_id
            )
            openai_count = len(openai_files.data)
            
            # Note: We can't directly access Weaviate count here
            # This would need to be provided by the caller
            
            return {
                'openai_count': openai_count,
                'weaviate_count': 'unknown'  # To be filled by caller
            }
            
        except Exception as e:
            logger.error(f"Error comparing document counts: {str(e)}")
            return {
                'openai_count': 0,
                'weaviate_count': 'unknown',
                'error': str(e)
            }

# Create a singleton instance
migration_service = MigrationService()
