# Facility Manager Agent for Gopalan Atlantis

A web-based facility management system built using OpenAI frameworks that functions as a Progressive Web App (PWA). This allows residents to access the application via a URL on their mobile devices without requiring installation from an app store.

## Features

The application consists of three key modules:

1. **Apartment Knowledge Base and Key Documents (AKC)**
   - Repository for community documents, guidelines, and resources
   - Searchable database of apartment information
   - FAQ section for common questions

2. **Owners Communication & Engagement Module (OCE)**
   - Community announcements and updates
   - Event scheduling and notifications
   - Resident feedback and polling

3. **Help Desk for Owner Queries (HDC)**
   - Ticket submission and tracking system
   - AI-powered query resolution
   - Escalation pathways for complex issues

## Technical Architecture

- **Frontend**: React-based Progressive Web App (PWA)
- **Backend**: Flask REST API with OpenAI integration
- **AI Integration**: OpenAI Agents framework for intelligent responses

## Installation

1. Clone the repository
2. Install backend dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Install frontend dependencies:
   ```
   cd frontend
   npm install
   ```

## Configuration

1. Create a `.env` file in the backend directory with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key
   ```

## Running the Application

1. Start the backend:
   ```
   cd backend
   python app.py
   ```
2. Start the frontend development server:
   ```
   cd frontend
   npm start
   ```

## Deployment

The application can be deployed to any platform that supports static sites (frontend) and Python applications (backend).
