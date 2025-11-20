# CanIBuyanAI with Hint AI
This project tries to solve Wheel of Fortune puzzles and now includes an AI-powered hint system!

## 🆕 New Features: Enhanced GUI & Gemini AI Hints
The game now includes major enhancements:

### 🎡 Enhanced Wheel of Fortune GUI
- **Realistic wheel spinning** with physics-based momentum and deceleration
- **3D visual effects** with gradients, shadows, and metallic hub design
- **Animated letter reveals** with flip effects and glowing highlights
- **Score counting animations** with color-coded feedback
- **Smooth transitions** and visual feedback for all game actions

### 🤖 Google Gemini AI Hints
- **AI-powered hints** using Google's Gemini AI (upgraded from ChatGPT)
- **Three difficulty levels**: Easy, Medium, and Hard
- **Fallback system** with rule-based hints when API unavailable
- **Limited hints per game** (3 hints) for balanced gameplay

### 🚀 Quick Setup for Gemini AI Hints
1. **Get API Key**:
   - Visit: https://makersuite.google.com/app/apikey
   - Create a new API key for Gemini

2. **Set Environment Variable**:
   ```bash
   export GEMINI_API_KEY="your-key-here"
   # or alternatively:
   export GOOGLE_API_KEY="your-key-here"
   ```

3. **Test Integration**:
   ```bash
   cd src/PlayGame
   python test_gemini_hints.py
   ```

**Note**: Without an API key, the system automatically uses rule-based fallback hints.

See [HINT_AI_README.md](./HINT_AI_README.md) for detailed documentation.

## Requirements
Tested using Python 3.6+. For the Hint AI feature:
```bash
pip install -r requirements.txt
```

## Scraper
See the [Puzzle Scraper README](./src/PuzzleScraper/README.md) for details.

Install the scraper dependencies:
```bash
pip install requests beautifulsoup4
```
## How to Play

Play a random Wheel of Fortune puzzle against simple computer strategies using [play_random_puzzle.py](./src/PlayGame/play_random_puzzle.py).

- Player types: `human`, `morse`, `oxford`, `trigram`, `smart`, `conservative`, `aggressive`
- As a human, you’ll be prompted each turn: 1 = Spin, 2 = Buy Vowel, 3 = Solve
- Smart AI players (`smart`, `conservative`, `aggressive`) use advanced decision-making logic to optimize spin vs buy vowel choices
- Run from the `src/PlayGame` directory so relative paths resolve (uses `../../data/puzzles/valid.csv` and `bigrams.txt`)
- **NEW: Hint AI** - Human players can now use option 4 to get AI-generated crossword-style hints with three difficulty levels!

Example:
```bash
cd src/PlayGame
python3 play_random_puzzle.py human morse oxford
# or, let it pick defaults if you omit/shorten the args
python3 play_random_puzzle.py
```

Tip: To visualize the wheel segment values used by the game, see the [ASCII Wheel](#ascii-wheel-optional) section below.

## ASCII Wheel (Optional)

Render an ASCII-art wheel of the segment values:

```bash
cd src/PlayGame
python3 ascii_wheel.py --label short
# long labels (BANKRUPT / LOSE TURN) and a larger radius
python3 ascii_wheel.py --label long --radius 14
# custom values
python3 ascii_wheel.py --values "0,-1,500,550,600,650,700,750,800,850,900,-1,500,550,600,650,700,750,800,850,900,500,550,600"
```

