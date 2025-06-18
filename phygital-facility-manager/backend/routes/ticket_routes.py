from flask import Blueprint, request, jsonify, current_app
import os
import json
from datetime import datetime
from sqlalchemy import desc, asc, func
import uuid
import requests

from db import get_db_session, Ticket, TicketComment, User, Document
from auth import login_required, admin_required, staff_required, get_current_user, get_user_from_token

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# Create blueprint
ticket_bp = Blueprint('ticket', __name__)

@ticket_bp.route('/', methods=['POST'])
@login_required
def create_ticket():
    """
    Create a new maintenance ticket
    """
    try:
        data = request.json
        
        if not data or not data.get('subject') or not data.get('description'):
            return jsonify({'error': 'Subject and description are required'}), 400
            
        # Get current user
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found'}), 401
            
        # Prepare ticket data
        ticket_data = {
            'subject': data['subject'],
            'description': data['description'],
            'category': data.get('category', 'general'),
            'priority': data.get('priority', 'medium'),
            'status': 'new',
            'apartment_unit': data.get('apartment_unit'),
            'location_details': data.get('location_details'),
            'created_by': current_user.id
        }
        
        # Create ticket in database
        with get_db_session() as session:
            ticket = Ticket(**ticket_data)
            session.add(ticket)
            session.commit()
            
            # Format response
            response_data = {
                'id': ticket.id,
                'subject': ticket.subject,
                'status': ticket.status,
                'created_at': ticket.created_at.isoformat() if ticket.created_at else None
            }
            
        # Optionally, send notification to staff
        if data.get('notify_staff', True):
            try:
                # Get staff members who should be notified
                with get_db_session() as session:
                    staff = session.query(User).filter(User.role.in_(['staff', 'admin'])).all()
                    staff_emails = [user.email for user in staff if user.email]
                
                # Send notification
                if staff_emails:
                    payload = {
                        'notificationType': 'ticket',
                        'recipients': staff_emails,
                        'subject': f"New Ticket: {ticket_data['subject']}",
                        'content': f"A new maintenance ticket has been created: {ticket_data['description'][:100]}...",
                        'sourceId': str(ticket.id),
                        'userId': current_user.id,
                        'metadata': {
                            'ticketId': str(ticket.id),
                            'status': 'new',
                            'priority': ticket_data['priority']
                        }
                    }
                    
                    headers = {
                        "apikey": SUPABASE_SERVICE_KEY,
                        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
                        "Content-Type": "application/json"
                    }
                    
                    requests.post(
                        f"{SUPABASE_URL}/functions/v1/notifications",
                        headers=headers,
                        json=payload
                    )
            except Exception as e:
                current_app.logger.error(f"Error sending ticket notification: {str(e)}")
                # Continue execution even if notification fails
            
        return jsonify(response_data), 201
        
    except Exception as e:
        current_app.logger.error(f"Error creating ticket: {str(e)}")
        return jsonify({'error': str(e)}), 500


@ticket_bp.route('/', methods=['GET'])
@login_required
def get_tickets():
    """
    Get tickets with pagination and filtering
    """
    try:
        # Parse query parameters
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        status = request.args.get('status')
        category = request.args.get('category')
        priority = request.args.get('priority')
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')
        
        # Get current user
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found'}), 401
            
        # Build query
        with get_db_session() as session:
            query = session.query(Ticket)
            
            # Apply filters based on user role
            if current_user.role == 'resident':
                # Residents can only see their own tickets
                query = query.filter(Ticket.created_by == current_user.id)
            
            # Apply status filter
            if status:
                query = query.filter(Ticket.status == status)
                
            # Apply category filter
            if category:
                query = query.filter(Ticket.category == category)
                
            # Apply priority filter
            if priority:
                query = query.filter(Ticket.priority == priority)
                
            # Apply sorting
            if hasattr(Ticket, sort_by):
                sort_attr = getattr(Ticket, sort_by)
                if sort_order.lower() == 'asc':
                    query = query.order_by(asc(sort_attr))
                else:
                    query = query.order_by(desc(sort_attr))
            else:
                query = query.order_by(desc(Ticket.created_at))
                
            # Get total count
            total_count = query.count()
            
            # Apply pagination
            offset = (page - 1) * per_page
            tickets = query.offset(offset).limit(per_page).all()
            
            # Format response
            result = []
            for ticket in tickets:
                # Get comment count
                comment_count = session.query(func.count(TicketComment.id)).filter(TicketComment.ticket_id == ticket.id).scalar()
                
                # Get creator name
                creator = session.query(User).filter(User.id == ticket.created_by).first()
                creator_name = f"{creator.first_name} {creator.last_name}" if creator else "Unknown"
                
                # Get assigned user name
                assigned_user = None
                if ticket.assigned_to:
                    assigned_user = session.query(User).filter(User.id == ticket.assigned_to).first()
                assigned_name = f"{assigned_user.first_name} {assigned_user.last_name}" if assigned_user else None
                
                result.append({
                    'id': ticket.id,
                    'subject': ticket.subject,
                    'description': ticket.description,
                    'category': ticket.category,
                    'priority': ticket.priority,
                    'status': ticket.status,
                    'apartment_unit': ticket.apartment_unit,
                    'location_details': ticket.location_details,
                    'created_at': ticket.created_at.isoformat() if ticket.created_at else None,
                    'updated_at': ticket.updated_at.isoformat() if ticket.updated_at else None,
                    'created_by': ticket.created_by,
                    'creator_name': creator_name,
                    'assigned_to': ticket.assigned_to,
                    'assigned_name': assigned_name,
                    'comment_count': comment_count
                })
            
            return jsonify({
                'tickets': result,
                'total': total_count,
                'page': page,
                'per_page': per_page,
                'pages': (total_count + per_page - 1) // per_page
            })
            
    except Exception as e:
        current_app.logger.error(f"Error getting tickets: {str(e)}")
        return jsonify({'error': str(e)}), 500


@ticket_bp.route('/<ticket_id>', methods=['GET'])
@login_required
def get_ticket(ticket_id):
    """
    Get a specific ticket by ID
    """
    try:
        # Get current user
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found'}), 401
            
        with get_db_session() as session:
            # Get ticket
            ticket = session.query(Ticket).filter(Ticket.id == ticket_id).first()
            
            if not ticket:
                return jsonify({'error': 'Ticket not found'}), 404
                
            # Check access rights
            if current_user.role == 'resident' and ticket.created_by != current_user.id:
                return jsonify({'error': 'You do not have permission to access this ticket'}), 403
                
            # Get comments
            comments = session.query(TicketComment).filter(TicketComment.ticket_id == ticket_id).order_by(TicketComment.created_at).all()
            
            # Get creator name
            creator = session.query(User).filter(User.id == ticket.created_by).first()
            creator_name = f"{creator.first_name} {creator.last_name}" if creator else "Unknown"
            
            # Get assigned user name
            assigned_user = None
            if ticket.assigned_to:
                assigned_user = session.query(User).filter(User.id == ticket.assigned_to).first()
            assigned_name = f"{assigned_user.first_name} {assigned_user.last_name}" if assigned_user else None
            
            # Get attached documents
            documents = session.query(Document).filter(Document.related_id == ticket_id, Document.related_type == 'ticket').all()
            
            # Format ticket data
            ticket_data = {
                'id': ticket.id,
                'subject': ticket.subject,
                'description': ticket.description,
                'category': ticket.category,
                'priority': ticket.priority,
                'status': ticket.status,
                'apartment_unit': ticket.apartment_unit,
                'location_details': ticket.location_details,
                'created_at': ticket.created_at.isoformat() if ticket.created_at else None,
                'updated_at': ticket.updated_at.isoformat() if ticket.updated_at else None,
                'created_by': ticket.created_by,
                'creator_name': creator_name,
                'assigned_to': ticket.assigned_to,
                'assigned_name': assigned_name,
                'comments': [{
                    'id': comment.id,
                    'content': comment.content,
                    'created_by': comment.created_by,
                    'created_at': comment.created_at.isoformat() if comment.created_at else None,
                    'author_name': session.query(User.first_name, User.last_name)
                                .filter(User.id == comment.created_by).first() or ('Unknown', 'User')
                } for comment in comments],
                'documents': [{
                    'id': doc.id,
                    'name': doc.title,
                    'file_type': doc.file_type,
                    'created_at': doc.created_at.isoformat() if doc.created_at else None
                } for doc in documents]
            }
            
            return jsonify(ticket_data)
            
    except Exception as e:
        current_app.logger.error(f"Error getting ticket details: {str(e)}")
        return jsonify({'error': str(e)}), 500


@ticket_bp.route('/<ticket_id>', methods=['PUT', 'PATCH'])
@login_required
def update_ticket(ticket_id):
    """
    Update an existing ticket
    """
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        # Get current user
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found'}), 401
            
        with get_db_session() as session:
            # Get ticket
            ticket = session.query(Ticket).filter(Ticket.id == ticket_id).first()
            
            if not ticket:
                return jsonify({'error': 'Ticket not found'}), 404
                
            # Check access rights
            if current_user.role == 'resident':
                # Residents can only update their own tickets and only certain fields
                if ticket.created_by != current_user.id:
                    return jsonify({'error': 'You do not have permission to update this ticket'}), 403
                    
                # Residents can only update description and add comments
                allowed_fields = ['description']
                for field in allowed_fields:
                    if field in data:
                        setattr(ticket, field, data[field])
            else:
                # Staff and admins can update all fields
                updateable_fields = ['subject', 'description', 'category', 'priority', 'status', 'location_details', 'assigned_to']
                for field in updateable_fields:
                    if field in data:
                        setattr(ticket, field, data[field])
            
            # Always update the updated_at timestamp
            ticket.updated_at = datetime.utcnow()
            
            # Check for status change to send notification
            status_changed = 'status' in data and data['status'] != ticket.status
            old_status = ticket.status
            
            # Save changes
            session.commit()
            
            # Get the ticket creator for notifications
            if status_changed and ticket.created_by != current_user.id:
                try:
                    # Get ticket creator
                    creator = session.query(User).filter(User.id == ticket.created_by).first()
                    
                    if creator and creator.email:
                        # Notify creator of status change
                        payload = {
                            'notificationType': 'ticket',
                            'recipients': [creator.email],
                            'subject': f"Ticket Update: {ticket.subject}",
                            'content': f"Your ticket status has changed from {old_status} to {ticket.status}.",
                            'sourceId': str(ticket.id),
                            'userId': current_user.id,
                            'metadata': {
                                'ticketId': str(ticket.id),
                                'status': ticket.status,
                                'priority': ticket.priority
                            }
                        }
                        
                        headers = {
                            "apikey": SUPABASE_SERVICE_KEY,
                            "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
                            "Content-Type": "application/json"
                        }
                        
                        requests.post(
                            f"{SUPABASE_URL}/functions/v1/notifications",
                            headers=headers,
                            json=payload
                        )
                except Exception as e:
                    current_app.logger.error(f"Error sending ticket update notification: {str(e)}")
            
            # Return updated ticket
            return jsonify({
                'id': ticket.id,
                'subject': ticket.subject,
                'status': ticket.status,
                'updated_at': ticket.updated_at.isoformat() if ticket.updated_at else None,
                'message': 'Ticket updated successfully'
            })
            
    except Exception as e:
        current_app.logger.error(f"Error updating ticket: {str(e)}")
        return jsonify({'error': str(e)}), 500


@ticket_bp.route('/<ticket_id>/comments', methods=['POST'])
@login_required
def add_comment(ticket_id):
    """
    Add a comment to a ticket
    """
    try:
        data = request.json
        if not data or not data.get('content'):
            return jsonify({'error': 'Comment content is required'}), 400
            
        # Get current user
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found'}), 401
            
        with get_db_session() as session:
            # Get ticket
            ticket = session.query(Ticket).filter(Ticket.id == ticket_id).first()
            
            if not ticket:
                return jsonify({'error': 'Ticket not found'}), 404
                
            # Check access rights for residents
            if current_user.role == 'resident' and ticket.created_by != current_user.id:
                return jsonify({'error': 'You do not have permission to comment on this ticket'}), 403
                
            # Create comment
            comment = TicketComment(
                ticket_id=ticket_id,
                content=data['content'],
                created_by=current_user.id
            )
            session.add(comment)
            
            # Update ticket timestamp
            ticket.updated_at = datetime.utcnow()
            
            session.commit()
            
            # Format response
            response_data = {
                'id': comment.id,
                'content': comment.content,
                'created_by': comment.created_by,
                'created_at': comment.created_at.isoformat() if comment.created_at else None,
                'ticket_id': ticket_id
            }
            
            # Notify relevant parties
            should_notify = data.get('notify', True)
            if should_notify:
                try:
                    # Determine who to notify
                    recipients = []
                    
                    # Always notify ticket creator if comment is from staff/admin
                    if current_user.role in ['staff', 'admin'] and ticket.created_by != current_user.id:
                        creator = session.query(User).filter(User.id == ticket.created_by).first()
                        if creator and creator.email:
                            recipients.append(creator.email)
                    
                    # Notify assigned staff if comment is from resident
                    if current_user.role == 'resident' and ticket.assigned_to and ticket.assigned_to != current_user.id:
                        assigned = session.query(User).filter(User.id == ticket.assigned_to).first()
                        if assigned and assigned.email:
                            recipients.append(assigned.email)
                    
                    # If no specific recipients, notify all staff
                    if not recipients and current_user.role == 'resident':
                        staff = session.query(User).filter(User.role.in_(['staff', 'admin'])).all()
                        recipients = [user.email for user in staff if user.email]
                    
                    if recipients:
                        payload = {
                            'notificationType': 'ticket',
                            'recipients': recipients,
                            'subject': f"New Comment on Ticket: {ticket.subject}",
                            'content': data['content'],
                            'sourceId': str(ticket.id),
                            'userId': current_user.id,
                            'metadata': {
                                'ticketId': str(ticket.id),
                                'commentId': str(comment.id),
                                'status': ticket.status
                            }
                        }
                        
                        headers = {
                            "apikey": SUPABASE_SERVICE_KEY,
                            "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
                            "Content-Type": "application/json"
                        }
                        
                        requests.post(
                            f"{SUPABASE_URL}/functions/v1/notifications",
                            headers=headers,
                            json=payload
                        )
                except Exception as e:
                    current_app.logger.error(f"Error sending comment notification: {str(e)}")
            
            return jsonify(response_data), 201
            
    except Exception as e:
        current_app.logger.error(f"Error adding comment: {str(e)}")
        return jsonify({'error': str(e)}), 500


@ticket_bp.route('/<ticket_id>/assign', methods=['POST'])
@staff_required
def assign_ticket(ticket_id):
    """
    Assign a ticket to a staff member (staff/admin only)
    """
    try:
        data = request.json
        if not data or 'assigned_to' not in data:
            return jsonify({'error': 'assigned_to user ID is required'}), 400
            
        # Get current user
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found'}), 401
            
        with get_db_session() as session:
            # Get ticket
            ticket = session.query(Ticket).filter(Ticket.id == ticket_id).first()
            
            if not ticket:
                return jsonify({'error': 'Ticket not found'}), 404
                
            # Verify assigned user exists and is staff/admin
            assigned_user_id = data['assigned_to']
            if assigned_user_id:
                assigned_user = session.query(User).filter(User.id == assigned_user_id).first()
                
                if not assigned_user:
                    return jsonify({'error': 'Assigned user not found'}), 400
                    
                if assigned_user.role not in ['staff', 'admin']:
                    return jsonify({'error': 'Can only assign tickets to staff or admin users'}), 400
            
            # Update ticket
            old_assigned_to = ticket.assigned_to
            ticket.assigned_to = assigned_user_id
            ticket.updated_at = datetime.utcnow()
            
            # Optionally update status
            if data.get('update_status') and data.get('status'):
                ticket.status = data['status']
            
            session.commit()
            
            # Get assigned user name for response
            assigned_name = None
            if assigned_user:
                assigned_name = f"{assigned_user.first_name} {assigned_user.last_name}"
            
            # Notify the newly assigned staff member
            if assigned_user_id and assigned_user_id != old_assigned_to and assigned_user_id != current_user.id:
                try:
                    if assigned_user and assigned_user.email:
                        # Notify the assigned staff member
                        payload = {
                            'notificationType': 'ticket',
                            'recipients': [assigned_user.email],
                            'subject': f"Ticket Assigned: {ticket.subject}",
                            'content': f"You have been assigned to ticket #{ticket_id}: {ticket.subject}\n\n{ticket.description}",
                            'sourceId': str(ticket.id),
                            'userId': current_user.id,
                            'metadata': {
                                'ticketId': str(ticket.id),
                                'status': ticket.status,
                                'priority': ticket.priority
                            }
                        }
                        
                        headers = {
                            "apikey": SUPABASE_SERVICE_KEY,
                            "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
                            "Content-Type": "application/json"
                        }
                        
                        requests.post(
                            f"{SUPABASE_URL}/functions/v1/notifications",
                            headers=headers,
                            json=payload
                        )
                except Exception as e:
                    current_app.logger.error(f"Error sending ticket assignment notification: {str(e)}")
            
            return jsonify({
                'id': ticket.id,
                'assigned_to': ticket.assigned_to,
                'assigned_name': assigned_name,
                'status': ticket.status,
                'message': 'Ticket assigned successfully'
            })
            
    except Exception as e:
        current_app.logger.error(f"Error assigning ticket: {str(e)}")
        return jsonify({'error': str(e)}), 500


@ticket_bp.route('/<ticket_id>/attachments', methods=['POST'])
@login_required
def add_attachment(ticket_id):
    """
    Add a document attachment to a ticket
    """
    try:
        # Validate input
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
            
        # Get current user
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found'}), 401
            
        with get_db_session() as session:
            # Get ticket
            ticket = session.query(Ticket).filter(Ticket.id == ticket_id).first()
            
            if not ticket:
                return jsonify({'error': 'Ticket not found'}), 404
                
            # Check access rights for residents
            if current_user.role == 'resident' and ticket.created_by != current_user.id:
                return jsonify({'error': 'You do not have permission to add attachments to this ticket'}), 403
            
            # Process the file
            filename = file.filename
            file_extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
            
            # Generate a unique filename
            unique_filename = f"{uuid.uuid4()}_{filename}"
            
            # Save file to temporary location
            temp_path = os.path.join('/tmp', unique_filename)
            file.save(temp_path)
            
            # Upload to Supabase Storage
            try:
                # First, create document record in database
                document = Document(
                    title=filename,
                    description=f"Attachment for ticket {ticket_id}",
                    file_type=file_extension,
                    related_id=ticket_id,
                    related_type='ticket',
                    created_by=current_user.id,
                    file_size_kb=os.path.getsize(temp_path) / 1024
                )
                
                session.add(document)
                session.flush()  # Get the document ID without committing transaction
                
                # Upload to Supabase with document ID as part of path
                storage_path = f"ticket-attachments/{ticket_id}/{document.id}_{unique_filename}"
                
                with open(temp_path, 'rb') as file_data:
                    # Prepare headers for Supabase storage API
                    headers = {
                        "apikey": SUPABASE_KEY,
                        "Authorization": f"Bearer {SUPABASE_KEY}",
                        "Content-Type": "application/octet-stream"
                    }
                    
                    # Upload to Supabase storage
                    response = requests.post(
                        f"{SUPABASE_URL}/storage/v1/object/public/{storage_path}",
                        headers=headers,
                        data=file_data
                    )
                    
                    if response.status_code != 200:
                        session.rollback()
                        return jsonify({'error': f"Failed to upload file to storage: {response.text}"}), 500
                        
                    # Update document with storage path
                    document.file_path = storage_path
                    document.public_url = f"{SUPABASE_URL}/storage/v1/object/public/{storage_path}"
                    
                    # Commit transaction
                    session.commit()
                    
                    # Remove temporary file
                    os.remove(temp_path)
                    
                    # Update ticket timestamp
                    ticket.updated_at = datetime.utcnow()
                    session.commit()
                    
                    return jsonify({
                        'id': document.id,
                        'name': document.title,
                        'file_type': document.file_type,
                        'url': document.public_url,
                        'created_at': document.created_at.isoformat() if document.created_at else None
                    }), 201
                    
            except Exception as e:
                # Clean up temporary file in case of error
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                raise e
                
    except Exception as e:
        current_app.logger.error(f"Error adding attachment: {str(e)}")
        return jsonify({'error': str(e)}), 500


@ticket_bp.route('/<ticket_id>', methods=['DELETE'])
@admin_required
def delete_ticket(ticket_id):
    """
    Delete a ticket (admin only)
    """
    try:
        with get_db_session() as session:
            # Get ticket
            ticket = session.query(Ticket).filter(Ticket.id == ticket_id).first()
            
            if not ticket:
                return jsonify({'error': 'Ticket not found'}), 404
                
            # Delete associated comments
            session.query(TicketComment).filter(TicketComment.ticket_id == ticket_id).delete()
            
            # Delete associated documents (for database records only)
            documents = session.query(Document).filter(
                Document.related_id == ticket_id, 
                Document.related_type == 'ticket'
            ).all()
            
            # Delete the ticket
            session.delete(ticket)
            session.commit()
            
            # Delete document files from Supabase storage
            headers = {
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}"
            }
            
            for doc in documents:
                if doc.file_path:
                    try:
                        requests.delete(
                            f"{SUPABASE_URL}/storage/v1/object/public/{doc.file_path}",
                            headers=headers
                        )
                    except Exception as e:
                        current_app.logger.error(f"Error deleting document file: {str(e)}")
            
            return jsonify({
                'message': 'Ticket and all associated data successfully deleted',
                'ticket_id': ticket_id
            })
            
    except Exception as e:
        current_app.logger.error(f"Error deleting ticket: {str(e)}")
        return jsonify({'error': str(e)}), 500


@ticket_bp.route('/statistics', methods=['GET'])
@staff_required
def ticket_statistics():
    """
    Get statistics about tickets for reporting
    """
    try:
        with get_db_session() as session:
            # Get total counts by status
            status_counts = {}
            for status in ['new', 'in_progress', 'pending', 'resolved', 'closed']:
                count = session.query(func.count(Ticket.id)).filter(Ticket.status == status).scalar()
                status_counts[status] = count
                
            # Get counts by category
            category_counts = {}
            categories = session.query(Ticket.category, func.count(Ticket.id)).group_by(Ticket.category).all()
            for category, count in categories:
                category_counts[category] = count
                
            # Get counts by priority
            priority_counts = {}
            for priority in ['low', 'medium', 'high', 'critical']:
                count = session.query(func.count(Ticket.id)).filter(Ticket.priority == priority).scalar()
                priority_counts[priority] = count
                
            # Get average resolution time (for resolved tickets)
            # This is a simplified calculation - in a real system you might store resolution timestamps
            # Here we're using updated_at as a proxy for resolution time
            avg_resolution_time = session.query(
                func.avg(Ticket.updated_at - Ticket.created_at)
            ).filter(Ticket.status.in_(['resolved', 'closed'])).scalar()
            
            if avg_resolution_time:
                avg_resolution_days = avg_resolution_time.total_seconds() / (24 * 3600)
            else:
                avg_resolution_days = 0
                
            # Get top staff by resolved tickets
            top_staff = session.query(
                User.id,
                User.first_name,
                User.last_name,
                func.count(Ticket.id).label('resolved_count')
            ).join(
                Ticket, Ticket.assigned_to == User.id
            ).filter(
                Ticket.status.in_(['resolved', 'closed'])
            ).group_by(
                User.id, User.first_name, User.last_name
            ).order_by(
                desc('resolved_count')
            ).limit(5).all()
            
            top_staff_list = [{
                'id': staff.id,
                'name': f"{staff.first_name} {staff.last_name}",
                'resolved_tickets': staff.resolved_count
            } for staff in top_staff]
            
            return jsonify({
                'status_counts': status_counts,
                'category_counts': category_counts,
                'priority_counts': priority_counts,
                'avg_resolution_time_days': avg_resolution_days,
                'top_staff': top_staff_list,
                'total_tickets': sum(status_counts.values()),
                'open_tickets': status_counts.get('new', 0) + status_counts.get('in_progress', 0) + status_counts.get('pending', 0),
            })
            
    except Exception as e:
        current_app.logger.error(f"Error getting ticket statistics: {str(e)}")
        return jsonify({'error': str(e)}), 500


@ticket_bp.route('/export', methods=['GET'])
@staff_required
def export_tickets():
    """
    Export tickets as CSV or JSON for reporting
    """
    try:
        # Parse query parameters
        export_format = request.args.get('format', 'json')
        status = request.args.get('status')
        category = request.args.get('category')
        priority = request.args.get('priority')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        with get_db_session() as session:
            # Build query
            query = session.query(Ticket)
            
            # Apply filters
            if status:
                query = query.filter(Ticket.status == status)
                
            if category:
                query = query.filter(Ticket.category == category)
                
            if priority:
                query = query.filter(Ticket.priority == priority)
                
            if date_from:
                date_from = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
                query = query.filter(Ticket.created_at >= date_from)
                
            if date_to:
                date_to = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
                query = query.filter(Ticket.created_at <= date_to)
            
            # Get tickets
            tickets = query.all()
            
            # Format for export
            if export_format.lower() == 'csv':
                # Generate CSV
                import csv
                from io import StringIO
                
                output = StringIO()
                fieldnames = ['id', 'subject', 'description', 'category', 'priority', 'status', 
                            'apartment_unit', 'location_details', 'created_at', 'updated_at',
                            'created_by', 'assigned_to']
                
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                
                for ticket in tickets:
                    writer.writerow({
                        'id': ticket.id,
                        'subject': ticket.subject,
                        'description': ticket.description,
                        'category': ticket.category,
                        'priority': ticket.priority,
                        'status': ticket.status,
                        'apartment_unit': ticket.apartment_unit,
                        'location_details': ticket.location_details,
                        'created_at': ticket.created_at.isoformat() if ticket.created_at else None,
                        'updated_at': ticket.updated_at.isoformat() if ticket.updated_at else None,
                        'created_by': ticket.created_by,
                        'assigned_to': ticket.assigned_to
                    })
                
                # Send as attachment
                response = current_app.response_class(
                    output.getvalue(),
                    mimetype='text/csv',
                    headers={'Content-Disposition': f'attachment; filename=tickets-{datetime.utcnow().strftime("%Y%m%d%H%M%S")}.csv'}
                )
                return response
                
            else:
                # Default to JSON
                result = []
                for ticket in tickets:
                    # Get creator name
                    creator = session.query(User).filter(User.id == ticket.created_by).first()
                    creator_name = f"{creator.first_name} {creator.last_name}" if creator else "Unknown"
                    
                    # Get assigned user name
                    assigned_user = None
                    if ticket.assigned_to:
                        assigned_user = session.query(User).filter(User.id == ticket.assigned_to).first()
                    assigned_name = f"{assigned_user.first_name} {assigned_user.last_name}" if assigned_user else None
                    
                    result.append({
                        'id': ticket.id,
                        'subject': ticket.subject,
                        'description': ticket.description,
                        'category': ticket.category,
                        'priority': ticket.priority,
                        'status': ticket.status,
                        'apartment_unit': ticket.apartment_unit,
                        'location_details': ticket.location_details,
                        'created_at': ticket.created_at.isoformat() if ticket.created_at else None,
                        'updated_at': ticket.updated_at.isoformat() if ticket.updated_at else None,
                        'created_by': ticket.created_by,
                        'creator_name': creator_name,
                        'assigned_to': ticket.assigned_to,
                        'assigned_name': assigned_name
                    })
                
                return jsonify({'tickets': result})
        
    except Exception as e:
        current_app.logger.error(f"Error exporting tickets: {str(e)}")
        return jsonify({'error': str(e)}), 500
