#!/usr/bin/env python3
"""
Remove Black Hint Overlay
MTG Quiz App - Remove the black overlay that shows set and mana cost information

Removes: The black hint text overlay that appears over the card image when guess is submitted
Keeps: All other functionality including the colored name overlay and result messages

Run from project root: python python/remove_black_hint_overlay.py
"""

import os
import sys

def update_card_guessing_game_component():
    """Update CardGuessingGame to remove the black hint overlay"""
    
    # Read the current file
    file_path = 'src/components/CardGuessingGame.tsx'
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: {file_path} not found")
        return False
    
    # Find and remove the hint text overlay block
    hint_overlay_block = '''                
                {/* Hint text overlay when guess is submitted */}
                {gameState.isGuessSubmitted && (
                  <div className="absolute top-2 left-2 right-2 bg-black bg-opacity-75 text-white p-2 rounded text-sm">
                    <p><span className="font-medium">Set:</span> {gameState.currentCard.set_name}</p>
                    {gameState.currentCard.mana_cost && (
                      <p><span className="font-medium">Cost:</span> {gameState.currentCard.mana_cost}</p>
                    )}
                  </div>
                )}'''
    
    # Remove the hint overlay block
    if hint_overlay_block in content:
        updated_content = content.replace(hint_overlay_block, '')
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            return True
        except Exception as e:
            print(f"Error writing to {file_path}: {e}")
            return False
    else:
        print("Error: Could not find the hint overlay block to remove")
        return False

def main():
    """Main execution function"""
    
    print("🚫 Removing Black Hint Overlay")
    print("=" * 30)
    
    # Check if we're in the right directory
    if not os.path.exists('src'):
        print("❌ Error: Not in project root directory (src/ not found)")
        return 1
    
    print("\n1. Updating CardGuessingGame.tsx...")
    if update_card_guessing_game_component():
        print("✅ Updated CardGuessingGame.tsx:")
        print("   • Removed black hint overlay completely")
        print("   • No more set/mana cost display over card image")
        print("   • Card image will be clean after guess submission")
        print("   • Colored name overlay still works normally")
        print("   • Result messages below card still show")
    else:
        print("❌ Failed to update CardGuessingGame.tsx")
        return 1
    
    print("\n" + "=" * 30)
    print("✅ SUCCESS! Black overlay removed.")
    print("\n🚫 No more black hint overlay when skipping or submitting!")
    print("   • Clean card image display")
    print("   • Full card visible after guess")
    print("   • Results still show below card")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
