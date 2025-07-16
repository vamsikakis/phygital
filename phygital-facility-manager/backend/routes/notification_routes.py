from flask import Blueprint, request, jsonify, current_app
import os
import json
import uuid
from datetime import datetime
import requests

from db import get_db_session
from auth import get_current_user, admin_required, staff_required, management_required

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# Create blueprint
notification_bp = Blueprint('notification', __name__)

@notification_bp.route('/send', methods=['POST'])
@admin_required
def send_notification():
    """
    Send an email notification to one or more recipients
    """
    try:
        data = request.json
        
        if not data or 'type' not in data:
            return jsonify({'error': 'Missing required fields'}), 400
            
        notification_type = data.get('type')
        recipients = data.get('recipients', [])
        subject = data.get('subject')
        content = data.get('content')
        source_id = data.get('source_id')
        
        # Construct payload for edge function
        payload = {
            'type': notification_type,
            'recipients': recipients,
            'subject': subject,
            'content': content,
            'source_id': source_id,
            'metadata': data.get('metadata', {})
        }
        
        # Call the send-notification edge function
        try:
            headers = {
                "apikey": SUPABASE_SERVICE_KEY,
                "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                f"{SUPABASE_URL}/functions/v1/notifications",
                headers=headers,
                json=payload
            )
            
            if response.status_code != 200:
                current_app.logger.error(f"Notification sending failed: {response.text}")
                return jsonify({'error': f"Notification sending failed: {response.text}"}), response.status_code
            
            result = response.json()
            
            # Log notification to database
            try:
                from db import NotificationLog
                session = get_db_session()
                
                log_entry = NotificationLog(
                    notification_type=notification_type,
                    recipients=json.dumps(recipients),
                    subject=subject,
                    source_id=source_id,
                    content=content,
                    status=result.get('status', 'processed'),
                    created_by=get_current_user().id if get_current_user() else None,
                    metadata=json.dumps(data.get('metadata', {}))
                )
                session.add(log_entry)
                session.commit()
            except Exception as e:
                current_app.logger.warning(f"Error logging notification: {str(e)}")
            
            return jsonify(result)
                
        except Exception as e:
            current_app.logger.error(f"Error calling notification function: {str(e)}")
            return jsonify({'error': str(e)}), 500
        
    except Exception as e:
        current_app.logger.error(f"Error processing notification: {str(e)}")
        return jsonify({'error': str(e)}), 500

@notification_bp.route('/announcement', methods=['POST'])
@management_required
def send_announcement():
    """
    Send an announcement notification to all apartment owners or a specific group
    """
    try:
        data = request.json
        
        if not data or 'subject' not in data or 'content' not in data:
            return jsonify({'error': 'Missing required fields'}), 400
            
        subject = data.get('subject')
        content = data.get('content')
        announcement_id = data.get('announcement_id')
        groups = data.get('groups', ['all'])
        
        # Get recipients based on groups
        recipients = []
        try:
            from db import User
            session = get_db_session()
            
            query = session.query(User)
            
            # Filter by groups if not 'all'
            if 'all' not in groups:
                query = query.filter(User.user_type.in_(groups))
                
            users = query.all()
            recipients = [user.email for user in users if user.email]
        except Exception as e:
            current_app.logger.error(f"Error fetching recipients: {str(e)}")
            return jsonify({'error': f"Error fetching recipients: {str(e)}"}), 500
        
        # Construct payload for edge function
        payload = {
            'type': 'announcement',
            'recipients': recipients,
            'subject': subject,
            'content': content,
            'source_id': announcement_id,
            'metadata': {
                'groups': groups,
                'announcement_id': announcement_id,
                'sent_by': get_current_user().id if get_current_user() else None
            }
        }
        
        # Call the send-notification edge function
        try:
            headers = {
                "apikey": SUPABASE_SERVICE_KEY,
                "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                f"{SUPABASE_URL}/functions/v1/notifications",
                headers=headers,
                json=payload
            )
            
            if response.status_code != 200:
                current_app.logger.error(f"Announcement sending failed: {response.text}")
                return jsonify({'error': f"Announcement sending failed: {response.text}"}), response.status_code
            
            result = response.json()
            
            # Log notification to database
            try:
                from db import NotificationLog
                session = get_db_session()
                
                log_entry = NotificationLog(
                    notification_type='announcement',
                    recipients=json.dumps(recipients),
                    subject=subject,
                    source_id=announcement_id,
                    content=content,
                    status=result.get('status', 'processed'),
                    created_by=get_current_user().id if get_current_user() else None,
                    metadata=json.dumps({'groups': groups, 'announcement_id': announcement_id})
                )
                session.add(log_entry)
                session.commit()
            except Exception as e:
                current_app.logger.warning(f"Error logging announcement notification: {str(e)}")
            
            return jsonify(result)
                
        except Exception as e:
            current_app.logger.error(f"Error calling announcement notification function: {str(e)}")
            return jsonify({'error': str(e)}), 500
        
    except Exception as e:
        current_app.logger.error(f"Error processing announcement notification: {str(e)}")
        return jsonify({'error': str(e)}), 500

@notification_bp.route('/event', methods=['POST'])
@admin_required
def send_event_notification():
    """
    Send an event notification to registered participants or all owners
    """
    try:
        data = request.json
        
        if not data or 'subject' not in data or 'content' not in data or 'event_id' not in data:
            return jsonify({'error': 'Missing required fields'}), 400
            
        subject = data.get('subject')
        content = data.get('content')
        event_id = data.get('event_id')
        notify_all = data.get('notify_all', False)
        
        # Get recipients
        recipients = []
        try:
            from db import User, EventParticipant
            session = get_db_session()
            
            if notify_all:
                # Notify all users
                users = session.query(User).all()
                recipients = [user.email for user in users if user.email]
            else:
                # Notify only registered participants
                participants = session.query(EventParticipant).filter(
                    EventParticipant.event_id == event_id
                ).all()
                
                # Get user emails for participants
                user_ids = [p.user_id for p in participants]
                users = session.query(User).filter(User.id.in_(user_ids)).all()
                recipients = [user.email for user in users if user.email]
        except Exception as e:
            current_app.logger.error(f"Error fetching event recipients: {str(e)}")
            return jsonify({'error': f"Error fetching event recipients: {str(e)}"}), 500
        
        # Construct payload for edge function
        payload = {
            'type': 'event',
            'recipients': recipients,
            'subject': subject,
            'content': content,
            'source_id': event_id,
            'metadata': {
                'event_id': event_id,
                'notify_all': notify_all,
                'sent_by': get_current_user().id if get_current_user() else None
            }
        }
        
        # Call the send-notification edge function
        try:
            headers = {
                "apikey": SUPABASE_SERVICE_KEY,
                "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                f"{SUPABASE_URL}/functions/v1/notifications",
                headers=headers,
                json=payload
            )
            
            if response.status_code != 200:
                current_app.logger.error(f"Event notification sending failed: {response.text}")
                return jsonify({'error': f"Event notification sending failed: {response.text}"}), response.status_code
            
            result = response.json()
            
            # Log notification to database
            try:
                from db import NotificationLog
                session = get_db_session()
                
                log_entry = NotificationLog(
                    notification_type='event',
                    recipients=json.dumps(recipients),
                    subject=subject,
                    source_id=event_id,
                    content=content,
                    status=result.get('status', 'processed'),
                    created_by=get_current_user().id if get_current_user() else None,
                    metadata=json.dumps({'event_id': event_id, 'notify_all': notify_all})
                )
                session.add(log_entry)
                session.commit()
            except Exception as e:
                current_app.logger.warning(f"Error logging event notification: {str(e)}")
            
            return jsonify(result)
                
        except Exception as e:
            current_app.logger.error(f"Error calling event notification function: {str(e)}")
            return jsonify({'error': str(e)}), 500
        
    except Exception as e:
        current_app.logger.error(f"Error processing event notification: {str(e)}")
        return jsonify({'error': str(e)}), 500

@notification_bp.route('/ticket', methods=['POST'])
@admin_required
def send_ticket_notification():
    """
    Send a ticket update notification to the ticket owner
    """
    try:
        data = request.json
        
        if not data or 'ticket_id' not in data:
            return jsonify({'error': 'Missing required fields'}), 400
            
        ticket_id = data.get('ticket_id')
        subject = data.get('subject')
        content = data.get('content')
        
        # Get ticket details and owner
        try:
            from db import Ticket, User
            session = get_db_session()
            
            ticket = session.query(Ticket).filter(Ticket.id == ticket_id).first()
            
            if not ticket:
                return jsonify({'error': 'Ticket not found'}), 404
                
            user = session.query(User).filter(User.id == ticket.created_by).first()
            
            if not user or not user.email:
                return jsonify({'error': 'Ticket owner has no email address'}), 400
                
            recipients = [user.email]
            
            # Auto-generate subject if not provided
            if not subject:
                subject = f"Update on your ticket: {ticket.title}"
                
            # Auto-generate content if not provided
            if not content:
                status_text = {
                    'new': 'received and is being reviewed',
                    'in_progress': 'now being worked on',
                    'on_hold': 'currently on hold',
                    'resolved': 'now resolved',
                    'closed': 'now closed'
                }.get(ticket.status, ticket.status)
                
                content = f"Your ticket '{ticket.title}' is {status_text}."
                if ticket.assigned_to:
                    assigned_user = session.query(User).filter(User.id == ticket.assigned_to).first()
                    if assigned_user:
                        content += f" It has been assigned to {assigned_user.full_name}."
                
        except Exception as e:
            current_app.logger.error(f"Error fetching ticket details: {str(e)}")
            return jsonify({'error': f"Error fetching ticket details: {str(e)}"}), 500
        
        # Construct payload for edge function
        payload = {
            'type': 'ticket',
            'recipients': recipients,
            'subject': subject,
            'content': content,
            'source_id': ticket_id,
            'metadata': {
                'ticket_id': ticket_id,
                'ticket_status': ticket.status,
                'sent_by': get_current_user().id if get_current_user() else None
            }
        }
        
        # Call the send-notification edge function
        try:
            headers = {
                "apikey": SUPABASE_SERVICE_KEY,
                "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                f"{SUPABASE_URL}/functions/v1/notifications",
                headers=headers,
                json=payload
            )
            
            if response.status_code != 200:
                current_app.logger.error(f"Ticket notification sending failed: {response.text}")
                return jsonify({'error': f"Ticket notification sending failed: {response.text}"}), response.status_code
            
            result = response.json()
            
            # Log notification to database
            try:
                from db import NotificationLog
                session = get_db_session()
                
                log_entry = NotificationLog(
                    notification_type='ticket',
                    recipients=json.dumps(recipients),
                    subject=subject,
                    source_id=ticket_id,
                    content=content,
                    status=result.get('status', 'processed'),
                    created_by=get_current_user().id if get_current_user() else None,
                    metadata=json.dumps({'ticket_id': ticket_id, 'ticket_status': ticket.status})
                )
                session.add(log_entry)
                session.commit()
            except Exception as e:
                current_app.logger.warning(f"Error logging ticket notification: {str(e)}")
            
            return jsonify(result)
                
        except Exception as e:
            current_app.logger.error(f"Error calling ticket notification function: {str(e)}")
            return jsonify({'error': str(e)}), 500
        
    except Exception as e:
        current_app.logger.error(f"Error processing ticket notification: {str(e)}")
        return jsonify({'error': str(e)}), 500

@notification_bp.route('/history', methods=['GET'])
@admin_required
def get_notification_history():
    """
    Get notification history with optional filtering
    """
    try:
        notification_type = request.args.get('type')
        source_id = request.args.get('source_id')
        status = request.args.get('status')
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        
        # Query notification logs
        from db import NotificationLog
        session = get_db_session()
        query = session.query(NotificationLog)
        
        # Apply filters if provided
        if notification_type:
            query = query.filter(NotificationLog.notification_type == notification_type)
            
        if source_id:
            query = query.filter(NotificationLog.source_id == source_id)
            
        if status:
            query = query.filter(NotificationLog.status == status)
            
        # Get total count
        total_count = query.count()
        
        # Apply pagination
        logs = query.order_by(NotificationLog.created_at.desc()).offset(offset).limit(limit).all()
        
        # Format response
        result = []
        for log in logs:
            result.append({
                'id': log.id,
                'notification_type': log.notification_type,
                'recipients': json.loads(log.recipients) if log.recipients else [],
                'subject': log.subject,
                'content': log.content,
                'source_id': log.source_id,
                'status': log.status,
                'created_at': log.created_at.isoformat() if log.created_at else None,
                'created_by': log.created_by,
                'metadata': json.loads(log.metadata) if log.metadata else {}
            })
            
        return jsonify({
            'notifications': result,
            'total': total_count,
            'limit': limit,
            'offset': offset
        })
        
    except Exception as e:
        current_app.logger.error(f"Error fetching notification history: {str(e)}")
        return jsonify({'error': str(e)}), 500
