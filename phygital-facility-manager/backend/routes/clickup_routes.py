"""
ClickUp API Routes
Provides REST endpoints for ClickUp task management integration
"""

from flask import Blueprint, request, jsonify
from services.clickup_service import clickup_service
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
clickup_bp = Blueprint('clickup', __name__)

@clickup_bp.route('/teams', methods=['GET'])
def get_teams():
    """Get all teams for the authenticated user"""
    try:
        teams = clickup_service.get_teams()
        return jsonify({
            'success': True,
            'teams': teams
        }), 200
    except Exception as e:
        logger.error(f"Failed to get teams: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@clickup_bp.route('/spaces', methods=['GET'])
def get_spaces():
    """Get all spaces for a team"""
    try:
        team_id = request.args.get('team_id')
        spaces = clickup_service.get_spaces(team_id)
        return jsonify({
            'success': True,
            'spaces': spaces
        }), 200
    except Exception as e:
        logger.error(f"Failed to get spaces: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@clickup_bp.route('/lists', methods=['GET'])
def get_lists():
    """Get all lists in a space"""
    try:
        space_id = request.args.get('space_id')
        lists = clickup_service.get_lists(space_id)
        return jsonify({
            'success': True,
            'lists': lists
        }), 200
    except Exception as e:
        logger.error(f"Failed to get lists: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@clickup_bp.route('/team/members', methods=['GET'])
def get_team_members():
    """Get all team members for task assignment"""
    try:
        team_id = request.args.get('team_id')
        members = clickup_service.get_team_members(team_id)
        return jsonify({
            'success': True,
            'members': members
        }), 200
    except Exception as e:
        logger.error(f"Failed to get team members: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@clickup_bp.route('/tasks', methods=['GET'])
def get_tasks():
    """Get tasks from a list with optional filters"""
    try:
        list_id = request.args.get('list_id')
        
        # Build filters from query parameters
        filters = {}
        if request.args.get('status'):
            filters['status'] = request.args.get('status')
        if request.args.get('assignee'):
            filters['assignee'] = request.args.get('assignee')
        if request.args.get('priority'):
            filters['priority'] = request.args.get('priority')
        if request.args.get('due_date_gt'):
            filters['due_date_gt'] = request.args.get('due_date_gt')
        if request.args.get('due_date_lt'):
            filters['due_date_lt'] = request.args.get('due_date_lt')
        
        tasks = clickup_service.get_tasks(list_id, filters if filters else None)
        return jsonify({
            'success': True,
            'tasks': tasks,
            'count': len(tasks)
        }), 200
    except Exception as e:
        logger.error(f"Failed to get tasks: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@clickup_bp.route('/tasks', methods=['POST'])
def create_task():
    """Create a new task in ClickUp"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body is required'
            }), 400
        
        if not data.get('name'):
            return jsonify({
                'success': False,
                'error': 'Task name is required'
            }), 400
        
        list_id = data.get('list_id')
        task = clickup_service.create_task(data, list_id)
        
        return jsonify({
            'success': True,
            'task': task,
            'message': 'Task created successfully'
        }), 201
    except Exception as e:
        logger.error(f"Failed to create task: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@clickup_bp.route('/tasks/<task_id>', methods=['GET'])
def get_task(task_id):
    """Get a specific task by ID"""
    try:
        task = clickup_service.get_task(task_id)
        return jsonify({
            'success': True,
            'task': task
        }), 200
    except Exception as e:
        logger.error(f"Failed to get task {task_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@clickup_bp.route('/tasks/<task_id>', methods=['PUT'])
def update_task(task_id):
    """Update an existing task"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body is required'
            }), 400
        
        task = clickup_service.update_task(task_id, data)
        return jsonify({
            'success': True,
            'task': task,
            'message': 'Task updated successfully'
        }), 200
    except Exception as e:
        logger.error(f"Failed to update task {task_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@clickup_bp.route('/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete a task"""
    try:
        success = clickup_service.delete_task(task_id)
        if success:
            return jsonify({
                'success': True,
                'message': 'Task deleted successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to delete task'
            }), 500
    except Exception as e:
        logger.error(f"Failed to delete task {task_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@clickup_bp.route('/tasks/<task_id>/comments', methods=['POST'])
def add_comment(task_id):
    """Add a comment to a task"""
    try:
        data = request.get_json()
        if not data or not data.get('comment_text'):
            return jsonify({
                'success': False,
                'error': 'Comment text is required'
            }), 400
        
        comment = clickup_service.add_comment(task_id, data['comment_text'])
        return jsonify({
            'success': True,
            'comment': comment,
            'message': 'Comment added successfully'
        }), 201
    except Exception as e:
        logger.error(f"Failed to add comment to task {task_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@clickup_bp.route('/config', methods=['GET'])
def get_config():
    """Get ClickUp configuration information"""
    try:
        config = {
            'team_id': clickup_service.team_id,
            'space_id': clickup_service.space_id,
            'folder_id': clickup_service.folder_id,
            'list_id': clickup_service.list_id,
            'api_configured': bool(clickup_service.api_token)
        }
        return jsonify({
            'success': True,
            'config': config
        }), 200
    except Exception as e:
        logger.error(f"Failed to get config: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@clickup_bp.route('/test', methods=['GET'])
def test_connection():
    """Test ClickUp API connection"""
    try:
        teams = clickup_service.get_teams()
        return jsonify({
            'success': True,
            'message': 'ClickUp API connection successful',
            'teams_count': len(teams)
        }), 200
    except Exception as e:
        logger.error(f"ClickUp API test failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'ClickUp API connection failed'
        }), 500

# Facility Management specific endpoints
@clickup_bp.route('/facility/maintenance-request', methods=['POST'])
def create_maintenance_request():
    """Create a maintenance request task in ClickUp"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body is required'
            }), 400
        
        # Prepare maintenance request task
        task_data = {
            'name': f"Maintenance Request: {data.get('title', 'Untitled')}",
            'description': f"""
**Maintenance Request Details:**

**Apartment:** {data.get('apartment', 'Not specified')}
**Category:** {data.get('category', 'General')}
**Priority:** {data.get('priority', 'Normal')}
**Description:** {data.get('description', 'No description provided')}

**Contact Information:**
- **Name:** {data.get('contact_name', 'Not provided')}
- **Phone:** {data.get('contact_phone', 'Not provided')}
- **Email:** {data.get('contact_email', 'Not provided')}

**Requested Date:** {data.get('requested_date', 'ASAP')}
            """.strip(),
            'priority': data.get('priority', 'normal').lower(),
            'tags': ['maintenance', 'facility-management', data.get('category', 'general').lower()],
            'due_date': data.get('due_date'),
            'custom_fields': [
                {
                    'id': 'apartment_number',
                    'value': data.get('apartment', '')
                },
                {
                    'id': 'category',
                    'value': data.get('category', 'General')
                }
            ]
        }
        
        task = clickup_service.create_task(task_data)
        
        return jsonify({
            'success': True,
            'task': task,
            'message': 'Maintenance request created successfully',
            'task_url': f"https://app.clickup.com/t/{task.get('id')}"
        }), 201
    except Exception as e:
        logger.error(f"Failed to create maintenance request: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
