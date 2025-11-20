#!/usr/bin/env python3
"""
Test script with mock OpenAI API to demonstrate hint generation.
"""

import os
import sys
import json
from unittest.mock import patch, MagicMock
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from hint_ai import HintAI

def create_mock_response(hint_text):
    """Create a mock response that mimics OpenAI API response."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": hint_text
                }
            }
        ]
    }
    mock_response.raise_for_status.return_value = None
    return mock_response

def test_with_mock_api():
    """Test hint generation with mocked OpenAI API responses."""
    
    print("🎯 TESTING HINT AI WITH MOCK API")
    print("=" * 50)
    
    # Set a fake API key for testing
    os.environ["OPENAI_API_KEY"] = "sk-test-fake-key-for-testing-purposes"
    
    # Create HintAI instance
    hint_ai = HintAI()
    print(f"✅ HintAI initialized with API key: {hint_ai.api_key is not None}")
    print()
    
    # Test puzzles
    test_cases = [
        {
            "puzzle": "WHEEL OF FORTUNE",
            "category": "TV Show",
            "description": "The iconic game show itself!"
        },
        {
            "puzzle": "BREAK A LEG",
            "category": "Phrase",
            "description": "Good luck wish for performers"
        },
        {
            "puzzle": "NEW YORK CITY",
            "category": "Place",
            "description": "The Big Apple"
        }
    ]
    
    # Mock responses for different difficulties
    mock_responses = {
        "easy": {
            "WHEEL OF FORTUNE": "This popular game show features spinning a large wheel and solving word puzzles.",
            "BREAK A LEG": "A common theatrical expression wishing someone good luck before a performance.",
            "NEW YORK CITY": "The most populous city in the United States, known as the Big Apple."
        },
        "medium": {
            "WHEEL OF FORTUNE": "Vanna's workplace where contestants spin for cash and prizes.",
            "BREAK A LEG": "Theatrical well-wishes that sound quite violent but mean the opposite.",
            "NEW YORK CITY": "Five boroughs united as one metropolis, home to the Statue of Liberty."
        },
        "hard": {
            "WHEEL OF FORTUNE": "Pat and Vanna's domain where circular fate meets alphabetical destiny.",
            "BREAK A LEG": "Stage superstition that reverses injury into triumph.",
            "NEW YORK CITY": "Concrete jungle where dreams are made, according to Alicia Keys."
        }
    }
    
    # Test each puzzle with mocked API responses
    for test_case in test_cases:
        puzzle = test_case["puzzle"]
        category = test_case["category"]
        
        print(f"📝 TESTING: {puzzle}")
        print(f"   Category: {category}")
        print()
        
        for difficulty in ["easy", "medium", "hard"]:
            # Mock the requests.post call
            mock_hint = mock_responses[difficulty][puzzle]
            mock_response = create_mock_response(mock_hint)
            
            with patch('requests.post', return_value=mock_response):
                result = hint_ai.generate_hint(puzzle, category, difficulty)
                
                difficulty_emoji = {"easy": "🟢", "medium": "🟡", "hard": "🔴"}[difficulty]
                print(f"   {difficulty_emoji} {difficulty.upper()} HINT: {result['hint']}")
                print(f"      Success: {result['success']}")
                print(f"      Fallback used: {result.get('fallback', False)}")
                print(f"      Hints remaining: {result['hints_remaining']}")
                print()
        
        # Reset hint counter for next puzzle
        hint_ai.reset_game()
        print("-" * 50)
        print()
    
    print("🎉 MOCK API TEST COMPLETED!")
    print()
    print("💡 This demonstrates what the hints would look like with a real OpenAI API key.")
    print("   To use real AI-generated hints, set your OPENAI_API_KEY environment variable.")

if __name__ == "__main__":
    test_with_mock_api()