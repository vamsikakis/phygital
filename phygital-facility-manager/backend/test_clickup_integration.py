#!/usr/bin/env python3
"""
Test ClickUp Integration
Tests the ClickUp API integration and task management functionality
"""

import requests
import json
from datetime import datetime

def test_clickup_endpoints():
    """Test all ClickUp API endpoints"""
    base_url = "http://localhost:5000/api/clickup"
    
    print("🚀 Testing ClickUp Integration")
    print("=" * 50)
    
    # Test 1: Configuration
    print("\n1️⃣ Testing Configuration Endpoint")
    try:
        response = requests.get(f"{base_url}/config")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            config = response.json()
            print(f"✅ Config loaded: {config}")
        else:
            print(f"❌ Config failed: {response.text}")
    except Exception as e:
        print(f"❌ Config error: {e}")
    
    # Test 2: Connection Test
    print("\n2️⃣ Testing Connection")
    try:
        response = requests.get(f"{base_url}/test")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Connection test: {result}")
        else:
            print(f"❌ Connection failed: {response.text}")
    except Exception as e:
        print(f"❌ Connection error: {e}")
    
    # Test 3: Create Task
    print("\n3️⃣ Testing Task Creation")
    try:
        task_data = {
            "name": f"Test Task - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "description": "This is a test task created by the integration test",
            "priority": "normal",
            "status": "to do",
            "tags": ["test", "integration", "facility-management"]
        }
        
        response = requests.post(
            f"{base_url}/tasks",
            headers={"Content-Type": "application/json"},
            json=task_data
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 201:
            result = response.json()
            print(f"✅ Task created: {result}")
            task_id = result.get('task', {}).get('id')
            return task_id
        else:
            print(f"❌ Task creation failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Task creation error: {e}")
        return None
    
def test_maintenance_request():
    """Test maintenance request creation"""
    print("\n4️⃣ Testing Maintenance Request")
    try:
        maintenance_data = {
            "title": "Test Pool Maintenance",
            "description": "Test maintenance request for pool cleaning",
            "apartment": "A-101",
            "category": "Maintenance",
            "priority": "high",
            "contact_name": "Test User",
            "contact_phone": "+91-9876543210",
            "contact_email": "test@example.com",
            "requested_date": datetime.now().strftime('%Y-%m-%d')
        }
        
        response = requests.post(
            "http://localhost:5000/api/clickup/facility/maintenance-request",
            headers={"Content-Type": "application/json"},
            json=maintenance_data
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 201:
            result = response.json()
            print(f"✅ Maintenance request created: {result}")
        else:
            print(f"❌ Maintenance request failed: {response.text}")
    except Exception as e:
        print(f"❌ Maintenance request error: {e}")

def test_task_operations(task_id):
    """Test task update and delete operations"""
    if not task_id:
        print("\n⏭️ Skipping task operations (no task ID)")
        return
    
    base_url = "http://localhost:5000/api/clickup"
    
    # Test 4: Get Task
    print(f"\n5️⃣ Testing Get Task ({task_id})")
    try:
        response = requests.get(f"{base_url}/tasks/{task_id}")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Task retrieved: {result.get('task', {}).get('name', 'Unknown')}")
        else:
            print(f"❌ Get task failed: {response.text}")
    except Exception as e:
        print(f"❌ Get task error: {e}")
    
    # Test 5: Update Task
    print(f"\n6️⃣ Testing Update Task ({task_id})")
    try:
        update_data = {
            "name": f"Updated Test Task - {datetime.now().strftime('%H:%M:%S')}",
            "description": "This task has been updated by the integration test",
            "status": "in progress",
            "priority": "high"
        }
        
        response = requests.put(
            f"{base_url}/tasks/{task_id}",
            headers={"Content-Type": "application/json"},
            json=update_data
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Task updated: {result}")
        else:
            print(f"❌ Update task failed: {response.text}")
    except Exception as e:
        print(f"❌ Update task error: {e}")
    
    # Test 6: Add Comment
    print(f"\n7️⃣ Testing Add Comment ({task_id})")
    try:
        comment_data = {
            "comment_text": f"Test comment added at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        }
        
        response = requests.post(
            f"{base_url}/tasks/{task_id}/comments",
            headers={"Content-Type": "application/json"},
            json=comment_data
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 201:
            result = response.json()
            print(f"✅ Comment added: {result}")
        else:
            print(f"❌ Add comment failed: {response.text}")
    except Exception as e:
        print(f"❌ Add comment error: {e}")

def test_get_tasks():
    """Test getting tasks list"""
    print("\n8️⃣ Testing Get Tasks")
    try:
        response = requests.get("http://localhost:5000/api/clickup/tasks")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Tasks retrieved: {result.get('count', 0)} tasks found")
        else:
            print(f"❌ Get tasks failed: {response.text}")
    except Exception as e:
        print(f"❌ Get tasks error: {e}")

if __name__ == "__main__":
    print("🎯 ClickUp Integration Test Suite")
    print("=" * 60)
    
    # Run basic tests
    task_id = test_clickup_endpoints()
    
    # Test maintenance request
    test_maintenance_request()
    
    # Test task operations
    test_task_operations(task_id)
    
    # Test getting tasks
    test_get_tasks()
    
    print("\n" + "=" * 60)
    print("🎉 ClickUp Integration Test Complete!")
    print("\nNote: Some tests may fail if ClickUp API credentials are not properly configured.")
    print("To configure ClickUp:")
    print("1. Get your API token from ClickUp")
    print("2. Update the .env file with your ClickUp credentials")
    print("3. Set CLICKUP_API_TOKEN, CLICKUP_TEAM_ID, CLICKUP_SPACE_ID, and CLICKUP_LIST_ID")
