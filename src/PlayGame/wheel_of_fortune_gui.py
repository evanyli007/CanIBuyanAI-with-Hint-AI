#!/usr/bin/env python3
"""
Wheel of Fortune GUI - A fully functional graphical interface for the Wheel of Fortune game.
Incorporates all existing features: AI players, hint system, smart decision making, etc.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import math
import random
import re
import threading
import time
from typing import List, Tuple, Optional, Dict, Any
import sys
import os

# Import existing game modules
from hint_ai import HintAI
from smart_player import computer_turn_smart, computer_turn_smart_conservative, computer_turn_smart_aggressive

class WheelOfFortuneGUI:
    """Main GUI class for Wheel of Fortune game."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Wheel of Fortune - AI Enhanced Edition")
        self.root.geometry("1200x800")
        self.root.configure(bg="#1e3a8a")  # Deep blue background
        
        # Game state
        self.puzzle = ""
        self.showing = ""
        self.clue = ""
        self.category = ""
        self.previous_guesses = []
        self.current_turn = 0
        self.winnings = [0, 0, 0]
        self.player_types = ["human", "smart", "conservative"]
        self.player_names = ["Human", "Smart AI", "Conservative AI"]
        self.is_game_active = False
        self.hint_ai = None
        self.game_thread = None
        self.wheel_spinning = False
        
        # Wheel configuration
        self.wheel_values = [0, -1, 500, 550, 600, 650, 700, 750, 800, 850, 900, -1, 
                           500, 550, 600, 650, 700, 750, 800, 850, 900, 500, 550, 600]
        self.wheel_colors = self._generate_wheel_colors()
        
        # GUI components
        self.setup_gui()
        self.setup_game()
        
    def _generate_wheel_colors(self) -> List[str]:
        """Generate colors for wheel segments."""
        colors = []
        for value in self.wheel_values:
            if value == -1:
                colors.append("#dc2626")  # Red for bankrupt
            elif value == 0:
                colors.append("#374151")  # Gray for lose turn
            elif value >= 800:
                colors.append("#059669")  # Green for high values
            elif value >= 600:
                colors.append("#2563eb")  # Blue for medium values
            else:
                colors.append("#7c3aed")  # Purple for lower values
        return colors
    
    def setup_gui(self):
        """Set up the main GUI layout."""
        # Main container
        main_frame = tk.Frame(self.root, bg="#1e3a8a")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top section: Game info and controls
        self.setup_top_section(main_frame)
        
        # Middle section: Puzzle board
        self.setup_puzzle_section(main_frame)
        
        # Bottom section: Wheel and player info
        self.setup_bottom_section(main_frame)
        
        # Status bar
        self.setup_status_bar(main_frame)
    
    def setup_top_section(self, parent):
        """Set up the top section with game controls and info."""
        top_frame = tk.Frame(parent, bg="#1e3a8a")
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Game title
        title_label = tk.Label(top_frame, text="🎡 WHEEL OF FORTUNE 🎡", 
                              font=("Arial", 24, "bold"), 
                              fg="#fbbf24", bg="#1e3a8a")
        title_label.pack(pady=5)
        
        # Control buttons frame
        controls_frame = tk.Frame(top_frame, bg="#1e3a8a")
        controls_frame.pack(pady=5)
        
        # New Game button
        self.new_game_btn = tk.Button(controls_frame, text="New Game", 
                                     command=self.start_new_game,
                                     font=("Arial", 12, "bold"),
                                     bg="#059669", fg="white",
                                     padx=20, pady=5)
        self.new_game_btn.pack(side=tk.LEFT, padx=5)
        
        # Player setup button
        self.setup_btn = tk.Button(controls_frame, text="Setup Players", 
                                  command=self.setup_players,
                                  font=("Arial", 12, "bold"),
                                  bg="#2563eb", fg="white",
                                  padx=20, pady=5)
        self.setup_btn.pack(side=tk.LEFT, padx=5)
        
        # Hint AI status
        self.hint_status_label = tk.Label(controls_frame, text="🤖 Hint AI: Ready", 
                                         font=("Arial", 10),
                                         fg="#10b981", bg="#1e3a8a")
        self.hint_status_label.pack(side=tk.RIGHT, padx=10)
    
    def setup_puzzle_section(self, parent):
        """Set up the puzzle display section."""
        puzzle_frame = tk.Frame(parent, bg="#1e3a8a", relief=tk.RAISED, bd=2)
        puzzle_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Category display
        self.category_label = tk.Label(puzzle_frame, text="Category: Loading...", 
                                      font=("Arial", 16, "bold"),
                                      fg="#fbbf24", bg="#1e3a8a")
        self.category_label.pack(pady=10)
        
        # Puzzle display area
        self.puzzle_frame = tk.Frame(puzzle_frame, bg="#1e3a8a")
        self.puzzle_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        
        # Previous guesses
        guesses_frame = tk.Frame(puzzle_frame, bg="#1e3a8a")
        guesses_frame.pack(pady=10)
        
        tk.Label(guesses_frame, text="Previous Guesses:", 
                font=("Arial", 12, "bold"), fg="white", bg="#1e3a8a").pack()
        
        self.guesses_label = tk.Label(guesses_frame, text="None", 
                                     font=("Arial", 14),
                                     fg="#94a3b8", bg="#1e3a8a")
        self.guesses_label.pack()
    
    def setup_bottom_section(self, parent):
        """Set up the bottom section with wheel and player info."""
        bottom_frame = tk.Frame(parent, bg="#1e3a8a")
        bottom_frame.pack(fill=tk.X, pady=10)
        
        # Left side: Wheel
        wheel_frame = tk.Frame(bottom_frame, bg="#1e3a8a")
        wheel_frame.pack(side=tk.LEFT, padx=20)
        
        tk.Label(wheel_frame, text="🎡 WHEEL", font=("Arial", 16, "bold"),
                fg="#fbbf24", bg="#1e3a8a").pack()
        
        # Wheel canvas
        self.wheel_canvas = tk.Canvas(wheel_frame, width=300, height=300, 
                                     bg="#374151", highlightthickness=2,
                                     highlightbackground="#fbbf24")
        self.wheel_canvas.pack(pady=10)
        
        # Spin button
        self.spin_btn = tk.Button(wheel_frame, text="🎯 SPIN WHEEL", 
                                 command=self.spin_wheel,
                                 font=("Arial", 14, "bold"),
                                 bg="#dc2626", fg="white",
                                 padx=20, pady=10,
                                 state=tk.DISABLED)
        self.spin_btn.pack(pady=5)
        
        # Right side: Players and controls
        players_frame = tk.Frame(bottom_frame, bg="#1e3a8a")
        players_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=20)
        
        self.setup_player_panels(players_frame)
        self.setup_human_controls(players_frame)
    
    def setup_player_panels(self, parent):
        """Set up player information panels."""
        tk.Label(parent, text="👥 PLAYERS", font=("Arial", 16, "bold"),
                fg="#fbbf24", bg="#1e3a8a").pack()
        
        self.player_panels = []
        for i in range(3):
            panel = tk.Frame(parent, bg="#374151", relief=tk.RAISED, bd=2)
            panel.pack(fill=tk.X, pady=5, padx=10)
            
            # Player name and type
            name_label = tk.Label(panel, text=f"Player {i+1}: {self.player_names[i]}", 
                                 font=("Arial", 12, "bold"),
                                 fg="white", bg="#374151")
            name_label.pack(anchor=tk.W, padx=10, pady=2)
            
            # Score
            score_label = tk.Label(panel, text="Score: $0", 
                                  font=("Arial", 11),
                                  fg="#10b981", bg="#374151")
            score_label.pack(anchor=tk.W, padx=10, pady=2)
            
            # Turn indicator
            turn_indicator = tk.Label(panel, text="", 
                                     font=("Arial", 10, "bold"),
                                     fg="#fbbf24", bg="#374151")
            turn_indicator.pack(anchor=tk.W, padx=10, pady=2)
            
            self.player_panels.append({
                'frame': panel,
                'name': name_label,
                'score': score_label,
                'turn': turn_indicator
            })
    
    def setup_human_controls(self, parent):
        """Set up human player control buttons."""
        controls_frame = tk.Frame(parent, bg="#1e3a8a")
        controls_frame.pack(fill=tk.X, pady=20)
        
        tk.Label(controls_frame, text="🎮 HUMAN CONTROLS", 
                font=("Arial", 14, "bold"),
                fg="#fbbf24", bg="#1e3a8a").pack()
        
        buttons_frame = tk.Frame(controls_frame, bg="#1e3a8a")
        buttons_frame.pack(pady=10)
        
        # Action buttons
        self.buy_vowel_btn = tk.Button(buttons_frame, text="💰 Buy Vowel ($250)", 
                                      command=self.buy_vowel,
                                      font=("Arial", 11, "bold"),
                                      bg="#7c3aed", fg="white",
                                      padx=15, pady=5,
                                      state=tk.DISABLED)
        self.buy_vowel_btn.pack(side=tk.LEFT, padx=5)
        
        self.solve_btn = tk.Button(buttons_frame, text="🎯 Solve Puzzle", 
                                  command=self.solve_puzzle,
                                  font=("Arial", 11, "bold"),
                                  bg="#059669", fg="white",
                                  padx=15, pady=5,
                                  state=tk.DISABLED)
        self.solve_btn.pack(side=tk.LEFT, padx=5)
        
        self.hint_btn = tk.Button(buttons_frame, text="💡 Get Hint", 
                                 command=self.get_hint,
                                 font=("Arial", 11, "bold"),
                                 bg="#f59e0b", fg="white",
                                 padx=15, pady=5,
                                 state=tk.DISABLED)
        self.hint_btn.pack(side=tk.LEFT, padx=5)
    
    def setup_status_bar(self, parent):
        """Set up the status bar."""
        self.status_bar = tk.Label(parent, text="Ready to play! Click 'New Game' to start.", 
                                  font=("Arial", 10),
                                  fg="white", bg="#374151",
                                  relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM, pady=(10, 0))
    
    def setup_game(self):
        """Initialize game components."""
        # Initialize Hint AI
        try:
            self.hint_ai = HintAI()
            if self.hint_ai.api_key:
                self.hint_status_label.config(text="🤖 Hint AI: OpenAI Ready", fg="#10b981")
            else:
                self.hint_status_label.config(text="🤖 Hint AI: Fallback Mode", fg="#f59e0b")
        except Exception as e:
            self.hint_status_label.config(text="🤖 Hint AI: Error", fg="#dc2626")
            print(f"Hint AI initialization error: {e}")
        
        # Draw initial wheel
        self.draw_wheel()
    
    def draw_wheel(self, highlight_segment: Optional[int] = None):
        """Draw the spinning wheel."""
        self.wheel_canvas.delete("all")
        
        center_x, center_y = 150, 150
        radius = 140
        
        # Calculate segment angle
        segment_angle = 360 / len(self.wheel_values)
        
        for i, (value, color) in enumerate(zip(self.wheel_values, self.wheel_colors)):
            start_angle = i * segment_angle
            
            # Highlight spinning segment
            if highlight_segment == i:
                color = "#fbbf24"  # Gold highlight
            
            # Draw segment
            self.wheel_canvas.create_arc(
                center_x - radius, center_y - radius,
                center_x + radius, center_y + radius,
                start=start_angle, extent=segment_angle,
                fill=color, outline="white", width=2
            )
            
            # Add text
            text_angle = math.radians(start_angle + segment_angle/2)
            text_x = center_x + (radius * 0.7) * math.cos(text_angle)
            text_y = center_y + (radius * 0.7) * math.sin(text_angle)
            
            # Format text
            if value == -1:
                text = "BANKRUPT"
                text_color = "white"
            elif value == 0:
                text = "LOSE\nTURN"
                text_color = "white"
            else:
                text = f"${value}"
                text_color = "white"
            
            self.wheel_canvas.create_text(text_x, text_y, text=text, 
                                        fill=text_color, font=("Arial", 8, "bold"))
        
        # Draw center circle and pointer
        self.wheel_canvas.create_oval(center_x-10, center_y-10, 
                                    center_x+10, center_y+10, 
                                    fill="#fbbf24", outline="white", width=2)
        
        # Draw pointer at top
        self.wheel_canvas.create_polygon(center_x, center_y-radius-10,
                                       center_x-10, center_y-radius+10,
                                       center_x+10, center_y-radius+10,
                                       fill="#dc2626", outline="white", width=2)
    
    def update_puzzle_display(self):
        """Update the puzzle display with current state."""
        # Clear existing puzzle display
        for widget in self.puzzle_frame.winfo_children():
            widget.destroy()
        
        if not self.showing:
            return
        
        words = self.showing.split(" ")
        
        for word_idx, word in enumerate(words):
            word_frame = tk.Frame(self.puzzle_frame, bg="#1e3a8a")
            word_frame.pack(pady=5)
            
            for char_idx, char in enumerate(word):
                if char == "_":
                    # Empty letter box
                    letter_frame = tk.Frame(word_frame, bg="white", 
                                          relief=tk.RAISED, bd=2,
                                          width=40, height=40)
                    letter_frame.pack(side=tk.LEFT, padx=2)
                    letter_frame.pack_propagate(False)
                else:
                    # Revealed letter
                    letter_frame = tk.Frame(word_frame, bg="#10b981", 
                                          relief=tk.RAISED, bd=2,
                                          width=40, height=40)
                    letter_frame.pack(side=tk.LEFT, padx=2)
                    letter_frame.pack_propagate(False)
                    
                    letter_label = tk.Label(letter_frame, text=char, 
                                          font=("Arial", 18, "bold"),
                                          fg="white", bg="#10b981")
                    letter_label.pack(expand=True)
    
    def update_player_display(self):
        """Update player information display."""
        for i, panel in enumerate(self.player_panels):
            # Update score
            panel['score'].config(text=f"Score: ${self.winnings[i]:,}")
            
            # Update turn indicator
            if i == self.current_turn % 3 and self.is_game_active:
                panel['turn'].config(text="👉 YOUR TURN", fg="#fbbf24")
                panel['frame'].config(bg="#4f46e5")  # Highlight current player
            else:
                panel['turn'].config(text="")
                panel['frame'].config(bg="#374151")
        
        # Update previous guesses
        if self.previous_guesses:
            guesses_text = " ".join(sorted(self.previous_guesses))
            self.guesses_label.config(text=guesses_text)
        else:
            self.guesses_label.config(text="None")
    
    def update_human_controls(self):
        """Update human control button states."""
        is_human_turn = (self.is_game_active and 
                        self.player_types[self.current_turn % 3] == "human")
        
        # Enable/disable buttons based on game state and player type
        if is_human_turn and not self.wheel_spinning:
            self.spin_btn.config(state=tk.NORMAL)
            self.solve_btn.config(state=tk.NORMAL)
            
            # Buy vowel only if player has enough money
            if self.winnings[self.current_turn % 3] >= 250:
                self.buy_vowel_btn.config(state=tk.NORMAL)
            else:
                self.buy_vowel_btn.config(state=tk.DISABLED)
            
            # Hint button only if hints available
            if self.hint_ai and self.hint_ai.get_hints_remaining() > 0:
                self.hint_btn.config(state=tk.NORMAL)
                self.hint_btn.config(text=f"💡 Get Hint ({self.hint_ai.get_hints_remaining()} left)")
            else:
                self.hint_btn.config(state=tk.DISABLED)
        else:
            self.spin_btn.config(state=tk.DISABLED)
            self.buy_vowel_btn.config(state=tk.DISABLED)
            self.solve_btn.config(state=tk.DISABLED)
            self.hint_btn.config(state=tk.DISABLED)
    
    def setup_players(self):
        """Open player setup dialog."""
        dialog = PlayerSetupDialog(self.root, self.player_types, self.player_names)
        if dialog.result:
            self.player_types, self.player_names = dialog.result
            # Update player panels
            for i, panel in enumerate(self.player_panels):
                panel['name'].config(text=f"Player {i+1}: {self.player_names[i]}")
            self.update_status("Player setup updated!")
    
    def start_new_game(self):
        """Start a new game."""
        if self.is_game_active:
            if not messagebox.askyesno("New Game", "A game is in progress. Start a new game?"):
                return
        
        # Get random puzzle
        puzzle_data = self.get_random_puzzle()
        if not puzzle_data:
            messagebox.showerror("Error", "Could not load puzzle data!")
            return
        
        self.puzzle, self.clue, _, _ = puzzle_data
        self.category = self.clue
        self.showing = re.sub(r"[A-Z]", "_", self.puzzle)
        self.previous_guesses = []
        self.current_turn = 0
        self.winnings = [0, 0, 0]
        self.is_game_active = True
        
        # Reset hint AI
        if self.hint_ai:
            self.hint_ai.reset_game()
        
        # Update display
        self.category_label.config(text=f"Category: {self.category}")
        self.update_puzzle_display()
        self.update_player_display()
        self.update_human_controls()
        
        self.update_status(f"New game started! Category: {self.category}")
        
        # Start game loop
        self.game_loop()
    
    def game_loop(self):
        """Main game loop - handles AI turns and game flow."""
        if not self.is_game_active:
            return
        
        # Check if puzzle is solved
        if self.showing == self.puzzle:
            self.end_game("Puzzle solved!")
            return
        
        current_player = self.player_types[self.current_turn % 3]
        
        if current_player == "human":
            # Human turn - wait for user input
            self.update_human_controls()
            self.update_status("Your turn! Choose an action.")
        else:
            # AI turn - process automatically
            self.update_status(f"{self.player_names[self.current_turn % 3]} is thinking...")
            self.root.after(1000, self.process_ai_turn)  # Delay for dramatic effect
    
    def process_ai_turn(self):
        """Process an AI player's turn."""
        if not self.is_game_active:
            return
        
        current_player = self.player_types[self.current_turn % 3]
        player_name = self.player_names[self.current_turn % 3]
        
        try:
            # Get AI decision
            if current_player == "smart":
                guess, dollar = computer_turn_smart(self.showing, self.winnings, 
                                                  self.previous_guesses, self.current_turn)
            elif current_player == "conservative":
                guess, dollar = computer_turn_smart_conservative(self.showing, self.winnings, 
                                                               self.previous_guesses, self.current_turn)
            elif current_player == "aggressive":
                guess, dollar = computer_turn_smart_aggressive(self.showing, self.winnings, 
                                                             self.previous_guesses, self.current_turn)
            else:
                # Fallback to basic AI
                guess, dollar = self.basic_ai_turn()
            
            # Process the guess
            self.process_guess(guess, dollar, f"{player_name} guessed: {guess}")
            
        except Exception as e:
            print(f"AI turn error: {e}")
            self.next_turn()
    
    def basic_ai_turn(self):
        """Basic AI turn logic as fallback."""
        alphabet = "ETAINOSHRDLUCMFWYGPBVKQJXZ"
        
        for char in alphabet:
            if char in self.previous_guesses:
                continue
            
            if self.is_vowel(char):
                if self.winnings[self.current_turn % 3] >= 250:
                    return char, 0  # Buy vowel
            else:
                dollar = random.choice(self.wheel_values)
                if dollar == 0:
                    return "_", 0  # Lost turn
                elif dollar == -1:
                    self.winnings[self.current_turn % 3] = 0
                    return "_", 0  # Bankrupt
                else:
                    return char, dollar
        
        return "_", 0  # No valid moves
    
    def spin_wheel(self):
        """Handle wheel spinning for human player."""
        if not self.is_game_active or self.wheel_spinning:
            return
        
        self.wheel_spinning = True
        self.update_human_controls()
        self.update_status("Spinning the wheel...")
        
        # Animate wheel spin
        self.animate_wheel_spin()
    
    def animate_wheel_spin(self):
        """Animate the wheel spinning."""
        spin_duration = 2.0  # seconds
        spin_steps = 20
        step_delay = int(spin_duration * 1000 / spin_steps)
        
        def spin_step(step):
            if step < spin_steps:
                # Highlight random segment during spin
                highlight = random.randint(0, len(self.wheel_values) - 1)
                self.draw_wheel(highlight)
                self.root.after(step_delay, lambda: spin_step(step + 1))
            else:
                # Final result
                result_value = random.choice(self.wheel_values)
                result_index = self.wheel_values.index(result_value)
                self.draw_wheel(result_index)
                
                # Process spin result
                self.process_spin_result(result_value)
        
        spin_step(0)
    
    def process_spin_result(self, dollar_value):
        """Process the result of a wheel spin."""
        self.wheel_spinning = False
        
        if dollar_value == -1:
            self.update_status("BANKRUPT! You lose all your money!")
            self.winnings[self.current_turn % 3] = 0
            self.next_turn()
        elif dollar_value == 0:
            self.update_status("LOSE A TURN! Next player's turn.")
            self.next_turn()
        else:
            self.update_status(f"You spun ${dollar_value}! Now guess a consonant.")
            self.get_consonant_guess(dollar_value)
    
    def get_consonant_guess(self, dollar_value):
        """Get consonant guess from human player."""
        consonants = "BCDFGHJKLMNPQRSTVWXYZ"
        available_consonants = [c for c in consonants if c not in self.previous_guesses]
        
        if not available_consonants:
            messagebox.showinfo("No Consonants", "No consonants left to guess!")
            self.next_turn()
            return
        
        # Create consonant selection dialog
        dialog = ConsonantDialog(self.root, available_consonants)
        if dialog.result:
            guess = dialog.result
            self.process_guess(guess, dollar_value, f"You guessed: {guess}")
        else:
            self.next_turn()
    
    def buy_vowel(self):
        """Handle buying a vowel."""
        if self.winnings[self.current_turn % 3] < 250:
            messagebox.showerror("Insufficient Funds", "You need at least $250 to buy a vowel!")
            return
        
        vowels = "AEIOU"
        available_vowels = [v for v in vowels if v not in self.previous_guesses]
        
        if not available_vowels:
            messagebox.showinfo("No Vowels", "No vowels left to buy!")
            return
        
        # Create vowel selection dialog
        dialog = VowelDialog(self.root, available_vowels)
        if dialog.result:
            guess = dialog.result
            self.winnings[self.current_turn % 3] -= 250
            self.process_guess(guess, 0, f"You bought vowel: {guess}")
        else:
            self.update_human_controls()
    
    def solve_puzzle(self):
        """Handle puzzle solving attempt."""
        solution = simpledialog.askstring("Solve Puzzle", 
                                         f"Enter your solution:\nCategory: {self.category}")
        if solution:
            solution = solution.upper().strip()
            if solution == self.puzzle:
                self.update_status("CORRECT! You solved the puzzle!")
                self.showing = self.puzzle
                self.update_puzzle_display()
                self.end_game(f"{self.player_names[self.current_turn % 3]} solved the puzzle!")
            else:
                self.update_status("Incorrect solution. Next player's turn.")
                self.next_turn()
    
    def get_hint(self):
        """Handle hint request."""
        if not self.hint_ai or self.hint_ai.get_hints_remaining() <= 0:
            messagebox.showinfo("No Hints", "No hints available!")
            return
        
        # Create hint difficulty dialog
        dialog = HintDialog(self.root)
        if dialog.result:
            difficulty = dialog.result
            self.update_status(f"Generating {difficulty} hint...")
            
            # Get hint from AI
            hint_result = self.hint_ai.generate_hint(self.puzzle, self.category, difficulty, self.showing)
            
            if hint_result['success']:
                messagebox.showinfo(f"{difficulty.title()} Hint", 
                                  f"💡 {hint_result['hint']}\n\n"
                                  f"Hints remaining: {hint_result['hints_remaining']}")
                self.update_status(f"Hint provided! {hint_result['hints_remaining']} hints left.")
            else:
                messagebox.showerror("Hint Error", "Could not generate hint.")
            
            self.update_human_controls()
    
    def process_guess(self, guess, dollar_value, message):
        """Process a letter guess."""
        if guess == "_":
            # Special case for lost turn/bankrupt
            self.next_turn()
            return
        
        if guess in self.previous_guesses:
            self.update_status("Letter already guessed! Next player's turn.")
            self.next_turn()
            return
        
        self.previous_guesses.append(guess)
        
        # Check if letter is in puzzle
        correct_positions = [i for i, char in enumerate(self.puzzle) if char == guess]
        
        if correct_positions:
            # Correct guess
            for pos in correct_positions:
                self.showing = self.showing[:pos] + guess + self.showing[pos + 1:]
            
            # Add winnings
            earnings = dollar_value * len(correct_positions)
            self.winnings[self.current_turn % 3] += earnings
            
            self.update_status(f"{message} - CORRECT! Found {len(correct_positions)} letter(s). "
                             f"Earned ${earnings}!")
            
            # Check if puzzle is solved
            if self.showing == self.puzzle:
                self.end_game(f"{self.player_names[self.current_turn % 3]} completed the puzzle!")
                return
        else:
            # Incorrect guess
            self.update_status(f"{message} - Not in the puzzle. Next player's turn.")
            self.next_turn()
            return
        
        # Update display
        self.update_puzzle_display()
        self.update_player_display()
        
        # Continue with same player if correct
        self.root.after(2000, self.game_loop)
    
    def next_turn(self):
        """Move to the next player's turn."""
        self.current_turn += 1
        self.update_player_display()
        self.update_human_controls()
        self.root.after(1000, self.game_loop)
    
    def end_game(self, message):
        """End the current game."""
        self.is_game_active = False
        self.update_human_controls()
        
        # Show final results
        winner_idx = self.winnings.index(max(self.winnings))
        winner_name = self.player_names[winner_idx]
        winner_score = self.winnings[winner_idx]
        
        result_message = f"{message}\n\n"
        result_message += f"🏆 WINNER: {winner_name} with ${winner_score:,}!\n\n"
        result_message += "Final Scores:\n"
        for i, (name, score) in enumerate(zip(self.player_names, self.winnings)):
            result_message += f"{name}: ${score:,}\n"
        
        messagebox.showinfo("Game Over", result_message)
        self.update_status("Game ended. Click 'New Game' to play again!")
    
    def get_random_puzzle(self):
        """Get a random puzzle from the data file."""
        try:
            puzzle_file = "../../data/puzzles/valid.csv"
            if not os.path.exists(puzzle_file):
                # Try alternative path
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
                return puzzle, clue, date, game_type
            
        except Exception as e:
            print(f"Error loading puzzle: {e}")
        
        # Fallback puzzle
        return "WHEEL OF FORTUNE", "TV Show", "2024", "Toss Up"
    
    def is_vowel(self, letter):
        """Check if a letter is a vowel."""
        return letter.upper() in "AEIOU"
    
    def update_status(self, message):
        """Update the status bar."""
        self.status_bar.config(text=message)
        self.root.update_idletasks()
    
    def run(self):
        """Start the GUI application."""
        self.root.mainloop()


class PlayerSetupDialog:
    """Dialog for setting up players."""
    
    def __init__(self, parent, current_types, current_names):
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Setup Players")
        self.dialog.geometry("400x300")
        self.dialog.configure(bg="#1e3a8a")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.player_types = current_types.copy()
        self.player_names = current_names.copy()
        
        self.setup_dialog()
    
    def setup_dialog(self):
        """Set up the dialog interface."""
        tk.Label(self.dialog, text="Player Setup", font=("Arial", 16, "bold"),
                fg="#fbbf24", bg="#1e3a8a").pack(pady=10)
        
        # Player type options
        type_options = ["human", "smart", "conservative", "aggressive", "morse", "oxford", "trigram"]
        
        self.type_vars = []
        for i in range(3):
            frame = tk.Frame(self.dialog, bg="#374151", relief=tk.RAISED, bd=2)
            frame.pack(fill=tk.X, padx=20, pady=5)
            
            tk.Label(frame, text=f"Player {i+1}:", font=("Arial", 12, "bold"),
                    fg="white", bg="#374151").pack(anchor=tk.W, padx=10, pady=5)
            
            type_var = tk.StringVar(value=self.player_types[i])
            type_combo = ttk.Combobox(frame, textvariable=type_var, values=type_options,
                                     state="readonly", width=15)
            type_combo.pack(anchor=tk.W, padx=10, pady=5)
            
            self.type_vars.append(type_var)
        
        # Buttons
        button_frame = tk.Frame(self.dialog, bg="#1e3a8a")
        button_frame.pack(pady=20)
        
        tk.Button(button_frame, text="OK", command=self.ok_clicked,
                 bg="#059669", fg="white", padx=20, pady=5).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cancel", command=self.cancel_clicked,
                 bg="#dc2626", fg="white", padx=20, pady=5).pack(side=tk.LEFT, padx=5)
    
    def ok_clicked(self):
        """Handle OK button click."""
        new_types = [var.get() for var in self.type_vars]
        new_names = []
        
        for player_type in new_types:
            if player_type == "human":
                new_names.append("Human")
            elif player_type == "smart":
                new_names.append("Smart AI")
            elif player_type == "conservative":
                new_names.append("Conservative AI")
            elif player_type == "aggressive":
                new_names.append("Aggressive AI")
            elif player_type == "morse":
                new_names.append("Morse AI")
            elif player_type == "oxford":
                new_names.append("Oxford AI")
            elif player_type == "trigram":
                new_names.append("Trigram AI")
            else:
                new_names.append(f"{player_type.title()} AI")
        
        self.result = (new_types, new_names)
        self.dialog.destroy()
    
    def cancel_clicked(self):
        """Handle Cancel button click."""
        self.dialog.destroy()


class ConsonantDialog:
    """Dialog for selecting a consonant."""
    
    def __init__(self, parent, available_consonants):
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Choose Consonant")
        self.dialog.geometry("300x200")
        self.dialog.configure(bg="#1e3a8a")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_dialog(available_consonants)
    
    def setup_dialog(self, consonants):
        """Set up the consonant selection dialog."""
        tk.Label(self.dialog, text="Choose a Consonant:", font=("Arial", 14, "bold"),
                fg="#fbbf24", bg="#1e3a8a").pack(pady=10)
        
        # Create buttons for each consonant
        button_frame = tk.Frame(self.dialog, bg="#1e3a8a")
        button_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)
        
        for i, consonant in enumerate(consonants):
            row = i // 5
            col = i % 5
            
            btn = tk.Button(button_frame, text=consonant, 
                           command=lambda c=consonant: self.select_consonant(c),
                           font=("Arial", 12, "bold"),
                           bg="#2563eb", fg="white",
                           width=3, height=2)
            btn.grid(row=row, col=col, padx=2, pady=2)
        
        # Cancel button
        tk.Button(self.dialog, text="Cancel", command=self.cancel,
                 bg="#dc2626", fg="white", padx=20, pady=5).pack(pady=10)
    
    def select_consonant(self, consonant):
        """Handle consonant selection."""
        self.result = consonant
        self.dialog.destroy()
    
    def cancel(self):
        """Handle cancel."""
        self.dialog.destroy()


class VowelDialog:
    """Dialog for selecting a vowel."""
    
    def __init__(self, parent, available_vowels):
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Buy Vowel ($250)")
        self.dialog.geometry("250x150")
        self.dialog.configure(bg="#1e3a8a")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_dialog(available_vowels)
    
    def setup_dialog(self, vowels):
        """Set up the vowel selection dialog."""
        tk.Label(self.dialog, text="Buy a Vowel ($250):", font=("Arial", 14, "bold"),
                fg="#fbbf24", bg="#1e3a8a").pack(pady=10)
        
        # Create buttons for each vowel
        button_frame = tk.Frame(self.dialog, bg="#1e3a8a")
        button_frame.pack(pady=10)
        
        for vowel in vowels:
            btn = tk.Button(button_frame, text=vowel, 
                           command=lambda v=vowel: self.select_vowel(v),
                           font=("Arial", 12, "bold"),
                           bg="#7c3aed", fg="white",
                           width=3, height=2)
            btn.pack(side=tk.LEFT, padx=5)
        
        # Cancel button
        tk.Button(self.dialog, text="Cancel", command=self.cancel,
                 bg="#dc2626", fg="white", padx=20, pady=5).pack(pady=10)
    
    def select_vowel(self, vowel):
        """Handle vowel selection."""
        self.result = vowel
        self.dialog.destroy()
    
    def cancel(self):
        """Handle cancel."""
        self.dialog.destroy()


class HintDialog:
    """Dialog for selecting hint difficulty."""
    
    def __init__(self, parent):
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Get Hint")
        self.dialog.geometry("300x200")
        self.dialog.configure(bg="#1e3a8a")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_dialog()
    
    def setup_dialog(self):
        """Set up the hint difficulty dialog."""
        tk.Label(self.dialog, text="Choose Hint Difficulty:", font=("Arial", 14, "bold"),
                fg="#fbbf24", bg="#1e3a8a").pack(pady=10)
        
        # Difficulty buttons
        difficulties = [
            ("🟢 Easy", "easy", "More direct guidance"),
            ("🟡 Medium", "medium", "Crossword-style clue"),
            ("🔴 Hard", "hard", "Cryptic wordplay")
        ]
        
        for emoji_text, difficulty, description in difficulties:
            frame = tk.Frame(self.dialog, bg="#1e3a8a")
            frame.pack(pady=5)
            
            btn = tk.Button(frame, text=emoji_text, 
                           command=lambda d=difficulty: self.select_difficulty(d),
                           font=("Arial", 12, "bold"),
                           bg="#f59e0b", fg="white",
                           width=15, height=2)
            btn.pack()
            
            tk.Label(frame, text=description, font=("Arial", 9),
                    fg="#94a3b8", bg="#1e3a8a").pack()
        
        # Cancel button
        tk.Button(self.dialog, text="Cancel", command=self.cancel,
                 bg="#dc2626", fg="white", padx=20, pady=5).pack(pady=10)
    
    def select_difficulty(self, difficulty):
        """Handle difficulty selection."""
        self.result = difficulty
        self.dialog.destroy()
    
    def cancel(self):
        """Handle cancel."""
        self.dialog.destroy()


def main():
    """Main function to run the GUI."""
    try:
        app = WheelOfFortuneGUI()
        app.run()
    except Exception as e:
        print(f"Error starting GUI: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()