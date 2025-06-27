#!/usr/bin/env python3
"""
Minimal Integration Test
Basic test to verify core AI functionality is working
"""

import os
import sys
import time

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import config
import openai

def test_minimal_openai():
    """Minimal OpenAI test"""
    print("🤖 Testing OpenAI...")
    
    try:
        client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=10
        )
        
        print("✅ OpenAI working")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI failed: {e}")
        return False

def test_minimal_embedding():
    """Minimal embedding test"""
    print("🔍 Testing Embeddings...")
    
    try:
        client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
        
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input="test"
        )
        
        print("✅ Embeddings working")
        return True
        
    except Exception as e:
        print(f"❌ Embeddings failed: {e}")
        return False

def main():
    """Run minimal tests"""
    print("🚀 Minimal Integration Test")
    print("=" * 30)
    
    tests = [test_minimal_openai, test_minimal_embedding]
    passed = sum(test() for test in tests)
    
    print(f"\n📊 {passed}/{len(tests)} tests passed")
    return passed == len(tests)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
