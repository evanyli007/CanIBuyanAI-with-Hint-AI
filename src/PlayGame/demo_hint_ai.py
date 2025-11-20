#!/usr/bin/env python3
"""
Demo script showcasing the Hint AI feature.
This script demonstrates the hint system without running a full game.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from hint_ai import HintAI
from play_random_puzzle import get_random_puzzle
import re

def demo_hint_ai():
    """Demonstrate the Hint AI feature with sample puzzles."""
    
    print("🎡 WHEEL OF FORTUNE - HINT AI DEMO")
    print("=" * 50)
    print()
    
    # Sample puzzles for demonstration
    demo_puzzles = [
        ("WHEEL OF FORTUNE", "TV Show", "The iconic game show itself!"),
        ("BREAK A LEG", "Phrase", "Good luck wish for performers"),
        ("CHOCOLATE CHIP COOKIE", "Food & Drink", "Sweet baked treat"),
        ("NEW YORK CITY", "Place", "The Big Apple"),
        ("SINGING IN THE RAIN", "Movie Title", "Classic musical film")
    ]
    
    for i, (puzzle, category, description) in enumerate(demo_puzzles, 1):
        print(f"📝 DEMO PUZZLE #{i}")
        print(f"Answer: {puzzle}")
        print(f"Category: {category}")
        print(f"Description: {description}")
        
        # Show puzzle with some letters revealed (simulate game state)
        showing = puzzle
        showing = re.sub(r"[A-Z]", "_", showing)
        # Reveal some common letters for demo
        for letter in "AEIOURST":
            showing = showing.replace("_", letter) if letter in puzzle else showing
            showing = re.sub(r"[A-Z]", "_", showing)
        
        # Actually reveal a few letters properly
        revealed_letters = ["E", "A", "R", "T"]
        for letter in revealed_letters:
            if letter in puzzle:
                for pos, char in enumerate(puzzle):
                    if char == letter:
                        showing = showing[:pos] + letter + showing[pos + 1:]
        
        print(f"Current state: {showing}")
        print()
        
        # Initialize fresh hint AI for each puzzle
        hint_ai = HintAI()
        
        # Generate hints for all difficulty levels
        difficulties = [
            ("easy", "🟢 EASY"),
            ("medium", "🟡 MEDIUM"), 
            ("hard", "🔴 HARD")
        ]
        
        for difficulty, label in difficulties:
            result = hint_ai.generate_hint(puzzle, category, difficulty, showing)
            print(f"{label} HINT: {result['hint']}")
            print(f"   Hints remaining: {result['hints_remaining']}")
            
        print()
        print("-" * 50)
        print()
    
    print("🎯 HINT AI FEATURES:")
    print("• Three difficulty levels (Easy, Medium, Hard)")
    print("• AI-powered hints using large language models")
    print("• Fallback to rule-based hints when API unavailable")
    print("• Limited to 3 hints per game for balanced gameplay")
    print("• Contextual hints based on puzzle category and current state")
    print()
    
    print("🚀 TO USE IN GAME:")
    print("1. Run: python play_random_puzzle.py human smart conservative")
    print("2. When it's your turn, select option 4: Get Hint")
    print("3. Choose your preferred difficulty level")
    print("4. Use the hint to help solve the puzzle!")
    print()
    
    print("💡 TIP: Set OPENAI_API_KEY environment variable for AI-powered hints")
    print("    Otherwise, the system uses rule-based fallback hints")

if __name__ == "__main__":
    demo_hint_ai()