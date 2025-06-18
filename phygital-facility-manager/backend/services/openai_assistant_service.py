import os
import time
import json
from typing import List, Dict, Any, Optional, Union
import openai
from openai import OpenAI
from flask import current_app

class OpenAIAssistantService:
    """Service for interacting with OpenAI Assistant API and Vector Store"""
    
    def __init__(self, client: OpenAI = None):
        """Initialize the OpenAI Assistant Service"""
        self.client = client or OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.assistant_id = os.getenv("OPENAI_ASSISTANT_ID")
        self.vector_store_id = None
        self._is_initialized = False
        
    def initialize(self) -> Dict[str, str]:
        """Initialize or retrieve the OpenAI Assistant and Vector Store"""
        try:
            # Check if we already have an assistant ID
            if self.assistant_id:
                # Verify the assistant exists
                try:
                    assistant = self.client.beta.assistants.retrieve(self.assistant_id)
                    current_app.logger.info(f"Using existing assistant: {assistant.id}")
                except Exception as e:
                    current_app.logger.warning(f"Could not retrieve assistant {self.assistant_id}: {str(e)}")
                    self.assistant_id = None
            
            # Create a new assistant if needed
            if not self.assistant_id:
                assistant = self.client.beta.assistants.create(
                    name="Gopalan Atlantis Facility Manager Assistant",
                    description="An assistant that helps residents with apartment-related queries and information",
                    instructions="""You are the Gopalan Atlantis Facility Manager Assistant. 
                    Your role is to help residents with information about the apartment complex, 
                    amenities, maintenance, and community events. Be helpful, concise, and friendly.
                    When answering questions, prioritize information from the knowledge base documents.
                    If you don't know the answer, politely say so and suggest contacting the facility management office.""",
                    model="gpt-4-turbo-preview",
                    tools=[{"type": "file_search"}]
                )
                self.assistant_id = assistant.id
                current_app.logger.info(f"Created new assistant: {assistant.id}")
            
            # Initialize or retrieve the vector store
            self.vector_store_id = self._initialize_vector_store()
            
            self._is_initialized = True
            return {
                "assistant_id": self.assistant_id,
                "vector_store_id": self.vector_store_id,
                "status": "initialized"
            }
        except Exception as e:
            current_app.logger.error(f"Error initializing OpenAI Assistant: {str(e)}")
            self._is_initialized = False
            raise
    
    def _initialize_vector_store(self) -> str:
        """Initialize or retrieve the vector store for document storage"""
        try:
            # For now, we'll use a simple approach without creating a separate vector store
            # The assistant will work with files directly
            current_app.logger.info("Using direct file access approach (no separate vector store)")
            return "direct-file-access"
            
        except Exception as e:
            current_app.logger.error(f"Error initializing vector store: {str(e)}")
            return None
    
    def create_thread(self) -> Dict[str, Any]:
        """Create a new conversation thread"""
        try:
            thread = self.client.beta.threads.create()
            return {
                "thread_id": thread.id,
                "created_at": thread.created_at
            }
        except Exception as e:
            current_app.logger.error(f"Error creating thread: {str(e)}")
            raise
    
    def get_thread(self, thread_id: str) -> Dict[str, Any]:
        """Get a thread by ID"""
        try:
            thread = self.client.beta.threads.retrieve(thread_id)
            return {
                "thread_id": thread.id,
                "created_at": thread.created_at,
                "metadata": thread.metadata
            }
        except Exception as e:
            current_app.logger.error(f"Error retrieving thread {thread_id}: {str(e)}")
            raise
    
    def list_threads(self, limit: int = 10) -> List[Dict[str, Any]]:
        """List available threads (Note: OpenAI API doesn't support listing threads yet)"""
        # This is a placeholder as the OpenAI API doesn't support listing threads
        # We would need to maintain our own database of threads
        return []
    
    def delete_thread(self, thread_id: str) -> Dict[str, Any]:
        """Delete a thread"""
        try:
            response = self.client.beta.threads.delete(thread_id)
            return {
                "thread_id": thread_id,
                "deleted": response.deleted
            }
        except Exception as e:
            current_app.logger.error(f"Error deleting thread {thread_id}: {str(e)}")
            raise
    
    def add_message(self, thread_id: str, content: str, role: str = "user", file_ids: list = None) -> Dict[str, Any]:
        """Add a message to a thread with optional file attachments"""
        try:
            message_data = {
                "thread_id": thread_id,
                "role": role,
                "content": content
            }
            
            # Add file attachments if provided
            if file_ids:
                message_data["attachments"] = [
                    {"file_id": file_id, "tools": [{"type": "file_search"}]} 
                    for file_id in file_ids
                ]
            
            message = self.client.beta.threads.messages.create(**message_data)
            
            return {
                "message_id": message.id,
                "thread_id": thread_id,
                "role": message.role,
                "content": message.content[0].text.value if message.content else "",
                "created_at": message.created_at
            }
        except Exception as e:
            current_app.logger.error(f"Error adding message to thread {thread_id}: {str(e)}")
            raise
    
    def get_thread_messages(self, thread_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get messages from a thread"""
        try:
            messages = self.client.beta.threads.messages.list(
                thread_id=thread_id,
                limit=limit
            )
            result = []
            for message in messages.data:
                content = ""
                if message.content and len(message.content) > 0:
                    content = message.content[0].text.value
                
                result.append({
                    "message_id": message.id,
                    "thread_id": thread_id,
                    "role": message.role,
                    "content": content,
                    "created_at": message.created_at
                })
            return result
        except Exception as e:
            current_app.logger.error(f"Error getting messages from thread {thread_id}: {str(e)}")
            raise
    
    def run_assistant_on_thread(self, thread_id: str, instructions: str = None) -> Dict[str, Any]:
        """Run the assistant on a thread and wait for completion"""
        if not self.assistant_id:
            raise ValueError("Assistant not initialized. Call initialize() first.")
        
        try:
            # Create the run
            run = self.client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=self.assistant_id,
                instructions=instructions
            )
            
            # Poll for completion
            while True:
                run_status = self.client.beta.threads.runs.retrieve(
                    thread_id=thread_id,
                    run_id=run.id
                )
                
                if run_status.status == "completed":
                    break
                elif run_status.status in ["failed", "cancelled", "expired"]:
                    raise Exception(f"Run failed with status: {run_status.status}")
                
                # Wait before polling again
                time.sleep(1)
            
            # Get the messages after completion
            messages = self.get_thread_messages(thread_id, limit=5)
            
            # The most recent message should be from the assistant
            assistant_messages = [msg for msg in messages if msg["role"] == "assistant"]
            latest_message = assistant_messages[0] if assistant_messages else None
            
            return {
                "run_id": run.id,
                "thread_id": thread_id,
                "status": "completed",
                "response": latest_message["content"] if latest_message else "",
                "created_at": run.created_at,
                "completed_at": run_status.completed_at
            }
        except Exception as e:
            current_app.logger.error(f"Error running assistant on thread {thread_id}: {str(e)}")
            raise
    
    def upload_file_to_vector_store(self, file_path: str, file_name: str = None) -> Dict[str, Any]:
        """Upload a file to the OpenAI vector store"""
        try:
            # Upload file to OpenAI for assistant use
            with open(file_path, "rb") as file:
                file_obj = self.client.files.create(
                    file=file,
                    purpose="assistants"
                )
            
            current_app.logger.info(f"Successfully uploaded file {file_obj.id} to OpenAI")
            
            return {
                "file_id": file_obj.id,
                "filename": file_name or os.path.basename(file_path),
                "purpose": file_obj.purpose,
                "bytes": file_obj.bytes,
                "created_at": file_obj.created_at,
                "status": "uploaded"
            }
        except Exception as e:
            current_app.logger.error(f"Error uploading file to vector store: {str(e)}")
            raise
    
    def list_files(self) -> List[Dict[str, Any]]:
        """List files in the vector store"""
        try:
            # Try to list all files with purpose 'assistants' as a fallback
            files = self.client.files.list(purpose='assistants')
            
            result = []
            for file in files.data:
                result.append({
                    "file_id": file.id,
                    "filename": file.filename,
                    "purpose": file.purpose,
                    "bytes": file.bytes,
                    "created_at": file.created_at,
                    "status": "uploaded"
                })
            
            current_app.logger.info(f"Retrieved {len(result)} files from OpenAI")
            return result
        except Exception as e:
            current_app.logger.error(f"Error listing files: {str(e)}")
            # Fallback: return empty list instead of raising error
            current_app.logger.info("Returning empty file list as fallback")
            return []
    
    def delete_file(self, file_id: str) -> Dict[str, Any]:
        """Delete a file from the vector store"""
        try:
            if not self.assistant_id:
                raise ValueError("Assistant not initialized. Call initialize() first.")
            
            # First remove from assistant
            self.client.beta.assistants.files.delete(
                assistant_id=self.assistant_id,
                file_id=file_id
            )
            
            # Then delete the file itself
            response = self.client.files.delete(file_id)
            
            return {
                "file_id": file_id,
                "deleted": response.deleted
            }
        except Exception as e:
            current_app.logger.error(f"Error deleting file {file_id}: {str(e)}")
            raise

# Create a singleton instance
openai_assistant_service = OpenAIAssistantService()
