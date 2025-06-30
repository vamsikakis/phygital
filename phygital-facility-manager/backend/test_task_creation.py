#!/usr/bin/env python3
"""Test ClickUp task creation with real credentials"""

import requests
import json
from datetime import datetime

def test_create_task():
    """Test creating a task in ClickUp"""
    print("🚀 Testing ClickUp Task Creation")
    print("=" * 40)
    
    url = "http://localhost:5000/api/clickup/tasks"
    
    task_data = {
        "name": f"Test Task - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "description": "This is a test task created from the Gopalan Atlantis facility management system",
        "priority": "normal",
        "status": "to do",
        "tags": ["test", "facility-management", "gopalan-atlantis"]
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
            print("✅ Task created successfully!")
            task_id = result.get('task', {}).get('id')
            task_url = result.get('task', {}).get('url')
            print(f"Task ID: {task_id}")
            print(f"Task URL: {task_url}")
            return task_id
        else:
            print("❌ Task creation failed")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_maintenance_request():
    """Test creating a maintenance request"""
    print("\n🔧 Testing Maintenance Request Creation")
    print("=" * 40)
    
    url = "http://localhost:5000/api/clickup/facility/maintenance-request"
    
    maintenance_data = {
        "title": "Pool Cleaning Required",
        "description": "The swimming pool needs cleaning and chemical balancing",
        "apartment": "A-101",
        "category": "Maintenance",
        "priority": "high",
        "contact_name": "John Doe",
        "contact_phone": "+91-9876543210",
        "contact_email": "john.doe@gopalanatlantis.com",
        "requested_date": datetime.now().strftime('%Y-%m-%d')
    }
    
    try:
        response = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            json=maintenance_data
        )
        
        print(f"Status Code: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        
        if response.status_code == 201 and result.get('success'):
            print("✅ Maintenance request created successfully!")
            task_url = result.get('task_url')
            print(f"Task URL: {task_url}")
        else:
            print("❌ Maintenance request creation failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🎯 ClickUp Task Creation Test")
    print("=" * 50)
    
    # Test basic task creation
    task_id = test_create_task()
    
    # Test maintenance request
    test_maintenance_request()
    
    print("\n" + "=" * 50)
    print("🎉 Test Complete!")
