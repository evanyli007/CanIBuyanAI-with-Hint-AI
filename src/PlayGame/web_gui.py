#!/usr/bin/env python3
"""
Web-based GUI for Wheel of Fortune using Flask.
Provides a browser-based interface that works in any environment.
"""

import json
import random
import re
import os
from flask import Flask, render_template, request, jsonify, session
from hint_ai import HintAI
from smart_player import computer_turn_smart, computer_turn_smart_conservative, computer_turn_smart_aggressive

app = Flask(__name__)
app.secret_key = 'wheel_of_fortune_secret_key_2024'

class WebGameEngine:
    """Game engine for web-based Wheel of Fortune."""
    
    def __init__(self):
        self.wheel_values = [0, -1, 500, 550, 600, 650, 700, 750, 800, 850, 900, -1, 
                           500, 550, 600, 650, 700, 750, 800, 850, 900, 500, 550, 600]
        self.hint_ai = None
        self.init_hint_ai()
    
    def init_hint_ai(self):
        """Initialize the Hint AI system."""
        try:
            self.hint_ai = HintAI()
        except Exception as e:
            print(f"Hint AI initialization error: {e}")
            self.hint_ai = None
    
    def get_random_puzzle(self):
        """Get a random puzzle from the data file."""
        try:
            puzzle_file = "../../data/puzzles/valid.csv"
            if not os.path.exists(puzzle_file):
                puzzle_file = "data/puzzles/valid.csv"
                if not os.path.exists(puzzle_file):
                    return None
            
            with open(puzzle_file, 'r') as f:
                lines = f.readlines()
            
            if not lines:
                return None
            
            random_line = random.choice(lines).strip()
            parts = random_line.split(',')
            
            if len(parts) >= 4:
                puzzle, clue, date, game_type = parts[:4]
                puzzle = puzzle.replace("&amp;", "&")
                clue = clue.replace("&amp;", "&")
                return {
                    'puzzle': puzzle,
                    'clue': clue,
                    'date': date,
                    'game_type': game_type
                }
        except Exception as e:
            print(f"Error loading puzzle: {e}")
        
        # Fallback puzzle
        return {
            'puzzle': 'WHEEL OF FORTUNE',
            'clue': 'TV Show',
            'date': '2024',
            'game_type': 'Toss Up'
        }
    
    def create_showing(self, puzzle):
        """Create the showing string with blanks."""
        return re.sub(r"[A-Z]", "_", puzzle)
    
    def is_vowel(self, letter):
        """Check if a letter is a vowel."""
        return letter.upper() in "AEIOU"
    
    def spin_wheel(self):
        """Spin the wheel and return a value."""
        return random.choice(self.wheel_values)
    
    def process_guess(self, puzzle, showing, guess):
        """Process a letter guess and return updated showing."""
        correct_positions = [i for i, char in enumerate(puzzle) if char == guess]
        
        if correct_positions:
            showing_list = list(showing)
            for pos in correct_positions:
                showing_list[pos] = guess
            return ''.join(showing_list), len(correct_positions)
        
        return showing, 0
    
    def get_ai_move(self, player_type, showing, winnings, previous_guesses, turn):
        """Get AI player move."""
        try:
            if player_type == "smart":
                return computer_turn_smart(showing, winnings, previous_guesses, turn)
            elif player_type == "conservative":
                return computer_turn_smart_conservative(showing, winnings, previous_guesses, turn)
            elif player_type == "aggressive":
                return computer_turn_smart_aggressive(showing, winnings, previous_guesses, turn)
            else:
                return self.basic_ai_move(showing, winnings, previous_guesses, turn)
        except Exception as e:
            print(f"AI move error: {e}")
            return self.basic_ai_move(showing, winnings, previous_guesses, turn)
    
    def basic_ai_move(self, showing, winnings, previous_guesses, turn):
        """Basic AI move as fallback."""
        alphabet = "ETAINOSHRDLUCMFWYGPBVKQJXZ"
        
        for char in alphabet:
            if char in previous_guesses:
                continue
            
            if self.is_vowel(char):
                if winnings[turn % 3] >= 250:
                    return char, 0  # Buy vowel
            else:
                dollar = self.spin_wheel()
                if dollar == 0:
                    return "_", 0  # Lost turn
                elif dollar == -1:
                    return "_", -1  # Bankrupt
                else:
                    return char, dollar
        
        return "_", 0  # No valid moves
    
    def get_hint(self, puzzle, category, difficulty, showing):
        """Get a hint from the AI system."""
        if not self.hint_ai:
            return {
                'success': False,
                'hint': 'Hint system not available',
                'hints_remaining': 0
            }
        
        return self.hint_ai.generate_hint(puzzle, category, difficulty, showing)

# Global game engine
game_engine = WebGameEngine()

@app.route('/')
def index():
    """Main game page."""
    return render_template('wheel_of_fortune.html')

@app.route('/api/new_game', methods=['POST'])
def new_game():
    """Start a new game."""
    data = request.json
    player_types = data.get('player_types', ['human', 'smart', 'conservative'])
    
    # Get random puzzle
    puzzle_data = game_engine.get_random_puzzle()
    
    # Initialize game state
    session['puzzle'] = puzzle_data['puzzle']
    session['clue'] = puzzle_data['clue']
    session['showing'] = game_engine.create_showing(puzzle_data['puzzle'])
    session['previous_guesses'] = []
    session['current_turn'] = 0
    session['winnings'] = [0, 0, 0]
    session['player_types'] = player_types
    session['is_active'] = True
    
    # Reset hint AI
    if game_engine.hint_ai:
        game_engine.hint_ai.reset_game()
    
    return jsonify({
        'success': True,
        'clue': puzzle_data['clue'],
        'showing': session['showing'],
        'winnings': session['winnings'],
        'current_turn': session['current_turn'],
        'previous_guesses': session['previous_guesses'],
        'hints_remaining': game_engine.hint_ai.get_hints_remaining() if game_engine.hint_ai else 0
    })

@app.route('/api/spin_wheel', methods=['POST'])
def spin_wheel():
    """Spin the wheel."""
    if not session.get('is_active'):
        return jsonify({'success': False, 'message': 'Game not active'})
    
    value = game_engine.spin_wheel()
    
    return jsonify({
        'success': True,
        'value': value,
        'message': f'Wheel landed on: {value}' if value > 0 else 
                  'BANKRUPT!' if value == -1 else 'LOSE A TURN!'
    })

@app.route('/api/guess_letter', methods=['POST'])
def guess_letter():
    """Process a letter guess."""
    if not session.get('is_active'):
        return jsonify({'success': False, 'message': 'Game not active'})
    
    data = request.json
    guess = data.get('guess', '').upper()
    dollar_value = data.get('dollar_value', 0)
    
    if not guess or len(guess) != 1:
        return jsonify({'success': False, 'message': 'Invalid guess'})
    
    if guess in session['previous_guesses']:
        return jsonify({'success': False, 'message': 'Letter already guessed'})
    
    # Process guess
    session['previous_guesses'].append(guess)
    new_showing, count = game_engine.process_guess(session['puzzle'], session['showing'], guess)
    session['showing'] = new_showing
    
    # Update winnings
    if count > 0:
        earnings = dollar_value * count
        session['winnings'][session['current_turn'] % 3] += earnings
        message = f'Correct! Found {count} letter(s). Earned ${earnings}!'
        next_turn = False
    else:
        message = 'Not in the puzzle. Next player\'s turn.'
        next_turn = True
    
    # Check if puzzle is solved
    puzzle_solved = session['showing'] == session['puzzle']
    
    if next_turn and not puzzle_solved:
        session['current_turn'] += 1
    
    return jsonify({
        'success': True,
        'showing': session['showing'],
        'winnings': session['winnings'],
        'current_turn': session['current_turn'],
        'previous_guesses': session['previous_guesses'],
        'message': message,
        'puzzle_solved': puzzle_solved,
        'next_turn': next_turn
    })

@app.route('/api/buy_vowel', methods=['POST'])
def buy_vowel():
    """Buy a vowel."""
    if not session.get('is_active'):
        return jsonify({'success': False, 'message': 'Game not active'})
    
    data = request.json
    vowel = data.get('vowel', '').upper()
    
    if not vowel or vowel not in 'AEIOU':
        return jsonify({'success': False, 'message': 'Invalid vowel'})
    
    if vowel in session['previous_guesses']:
        return jsonify({'success': False, 'message': 'Vowel already guessed'})
    
    current_player = session['current_turn'] % 3
    if session['winnings'][current_player] < 250:
        return jsonify({'success': False, 'message': 'Insufficient funds'})
    
    # Deduct cost
    session['winnings'][current_player] -= 250
    
    # Process vowel
    session['previous_guesses'].append(vowel)
    new_showing, count = game_engine.process_guess(session['puzzle'], session['showing'], vowel)
    session['showing'] = new_showing
    
    message = f'Bought vowel {vowel}. Found {count} letter(s)!' if count > 0 else f'Bought vowel {vowel}. Not in puzzle.'
    next_turn = count == 0
    
    # Check if puzzle is solved
    puzzle_solved = session['showing'] == session['puzzle']
    
    if next_turn and not puzzle_solved:
        session['current_turn'] += 1
    
    return jsonify({
        'success': True,
        'showing': session['showing'],
        'winnings': session['winnings'],
        'current_turn': session['current_turn'],
        'previous_guesses': session['previous_guesses'],
        'message': message,
        'puzzle_solved': puzzle_solved,
        'next_turn': next_turn
    })

@app.route('/api/solve_puzzle', methods=['POST'])
def solve_puzzle():
    """Attempt to solve the puzzle."""
    if not session.get('is_active'):
        return jsonify({'success': False, 'message': 'Game not active'})
    
    data = request.json
    solution = data.get('solution', '').upper().strip()
    
    if solution == session['puzzle']:
        session['showing'] = session['puzzle']
        session['is_active'] = False
        return jsonify({
            'success': True,
            'correct': True,
            'showing': session['showing'],
            'message': 'Correct! You solved the puzzle!',
            'puzzle_solved': True
        })
    else:
        session['current_turn'] += 1
        return jsonify({
            'success': True,
            'correct': False,
            'current_turn': session['current_turn'],
            'message': 'Incorrect solution. Next player\'s turn.',
            'puzzle_solved': False
        })

@app.route('/api/get_hint', methods=['POST'])
def get_hint():
    """Get a hint from the AI system."""
    if not session.get('is_active'):
        return jsonify({'success': False, 'message': 'Game not active'})
    
    data = request.json
    difficulty = data.get('difficulty', 'medium')
    
    hint_result = game_engine.get_hint(
        session['puzzle'], 
        session['clue'], 
        difficulty, 
        session['showing']
    )
    
    return jsonify(hint_result)

@app.route('/api/ai_turn', methods=['POST'])
def ai_turn():
    """Process an AI player's turn."""
    if not session.get('is_active'):
        return jsonify({'success': False, 'message': 'Game not active'})
    
    current_player = session['current_turn'] % 3
    player_type = session['player_types'][current_player]
    
    if player_type == 'human':
        return jsonify({'success': False, 'message': 'Not an AI turn'})
    
    # Get AI move
    guess, dollar = game_engine.get_ai_move(
        player_type,
        session['showing'],
        session['winnings'],
        session['previous_guesses'],
        session['current_turn']
    )
    
    if guess == "_":
        # AI lost turn or went bankrupt
        if dollar == -1:
            session['winnings'][current_player] = 0
            message = f"{player_type.title()} AI went BANKRUPT!"
        else:
            message = f"{player_type.title()} AI lost a turn."
        
        session['current_turn'] += 1
        return jsonify({
            'success': True,
            'message': message,
            'winnings': session['winnings'],
            'current_turn': session['current_turn'],
            'next_turn': True
        })
    
    # Process AI guess
    if guess in session['previous_guesses']:
        session['current_turn'] += 1
        return jsonify({
            'success': True,
            'message': f"{player_type.title()} AI guessed already used letter. Next turn.",
            'current_turn': session['current_turn'],
            'next_turn': True
        })
    
    session['previous_guesses'].append(guess)
    new_showing, count = game_engine.process_guess(session['puzzle'], session['showing'], guess)
    session['showing'] = new_showing
    
    if count > 0:
        earnings = dollar * count
        session['winnings'][current_player] += earnings
        message = f"{player_type.title()} AI guessed {guess} - Correct! Found {count} letter(s). Earned ${earnings}!"
        next_turn = False
    else:
        message = f"{player_type.title()} AI guessed {guess} - Not in puzzle. Next turn."
        next_turn = True
        session['current_turn'] += 1
    
    # Check if puzzle is solved
    puzzle_solved = session['showing'] == session['puzzle']
    if puzzle_solved:
        session['is_active'] = False
    
    return jsonify({
        'success': True,
        'showing': session['showing'],
        'winnings': session['winnings'],
        'current_turn': session['current_turn'],
        'previous_guesses': session['previous_guesses'],
        'message': message,
        'puzzle_solved': puzzle_solved,
        'next_turn': next_turn,
        'ai_guess': guess
    })

@app.route('/api/game_state', methods=['GET'])
def game_state():
    """Get current game state."""
    return jsonify({
        'puzzle': session.get('puzzle', ''),
        'clue': session.get('clue', ''),
        'showing': session.get('showing', ''),
        'previous_guesses': session.get('previous_guesses', []),
        'current_turn': session.get('current_turn', 0),
        'winnings': session.get('winnings', [0, 0, 0]),
        'player_types': session.get('player_types', ['human', 'smart', 'conservative']),
        'is_active': session.get('is_active', False),
        'hints_remaining': game_engine.hint_ai.get_hints_remaining() if game_engine.hint_ai else 0
    })

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    print("🌐 Starting Wheel of Fortune Web GUI...")
    print("🎮 Open your browser to: http://localhost:12000")
    app.run(host='0.0.0.0', port=12000, debug=False)