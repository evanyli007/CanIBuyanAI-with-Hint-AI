#!/usr/bin/env python3
"""
Test script to debug OpenAI API integration.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from hint_ai import HintAI
import requests

def test_openai_api():
    """Test the OpenAI API integration step by step."""
    
    print("🔍 DEBUGGING OPENAI API INTEGRATION")
    print("=" * 50)
    
    # Check if API key is set
    api_key = os.getenv("OPENAI_API_KEY")
    print(f"1. API Key Status: {'✅ Set' if api_key else '❌ Not set'}")
    if api_key:
        print(f"   Key preview: {api_key[:10]}...{api_key[-4:] if len(api_key) > 14 else ''}")
    print()
    
    # Test HintAI initialization
    print("2. Testing HintAI initialization...")
    hint_ai = HintAI()
    print(f"   API Key available: {'✅ Yes' if hint_ai.api_key else '❌ No'}")
    print(f"   Model: {hint_ai.model}")
    print(f"   Base URL: {hint_ai.base_url}")
    print()
    
    # Test a simple API call manually
    if hint_ai.api_key:
        print("3. Testing direct API call...")
        try:
            headers = {
                "Authorization": f"Bearer {hint_ai.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Say 'API test successful' if you can read this."}
                ],
                "max_tokens": 20,
                "temperature": 0.1
            }
            
            print("   Making API request...")
            response = requests.post("https://api.openai.com/v1/chat/completions", 
                                   headers=headers, json=data, timeout=30)
            
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"].strip()
                print(f"   ✅ API Response: {content}")
            else:
                print(f"   ❌ API Error: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")
    else:
        print("3. ⏭️  Skipping API test (no API key)")
    
    print()
    
    # Test hint generation
    print("4. Testing hint generation...")
    test_puzzle = "WHEEL OF FORTUNE"
    test_category = "TV Show"
    
    for difficulty in ["easy", "medium", "hard"]:
        print(f"   Testing {difficulty} difficulty:")
        result = hint_ai.generate_hint(test_puzzle, test_category, difficulty)
        print(f"     Success: {result['success']}")
        print(f"     Hint: {result['hint']}")
        print(f"     Fallback used: {result.get('fallback', 'Unknown')}")
        print()
    
    print("5. Recommendations:")
    if not api_key:
        print("   • Set your OpenAI API key: export OPENAI_API_KEY='your-key-here'")
        print("   • Get an API key from: https://platform.openai.com/api-keys")
    else:
        print("   • API key is set - check if it's valid and has credits")
        print("   • Verify your OpenAI account has sufficient balance")

if __name__ == "__main__":
    test_openai_api()