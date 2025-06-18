#!/usr/bin/env python3
"""
Enhanced Mock Server for Verba RAG document management
"""

from flask import Flask, request, jsonify, send_file, url_for, render_template_string
from flask_cors import CORS
import os
import json
import uuid
import datetime
import shutil
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Enable CORS for all routes - allow all origins in development
CORS(app, resources={r"/*": {"origins": "*"}}, 
     methods=["GET", "POST", "OPTIONS", "PUT", "DELETE"], 
     allow_headers=["Content-Type", "Authorization", "Accept", "X-Requested-With"],
     supports_credentials=True,
     expose_headers=["Content-Type", "X-Total-Count"])

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'mock_verba_data')
DOCUMENT_FOLDER = os.path.join(UPLOAD_FOLDER, 'documents')
METADATA_FILE = os.path.join(UPLOAD_FOLDER, 'metadata.json')
MOCK_DOCS_FOLDER = os.path.join(BASE_DIR, 'mock_docs')

# Create necessary directories
os.makedirs(DOCUMENT_FOLDER, exist_ok=True)

# Initialize data structures
collections = ["apartment_documents"]
documents = {}

# Load existing metadata if available
def load_metadata():
    global documents
    if os.path.exists(METADATA_FILE):
        try:
            with open(METADATA_FILE, 'r') as f:
                documents = json.load(f)
            print(f"Loaded {len(documents)} documents from metadata file")
        except Exception as e:
            print(f"Error loading metadata: {str(e)}")
            documents = {}
    else:
        documents = {}

# Save metadata to file
def save_metadata():
    try:
        with open(METADATA_FILE, 'w') as f:
            json.dump(documents, f, indent=2)
        print(f"Saved {len(documents)} documents to metadata file")
    except Exception as e:
        print(f"Error saving metadata: {str(e)}")

# Load metadata at startup
load_metadata()

@app.route('/api/verba/status', methods=['GET', 'OPTIONS'])
def status():
    """Check if the server is running"""
    response = jsonify({"initialized": True, "version": "mock-1.0.0"})
    return response

@app.route('/api/verba/collections', methods=['GET', 'OPTIONS'])
def get_collections():
    """Get all available collections"""
    response = jsonify({"collections": collections})
    return response

@app.route('/api/verba/documents', methods=['GET', 'OPTIONS'])
def get_documents():
    """Get all documents in a collection"""
    if request.method == 'OPTIONS':
        response = app.make_default_options_response()
        return response
        
    collection = request.args.get('collection', 'apartment_documents')
    
    # Filter documents by collection
    collection_docs = []
    for doc_id, doc in documents.items():
        if doc.get('collection') == collection:
            # Format document for frontend
            formatted_doc = {
                'id': doc_id,
                'title': doc.get('metadata', {}).get('title', 'Untitled'),
                'category': doc.get('metadata', {}).get('category', 'Uncategorized'),
                'fileUrl': doc.get('direct_access_url', ''),
                'uploadDate': doc.get('metadata', {}).get('uploaded_at', ''),
                'fileType': doc.get('metadata', {}).get('mime_type', ''),
                'fileSize': doc.get('metadata', {}).get('size', 0)
            }
            collection_docs.append(formatted_doc)
    
    return jsonify(collection_docs)

@app.route('/api/verba/upload', methods=['POST', 'OPTIONS'])
def upload_document():
    """Handle document upload with physical file storage"""
    if request.method == 'OPTIONS':
        # Handle preflight request
        response = app.make_default_options_response()
        return response
        
    try:
        print("Upload request received")
        print(f"Form data: {request.form}")
        print(f"Files: {request.files}")
        
        # Generate a unique document ID
        doc_id = str(uuid.uuid4())
        
        # Try to get file info if available
        file_info = "No file uploaded"
        if 'file' in request.files:
            file = request.files['file']
            if file.filename:
                # Secure the filename
                filename = secure_filename(file.filename)
                file_info = f"File received: {filename}"
                print(f"File received: {filename}")
                
                # Create document directory
                doc_dir = os.path.join(DOCUMENT_FOLDER, doc_id)
                os.makedirs(doc_dir, exist_ok=True)
                
                # Save the file
                file_path = os.path.join(doc_dir, filename)
                file.save(file_path)
                print(f"File saved to: {file_path}")
                
                # Get current timestamp
                timestamp = datetime.datetime.now().isoformat()
                
                # Create document entry with direct access URL
                documents[doc_id] = {
                    "id": doc_id,
                    "collection": request.form.get('collection', 'apartment_documents'),
                    "content": f"Content of {filename}",  # In a real system, this would be the extracted text
                    "file_path": file_path,
                    "direct_access_url": f"/api/verba/documents/{doc_id}/view",
                    "metadata": {
                        "title": request.form.get('title', filename),
                        "category": request.form.get('category', 'General'),
                        "file_name": filename,
                        "uploaded_at": timestamp,
                        "size": os.path.getsize(file_path),
                        "mime_type": file.content_type if hasattr(file, 'content_type') else "application/octet-stream"
                    }
                }
                
                # Save metadata
                save_metadata()
                
                print(f"Created document: {documents[doc_id]}")
        else:
            print("No file found in request")
        
        response = jsonify({
            "success": True,
            "message": f"Document uploaded: {file_info}",
            "document_id": doc_id,
            "direct_access_url": f"/api/verba/documents/{doc_id}/view" if 'file' in request.files and file.filename else None
        })
        
        # Add CORS headers to response
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    
    except Exception as e:
        print(f"Error in upload_document: {str(e)}")
        response = jsonify({"error": str(e)})
        response.status_code = 500
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

@app.route('/api/verba/query', methods=['POST', 'OPTIONS'])
def query_documents():
    """Query documents using RAG"""
    if request.method == 'OPTIONS':
        response = app.make_default_options_response()
        return response
        
    try:
        data = request.json
        query = data.get('query', '')
        collection = data.get('collection', 'apartment_documents')
        limit = data.get('limit', 3)
        
        # Special handling for club house related queries
        if 'club' in query.lower() and 'house' in query.lower():
            club_house_content = """
# Clubhouse Usage Guidelines

## Hours of Operation
- Monday to Friday: 6:00 AM to 10:00 PM
- Weekends and Holidays: 7:00 AM to 11:00 PM

## Booking Rules
1. Residents can book the clubhouse up to 30 days in advance
2. Maximum booking duration is 4 hours
3. Cleaning deposit of ₹2000 is required
4. Cancellations must be made 48 hours in advance for full refund

## Capacity and Restrictions
- Maximum capacity: 50 people
- No smoking allowed
- No loud music after 9:00 PM
- Pets must be kept on leash in outdoor areas only
            """
            
            # Generate a contextual answer based on the query
            answer = ""
            query_lower = query.lower()
            if 'book' in query_lower or 'reserve' in query_lower or 'schedule' in query_lower:
                answer = "To book the Club House at Gopalan Atlantis, you can reserve it up to 30 days in advance. The maximum booking duration is 4 hours, and you'll need to provide a cleaning deposit of ₹2000. Remember that cancellations must be made 48 hours in advance for a full refund."
            elif 'hour' in query_lower or 'time' in query_lower or 'when' in query_lower or 'open' in query_lower:
                answer = "The Club House at Gopalan Atlantis is open Monday to Friday from 6:00 AM to 10:00 PM, and on weekends and holidays from 7:00 AM to 11:00 PM."
            elif 'deposit' in query_lower or 'fee' in query_lower or 'cost' in query_lower or 'price' in query_lower:
                answer = "For Club House bookings at Gopalan Atlantis, you need to provide a cleaning deposit of ₹2000. This deposit is fully refundable if cancellations are made 48 hours in advance."
            elif 'capacity' in query_lower or 'people' in query_lower or 'many' in query_lower:
                answer = "The Club House at Gopalan Atlantis has a maximum capacity of 50 people."
            elif 'rule' in query_lower or 'restriction' in query_lower or 'policy' in query_lower or 'guideline' in query_lower:
                answer = "The Club House at Gopalan Atlantis has several restrictions: no smoking is allowed, no loud music after 9:00 PM, and pets must be kept on a leash in outdoor areas only."
            elif 'cancel' in query_lower:
                answer = "For Club House bookings at Gopalan Atlantis, cancellations must be made 48 hours in advance to receive a full refund of your deposit."
            else:
                answer = "Here are the Club House usage guidelines for Gopalan Atlantis:"
            
            return jsonify({
                "answer": answer,
                "sources": [
                    {
                        "content": club_house_content,
                        "document": "Club House Usage",
                        "document_id": "clubhouse",
                        "metadata": {
                            "title": "Club House Usage",
                            "category": "Apartment Rules & Regulations"
                        },
                        "score": 0.98
                    }
                ]
            })
        
        # Check for other document matches in uploaded documents
        query_lower = query.lower()
        query_terms = query_lower.split()
        matching_docs = []
        
        # Search through all uploaded documents
        for doc_id, doc_data in documents.items():
            if not doc_data or 'metadata' not in doc_data:
                continue
                
            # Get document content - either from content field or from file
            content = ""
            if 'content' in doc_data and doc_data['content']:
                content = doc_data['content']
            elif 'file_path' in doc_data and os.path.exists(doc_data['file_path']):
                try:
                    with open(doc_data['file_path'], 'r') as f:
                        content = f.read()
                except Exception as e:
                    print(f"Error reading file {doc_data['file_path']}: {str(e)}")
                    continue
                    
            if not content:
                continue
                
            title = doc_data['metadata'].get('title', '').lower()
            content_lower = content.lower()
            
            # Check if query terms are in the document title or content
            match_score = 0
            title_matches = 0
            content_matches = 0
            
            for term in query_terms:
                if term in title:
                    match_score += 0.3  # Higher weight for title matches
                    title_matches += 1
                if term in content_lower:
                    match_score += 0.1  # Lower weight for content matches
                    content_matches += 1
            
            # Boost score if most query terms match
            if title_matches > len(query_terms) * 0.7:
                match_score += 0.5  # Big boost if most terms match the title
            if content_matches > len(query_terms) * 0.7:
                match_score += 0.2  # Smaller boost if most terms match the content
            
            # If we have a reasonable match, include this document
            if match_score > 0.2:
                # Extract relevant content based on query terms
                relevant_content = extract_relevant_content(content, query_terms)
                
                matching_docs.append({
                    "content": relevant_content,
                    "document": doc_data['metadata'].get('title', f"Document {doc_id}"),
                    "document_id": doc_id,
                    "metadata": doc_data['metadata'],
                    "score": min(0.99, match_score)  # Cap at 0.99
                })
        
        # If we found matching documents, return them
        if matching_docs:
            # Sort by score descending
            matching_docs.sort(key=lambda x: x["score"], reverse=True)
            
            # Generate a contextual answer based on the top document
            top_doc = matching_docs[0]
            document_title = top_doc['document']
            answer = generate_answer_from_content(query, top_doc['content'], document_title)
            
            # Return the results
            return jsonify({
                "answer": answer,
                "sources": matching_docs[:limit]  # Return top matches based on limit
            })
        
        # Check for specific topics even if no document matches
        query_lower = query.lower()
        if 'barbeque' in query_lower or 'bbq' in query_lower:
            return jsonify({
                "answer": "Here's information about the Barbeque Area at Gopalan Atlantis:",
                "sources": [{
                    "content": get_mock_document_content('barbeque'),
                    "document": "Barbeque Area Usage",
                    "document_id": "barbeque_area",
                    "metadata": {
                        "title": "Barbeque Area Usage",
                        "category": "Apartment Amenities"
                    },
                    "score": 0.9
                }]
            })
        elif 'printer' in query_lower or 'printing' in query_lower:
            return jsonify({
                "answer": "Here's information about printer usage at Gopalan Atlantis:",
                "sources": [{
                    "content": get_mock_document_content('printer'),
                    "document": "Printer Usage Policy",
                    "document_id": "printer_usage",
                    "metadata": {
                        "title": "Printer Usage Policy",
                        "category": "Apartment Services"
                    },
                    "score": 0.9
                }]
            })
        elif 'lease' in query_lower or 'agreement' in query_lower or 'contract' in query_lower:
            return jsonify({
                "answer": "Here's information about lease agreements at Gopalan Atlantis:",
                "sources": [{
                    "content": get_mock_document_content('lease'),
                    "document": "Lease Agreement",
                    "document_id": "lease_agreement",
                    "metadata": {
                        "title": "Lease Agreement",
                        "category": "Legal Documents"
                    },
                    "score": 0.9
                }]
            })
        elif 'maintenance' in query_lower or 'repair' in query_lower or 'fix' in query_lower:
            return jsonify({
                "answer": "Here's information about maintenance requests at Gopalan Atlantis:",
                "sources": [{
                    "content": get_mock_document_content('maintenance'),
                    "document": "Maintenance Request Form",
                    "document_id": "maintenance_request",
                    "metadata": {
                        "title": "Maintenance Request Form",
                        "category": "Apartment Services"
                    },
                    "score": 0.9
                }]
            })
        
        # Default response for other queries
        return jsonify({
            "answer": f"I couldn't find specific information about '{query}' in the uploaded documents. Please try a different query or upload relevant documents.",
            "sources": []
        })
    except Exception as e:
        print(f"Error in query_documents: {str(e)}")
        return jsonify({
            "answer": "Sorry, an error occurred while processing your query. Please try again later.",
            "sources": [],
            "error": str(e)
        }), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Helper functions for document processing
def extract_relevant_content(content, query_terms, max_chars=800):
    """Extract the most relevant parts of the content based on query terms"""
    # If content is short enough, return it all
    if len(content) <= max_chars:
        return content
    
    # Split content into paragraphs
    paragraphs = content.split('\n\n')
    
    # Score each paragraph based on query term matches
    scored_paragraphs = []
    for para in paragraphs:
        if not para.strip():
            continue
            
        score = 0
        for term in query_terms:
            if term in para.lower():
                score += 1
                
        scored_paragraphs.append((para, score))
    
    # Sort paragraphs by score (highest first)
    scored_paragraphs.sort(key=lambda x: x[1], reverse=True)
    
    # Take top paragraphs until we reach max_chars
    result = ""
    char_count = 0
    
    for para, _ in scored_paragraphs:
        if char_count + len(para) + 2 > max_chars:  # +2 for newlines
            break
            
        if result:
            result += "\n\n"
            
        result += para
        char_count += len(para) + 2
    
    return result

def generate_answer_from_content(query, content, document_title):
    """Generate a contextual answer based on document content"""
    query_lower = query.lower()
    
    # Check for specific question types
    if any(word in query_lower for word in ['how', 'what is', 'explain']):
        # Explanatory question
        if 'book' in query_lower or 'reserve' in query_lower or 'schedule' in query_lower:
            return f"According to the {document_title}, here's information about booking or reservations:"
        elif 'time' in query_lower or 'hour' in query_lower or 'when' in query_lower:
            return f"According to the {document_title}, here are the relevant hours or timing details:"
        elif 'cost' in query_lower or 'fee' in query_lower or 'price' in query_lower or 'deposit' in query_lower:
            return f"According to the {document_title}, here's information about costs or fees:"
        elif 'rule' in query_lower or 'policy' in query_lower or 'guideline' in query_lower:
            return f"According to the {document_title}, here are the relevant rules or guidelines:"
        else:
            return f"Based on the {document_title}, here's information that might answer your question:"
    elif any(word in query_lower for word in ['where', 'location']):
        # Location question
        return f"According to the {document_title}, here's information about the location:"
    elif any(word in query_lower for word in ['who', 'contact', 'responsible']):
        # Person/contact question
        return f"According to the {document_title}, here's information about contacts or responsible parties:"
    elif any(word in query_lower for word in ['when', 'date', 'deadline', 'schedule']):
        # Time/date question
        return f"According to the {document_title}, here's information about dates and schedules:"
    elif any(word in query_lower for word in ['can i', 'allowed', 'permitted', 'restriction']):
        # Permission question
        return f"According to the {document_title}, here's information about what is allowed or restricted:"
    else:
        # Generic response
        return f"Based on the {document_title}, I found this relevant information:"

# Add new routes for direct document access
def get_mock_document_content(doc_id):
    """Get mock content for specific document types"""
    doc_id = doc_id.lower()
    
    if "lease" in doc_id or "agreement" in doc_id:
        return """
        <h1>Lease Agreement</h1>
        <h2>Agreement Terms</h2>
        <p>This agreement is made between Gopalan Atlantis and the resident.</p>
        <h3>Term</h3>
        <p>The lease term is for 12 months starting from the date of occupancy.</p>
        <h3>Rent</h3>
        <p>Monthly rent is payable on the 5th of each month.</p>
        <h3>Security Deposit</h3>
        <p>A security deposit equal to two months' rent is required.</p>
        """
    elif "maintenance" in doc_id:
        return """
        <h1>Maintenance Request Form</h1>
        <p>Please fill out this form to request maintenance services.</p>
        <p><strong>Apartment Number:</strong> _______________</p>
            <li>Cleaning deposit of ₹2000 is required</li>
            <li>Cancellations must be made 48 hours in advance for full refund</li>
        </ol>
        <h2>Capacity and Restrictions</h2>
        <ul>
            <li>Maximum capacity: 50 people</li>
            <li>No smoking allowed</li>
            <li>No loud music after 9:00 PM</li>
            <li>Pets must be kept on leash in outdoor areas only</li>
        </ul>
        """
    elif "policy" in doc_id or "guideline" in doc_id:
        return f"""
        <h1>{doc_id.replace('_', ' ').title()}</h1>
        <h2>Purpose</h2>
        <p>This policy document outlines the guidelines and procedures for residents of Gopalan Atlantis.</p>
        
        <h2>Scope</h2>
        <p>This policy applies to all residents, visitors, and staff of Gopalan Atlantis.</p>
        
        <h2>Guidelines</h2>
        <ol>
            <li>All residents must adhere to community rules and regulations</li>
            <li>Quiet hours are from 10:00 PM to 6:00 AM</li>
            <li>Common areas should be kept clean and tidy</li>
            <li>Pets must be leashed in common areas</li>
            <li>Parking is restricted to designated areas only</li>
        </ol>
        
        <h2>Enforcement</h2>
        <p>Violations of these guidelines may result in warnings or fines as determined by the management.</p>
        
        <h2>Contact</h2>
        <p>For questions or concerns, please contact the management office at 080-12345678.</p>
        """
    elif "notice" in doc_id or "announcement" in doc_id:
        return f"""
        <h1>{doc_id.replace('_', ' ').title()}</h1>
        <h2>Important Announcement</h2>
        <p>Date: June 10, 2025</p>
        
        <div class="notice-content">
            <p>Dear Residents,</p>
            <p>We would like to inform you about upcoming maintenance work in the community.</p>
            <p>The swimming pool will be closed for maintenance from June 15-20, 2025.</p>
            <p>We apologize for any inconvenience and thank you for your understanding.</p>
            <p>Best regards,<br>Gopalan Atlantis Management</p>
        </div>
        """
    elif "form" in doc_id or "application" in doc_id:
        return f"""
        <h1>{doc_id.replace('_', ' ').title()}</h1>
        <div class="form-content">
            <h2>Resident Information</h2>
            <p><strong>Name:</strong> ___________________________</p>
            <p><strong>Apartment Number:</strong> _______________</p>
            <p><strong>Contact Number:</strong> ________________</p>
            <p><strong>Email:</strong> _________________________</p>
            
            <h2>Request Details</h2>
            <p><strong>Type of Request:</strong></p>
            <p>□ Maintenance □ Complaint □ Suggestion □ Other</p>
            <p><strong>Description:</strong></p>
            <p>_________________________________________</p>
            <p>_________________________________________</p>
            
            <h2>Authorization</h2>
            <p><strong>Signature:</strong> ____________________</p>
            <p><strong>Date:</strong> ________________________</p>
        </div>
        """
    else:
        # Enhanced generic content for other documents
        return f"""
        <h1>{doc_id.replace('_', ' ').title()}</h1>
        <div class="document-content">
            <h2>Document Overview</h2>
            <p>This document contains important information for residents of Gopalan Atlantis.</p>
            <p>Please read it carefully and contact the management office if you have any questions.</p>
            
            <h2>Key Information</h2>
            <ul>
                <li>This document was last updated on June 10, 2025</li>
                <li>For questions, contact the management office at 080-12345678</li>
                <li>Office hours: Monday-Saturday, 9:00 AM to 6:00 PM</li>
            </ul>
            
            <h2>Updates</h2>
            <p>This document may be updated periodically. Residents will be notified of any changes via email and notices in common areas.</p>
        </div>
        """

@app.route('/api/verba/documents/<doc_id>/view', methods=['GET', 'OPTIONS'])
def get_document_view(doc_id):
    """Get document content for viewing"""
    if request.method == 'OPTIONS':
        response = app.make_default_options_response()
        return response
        
    # Normal document handling
    if doc_id in documents:
        doc = documents[doc_id]
        file_path = doc.get('file_path')
        title = doc.get('metadata', {}).get('title', doc_id)
        category = doc.get('metadata', {}).get('category', 'General')
        
        if file_path and os.path.exists(file_path):
            # Check the file extension
            _, ext = os.path.splitext(file_path)
            
            # For text files, read and convert to formatted HTML
            if ext.lower() in ['.txt', '.md']:
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                    
                    # Format as HTML with proper structure
                    html_content = f"<h1>{title}</h1>\n<div class=\"document-content\">\n"
                    
                    # Process the content line by line for better formatting
                    lines = content.split('\n')
                    in_list = False
                    list_type = None
                    
                    for line in lines:
                        line = line.strip()
                        if not line:
                            continue
                            
                        # Check for headers
                        if line.startswith('# '):
                            if in_list:
                                html_content += f"</{'ul' if list_type == 'ul' else 'ol'}>\n"
                                in_list = False
                            html_content += f"<h2>{line[2:]}</h2>\n"
                        elif line.startswith('## '):
                            if in_list:
                                html_content += f"</{'ul' if list_type == 'ul' else 'ol'}>\n"
                                in_list = False
                            html_content += f"<h3>{line[3:]}</h3>\n"
                        # Check for unordered list items
                        elif line.startswith('- ') or line.startswith('* '):
                            if not in_list or list_type != 'ul':
                                if in_list:
                                    html_content += f"</{'ul' if list_type == 'ul' else 'ol'}>\n"
                                html_content += "<ul>\n"
                                in_list = True
                                list_type = 'ul'
                            html_content += f"<li>{line[2:]}</li>\n"
                        # Check for ordered list items
                        elif line[0].isdigit() and line[1:].startswith('. '):
                            if not in_list or list_type != 'ol':
                                if in_list:
                                    html_content += f"</{'ul' if list_type == 'ul' else 'ol'}>\n"
                                html_content += "<ol>\n"
                                in_list = True
                                list_type = 'ol'
                            html_content += f"<li>{line[line.find('.')+2:]}</li>\n"
                        else:
                            # Close any open list
                            if in_list:
                                html_content += f"</{'ul' if list_type == 'ul' else 'ol'}>\n"
                                in_list = False
                            # Regular paragraph
                            html_content += f"<p>{line}</p>\n"
                    
                    # Close any open list
                    if in_list:
                        html_content += f"</{'ul' if list_type == 'ul' else 'ol'}>\n"
                    
                    html_content += "</div>"
                    return html_content
                except Exception as e:
                    print(f"Error reading text file: {str(e)}")
                    # Fall back to mock content
                    return get_formatted_document_content(doc_id, title, category)
        
        # If we couldn't process the file, use the mock content
        return get_formatted_document_content(doc_id, title, category)
    
    # If document not found, return a generic message
    return f"""
    <h1>Document Not Found</h1>
    <div class="document-content">
        <p>Document ID: {doc_id}</p>
        <p>This document is not available for viewing. Please contact the management office for more information.</p>
    </div>
    """

def get_formatted_document_content(doc_id, title, category):
    """Generate formatted HTML content for a document"""
    # Special case for Club House document
    if 'club house' in title.lower() or 'clubhouse' in title.lower():
        return """
        <h1>Club House Usage Guidelines</h1>
        <div class="document-content">
            <h2>Hours of Operation</h2>
            <p>The Club House is open from 6:00 AM to 10:00 PM daily.</p>
            
            <h2>Booking Requirements</h2>
            <p>Residents must book the Club House at least 48 hours in advance for private events.</p>
            <p>A refundable security deposit of ₹5,000 is required for all bookings.</p>
            
            <h2>Restrictions</h2>
            <ul>
                <li>No smoking is allowed in the Club House or surrounding areas.</li>
                <li>No loud music after 9:00 PM.</li>
                <li>Pets must be kept on a leash and are only allowed in outdoor areas.</li>
            </ul>
            
            <h2>Cleaning</h2>
            <p>Residents are responsible for cleaning the Club House after use.</p>
            <p>A cleaning fee of ₹1,000 will be charged if the Club House is not properly cleaned.</p>
        </div>
        """
    
    # Special case for Pet Policy document
    elif 'pet' in title.lower():
        return """
        <h1>Pet Policy</h1>
        <div class="document-content">
            <h2>Registration Requirements</h2>
            <p>All pets must be registered with the management office within 7 days of moving in or acquiring a new pet.</p>
            
            <h2>Allowed Pets</h2>
            <ul>
                <li>Dogs (maximum 2 per apartment)</li>
                <li>Cats (maximum 2 per apartment)</li>
                <li>Small caged birds</li>
                <li>Fish in aquariums up to 20 gallons</li>
            </ul>
            
            <h2>Restrictions</h2>
            <p>Dogs must be leashed at all times in common areas.</p>
            <p>Pet owners must clean up after their pets immediately.</p>
            <p>Pets are not allowed in the swimming pool area, gym, or indoor clubhouse.</p>
            
            <h2>Complaints</h2>
            <p>Excessive barking or other disturbances may result in fines.</p>
            <p>Three valid complaints may result in the pet being removed from the premises.</p>
        </div>
        """
    
    # Generic document template for other documents
    else:
        return f"""
        <h1>{title}</h1>
        <div class="document-content">
            <h2>Document Information</h2>
            <p><strong>Category:</strong> {category}</p>
            <p><strong>Document ID:</strong> {doc_id}</p>
            
            <h2>Content</h2>
            <p>This document contains important information for residents of Gopalan Atlantis.</p>
            <p>Please review the entire document carefully and contact the management office if you have any questions.</p>
            
            <h2>Compliance</h2>
            <p>All residents are expected to comply with the guidelines outlined in this document.</p>
            <p>Non-compliance may result in warnings or fines as determined by the Resident Association.</p>
        </div>
        """

@app.route('/api/verba/documents/<doc_id>/download', methods=['GET'])
def download_document(doc_id):
    """Download a document"""
    try:
        if doc_id not in documents:
            return jsonify({"error": "Document not found"}), 404
            
        doc = documents[doc_id]
        file_path = doc.get('file_path')
        
        if not file_path or not os.path.exists(file_path):
            return jsonify({"error": "Document file not found"}), 404
            
        # Return the file for download
        return send_file(
            file_path,
            as_attachment=True,
            download_name=doc['metadata']['file_name'],
            mimetype=doc['metadata'].get('mime_type', 'application/octet-stream')
        )
    except Exception as e:
        print(f"Error downloading document: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/verba/documents/<doc_id>/delete', methods=['DELETE', 'OPTIONS'])
def delete_document(doc_id):
    """Delete a document"""
    if request.method == 'OPTIONS':
        response = app.make_default_options_response()
        return response
        
    try:
        if doc_id not in documents:
            return jsonify({"error": "Document not found"}), 404
            
        # Get document info
        doc = documents[doc_id]
        file_path = doc.get('file_path')
        
        # Delete the file if it exists
        if file_path and os.path.exists(os.path.dirname(file_path)):
            shutil.rmtree(os.path.dirname(file_path))
            print(f"Deleted document files at: {os.path.dirname(file_path)}")
        
        # Remove from documents dictionary
        del documents[doc_id]
        
        # Save metadata
        save_metadata()
        
        return jsonify({"success": True, "message": f"Document {doc_id} deleted"})
    except Exception as e:
        print(f"Error deleting document: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Document viewer HTML template
DOCUMENT_VIEWER_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>{{ title }} - Document Viewer</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            color: #333;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: #fff;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            border-bottom: 1px solid #eee;
            padding-bottom: 10px;
        }
        .metadata {
            background: #f9f9f9;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .metadata p {
            margin: 5px 0;
        }
        .content {
            white-space: pre-wrap;
            background: #f5f5f5;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #3498db;
        }
        .actions {
            margin-top: 20px;
            display: flex;
            gap: 10px;
        }
        .actions a {
            display: inline-block;
            background: #3498db;
            color: white;
            padding: 8px 16px;
            text-decoration: none;
            border-radius: 4px;
        }
        .actions a:hover {
            background: #2980b9;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>{{ title }}</h1>
        
        <div class="metadata">
            <p><strong>Category:</strong> {{ category }}</p>
            <p><strong>Uploaded:</strong> {{ uploaded_at }}</p>
            <p><strong>File:</strong> {{ file_name }}</p>
        </div>
        
        <div class="content">
            {{ content }}
        </div>
        
        <div class="actions">
            <a href="{{ download_url }}" download>Download Document</a>
            <a href="javascript:history.back()">Back</a>
        </div>
    </div>
</body>
</html>
"""

@app.route('/api/verba/view/<doc_id>', methods=['GET'])
def html_document_viewer(doc_id):
    """HTML document viewer"""
    try:
        if doc_id not in documents:
            return "Document not found", 404
            
        doc = documents[doc_id]
        metadata = doc['metadata']
        
        # Render HTML template
        return render_template_string(
            DOCUMENT_VIEWER_TEMPLATE,
            title=metadata.get('title', 'Document'),
            category=metadata.get('category', 'Uncategorized'),
            uploaded_at=metadata.get('uploaded_at', 'Unknown'),
            file_name=metadata.get('file_name', 'Unknown'),
            content=doc.get('content', 'Content not available'),
            download_url=f"/api/verba/documents/{doc_id}/download"
        )
    except Exception as e:
        print(f"Error rendering document viewer: {str(e)}")
        return f"Error: {str(e)}", 500

# Add route to serve mock documents
@app.route('/mock_docs/<filename>', methods=['GET', 'OPTIONS'])
def serve_mock_document(filename):
    """Serve sample documents from the mock_docs folder"""
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = app.make_default_options_response()
        return response
    
    try:
        file_path = os.path.join(MOCK_DOCS_FOLDER, filename)
        print(f"Attempting to serve mock document: {file_path}")
        
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return jsonify({"error": "File not found"}), 404
        
        # Determine content type based on file extension
        content_type = "text/plain"  # Default
        if filename.endswith('.pdf'):
            content_type = "application/pdf"
        elif filename.endswith('.docx'):
            content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        
        print(f"Serving file {filename} with content type {content_type}")
        
        # Create response with appropriate headers
        response = send_file(
            file_path,
            mimetype=content_type,
            as_attachment=False,
            download_name=filename
        )
        
        # Add CORS headers
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
        
    except Exception as e:
        print(f"Error serving mock document: {str(e)}")
        response = jsonify({"error": str(e)})
        response.status_code = 500
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 500

@app.route('/api/documents', methods=['GET'])
def get_library_documents():
    """Get all documents for the Document Library section"""
    try:
        # Create a list of documents for the Document Library
        library_docs = [
            {
                "id": 1,
                "title": "Lease Agreement",
                "type": "Legal Document",
                "category": "Contracts",
                "fileUrl": "/api/documents/1/download",
                "uploadedBy": "Admin",
                "uploadedAt": "2025-05-01T10:00:00Z",
                "status": "Active",
                "tags": ["lease", "agreement"],
                "metadata": {
                    "size": 1024,
                    "pages": 5,
                    "language": "English"
                }
            },
            {
                "id": 2,
                "title": "Maintenance Request Form",
                "type": "Form",
                "category": "Maintenance",
                "fileUrl": "/api/documents/2/download",
                "uploadedBy": "Admin",
                "uploadedAt": "2025-05-02T11:30:00Z",
                "status": "Active",
                "tags": ["maintenance", "form"],
                "metadata": {
                    "size": 512,
                    "pages": 2,
                    "language": "English"
                }
            },
            {
                "id": 3,
                "title": "Community Newsletter",
                "type": "Information",
                "category": "Communications",
                "fileUrl": "/api/documents/3/download",
                "uploadedBy": "Admin",
                "uploadedAt": "2025-05-10T09:15:00Z",
                "status": "Active",
                "tags": ["newsletter", "community"],
                "metadata": {
                    "size": 2048,
                    "pages": 8,
                    "language": "English"
                }
            },
            {
                "id": 4,
                "title": "Club House Usage",
                "type": "Rules & Regulations",
                "category": "Apartment Rules & Regulations",
                "fileUrl": "/api/verba/documents/clubhouse/view",
                "uploadedBy": "Admin",
                "uploadedAt": "2025-06-11T16:02:38.388564",
                "status": "Active",
                "tags": ["clubhouse", "rules"],
                "metadata": {
                    "size": 30480,
                    "pages": 1,
                    "language": "English"
                }
            }
        ]
        
        # Add other Verba documents to library (except Club House which is already added)
        next_id = len(library_docs) + 1
        for doc_id, doc in documents.items():
            if doc and 'metadata' in doc and 'title' in doc['metadata']:
                title = doc['metadata']['title']
                # Skip Club House document as we already added it
                if "club" in title.lower() and "house" in title.lower():
                    continue
                    
                # Add other documents with appropriate categories
                if "gym" in title.lower() or "swimming" in title.lower() or "pet" in title.lower() or "waste" in title.lower() or "security" in title.lower() or "barbeque" in title.lower() or "printer" in title.lower():
                    library_docs.append({
                        "id": next_id,
                        "title": title,
                        "type": "Rules & Regulations",
                        "category": "Apartment Rules & Regulations",
                        "fileUrl": f"/api/verba/documents/{doc_id}/view",
                        "uploadedBy": "Admin",
                        "uploadedAt": doc['metadata'].get('uploaded_at', datetime.datetime.now().isoformat()),
                        "status": "Active",
                        "tags": [title.split()[0].lower()],
                        "metadata": {
                            "size": doc['metadata'].get('size', 0),
                            "pages": 1,
                            "language": "English"
                        }
                    })
                    next_id += 1
        
        return jsonify(library_docs)
    except Exception as e:
        print(f"Error getting library documents: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/documents/types', methods=['GET'])
def get_document_types():
    """Get all document types for the Document Library"""
    try:
        types = [
            {
                "id": 1,
                "name": "Legal Document",
                "description": "Legal agreements and contracts",
                "icon": "description"
            },
            {
                "id": 2,
                "name": "Form",
                "description": "Forms and templates",
                "icon": "assignment"
            },
            {
                "id": 3,
                "name": "Information",
                "description": "Informational documents",
                "icon": "info"
            },
            {
                "id": 4,
                "name": "Rules & Regulations",
                "description": "Community rules and regulations",
                "icon": "gavel"
            }
        ]
        return jsonify(types)
    except Exception as e:
        print(f"Error getting document types: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/documents/search', methods=['GET'])
def search_library_documents():
    """Search documents in the Document Library"""
    try:
        query = request.args.get('query', '').lower()
        # This is a simplified search that would call get_library_documents and filter
        # In a real implementation, this would use a more sophisticated search algorithm
        documents_response = get_library_documents()
        documents_data = json.loads(documents_response.get_data(as_text=True))
        
        if query:
            filtered_docs = [doc for doc in documents_data if 
                            query in doc['title'].lower() or 
                            query in doc['category'].lower() or 
                            any(query in tag.lower() for tag in doc['tags'])]
            return jsonify(filtered_docs)
        else:
            return jsonify(documents_data)
    except Exception as e:
        print(f"Error searching documents: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("Starting Enhanced Verba Mock Server on port 5001...")
    try:
        app.run(host='0.0.0.0', port=5001, debug=True)
    except Exception as e:
        print(f"Error starting server: {str(e)}")
