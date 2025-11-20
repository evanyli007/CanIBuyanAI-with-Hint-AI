#!/usr/bin/env python3
"""
Launcher script for Wheel of Fortune GUI.
Handles different environments and provides fallback options.
"""

import sys
import os

def check_display():
    """Check if GUI display is available."""
    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()  # Hide the window
        root.destroy()
        return True
    except Exception as e:
        print(f"GUI display not available: {e}")
        return False

def launch_gui():
    """Launch the GUI application."""
    if not check_display():
        print("❌ GUI display not available in this environment.")
        print("🌐 Consider using the web version instead!")
        print("\nTo run the GUI on your local machine:")
        print("1. Copy the project to your local computer")
        print("2. Install Python 3.6+ with tkinter support")
        print("3. Run: python wheel_of_fortune_gui.py")
        print("\nOr use the terminal version:")
        print("python play_random_puzzle.py human smart conservative")
        return False
    
    try:
        from wheel_of_fortune_gui import WheelOfFortuneGUI
        print("🎡 Starting Wheel of Fortune GUI...")
        app = WheelOfFortuneGUI()
        app.run()
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all required modules are available.")
        return False
    except Exception as e:
        print(f"❌ Error starting GUI: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main launcher function."""
    print("🎮 WHEEL OF FORTUNE - GUI LAUNCHER")
    print("=" * 40)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--force":
        print("🔧 Force mode: Attempting to launch GUI...")
        try:
            from wheel_of_fortune_gui import WheelOfFortuneGUI
            app = WheelOfFortuneGUI()
            app.run()
        except Exception as e:
            print(f"❌ Force launch failed: {e}")
    else:
        launch_gui()

if __name__ == "__main__":
    main()