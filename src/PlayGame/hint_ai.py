"""
Hint AI module for Wheel of Fortune game.
Provides crossword-style hints using Google Gemini AI.
"""

import os
import json
import requests
from typing import Optional, Dict, Any


class HintAI:
    """AI-powered hint generator for Wheel of Fortune puzzles using Google Gemini."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-1.5-flash"):
        """
        Initialize the Hint AI with Google Gemini.
        
        Args:
            api_key: Google Gemini API key (if None, will try to get from environment)
            model: Gemini model to use for hint generation
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
        self.model = model
        self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        
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
        """Call the Google Gemini API to generate a hint."""
        
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
        
        # Gemini API format
        headers = {
            "Content-Type": "application/json"
        }
        
        data = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": f"You are a professional crossword puzzle writer creating hints for a Wheel of Fortune game.\n\n{prompt}"
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.7,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 100,
                "stopSequences": []
            },
            "safetySettings": [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                }
            ]
        }
        
        # Add API key to URL
        url_with_key = f"{self.base_url}?key={self.api_key}"
        
        # Debug information
        if os.getenv("DEBUG_HINTS"):
            print(f"🔍 DEBUG: Making API call to Gemini")
            print(f"🔍 DEBUG: Model: {self.model}")
            print(f"🔍 DEBUG: Puzzle: {puzzle}, Category: {category}, Difficulty: {difficulty}")
        
        response = requests.post(url_with_key, headers=headers, json=data, timeout=30)
        
        if os.getenv("DEBUG_HINTS"):
            print(f"🔍 DEBUG: API Response Status: {response.status_code}")
            if response.status_code != 200:
                print(f"🔍 DEBUG: Response content: {response.text}")
        
        response.raise_for_status()
        
        result = response.json()
        
        # Extract text from Gemini response format
        if "candidates" in result and len(result["candidates"]) > 0:
            candidate = result["candidates"][0]
            if "content" in candidate and "parts" in candidate["content"]:
                hint_text = candidate["content"]["parts"][0]["text"].strip()
            else:
                raise Exception("Unexpected response format from Gemini API")
        else:
            raise Exception("No candidates in Gemini API response")
        
        if os.getenv("DEBUG_HINTS"):
            print(f"🔍 DEBUG: Generated hint: {hint_text}")
        
        return hint_text
    
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