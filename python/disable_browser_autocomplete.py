#!/usr/bin/env python3
"""
Disable Browser Autocomplete
MTG Quiz App - Disable native browser autocomplete to prevent interference with custom autocomplete

Fix: Add autoComplete="off" to input field to disable browser autocomplete
Keeps: All existing functionality and custom Scryfall autocomplete

Run from project root: python python/disable_browser_autocomplete.py
"""

import os
import sys

def update_card_guessing_game_component():
    """Update CardGuessingGame to disable browser autocomplete on input"""
    
    # Read the current file
    file_path = 'src/components/CardGuessingGame.tsx'
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: {file_path} not found")
        return False
    
    # Find and replace the input element to add autoComplete="off"
    old_input = '''<input
                  ref={inputRef}
                  id="guess-input"
                  type="text"
                  value={guessInput}
                  onChange={(e) => handleInputChange(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Start typing a card name..."
                  className="w-full p-4 text-lg border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />'''
    
    new_input = '''<input
                  ref={inputRef}
                  id="guess-input"
                  type="text"
                  value={guessInput}
                  onChange={(e) => handleInputChange(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Start typing a card name..."
                  autoComplete="off"
                  className="w-full p-4 text-lg border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />'''
    
    # Replace the input element
    if old_input in content:
        updated_content = content.replace(old_input, new_input)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            return True
        except Exception as e:
            print(f"Error writing to {file_path}: {e}")
            return False
    else:
        print("Error: Could not find the input element to update")
        return False

def main():
    """Main execution function"""
    
    print("🚫 Disabling Browser Autocomplete")
    print("=" * 35)
    
    # Check if we're in the right directory
    if not os.path.exists('src'):
        print("❌ Error: Not in project root directory (src/ not found)")
        return 1
    
    print("\n1. Updating CardGuessingGame.tsx...")
    if update_card_guessing_game_component():
        print("✅ Updated CardGuessingGame.tsx:")
        print("   • Added autoComplete=\"off\" to input field")
        print("   • Disables browser's native autocomplete")
        print("   • Prevents interference with custom Scryfall autocomplete")
        print("   • Maintains all existing functionality")
    else:
        print("❌ Failed to update CardGuessingGame.tsx")
        return 1
    
    print("\n" + "=" * 35)
    print("✅ SUCCESS! Browser autocomplete disabled.")
    print("\n🚫 The input field will now only show your custom autocomplete!")
    print("   • No more browser history suggestions")
    print("   • Clean Scryfall autocomplete experience")
    print("   • No conflicting dropdown menus")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
