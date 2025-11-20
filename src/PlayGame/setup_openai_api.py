#!/usr/bin/env python3
"""
Setup guide and test script for OpenAI API integration.
"""

import os
import sys
import requests
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from hint_ai import HintAI

def check_api_key_format(api_key):
    """Check if the API key has the correct format."""
    if not api_key:
        return False, "API key is empty"
    
    if not api_key.startswith('sk-'):
        return False, "API key should start with 'sk-'"
    
    if len(api_key) < 20:
        return False, "API key seems too short"
    
    return True, "API key format looks correct"

def test_api_connection(api_key):
    """Test if the API key works with a simple request."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "user", "content": "Say 'API test successful' if you can read this."}
        ],
        "max_tokens": 10,
        "temperature": 0.1
    }
    
    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", 
                               headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"].strip()
            return True, f"Success! API responded: {content}"
        elif response.status_code == 401:
            return False, "Invalid API key - check your key and try again"
        elif response.status_code == 429:
            return False, "Rate limit exceeded - try again later"
        elif response.status_code == 402:
            return False, "Insufficient credits - check your OpenAI billing"
        else:
            return False, f"API error {response.status_code}: {response.text}"
            
    except requests.exceptions.Timeout:
        return False, "Request timed out - check your internet connection"
    except requests.exceptions.RequestException as e:
        return False, f"Network error: {str(e)}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"

def setup_guide():
    """Interactive setup guide for OpenAI API."""
    
    print("🚀 OPENAI API SETUP GUIDE FOR WHEEL OF FORTUNE HINT AI")
    print("=" * 60)
    print()
    
    # Check current status
    current_key = os.getenv("OPENAI_API_KEY")
    if current_key:
        print(f"✅ API key found in environment: {current_key[:10]}...{current_key[-4:]}")
        
        # Test the current key
        print("🔍 Testing current API key...")
        success, message = test_api_connection(current_key)
        if success:
            print(f"✅ {message}")
            print()
            print("🎉 Your API key is working! You can now use AI-powered hints.")
            return True
        else:
            print(f"❌ {message}")
            print()
    else:
        print("❌ No API key found in environment")
        print()
    
    # Setup instructions
    print("📋 SETUP INSTRUCTIONS:")
    print()
    print("1. Get an OpenAI API Key:")
    print("   • Go to: https://platform.openai.com/api-keys")
    print("   • Sign in or create an account")
    print("   • Click 'Create new secret key'")
    print("   • Copy the key (starts with 'sk-')")
    print()
    
    print("2. Set the API key in your environment:")
    print("   For this session:")
    print("   export OPENAI_API_KEY='your-api-key-here'")
    print()
    print("   For permanent setup (add to ~/.bashrc or ~/.zshrc):")
    print("   echo 'export OPENAI_API_KEY=\"your-api-key-here\"' >> ~/.bashrc")
    print()
    
    print("3. Verify your setup:")
    print("   python setup_openai_api.py")
    print()
    
    # Interactive key entry
    print("🔧 INTERACTIVE SETUP:")
    print("You can test your API key right now!")
    print()
    
    while True:
        api_key = input("Enter your OpenAI API key (or 'skip' to exit): ").strip()
        
        if api_key.lower() == 'skip':
            print("Setup skipped. You can run this script again anytime.")
            return False
        
        if not api_key:
            print("❌ Please enter a valid API key or 'skip'")
            continue
        
        # Check format
        format_ok, format_msg = check_api_key_format(api_key)
        if not format_ok:
            print(f"❌ {format_msg}")
            continue
        
        print(f"✅ {format_msg}")
        
        # Test the key
        print("🔍 Testing API key...")
        success, message = test_api_connection(api_key)
        
        if success:
            print(f"✅ {message}")
            print()
            print("🎉 API key is working!")
            print()
            print("To use this key permanently, run:")
            print(f"export OPENAI_API_KEY='{api_key}'")
            print()
            
            # Set for this session
            os.environ["OPENAI_API_KEY"] = api_key
            return True
        else:
            print(f"❌ {message}")
            print("Please try again with a different key.")
            print()

def test_hint_generation():
    """Test hint generation with the configured API key."""
    
    print("🎯 TESTING HINT GENERATION")
    print("=" * 30)
    
    hint_ai = HintAI()
    
    if not hint_ai.api_key:
        print("❌ No API key available - using fallback hints")
        print()
    else:
        print("✅ API key configured - testing AI hints")
        print()
    
    # Test with a simple puzzle
    puzzle = "WHEEL OF FORTUNE"
    category = "TV Show"
    
    print(f"📝 Test Puzzle: {puzzle}")
    print(f"   Category: {category}")
    print()
    
    for difficulty in ["easy", "medium", "hard"]:
        print(f"Testing {difficulty} difficulty...")
        
        # Enable debug mode
        os.environ["DEBUG_HINTS"] = "1"
        
        result = hint_ai.generate_hint(puzzle, category, difficulty)
        
        # Disable debug mode
        if "DEBUG_HINTS" in os.environ:
            del os.environ["DEBUG_HINTS"]
        
        difficulty_emoji = {"easy": "🟢", "medium": "🟡", "hard": "🔴"}[difficulty]
        print(f"{difficulty_emoji} {difficulty.upper()}: {result['hint']}")
        print(f"   Success: {result['success']}")
        print(f"   Fallback: {result.get('fallback', 'Unknown')}")
        print(f"   Remaining: {result['hints_remaining']}")
        print()

def main():
    """Main setup and test function."""
    
    # Run setup guide
    api_configured = setup_guide()
    
    print()
    print("-" * 60)
    print()
    
    # Test hint generation
    test_hint_generation()
    
    print()
    print("🎮 READY TO PLAY!")
    print("Run the game with: python play_random_puzzle.py human smart")
    print("Select option 4 during your turn to get AI-powered hints!")

if __name__ == "__main__":
    main()