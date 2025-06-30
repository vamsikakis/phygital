#!/usr/bin/env python3
"""
Test Firefly III Setup and Integration
This script verifies that Firefly III is properly configured and accessible
"""

import requests
import os
import sys
from datetime import datetime

def test_docker_firefly():
    """Test if Firefly III is running in Docker"""
    print("🐳 Testing Firefly III Docker Container")
    print("=" * 50)
    
    try:
        # Test if Firefly III is accessible
        response = requests.get('http://localhost:8080', timeout=5)
        if response.status_code == 200:
            print("✅ Firefly III is running at http://localhost:8080")
            return True
        else:
            print(f"❌ Firefly III returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Firefly III at http://localhost:8080")
        print("   Make sure Firefly III is running:")
        print("   docker ps | grep firefly-iii")
        return False
    except Exception as e:
        print(f"❌ Error connecting to Firefly III: {e}")
        return False

def test_api_token():
    """Test if API token is configured and working"""
    print("\n🔑 Testing API Token Configuration")
    print("=" * 50)
    
    # Check environment variables
    base_url = os.getenv('FIREFLY_BASE_URL', 'http://localhost:8080')
    api_token = os.getenv('FIREFLY_API_TOKEN')
    
    if not api_token or api_token == 'your_firefly_personal_access_token_here':
        print("❌ FIREFLY_API_TOKEN not configured in environment")
        print("   Please set up your Personal Access Token:")
        print("   1. Go to http://localhost:8080")
        print("   2. Login and go to Profile → OAuth → Personal Access Tokens")
        print("   3. Create new token named 'Facility Manager Integration'")
        print("   4. Add to .env file: FIREFLY_API_TOKEN=your_very_long_token")
        return False
    
    print(f"✅ Base URL configured: {base_url}")
    print(f"✅ API Token configured: {api_token[:20]}...{api_token[-10:]}")
    
    # Test API connection
    try:
        headers = {
            'Authorization': f'Bearer {api_token}',
            'Accept': 'application/vnd.api+json'
        }
        
        response = requests.get(f'{base_url}/api/v1/about', headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            version = data.get('data', {}).get('version', 'Unknown')
            api_version = data.get('data', {}).get('api_version', 'Unknown')
            print(f"✅ API connection successful!")
            print(f"   Firefly III Version: {version}")
            print(f"   API Version: {api_version}")
            return True
        else:
            print(f"❌ API returned status code: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        return False

def test_facility_manager_integration():
    """Test if the facility manager can connect to Firefly III"""
    print("\n🏢 Testing Facility Manager Integration")
    print("=" * 50)
    
    try:
        # Test the facility manager's Firefly III endpoint
        response = requests.get('http://localhost:5000/api/firefly/test', timeout=10)
        data = response.json()
        
        if data.get('success'):
            print("✅ Facility Manager → Firefly III integration working!")
            print(f"   Message: {data.get('message')}")
            print(f"   Version: {data.get('version', 'Unknown')}")
            return True
        else:
            print("❌ Facility Manager integration failed")
            print(f"   Error: {data.get('error')}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Facility Manager at http://localhost:5000")
        print("   Make sure the backend is running: python app.py")
        return False
    except Exception as e:
        print(f"❌ Error testing integration: {e}")
        return False

def test_sample_data():
    """Test if we can retrieve sample financial data"""
    print("\n📊 Testing Financial Data Retrieval")
    print("=" * 50)
    
    try:
        # Test accounts endpoint
        response = requests.get('http://localhost:5000/api/firefly/accounts', timeout=10)
        data = response.json()
        
        if data.get('success'):
            accounts = data.get('accounts', [])
            print(f"✅ Retrieved {len(accounts)} accounts")
            
            if accounts:
                print("   Sample accounts:")
                for account in accounts[:3]:  # Show first 3
                    name = account.get('name', 'Unknown')
                    balance = account.get('current_balance', '0')
                    account_type = account.get('type', 'Unknown')
                    print(f"   - {name} ({account_type}): {balance}")
            else:
                print("   ℹ️  No accounts found - create some in Firefly III")
            
            return True
        else:
            print("❌ Failed to retrieve accounts")
            print(f"   Error: {data.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error retrieving financial data: {e}")
        return False

def main():
    """Run all tests"""
    print("🏦 Firefly III Setup Verification")
    print("=" * 60)
    print(f"Test run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tests = [
        ("Docker Container", test_docker_firefly),
        ("API Token", test_api_token),
        ("Integration", test_facility_manager_integration),
        ("Sample Data", test_sample_data)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All tests passed! Your Firefly III integration is working perfectly!")
        print("   You can now use the Financial Dashboard in your facility manager.")
    else:
        print(f"\n⚠️  {len(results) - passed} test(s) failed. Please check the setup instructions above.")
        print("   Refer to the setup guide: FIREFLY_SETUP.md")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
