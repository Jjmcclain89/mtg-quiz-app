#!/usr/bin/env python3
"""
Remove Autocomplete Debounce
MTG Quiz App - Remove the 300ms debounce delay from autocomplete requests for instant response

Change: Make autocomplete requests immediately when user types instead of waiting 300ms
Keeps: All other autocomplete functionality and keyboard navigation

Run from project root: python python/remove_autocomplete_debounce.py
"""

import os
import sys

def update_card_guessing_game_component():
    """Update CardGuessingGame to remove debounce from autocomplete"""
    
    # Read the current file
    file_path = 'src/components/CardGuessingGame.tsx'
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: {file_path} not found")
        return False
    
    # Find and replace the autocomplete useEffect to remove debouncing
    old_autocomplete_effect = '''  // Autocomplete functionality with debouncing
  useEffect(() => {
    // Clear existing timeout
    if (autocompleteTimeoutRef.current) {
      clearTimeout(autocompleteTimeoutRef.current);
    }

    // Don't show autocomplete if guess is submitted or input is empty
    if (gameState.isGuessSubmitted || guessInput.length < 2) {
      setShowAutocomplete(false);
      setAutocompleteOptions([]);
      setHighlightedIndex(-1);
      return;
    }

    // Debounce autocomplete requests
    autocompleteTimeoutRef.current = setTimeout(async () => {
      try {
        setIsLoadingAutocomplete(true);
        const suggestions = await getCardNameAutocomplete(guessInput);
        setAutocompleteOptions(suggestions.slice(0, 8)); // Limit to 8 suggestions
        setShowAutocomplete(suggestions.length > 0);
      } catch (error) {
        console.error('Autocomplete error:', error);
        setAutocompleteOptions([]);
        setShowAutocomplete(false);
      } finally {
        setIsLoadingAutocomplete(false);
      }
    }, 300);

    return () => {
      if (autocompleteTimeoutRef.current) {
        clearTimeout(autocompleteTimeoutRef.current);
      }
    };
  }, [guessInput, gameState.isGuessSubmitted]);'''
    
    new_autocomplete_effect = '''  // Autocomplete functionality - immediate response
  useEffect(() => {
    // Don't show autocomplete if guess is submitted or input is empty
    if (gameState.isGuessSubmitted || guessInput.length < 2) {
      setShowAutocomplete(false);
      setAutocompleteOptions([]);
      setHighlightedIndex(-1);
      return;
    }

    // Make autocomplete request immediately
    const fetchAutocomplete = async () => {
      try {
        setIsLoadingAutocomplete(true);
        const suggestions = await getCardNameAutocomplete(guessInput);
        setAutocompleteOptions(suggestions.slice(0, 8)); // Limit to 8 suggestions
        setShowAutocomplete(suggestions.length > 0);
      } catch (error) {
        console.error('Autocomplete error:', error);
        setAutocompleteOptions([]);
        setShowAutocomplete(false);
      } finally {
        setIsLoadingAutocomplete(false);
      }
    };

    fetchAutocomplete();
  }, [guessInput, gameState.isGuessSubmitted]);'''
    
    # Replace the autocomplete effect
    if old_autocomplete_effect in content:
        updated_content = content.replace(old_autocomplete_effect, new_autocomplete_effect)
        
        # Also remove the autocompleteTimeoutRef since we're not using it anymore
        # Remove the ref declaration
        updated_content = updated_content.replace(
            '  const autocompleteTimeoutRef = useRef<NodeJS.Timeout>();',
            ''
        )
        
        # Remove timeout cleanup in loadNewCard function
        updated_content = updated_content.replace(
            '''      // Reset input
      setGuessInput('');
      setShowAutocomplete(false);
      setAutocompleteOptions([]);
      setHighlightedIndex(-1);''',
            '''      // Reset input
      setGuessInput('');
      setShowAutocomplete(false);
      setAutocompleteOptions([]);
      setHighlightedIndex(-1);'''
        )
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            return True
        except Exception as e:
            print(f"Error writing to {file_path}: {e}")
            return False
    else:
        print("Error: Could not find the autocomplete effect to update")
        return False

def main():
    """Main execution function"""
    
    print("⚡ Removing Autocomplete Debounce")
    print("=" * 35)
    
    # Check if we're in the right directory
    if not os.path.exists('src'):
        print("❌ Error: Not in project root directory (src/ not found)")
        return 1
    
    print("\n1. Updating CardGuessingGame.tsx...")
    if update_card_guessing_game_component():
        print("✅ Updated CardGuessingGame.tsx:")
        print("   • Removed 300ms debounce delay")
        print("   • Autocomplete requests now fire immediately")
        print("   • Removed autocompleteTimeoutRef")
        print("   • Simplified autocomplete logic")
        print("   • Maintains all keyboard navigation features")
    else:
        print("❌ Failed to update CardGuessingGame.tsx")
        return 1
    
    print("\n" + "=" * 35)
    print("✅ SUCCESS! Autocomplete debounce removed.")
    print("\n⚡ Autocomplete now responds instantly as you type!")
    print("   • No more 300ms delay")
    print("   • Immediate feedback")
    print("   • Faster user experience")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
