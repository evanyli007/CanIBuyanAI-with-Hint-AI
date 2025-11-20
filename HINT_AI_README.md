# Hint AI Feature for Wheel of Fortune

## Overview

The Hint AI feature adds intelligent hint generation to the Wheel of Fortune game, providing players with New York Times-style crossword hints to help solve puzzles. The system uses Google's Gemini AI to generate contextual hints with three difficulty levels.

## Features

### 🤖 AI-Powered Hints
- Integrates with Google Gemini AI for intelligent hint generation
- Upgraded from ChatGPT to Gemini for improved performance
- Fallback to rule-based hints when API is unavailable
- Contextual hints based on puzzle category and current game state

### 🎯 Three Difficulty Levels

1. **Easy**: Direct, helpful hints that give clear direction
   - May reference specific aspects of the answer
   - Provides word/letter counts
   - Most straightforward guidance

2. **Medium**: New York Times crossword-style clues
   - Uses wordplay, synonyms, and indirect references
   - Challenging but fair
   - Classic crossword puzzle approach

3. **Hard**: Cryptic, challenging hints
   - Requires creative thinking
   - Uses metaphors and very indirect references
   - Most challenging level

### 🎮 Game Integration
- Seamlessly integrated into existing game flow
- Available as option 4 during human turns
- Limited to 3 hints per game to maintain challenge
- Works with existing player types and game modes

## Usage

### For Players

When it's your turn as a human player, you'll see:
```
1: Spin, 2: Buy Vowel, 3: Solve, 4: Get Hint ....
```

Select option 4 to get a hint, then choose your difficulty:
```
Choose hint difficulty:
1: Easy (more direct)
2: Medium (crossword-style)  
3: Hard (cryptic)
```

### Setting Up API Access

To use AI-powered hints, set your Google Gemini API key:

```bash
export GEMINI_API_KEY="your-api-key-here"
# or alternatively:
export GOOGLE_API_KEY="your-api-key-here"
```

Get your API key from: https://makersuite.google.com/app/apikey

Or the system will automatically fall back to rule-based hints.

### Running the Game

```bash
cd src/PlayGame
python play_random_puzzle.py human smart conservative
```

## Technical Implementation

### Core Components

1. **`hint_ai.py`**: Main hint generation module
   - `HintAI` class handles all hint logic
   - Supports both API and fallback modes
   - Tracks hint usage per game

2. **Modified `play_random_puzzle.py`**: 
   - Integrated hint option into human turns
   - Added hint AI initialization
   - Enhanced user interface

### API Integration

The system uses Google Gemini's API with carefully crafted prompts:

```python
# Example API call structure
{
    "contents": [
        {
            "parts": [
                {
                    "text": "You are a professional crossword puzzle writer creating hints for a Wheel of Fortune game.\n\nCreate a hint for: WHEEL OF FORTUNE..."
                }
            ]
        }
    ],
    "generationConfig": {
        "maxOutputTokens": 100,
    "temperature": 0.7
}
```

### Fallback System

When API access is unavailable, the system provides rule-based hints:
- Word and letter counts for easy mode
- Category-based guidance for medium mode  
- Minimal cryptic hints for hard mode

## Examples

### Easy Hint Example
**Puzzle**: "CHOCOLATE CHIP COOKIE"  
**Category**: "Food & Drink"  
**Easy Hint**: "This sweet treat has 3 words and is perfect with milk"

### Medium Hint Example  
**Puzzle**: "BREAK A LEG"  
**Category**: "Phrase"  
**Medium Hint**: "Theater performer's good luck wish"

### Hard Hint Example
**Puzzle**: "WHEEL OF FORTUNE"  
**Category**: "TV Show"  
**Hard Hint**: "Circular fate spinner meets lady luck's favor"

## Configuration

### Hint Limits
- Default: 3 hints per game
- Configurable in `HintAI.__init__()`

### API Settings
- Default model: `gpt-3.5-turbo`
- Timeout: 30 seconds
- Max tokens: 100

### Customization

You can customize the hint system by modifying:

```python
# In hint_ai.py
class HintAI:
    def __init__(self, api_key=None, model="gpt-3.5-turbo"):
        self.max_hints = 3  # Change hint limit
        self.model = model  # Change AI model
```

## Dependencies

- `requests>=2.25.0` for API calls
- Google Gemini API key (optional, for AI hints)

Install dependencies:
```bash
pip install -r requirements.txt
```

## Testing

Run the test suite:
```bash
cd src/PlayGame
python test_hint_integration.py
```

Test individual components:
```bash
python hint_ai.py  # Test hint generation
```

## Error Handling

The system gracefully handles:
- Missing API keys (falls back to rule-based hints)
- Network timeouts (falls back to rule-based hints)
- API rate limits (shows appropriate error messages)
- Invalid difficulty selections (defaults to medium)

## Future Enhancements

Potential improvements:
- Support for additional LLM providers (Anthropic, OpenAI, etc.)
- Hint difficulty based on player performance
- Hint history and analytics
- Multi-language hint support
- Custom hint templates per category
- Multiplayer hint sharing options

## Contributing

When contributing to the hint system:
1. Maintain backward compatibility with existing game modes
2. Test both API and fallback modes
3. Ensure hints don't reveal the answer directly
4. Follow the existing code style and patterns

## License

This feature is part of the CanIBuyanAI-with-Hint-AI project and follows the same licensing terms.