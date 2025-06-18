import json
import os
from datetime import datetime
from openai import OpenAI

class OwnersCommunication:
    """
    Module for handling resident communication and engagement.
    This module manages announcements, events, feedback, and polls for the community.
    """
    def __init__(self, client):
        self.client = client
        # In a real implementation, these would be stored in a database
        self.announcements = [
            {
                "id": "ann001",
                "title": "Monthly Maintenance Schedule",
                "content": "The maintenance team will be servicing all common areas on the 15th of this month.",
                "date": "2025-06-05",
                "priority": "normal"
            },
            {
                "id": "ann002",
                "title": "Swimming Pool Closure",
                "content": "The swimming pool will be closed for maintenance from June 20th to June 22nd.",
                "date": "2025-06-08",
                "priority": "high"
            },
            {
                "id": "ann003",
                "title": "Community Gathering",
                "content": "Join us for a community BBQ on the 25th of this month at the central garden.",
                "date": "2025-06-10",
                "priority": "normal"
            }
        ]
        
        self.events = [
            {
                "id": "evt001",
                "title": "Community BBQ",
                "description": "Summer community gathering with food and games.",
                "date": "2025-06-25",
                "time": "18:00-21:00",
                "location": "Central Garden"
            },
            {
                "id": "evt002",
                "title": "Yoga Session",
                "description": "Weekly yoga session for all residents.",
                "date": "2025-06-15",
                "time": "08:00-09:00",
                "location": "Community Hall"
            }
        ]
        
        self.polls = [
            {
                "id": "poll001",
                "title": "Garden Renovation Options",
                "description": "Vote for your preferred garden renovation design.",
                "options": ["Modern design", "Traditional design", "Eco-friendly design"],
                "closing_date": "2025-06-20"
            }
        ]
        
    def get_announcements(self):
        """Return the list of current announcements"""
        return self.announcements
    
    def get_events(self):
        """Return the list of upcoming events"""
        return self.events
    
    def get_polls(self):
        """Return the list of active polls"""
        return self.polls
    
    def create_announcement(self, title, content, priority="normal"):
        """Create a new announcement"""
        # In a real implementation, this would save to a database
        new_announcement = {
            "id": f"ann{len(self.announcements) + 1:03d}",
            "title": title,
            "content": content,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "priority": priority
        }
        self.announcements.append(new_announcement)
        return new_announcement["id"]
    
    def create_event(self, title, description, date, time, location):
        """Create a new event"""
        new_event = {
            "id": f"evt{len(self.events) + 1:03d}",
            "title": title,
            "description": description,
            "date": date,
            "time": time,
            "location": location
        }
        self.events.append(new_event)
        return new_event["id"]
    
    def create_poll(self, title, description, options, closing_date):
        """Create a new poll"""
        new_poll = {
            "id": f"poll{len(self.polls) + 1:03d}",
            "title": title,
            "description": description,
            "options": options,
            "closing_date": closing_date
        }
        self.polls.append(new_poll)
        return new_poll["id"]
    
    def process_query(self, query):
        """
        Process a user query about community communications using OpenAI.
        """
        try:
            system_message = """
            You are the Gopalan Atlantis Facility Manager's communication assistant.
            Answer questions about community announcements, events, and engagement activities.
            Provide helpful and relevant information about upcoming events, current announcements, 
            and ways residents can engage with the community.
            If you don't know the answer, suggest how the resident might find the information.
            Always maintain a helpful and professional tone.
            """
            
            # Create context with current announcements and events
            context = "Current announcements:\n"
            for ann in self.announcements:
                context += f"- {ann['title']} ({ann['date']}): {ann['content']}\n"
                
            context += "\nUpcoming events:\n"
            for evt in self.events:
                context += f"- {evt['title']} on {evt['date']} at {evt['time']}, {evt['location']}: {evt['description']}\n"
                
            if self.polls:
                context += "\nActive polls:\n"
                for poll in self.polls:
                    context += f"- {poll['title']}: {poll['description']} (Closes on {poll['closing_date']})\n"
            
            response = self.client.chat.completions.create(
                model="gpt-4-turbo",  # Use appropriate model
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": f"{context}\n\nUser query: {query}"}
                ]
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error processing query: {e}")
            return "I apologize, but I'm having trouble processing your query right now. Please try again later."
