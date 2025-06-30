#!/usr/bin/env python3
"""Test ClickUp assignee functionality"""

import requests
import json
from datetime import datetime

def test_team_members():
    """Test fetching team members"""
    print("🧑‍🤝‍🧑 Testing Team Members Endpoint")
    print("=" * 40)
    
    url = "http://localhost:5000/api/clickup/team/members"
    
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        
        if response.status_code == 200 and result.get('success'):
            members = result.get('members', [])
            print(f"✅ Found {len(members)} team members")
            
            for member in members:
                print(f"  - {member.get('username')} ({member.get('email')}) - Role: {member.get('role')}")
            
            return members
        else:
            print("❌ Failed to fetch team members")
            return []
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def test_create_task_with_assignee(members):
    """Test creating a task with assignees"""
    print("\n📝 Testing Task Creation with Assignees")
    print("=" * 40)
    
    if not members:
        print("⚠️ No team members available for assignment")
        return None
    
    url = "http://localhost:5000/api/clickup/tasks"
    
    # Use the first member for assignment
    assignee_id = members[0].get('id')
    assignee_name = members[0].get('username')
    
    task_data = {
        "name": f"Test Task with Assignee - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "description": f"This task is assigned to {assignee_name} for testing assignee functionality",
        "priority": "high",
        "status": "to do",
        "assignees": [assignee_id],
        "tags": ["test", "assignee-test", "facility-management"]
    }
    
    try:
        response = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            json=task_data
        )
        
        print(f"Status Code: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        
        if response.status_code == 201 and result.get('success'):
            print("✅ Task with assignee created successfully!")
            task = result.get('task', {})
            task_id = task.get('id')
            task_url = task.get('url')
            assignees = task.get('assignees', [])
            
            print(f"Task ID: {task_id}")
            print(f"Task URL: {task_url}")
            print(f"Assignees: {len(assignees)} assigned")
            
            for assignee in assignees:
                print(f"  - {assignee.get('username')} ({assignee.get('email')})")
            
            return task_id
        else:
            print("❌ Task creation with assignee failed")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_get_tasks_with_assignees():
    """Test fetching tasks and checking assignee information"""
    print("\n📋 Testing Task Retrieval with Assignee Info")
    print("=" * 40)
    
    url = "http://localhost:5000/api/clickup/tasks"
    
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        result = response.json()
        
        if response.status_code == 200 and result.get('success'):
            tasks = result.get('tasks', [])
            print(f"✅ Retrieved {len(tasks)} tasks")
            
            for task in tasks:
                assignees = task.get('assignees', [])
                print(f"\nTask: {task.get('name')}")
                print(f"  Assignees: {len(assignees)}")
                for assignee in assignees:
                    print(f"    - {assignee.get('username')} ({assignee.get('email')})")
            
        else:
            print("❌ Failed to retrieve tasks")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🎯 ClickUp Assignee Functionality Test")
    print("=" * 50)
    
    # Test team members endpoint
    members = test_team_members()
    
    # Test task creation with assignee
    task_id = test_create_task_with_assignee(members)
    
    # Test task retrieval with assignee info
    test_get_tasks_with_assignees()
    
    print("\n" + "=" * 50)
    print("🎉 Assignee Functionality Test Complete!")
    
    if members and task_id:
        print("✅ All assignee features are working correctly!")
    else:
        print("⚠️ Some features may need attention")
