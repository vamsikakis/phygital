#!/usr/bin/env python3
"""
Test script to verify all routes are properly registered
Run this to diagnose route registration issues
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        from flask import Flask
        print("✅ Flask imported successfully")
    except ImportError as e:
        print(f"❌ Flask import failed: {e}")
        return False
    
    try:
        from services.openai_assistant_service import openai_assistant_service
        print("✅ OpenAI Assistant Service imported successfully")
    except ImportError as e:
        print(f"❌ OpenAI Assistant Service import failed: {e}")
        return False
    
    try:
        from routes.assistant_routes import assistant_bp
        print("✅ Assistant routes imported successfully")
    except ImportError as e:
        print(f"❌ Assistant routes import failed: {e}")
        return False
    
    try:
        from config import config
        print("✅ Config imported successfully")
    except ImportError as e:
        print(f"❌ Config import failed: {e}")
        return False
    
    return True

def test_environment_variables():
    """Test if required environment variables are set"""
    print("\n🔍 Testing environment variables...")
    
    required_vars = [
        'OPENAI_API_KEY',
        'DATABASE_URL',
        'SECRET_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
            print(f"❌ {var} is not set")
        else:
            print(f"✅ {var} is set")
    
    return len(missing_vars) == 0

def test_app_creation():
    """Test if the Flask app can be created and routes registered"""
    print("\n🔍 Testing Flask app creation...")
    
    try:
        from app import app
        print("✅ Flask app created successfully")
        
        # List all registered routes
        print("\n📋 Registered routes:")
        for rule in app.url_map.iter_rules():
            print(f"  {rule.methods} {rule.rule}")
        
        # Check if assistant routes are registered
        assistant_routes = [rule for rule in app.url_map.iter_rules() if '/api/assistant' in rule.rule]
        if assistant_routes:
            print(f"\n✅ Found {len(assistant_routes)} assistant routes:")
            for route in assistant_routes:
                print(f"  {route.methods} {route.rule}")
        else:
            print("\n❌ No assistant routes found!")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Flask app creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_openai_connection():
    """Test OpenAI API connection"""
    print("\n🔍 Testing OpenAI connection...")
    
    try:
        import openai
        client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Test a simple API call
        response = client.models.list()
        print("✅ OpenAI API connection successful")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI API connection failed: {e}")
        return False

def test_database_connection():
    """Test database connection"""
    print("\n🔍 Testing database connection...")
    
    try:
        import psycopg2
        from urllib.parse import urlparse
        
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            print("❌ DATABASE_URL not set")
            return False
        
        # Parse the database URL
        parsed = urlparse(database_url)
        
        # Test connection
        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port,
            database=parsed.path[1:],  # Remove leading slash
            user=parsed.username,
            password=parsed.password,
            sslmode='require'
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ Database connection successful: {version[0]}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting diagnostic tests for Phygital Facility Manager Backend")
    print("=" * 70)
    
    tests = [
        ("Import Tests", test_imports),
        ("Environment Variables", test_environment_variables),
        ("Flask App Creation", test_app_creation),
        ("OpenAI Connection", test_openai_connection),
        ("Database Connection", test_database_connection)
    ]
    
    results = {}
    for test_name, test_func in tests:
        print(f"\n{'=' * 20} {test_name} {'=' * 20}")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    
    passed = 0
    total = len(tests)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:.<50} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your backend should work correctly.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please fix the issues above.")
        
        # Provide specific guidance
        if not results.get("Import Tests", True):
            print("\n💡 Import issues suggest missing dependencies. Run: pip install -r requirements.txt")
        
        if not results.get("Environment Variables", True):
            print("\n💡 Environment variable issues. Check your .env file.")
        
        if not results.get("Flask App Creation", True):
            print("\n💡 Flask app creation failed. Check for syntax errors in app.py")
        
        if not results.get("OpenAI Connection", True):
            print("\n💡 OpenAI connection failed. Check your API key.")
        
        if not results.get("Database Connection", True):
            print("\n💡 Database connection failed. Check your DATABASE_URL.")

if __name__ == "__main__":
    main()
