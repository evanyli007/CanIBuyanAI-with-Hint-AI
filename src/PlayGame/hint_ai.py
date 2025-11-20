"""
Hint AI module for Wheel of Fortune game.
Provides crossword-style hints using large language models.
"""

import os
import json
import requests
from typing import Optional, Dict, Any


class HintAI:
    """AI-powered hint generator for Wheel of Fortune puzzles."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        """
        Initialize the Hint AI.
        
        Args:
            api_key: OpenAI API key (if None, will try to get from environment)
            model: OpenAI model to use for hint generation
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.model = model
        self.base_url = "https://api.openai.com/v1/chat/completions"
        
        # Track hint usage per game
        self.hints_used = 0
        self.max_hints = 3  # Maximum hints per game
        
    def generate_hint(self, puzzle: str, category: str, difficulty: str = "medium", 
                     current_state: str = None) -> Dict[str, Any]:
        """
        Generate a crossword-style hint for the puzzle.
        
        Args:
            puzzle: The complete puzzle answer
            category: The puzzle category (e.g., "Phrase", "Thing", etc.)
            difficulty: Hint difficulty level ("easy", "medium", "hard")
            current_state: Current state of the puzzle with guessed letters
            
        Returns:
            Dictionary containing the hint and metadata
        """
        if self.hints_used >= self.max_hints:
            return {
                "hint": "No more hints available for this game!",
                "success": False,
                "hints_remaining": 0
            }
        
        if not self.api_key:
            # Fallback to rule-based hints if no API key
            return self._generate_fallback_hint(puzzle, category, difficulty, current_state)
        
        try:
            hint_text = self._call_llm(puzzle, category, difficulty, current_state)
            self.hints_used += 1
            
            return {
                "hint": hint_text,
                "success": True,
                "hints_remaining": self.max_hints - self.hints_used,
                "difficulty": difficulty
            }
            
        except Exception as e:
            print(f"Error generating AI hint: {e}")
            # Fallback to rule-based hint
            return self._generate_fallback_hint(puzzle, category, difficulty, current_state)
    
    def _call_llm(self, puzzle: str, category: str, difficulty: str, current_state: str) -> str:
        """Call the LLM API to generate a hint."""
        
        # Create difficulty-specific prompts
        difficulty_instructions = {
            "easy": """
            Create a straightforward, helpful hint that gives clear direction about the answer.
            You may reference specific words or parts of the phrase directly.
            Make it easier for the player to guess.
            """,
            "medium": """
            Create a New York Times crossword-style clue that's clever but fair.
            Use wordplay, synonyms, or indirect references.
            The hint should be challenging but solvable.
            """,
            "hard": """
            Create a cryptic, challenging hint that requires creative thinking.
            Use metaphors, very indirect references, or wordplay.
            Make it quite difficult but not impossible.
            """
        }
        
        current_info = f"\nCurrent puzzle state: {current_state}" if current_state else ""
        
        prompt = f"""
        You are creating a crossword-style hint for a Wheel of Fortune puzzle.
        
        Puzzle Answer: "{puzzle}"
        Category: {category}
        Difficulty Level: {difficulty}
        {current_info}
        
        Instructions for {difficulty} difficulty:
        {difficulty_instructions[difficulty]}
        
        Rules:
        1. Do NOT reveal the exact answer or any letters directly
        2. Keep the hint concise (1-2 sentences max)
        3. Make it appropriate for a family game show
        4. The hint should help players think about the answer without giving it away
        5. Consider the category when crafting your hint
        
        Generate only the hint text, nothing else:
        """
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a professional crossword puzzle writer creating hints for a Wheel of Fortune game."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 100,
            "temperature": 0.7
        }
        
        response = requests.post(self.base_url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        return result["choices"][0]["message"]["content"].strip()
    
    def _generate_fallback_hint(self, puzzle: str, category: str, difficulty: str, 
                               current_state: str) -> Dict[str, Any]:
        """Generate a rule-based hint when LLM is not available."""
        
        self.hints_used += 1
        
        # Simple rule-based hints based on category and difficulty
        word_count = len(puzzle.split())
        letter_count = len([c for c in puzzle if c.isalpha()])
        
        if difficulty == "easy":
            if category.lower() == "phrase":
                hint = f"This common saying has {word_count} words and {letter_count} letters total."
            elif category.lower() == "thing":
                hint = f"This object or item has {letter_count} letters in its name."
            elif category.lower() == "title":
                hint = f"This title or name consists of {word_count} words."
            else:
                hint = f"This {category.lower()} has {word_count} words and {letter_count} letters."
        
        elif difficulty == "medium":
            if "AND" in puzzle:
                hint = "This answer connects two related concepts."
            elif word_count == 1:
                hint = f"A single word in the {category} category."
            else:
                hint = f"Multiple words that fit the {category} theme."
        
        else:  # hard
            hint = f"Think about what belongs in the '{category}' category..."
        
        return {
            "hint": hint,
            "success": True,
            "hints_remaining": self.max_hints - self.hints_used,
            "difficulty": difficulty,
            "fallback": True
        }
    
    def reset_game(self):
        """Reset hint counter for a new game."""
        self.hints_used = 0
    
    def get_hints_remaining(self) -> int:
        """Get the number of hints remaining for this game."""
        return max(0, self.max_hints - self.hints_used)


def demo_hint_ai():
    """Demo function to test the Hint AI."""
    hint_ai = HintAI()
    
    # Test puzzles
    test_cases = [
        ("WHEEL OF FORTUNE", "Title", "medium"),
        ("CHOCOLATE CHIP COOKIE", "Food & Drink", "easy"),
        ("BREAK A LEG", "Phrase", "hard"),
    ]
    
    for puzzle, category, difficulty in test_cases:
        print(f"\nTesting: {puzzle} ({category}) - {difficulty}")
        result = hint_ai.generate_hint(puzzle, category, difficulty)
        print(f"Hint: {result['hint']}")
        print(f"Hints remaining: {result['hints_remaining']}")
        print("-" * 50)


if __name__ == "__main__":
    demo_hint_ai()