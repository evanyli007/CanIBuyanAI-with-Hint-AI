#!/usr/bin/env python3
"""
Compare AI-generated hints vs fallback hints side by side.
"""

import os
import sys
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

def compare_hints():
    """Compare AI vs fallback hints for the same puzzles."""
    
    print("🔍 COMPARING AI HINTS VS FALLBACK HINTS")
    print("=" * 50)
    print()
    
    test_puzzles = [
        {
            "puzzle": "WHEEL OF FORTUNE",
            "category": "TV Show",
            "ai_hints": {
                "easy": "This popular game show features spinning a large wheel and solving word puzzles.",
                "medium": "Vanna's workplace where contestants spin for cash and prizes.",
                "hard": "Pat and Vanna's domain where circular fate meets alphabetical destiny."
            }
        },
        {
            "puzzle": "CHOCOLATE CHIP COOKIE",
            "category": "Food & Drink",
            "ai_hints": {
                "easy": "A sweet baked treat with small pieces of chocolate mixed into the dough.",
                "medium": "Baker's delight studded with cocoa morsels, perfect with milk.",
                "hard": "Dough-based confection dotted with cacao fragments, a jar-dwelling temptation."
            }
        },
        {
            "puzzle": "BREAK A LEG",
            "category": "Phrase",
            "ai_hints": {
                "easy": "A common theatrical expression wishing someone good luck before a performance.",
                "medium": "Theatrical well-wishes that sound quite violent but mean the opposite.",
                "hard": "Stage superstition that reverses injury into triumph."
            }
        }
    ]
    
    for test_case in test_puzzles:
        puzzle = test_case["puzzle"]
        category = test_case["category"]
        ai_hints = test_case["ai_hints"]
        
        print(f"📝 PUZZLE: {puzzle}")
        print(f"   Category: {category}")
        print()
        
        for difficulty in ["easy", "medium", "hard"]:
            difficulty_emoji = {"easy": "🟢", "medium": "🟡", "hard": "🔴"}[difficulty]
            
            print(f"   {difficulty_emoji} {difficulty.upper()} DIFFICULTY:")
            
            # Get AI hint (mocked)
            hint_ai_with_key = HintAI()
            hint_ai_with_key.api_key = "sk-fake-key-for-testing"
            
            mock_response = create_mock_response(ai_hints[difficulty])
            with patch('requests.post', return_value=mock_response):
                ai_result = hint_ai_with_key.generate_hint(puzzle, category, difficulty)
            
            # Get fallback hint
            hint_ai_no_key = HintAI()
            hint_ai_no_key.api_key = None
            fallback_result = hint_ai_no_key.generate_hint(puzzle, category, difficulty)
            
            print(f"      🤖 AI HINT:       {ai_result['hint']}")
            print(f"      🔧 FALLBACK HINT: {fallback_result['hint']}")
            print()
            
            # Reset counters
            hint_ai_with_key.reset_game()
            hint_ai_no_key.reset_game()
        
        print("-" * 50)
        print()
    
    print("💡 KEY DIFFERENCES:")
    print("   🤖 AI Hints: Creative, contextual, varied language")
    print("   🔧 Fallback Hints: Factual, consistent, always available")
    print()
    print("🎯 RECOMMENDATION:")
    print("   Set up OpenAI API key for the best experience!")
    print("   Fallback hints ensure the game always works.")

if __name__ == "__main__":
    compare_hints()