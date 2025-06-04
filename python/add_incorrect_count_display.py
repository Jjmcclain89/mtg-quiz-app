#!/usr/bin/env python3
"""
Add Incorrect Count Display
MTG Quiz App - Add an "Incorrect" count to the score display header

Adds: A 4th stat showing number of incorrect answers (totalGuesses - score)
Changes: Updates grid from 3 columns to 4 columns in the score display

Run from project root: python python/add_incorrect_count_display.py
"""

import os
import sys

def update_card_guessing_game_component():
    """Update CardGuessingGame to add incorrect count display"""
    
    # Read the current file
    file_path = 'src/components/CardGuessingGame.tsx'
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: {file_path} not found")
        return False
    
    # Find the current score display section and replace it
    old_score_display = '''          {/* Score Display */}
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold text-green-600">{gameState.score}</div>
              <div className="text-sm text-gray-600">Correct</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-blue-600">{gameState.streak}</div>
              <div className="text-sm text-gray-600">Streak</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-600">{accuracy}%</div>
              <div className="text-sm text-gray-600">Accuracy</div>
            </div>
          </div>'''
    
    new_score_display = '''          {/* Score Display */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold text-green-600">{gameState.score}</div>
              <div className="text-sm text-gray-600">Correct</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-red-600">{gameState.totalGuesses - gameState.score}</div>
              <div className="text-sm text-gray-600">Incorrect</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-blue-600">{gameState.streak}</div>
              <div className="text-sm text-gray-600">Streak</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-600">{accuracy}%</div>
              <div className="text-sm text-gray-600">Accuracy</div>
            </div>
          </div>'''
    
    # Replace the score display section
    if old_score_display in content:
        updated_content = content.replace(old_score_display, new_score_display)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            return True
        except Exception as e:
            print(f"Error writing to {file_path}: {e}")
            return False
    else:
        print("Error: Could not find the score display section to update")
        return False

def main():
    """Main execution function"""
    
    print("🔢 Adding Incorrect Count Display")
    print("=" * 35)
    
    # Check if we're in the right directory
    if not os.path.exists('src'):
        print("❌ Error: Not in project root directory (src/ not found)")
        return 1
    
    print("\n1. Updating CardGuessingGame.tsx...")
    if update_card_guessing_game_component():
        print("✅ Updated CardGuessingGame.tsx:")
        print("   • Added 'Incorrect' count display (red)")
        print("   • Changed grid to 4 columns (2 on mobile, 4 on desktop)")
        print("   • Shows: Correct | Incorrect | Streak | Accuracy")
        print("   • Incorrect count = totalGuesses - score")
        print("   • Responsive layout for mobile devices")
    else:
        print("❌ Failed to update CardGuessingGame.tsx")
        return 1
    
    print("\n" + "=" * 35)
    print("✅ SUCCESS! Incorrect count added to stats.")
    print("\n🔢 Stats now show: Correct | Incorrect | Streak | Accuracy")
    print("   • Incorrect count in red")
    print("   • Mobile-friendly 2x2 grid")
    print("   • Desktop 4-column layout")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
