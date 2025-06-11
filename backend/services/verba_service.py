import os
import weaviate
from dotenv import load_dotenv
from goldenverba.api.client import VerbaClient
from goldenverba.api.types import document_types

load_dotenv()

class VerbaService:
    """Service for integrating with Verba RAG capabilities"""
    
    def __init__(self):
        # Initialize Verba client
        try:
            self.verba_client = VerbaClient(
                weaviate_url=os.getenv('WEAVIATE_URL', 'http://localhost:8080'),
                weaviate_api_key=os.getenv('WEAVIATE_API_KEY', None),
                openai_api_key=os.getenv('OPENAI_API_KEY')
            )
            self.initialized = True
        except Exception as e:
            print(f"Error initializing Verba: {str(e)}")
            self.initialized = False
            
    def is_initialized(self):
        """Check if the Verba service is properly initialized"""
        return self.initialized
    
    def get_collections(self):
        """Get all collections from Verba"""
        if not self.initialized:
            return []
        
        try:
            return self.verba_client.list_collections()
        except Exception as e:
            print(f"Error getting collections: {str(e)}")
            return []
    
    def create_apartment_collection(self, name="apartment_documents"):
        """Create a collection specifically for apartment documents"""
        if not self.initialized:
            return None
            
        try:
            # Create collection if it doesn't exist
            collections = self.get_collections()
            if name not in collections:
                self.verba_client.create_collection(name)
            
            return name
        except Exception as e:
            print(f"Error creating apartment collection: {str(e)}")
            return None
    
    def upload_document(self, file_path, collection_name="apartment_documents", metadata=None):
        """Upload a document to Verba collection"""
        if not self.initialized:
            return False
            
        try:
            # Create collection if doesn't exist
            self.create_apartment_collection(collection_name)
            
            # Determine document type based on extension
            file_ext = file_path.split('.')[-1].lower()
            
            if file_ext in ['pdf']:
                doc_type = document_types.PDF
            elif file_ext in ['txt']:
                doc_type = document_types.TXT
            elif file_ext in ['docx', 'doc']:
                doc_type = document_types.DOCX
            else:
                doc_type = document_types.TXT  # Default
            
            # Upload document
            result = self.verba_client.upload_document(
                collection_name=collection_name,
                file_path=file_path,
                document_type=doc_type,
                metadata=metadata or {}
            )
            
            return result
        except Exception as e:
            print(f"Error uploading document: {str(e)}")
            return False
    
    def query_documents(self, query_text, collection_name="apartment_documents", limit=5):
        """Query documents using RAG"""
        if not self.initialized:
            return {"error": "Verba service not initialized"}
            
        try:
            # Set collection
            self.verba_client.set_collection(collection_name)
            
            # Query with RAG
            response = self.verba_client.query(
                query=query_text,
                limit_results=limit
            )
            
            return {
                "answer": response.answer,
                "sources": [
                    {
                        "content": source.content,
                        "document": source.document,
                        "metadata": source.metadata,
                        "score": source.score
                    } for source in response.sources
                ]
            }
        except Exception as e:
            print(f"Error querying documents: {str(e)}")
            return {"error": str(e)}
    
    def get_document_metadata(self, collection_name="apartment_documents"):
        """Get metadata for all documents in a collection"""
        if not self.initialized:
            return []
            
        try:
            self.verba_client.set_collection(collection_name)
            documents = self.verba_client.get_documents()
            
            return [doc.to_dict() for doc in documents]
        except Exception as e:
            print(f"Error getting document metadata: {str(e)}")
            return []

# Create a singleton instance
verba_service = VerbaService()
