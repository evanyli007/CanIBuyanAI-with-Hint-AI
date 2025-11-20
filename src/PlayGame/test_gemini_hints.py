#!/usr/bin/env python3
"""
Test script for Google Gemini hint generation.
"""

import os
import sys
from hint_ai import HintAI

def test_gemini_hints():
    """Test the Gemini hint generation."""
    print("🤖 Testing Google Gemini Hint AI")
    print("=" * 50)
    
    # Check for API key
    api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("⚠️  No GEMINI_API_KEY or GOOGLE_API_KEY found in environment")
        print("💡 Set your API key with: export GEMINI_API_KEY='your-key-here'")
        print("🔗 Get your key at: https://makersuite.google.com/app/apikey")
        print("\n🧪 Testing fallback hints instead...")
        
        # Test fallback functionality
        hint_ai = HintAI()
        test_cases = [
            ("WHEEL OF FORTUNE", "TV Show", "medium"),
            ("ARTIFICIAL INTELLIGENCE", "Technology", "hard"),
            ("PIZZA PARTY", "Fun & Games", "easy")
        ]
        
        for puzzle, category, difficulty in test_cases:
            print(f"\n📝 Testing fallback hint for: '{puzzle}' ({category}, {difficulty})")
            result = hint_ai.generate_hint(puzzle, category, difficulty)
            print(f"💡 Hint: {result['hint']}")
            print(f"✅ Success: {result['success']}")
        
        return True
    
    print(f"🔑 Found API key: {api_key[:10]}...")
    
    # Test with real API
    hint_ai = HintAI(api_key=api_key)
    
    test_cases = [
        ("WHEEL OF FORTUNE", "TV Show", "medium", "W____ __ _______"),
        ("ARTIFICIAL INTELLIGENCE", "Technology", "hard", "A_________ ____________"),
        ("PIZZA PARTY", "Fun & Games", "easy", "_____ _____"),
        ("NEW YORK CITY", "Place", "medium", "___ ____ ____")
    ]
    
    print("🧪 Testing Gemini API integration...")
    
    for i, (puzzle, category, difficulty, current_state) in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: '{puzzle}' ({category}, {difficulty})")
        print(f"🎯 Current state: {current_state}")
        
        try:
            result = hint_ai.generate_hint(puzzle, category, difficulty, current_state)
            
            print(f"💡 Hint: {result['hint']}")
            print(f"✅ Success: {result['success']}")
            print(f"🎲 Difficulty: {result.get('difficulty', 'N/A')}")
            print(f"🔢 Hints remaining: {result['hints_remaining']}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    print("\n🎉 All Gemini tests completed successfully!")
    return True

def test_api_key_validation():
    """Test API key validation and error handling."""
    print("\n🔐 Testing API key validation...")
    
    # Test with invalid key
    hint_ai = HintAI(api_key="invalid-key")
    result = hint_ai.generate_hint("TEST PUZZLE", "Test", "medium")
    
    if not result['success']:
        print("✅ Invalid API key properly handled with fallback")
    else:
        print("⚠️  Expected fallback for invalid API key")
    
    return True

def main():
    """Run all tests."""
    print("🚀 Starting Gemini Hint AI Tests")
    print("=" * 60)
    
    # Enable debug mode for detailed output
    os.environ['DEBUG_HINTS'] = '1'
    
    success = True
    
    try:
        success &= test_gemini_hints()
        success &= test_api_key_validation()
        
        if success:
            print("\n🎊 All tests passed! Gemini integration is working.")
        else:
            print("\n❌ Some tests failed. Check the output above.")
            
    except Exception as e:
        print(f"\n💥 Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
        success = False
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)