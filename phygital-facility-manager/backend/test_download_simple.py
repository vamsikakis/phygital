#!/usr/bin/env python3
"""Simple test for document download"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_openai_api():
    """Test OpenAI API directly"""
    try:
        from openai import OpenAI
        
        api_key = os.getenv("OPENAI_API_KEY")
        print(f"API Key loaded: {'Yes' if api_key else 'No'}")
        print(f"API Key starts with: {api_key[:10] if api_key else 'None'}...")
        
        if not api_key:
            print("❌ No OpenAI API key found")
            return
        
        client = OpenAI(api_key=api_key)
        
        # Test with a known file ID
        file_id = "file-SS3qm7viG6KZNMbD62JcEK"
        
        print(f"Testing file download for: {file_id}")
        
        # Get file info
        file_info = client.files.retrieve(file_id)
        print(f"File info: {file_info.filename}, {file_info.bytes} bytes")
        
        # Download content
        file_content = client.files.content(file_id)
        print(f"Content type: {type(file_content)}")
        print(f"Content length: {len(file_content.content)} bytes")
        
        # Save to test file
        with open(f"test_{file_info.filename}", "wb") as f:
            f.write(file_content.content)
        
        print(f"✅ Successfully downloaded {file_info.filename}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🔍 Simple OpenAI Download Test")
    print("=" * 40)
    test_openai_api()
