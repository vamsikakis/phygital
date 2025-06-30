"""
ClickUp API Integration Service
Handles task creation, updates, and management through ClickUp API
"""

import os
import requests
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ClickUpService:
    """Service for integrating with ClickUp API"""
    
    def __init__(self):
        """Initialize ClickUp service with API credentials"""
        self.api_token = os.getenv('CLICKUP_API_TOKEN')
        self.team_id = os.getenv('CLICKUP_TEAM_ID')
        self.space_id = os.getenv('CLICKUP_SPACE_ID')
        self.folder_id = os.getenv('CLICKUP_FOLDER_ID')
        self.list_id = os.getenv('CLICKUP_LIST_ID')
        self.api_url = os.getenv('CLICKUP_API_URL', 'https://api.clickup.com/api/v2')
        
        if not self.api_token:
            raise ValueError("ClickUp API token not found in environment variables")
        
        self.headers = {
            'Authorization': self.api_token,
            'Content-Type': 'application/json'
        }
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make HTTP request to ClickUp API"""
        url = f"{self.api_url}/{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=self.headers)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=self.headers, json=data)
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=self.headers, json=data)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=self.headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json() if response.content else {}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"ClickUp API request failed: {e}")
            raise Exception(f"ClickUp API error: {str(e)}")
    
    def get_teams(self) -> List[Dict[str, Any]]:
        """Get all teams for the authenticated user"""
        try:
            response = self._make_request('GET', 'team')
            return response.get('teams', [])
        except Exception as e:
            logger.error(f"Failed to get teams: {e}")
            return []
    
    def get_spaces(self, team_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all spaces for a team"""
        team_id = team_id or self.team_id
        if not team_id:
            raise ValueError("Team ID is required")
        
        try:
            response = self._make_request('GET', f'team/{team_id}/space')
            return response.get('spaces', [])
        except Exception as e:
            logger.error(f"Failed to get spaces: {e}")
            return []
    
    def get_lists(self, space_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all lists in a space"""
        space_id = space_id or self.space_id
        if not space_id:
            raise ValueError("Space ID is required")
        
        try:
            response = self._make_request('GET', f'space/{space_id}/list')
            return response.get('lists', [])
        except Exception as e:
            logger.error(f"Failed to get lists: {e}")
            return []

    def get_team_members(self, team_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all team members for task assignment"""
        team_id = team_id or self.team_id
        if not team_id:
            raise ValueError("Team ID is required")

        try:
            # Try the correct ClickUp API endpoint for team members
            response = self._make_request('GET', f'team/{team_id}')
            team_data = response.get('team', {})
            members = team_data.get('members', [])

            # If no members found, try alternative endpoint
            if not members:
                try:
                    response = self._make_request('GET', f'team')
                    teams = response.get('teams', [])
                    for team in teams:
                        if team.get('id') == team_id:
                            members = team.get('members', [])
                            break
                except:
                    pass

            # Format members for frontend use
            formatted_members = []
            for member in members:
                # Handle different response formats
                user = member.get('user', member)
                formatted_members.append({
                    'id': user.get('id'),
                    'username': user.get('username'),
                    'email': user.get('email'),
                    'color': user.get('color'),
                    'profilePicture': user.get('profilePicture'),
                    'initials': user.get('initials'),
                    'role': member.get('role', 'member')
                })

            return formatted_members
        except Exception as e:
            logger.error(f"Failed to get team members: {e}")
            return []

    def create_task(self, task_data: Dict[str, Any], list_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new task in ClickUp
        
        Args:
            task_data: Task information including name, description, priority, etc.
            list_id: ClickUp list ID (optional, uses default if not provided)
            
        Returns:
            Created task information
        """
        list_id = list_id or self.list_id
        if not list_id:
            raise ValueError("List ID is required")
        
        # Prepare task payload
        payload = {
            'name': task_data.get('name', 'Untitled Task'),
            'description': task_data.get('description', ''),
            'priority': self._map_priority(task_data.get('priority', 'normal')),
            'status': task_data.get('status', 'to do'),
            'assignees': task_data.get('assignees', []),
            'tags': task_data.get('tags', []),
            'due_date': self._format_date(task_data.get('due_date')),
            'start_date': self._format_date(task_data.get('start_date')),
            'time_estimate': task_data.get('time_estimate'),  # in milliseconds
            'custom_fields': task_data.get('custom_fields', [])
        }
        
        # Remove None values
        payload = {k: v for k, v in payload.items() if v is not None}
        
        try:
            response = self._make_request('POST', f'list/{list_id}/task', payload)
            logger.info(f"Created ClickUp task: {response.get('id')}")
            return response
        except Exception as e:
            logger.error(f"Failed to create task: {e}")
            raise
    
    def update_task(self, task_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing task in ClickUp
        
        Args:
            task_id: ClickUp task ID
            task_data: Updated task information
            
        Returns:
            Updated task information
        """
        # Prepare update payload
        payload = {}
        
        if 'name' in task_data:
            payload['name'] = task_data['name']
        if 'description' in task_data:
            payload['description'] = task_data['description']
        if 'priority' in task_data:
            payload['priority'] = self._map_priority(task_data['priority'])
        if 'status' in task_data:
            payload['status'] = task_data['status']
        if 'assignees' in task_data:
            payload['assignees'] = task_data['assignees']
        if 'due_date' in task_data:
            payload['due_date'] = self._format_date(task_data['due_date'])
        if 'time_estimate' in task_data:
            payload['time_estimate'] = task_data['time_estimate']
        
        try:
            response = self._make_request('PUT', f'task/{task_id}', payload)
            logger.info(f"Updated ClickUp task: {task_id}")
            return response
        except Exception as e:
            logger.error(f"Failed to update task {task_id}: {e}")
            raise
    
    def get_task(self, task_id: str) -> Dict[str, Any]:
        """Get a specific task by ID"""
        try:
            response = self._make_request('GET', f'task/{task_id}')
            return response
        except Exception as e:
            logger.error(f"Failed to get task {task_id}: {e}")
            raise
    
    def get_tasks(self, list_id: Optional[str] = None, filters: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Get tasks from a list with optional filters
        
        Args:
            list_id: ClickUp list ID (optional, uses default if not provided)
            filters: Optional filters like status, assignee, etc.
            
        Returns:
            List of tasks
        """
        list_id = list_id or self.list_id
        if not list_id:
            raise ValueError("List ID is required")
        
        # Build query parameters
        params = {}
        if filters:
            if 'status' in filters:
                params['statuses[]'] = filters['status']
            if 'assignee' in filters:
                params['assignees[]'] = filters['assignee']
            if 'priority' in filters:
                params['priority'] = filters['priority']
            if 'due_date_gt' in filters:
                params['due_date_gt'] = self._format_date(filters['due_date_gt'])
            if 'due_date_lt' in filters:
                params['due_date_lt'] = self._format_date(filters['due_date_lt'])
        
        try:
            endpoint = f'list/{list_id}/task'
            if params:
                query_string = '&'.join([f'{k}={v}' for k, v in params.items()])
                endpoint += f'?{query_string}'
            
            response = self._make_request('GET', endpoint)
            return response.get('tasks', [])
        except Exception as e:
            logger.error(f"Failed to get tasks: {e}")
            return []
    
    def delete_task(self, task_id: str) -> bool:
        """Delete a task"""
        try:
            self._make_request('DELETE', f'task/{task_id}')
            logger.info(f"Deleted ClickUp task: {task_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete task {task_id}: {e}")
            return False
    
    def add_comment(self, task_id: str, comment_text: str) -> Dict[str, Any]:
        """Add a comment to a task"""
        payload = {
            'comment_text': comment_text,
            'notify_all': True
        }
        
        try:
            response = self._make_request('POST', f'task/{task_id}/comment', payload)
            logger.info(f"Added comment to task {task_id}")
            return response
        except Exception as e:
            logger.error(f"Failed to add comment to task {task_id}: {e}")
            raise
    
    def _map_priority(self, priority: str) -> int:
        """Map priority string to ClickUp priority number"""
        priority_map = {
            'urgent': 1,
            'high': 2,
            'normal': 3,
            'low': 4
        }
        return priority_map.get(priority.lower(), 3)
    
    def _format_date(self, date_input: Any) -> Optional[int]:
        """Format date to ClickUp timestamp (milliseconds since epoch)"""
        if not date_input:
            return None
        
        if isinstance(date_input, str):
            try:
                dt = datetime.fromisoformat(date_input.replace('Z', '+00:00'))
            except ValueError:
                try:
                    dt = datetime.strptime(date_input, '%Y-%m-%d')
                    dt = dt.replace(tzinfo=timezone.utc)
                except ValueError:
                    logger.warning(f"Invalid date format: {date_input}")
                    return None
        elif isinstance(date_input, datetime):
            dt = date_input
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
        else:
            logger.warning(f"Unsupported date type: {type(date_input)}")
            return None
        
        return int(dt.timestamp() * 1000)

# Create a global instance
clickup_service = ClickUpService()
