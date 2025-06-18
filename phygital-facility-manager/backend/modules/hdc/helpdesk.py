import json
import os
from datetime import datetime
import uuid
from openai import OpenAI

class HelpDesk:
    """
    Module for handling help desk operations and solving owner queries.
    This module uses OpenAI Agents to process complex queries and provide intelligent responses.
    """
    def __init__(self, client):
        self.client = client
        # In a real implementation, these would be stored in a database
        self.tickets = []
        self.ticket_categories = ["Maintenance", "Security", "Amenities", "Billing", "General"]
        self.faqs = {
            "How do I submit a maintenance request?": 
                "You can submit a maintenance request through the app's Help Desk section by selecting 'Create New Ticket' and choosing the 'Maintenance' category.",
            "What are the pool hours?": 
                "The community pool is open from 6:00 AM to 10:00 PM daily.",
            "How do I reserve the community hall?": 
                "To reserve the community hall, go to the OCE module, select 'Amenity Booking', and choose your preferred date and time.",
            "When is the monthly maintenance fee due?": 
                "The monthly maintenance fee is due on the 5th of each month.",
            "How do I update my contact information?": 
                "You can update your contact information in the Profile section of the app."
        }
        
        # In a production implementation, you would initialize the OpenAI agent with proper tools and config
        self._initialize_agent()
        
    def _initialize_agent(self):
        """Initialize the OpenAI agent for the help desk"""
        # This is a placeholder - in a real implementation you would define functions and tools
        # for the OpenAI agent to use
        try:
            # Define the agent's capabilities and instructions
            self.agent_definition = {
                "name": "GopalaAtlantisHelpDesk",
                "description": "A help desk agent for Gopalan Atlantis apartment residents",
                "instructions": """
                You are the Gopalan Atlantis help desk assistant.
                Your goal is to assist residents with their queries and issues related to the apartment complex.
                Provide helpful, accurate, and concise responses.
                For issues that require human intervention, create a support ticket and provide the ticket ID to the resident.
                Always be professional and courteous in your responses.
                """,
                # In a real implementation, you would define tools for the agent to use
                "tools": []
            }
            print("Agent initialized successfully")
        except Exception as e:
            print(f"Error initializing agent: {e}")
        
    def create_ticket(self, description, category="General"):
        """Create a new support ticket"""
        if category not in self.ticket_categories:
            category = "General"
            
        ticket_id = str(uuid.uuid4())[:8]  # Generate a short unique ID
        new_ticket = {
            "id": ticket_id,
            "description": description,
            "category": category,
            "status": "Open",
            "created_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "comments": []
        }
        self.tickets.append(new_ticket)
        return ticket_id
    
    def update_ticket(self, ticket_id, status=None, comment=None):
        """Update an existing ticket's status or add a comment"""
        for ticket in self.tickets:
            if ticket["id"] == ticket_id:
                if status:
                    ticket["status"] = status
                if comment:
                    ticket["comments"].append({
                        "text": comment,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                ticket["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                return True
        return False
    
    def get_ticket(self, ticket_id):
        """Get a specific ticket by ID"""
        for ticket in self.tickets:
            if ticket["id"] == ticket_id:
                return ticket
        return None
    
    def get_tickets_by_status(self, status="Open"):
        """Get all tickets with a specific status"""
        return [ticket for ticket in self.tickets if ticket["status"] == status]
    
    def process_query(self, query):
        """
        Process a user query using OpenAI.
        For complex queries, this will create a ticket in the future.
        """
        try:
            # Check if the query matches any FAQ
            for question, answer in self.faqs.items():
                if query.lower() in question.lower() or question.lower() in query.lower():
                    return answer
            
            # Use OpenAI to generate a response
            system_message = """
            You are the Gopalan Atlantis Facility Manager's help desk assistant.
            Answer residents' questions about the apartment complex, maintenance, amenities, and general inquiries.
            If the query requires creating a ticket (like specific maintenance requests or complex issues),
            suggest to the resident that you can create a ticket for them and explain the process.
            Be helpful, concise, and professional in your responses.
            """
            
            # Create a context with available FAQ information
            faq_context = "Frequently Asked Questions:\n"
            for question, answer in self.faqs.items():
                faq_context += f"Q: {question}\nA: {answer}\n\n"
            
            # Include ticket categories information
            categories = "Available ticket categories: " + ", ".join(self.ticket_categories)
            
            response = self.client.chat.completions.create(
                model="gpt-4-turbo",  # Use appropriate model
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": f"{faq_context}\n{categories}\n\nUser query: {query}"}
                ]
            )
            
            # In a future implementation, using OpenAI Agents would allow more complex interactions
            # such as automatically determining when to create tickets, extracting information from
            # user queries, etc.
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error processing query: {e}")
            return "I apologize, but I'm having trouble processing your query right now. Please try again later."
