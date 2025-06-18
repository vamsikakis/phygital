import json
import os
from datetime import datetime
from openai import OpenAI

class ApartmentKnowledgeBase:
    """
    Module for handling apartment knowledge base and key documents.
    This module uses OpenAI to process and respond to queries about apartment documents,
    policies, rules, and other important information.
    """
    def __init__(self, client):
        self.client = client
        # In a real implementation, this would load from a database
        self.documents = {
            "bylaws": {
                "title": "Gopalan Atlantis Bylaws",
                "last_updated": "2025-01-15",
                "description": "Official bylaws governing the Gopalan Atlantis community"
            },
            "rules": {
                "title": "Community Rules and Regulations",
                "last_updated": "2025-03-20",
                "description": "Detailed rules for residents including noise policies, common area usage, and pet policies"
            },
            "maintenance": {
                "title": "Maintenance Procedures",
                "last_updated": "2025-05-01",
                "description": "Guidelines for requesting and scheduling maintenance services"
            },
            "amenities": {
                "title": "Amenities Guide",
                "last_updated": "2025-04-10",
                "description": "Information about community amenities, hours, and usage policies"
            },
            "emergency": {
                "title": "Emergency Procedures",
                "last_updated": "2025-02-28",
                "description": "Steps to follow during emergencies, including contact information"
            }
        }
        
    def get_documents(self):
        """Return the list of available documents"""
        return self.documents
    
    def get_document_content(self, doc_id):
        """
        In a real implementation, this would retrieve the actual content of the document.
        Here we're returning placeholder content.
        """
        if doc_id not in self.documents:
            return None
        
        # This would typically load from a file or database
        return f"This is the content of {self.documents[doc_id]['title']}"
    
    def process_query(self, query):
        """
        Process a user query about apartment knowledge or documents using OpenAI.
        """
        try:
            # In a production system, you would load the actual knowledge base content to provide context
            system_message = """
            You are the Gopalan Atlantis Facility Manager's knowledge base assistant.
            Answer questions about apartment documents, bylaws, rules, and policies accurately and concisely.
            If you don't know the answer, suggest where the resident might find the information.
            Always maintain a helpful and professional tone.
            """
            
            # Create a list of document summaries for context
            doc_context = "\n".join([
                f"- {details['title']}: {details['description']} (Last updated: {details['last_updated']})"
                for doc_id, details in self.documents.items()
            ])
            
            response = self.client.chat.completions.create(
                model="gpt-4-turbo",  # Use appropriate model
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": f"Here are the available documents in our knowledge base:\n{doc_context}\n\nUser query: {query}"}
                ]
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error processing query: {e}")
            return "I apologize, but I'm having trouble processing your query right now. Please try again later."
            
    def search_documents(self, search_term):
        """Search for documents matching the search term"""
        results = []
        for doc_id, details in self.documents.items():
            if (search_term.lower() in details['title'].lower() or 
                search_term.lower() in details['description'].lower()):
                results.append({
                    "id": doc_id,
                    **details
                })
        return results
