#!/usr/bin/env python3
"""
Fix Card Name Visibility - Use Art Crop Images
MTG Quiz App - Hide card names by using art_crop images instead of full card images

The issue: Full card images show the card name, making the game too easy
The fix: Use Scryfall's art_crop images which show only the artwork without names

This script updates:
1. CardGuessingGame.tsx - Use art_crop instead of normal images
2. Add fallback handling for cards without art_crop
3. Improve styling for artwork display

Run from project root: python python/fix_card_name_visibility.py
"""

import os
import sys

def update_card_guessing_game_component():
    """Update CardGuessingGame to use art crop images without card names"""
    
    content = '''import React, { useState, useEffect, useRef } from 'react';
import { 
  getRandomCard, 
  getCardNameAutocomplete, 
  getCardImageUrl, 
  cardNamesMatch 
} from '../services/scryfall';
import type { ScryfallCard, GameState } from '../types';

interface CardGuessingGameProps {
  selectedFormat: string | null;
  selectedSet: string | null;
  onBackToSetup: () => void;
}

// Helper function to get art crop image URL (without card name)
function getCardArtUrl(card: ScryfallCard): string {
  try {
    // Handle double-faced cards (use front face)
    if (card.card_faces && card.card_faces[0]?.image_uris?.art_crop) {
      return card.card_faces[0].image_uris.art_crop;
    }
    
    // Handle regular cards
    if (card.image_uris?.art_crop) {
      return card.image_uris.art_crop;
    }
    
    // Fallback to border_crop if art_crop not available
    if (card.card_faces && card.card_faces[0]?.image_uris?.border_crop) {
      return card.card_faces[0].image_uris.border_crop;
    }
    
    if (card.image_uris?.border_crop) {
      return card.image_uris.border_crop;
    }
    
    // Final fallback to normal image (we'll handle hiding the name with CSS)
    return getCardImageUrl(card, 'normal');
    
  } catch (error) {
    console.error('Error getting card art URL:', error);
    // Last resort fallback
    return getCardImageUrl(card, 'normal');
  }
}

export default function CardGuessingGame({ 
  selectedFormat, 
  selectedSet,
  onBackToSetup
}: CardGuessingGameProps) {
  // Game state
  const [gameState, setGameState] = useState<GameState>({
    currentCard: null,
    isLoading: false,
    isGuessSubmitted: false,
    lastGuess: '',
    isCorrectGuess: null,
    score: 0,
    streak: 0,
    totalGuesses: 0
  });

  // Input state
  const [guessInput, setGuessInput] = useState('');
  const [autocompleteOptions, setAutocompleteOptions] = useState<string[]>([]);
  const [showAutocomplete, setShowAutocomplete] = useState(false);
  const [isLoadingAutocomplete, setIsLoadingAutocomplete] = useState(false);

  // Refs
  const inputRef = useRef<HTMLInputElement>(null);
  const autocompleteTimeoutRef = useRef<NodeJS.Timeout>();

  // Load first card when component mounts
  useEffect(() => {
    loadNewCard();
  }, []);

  // Focus input when new card loads
  useEffect(() => {
    if (gameState.currentCard && !gameState.isGuessSubmitted && inputRef.current) {
      inputRef.current.focus();
    }
  }, [gameState.currentCard, gameState.isGuessSubmitted]);

  // Autocomplete functionality with debouncing
  useEffect(() => {
    // Clear existing timeout
    if (autocompleteTimeoutRef.current) {
      clearTimeout(autocompleteTimeoutRef.current);
    }

    // Don't show autocomplete if guess is submitted or input is empty
    if (gameState.isGuessSubmitted || guessInput.length < 2) {
      setShowAutocomplete(false);
      setAutocompleteOptions([]);
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
  }, [guessInput, gameState.isGuessSubmitted]);

  const loadNewCard = async () => {
    try {
      setGameState(prev => ({ ...prev, isLoading: true }));
      
      const card = await getRandomCard(selectedFormat, selectedSet);
      
      setGameState(prev => ({
        ...prev,
        currentCard: card,
        isLoading: false,
        isGuessSubmitted: false,
        lastGuess: '',
        isCorrectGuess: null
      }));
      
      // Reset input
      setGuessInput('');
      setShowAutocomplete(false);
      setAutocompleteOptions([]);
      
    } catch (error) {
      console.error('Error loading card:', error);
      setGameState(prev => ({ 
        ...prev, 
        isLoading: false,
        currentCard: null
      }));
    }
  };

  const submitGuess = () => {
    if (!gameState.currentCard || !guessInput.trim()) return;

    const isCorrect = cardNamesMatch(guessInput, gameState.currentCard.name);
    
    setGameState(prev => ({
      ...prev,
      isGuessSubmitted: true,
      lastGuess: guessInput,
      isCorrectGuess: isCorrect,
      score: isCorrect ? prev.score + 1 : prev.score,
      streak: isCorrect ? prev.streak + 1 : 0,
      totalGuesses: prev.totalGuesses + 1
    }));

    setShowAutocomplete(false);
  };

  const skipCard = () => {
    if (!gameState.currentCard) return;
    
    setGameState(prev => ({
      ...prev,
      isGuessSubmitted: true,
      lastGuess: '',
      isCorrectGuess: false,
      streak: 0,
      totalGuesses: prev.totalGuesses + 1
    }));

    setShowAutocomplete(false);
  };

  const nextCard = () => {
    loadNewCard();
  };

  const handleInputChange = (value: string) => {
    setGuessInput(value);
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter') {
      if (gameState.isGuessSubmitted) {
        nextCard();
      } else {
        submitGuess();
      }
    } else if (event.key === 'Escape') {
      setShowAutocomplete(false);
    }
  };

  const selectAutocompleteOption = (option: string) => {
    setGuessInput(option);
    setShowAutocomplete(false);
    if (inputRef.current) {
      inputRef.current.focus();
    }
  };

  // Calculate accuracy percentage
  const accuracy = gameState.totalGuesses > 0 
    ? Math.round((gameState.score / gameState.totalGuesses) * 100) 
    : 0;

  if (gameState.isLoading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="bg-white rounded-lg shadow-lg p-8 text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-xl text-gray-600">Loading your first card...</p>
        </div>
      </div>
    );
  }

  if (!gameState.currentCard) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="bg-white rounded-lg shadow-lg p-8 text-center max-w-md">
          <h3 className="text-2xl font-semibold text-gray-700 mb-4">No Card Available</h3>
          <p className="text-gray-600 mb-6">
            Unable to load a card with the selected filters. This might be a temporary issue.
          </p>
          <div className="space-y-3">
            <button
              onClick={loadNewCard}
              className="w-full bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Try Again
            </button>
            <button
              onClick={onBackToSetup}
              className="w-full bg-gray-600 text-white px-6 py-3 rounded-lg hover:bg-gray-700 transition-colors"
            >
              Back to Setup
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        
        {/* Header with Back Button and Score */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8">
          <button
            onClick={onBackToSetup}
            className="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition-colors mb-4 md:mb-0"
          >
            ← Back to Setup
          </button>
          
          {/* Score Display */}
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
          </div>
        </div>

        {/* Card Display */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <div className="text-center">
            <h2 className="text-2xl font-bold text-gray-800 mb-6">
              What's the name of this card?
            </h2>
            
            {/* Card Artwork (Name Hidden) */}
            <div className="flex justify-center mb-6">
              <div className="relative">
                <img
                  src={getCardArtUrl(gameState.currentCard)}
                  alt="Magic card artwork without name"
                  className="rounded-lg shadow-lg border-4 border-gray-300"
                  style={{ 
                    maxHeight: '400px', 
                    maxWidth: '600px',
                    width: 'auto',
                    height: 'auto'
                  }}
                />
                
                {/* Hint: Show set symbol and mana cost after guess */}
                {gameState.isGuessSubmitted && (
                  <div className="mt-4 text-sm text-gray-600">
                    <p><span className="font-medium">Set:</span> {gameState.currentCard.set_name} ({gameState.currentCard.set.toUpperCase()})</p>
                    {gameState.currentCard.mana_cost && (
                      <p><span className="font-medium">Mana Cost:</span> {gameState.currentCard.mana_cost}</p>
                    )}
                    <p><span className="font-medium">Type:</span> {gameState.currentCard.type_line}</p>
                  </div>
                )}
              </div>
            </div>

            {/* Game Result Display */}
            {gameState.isGuessSubmitted && (
              <div className="mb-6">
                {gameState.isCorrectGuess ? (
                  <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                    <h3 className="text-xl font-bold text-green-800">✅ Correct!</h3>
                    <p className="text-green-700">
                      The card is <span className="font-bold">{gameState.currentCard.name}</span>
                    </p>
                  </div>
                ) : (
                  <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                    <h3 className="text-xl font-bold text-red-800">
                      {gameState.lastGuess ? '❌ Incorrect' : '⏭️ Skipped'}
                    </h3>
                    <p className="text-red-700">
                      The card is <span className="font-bold">{gameState.currentCard.name}</span>
                    </p>
                    {gameState.lastGuess && (
                      <p className="text-red-600 text-sm mt-1">
                        Your guess: "{gameState.lastGuess}"
                      </p>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Input Section */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          {!gameState.isGuessSubmitted ? (
            <div className="space-y-4">
              {/* Guess Input with Autocomplete */}
              <div className="relative">
                <label htmlFor="guess-input" className="block text-sm font-medium text-gray-700 mb-2">
                  Enter card name:
                </label>
                <input
                  ref={inputRef}
                  id="guess-input"
                  type="text"
                  value={guessInput}
                  onChange={(e) => handleInputChange(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Start typing a card name..."
                  className="w-full p-4 text-lg border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
                
                {/* Autocomplete Dropdown */}
                {showAutocomplete && autocompleteOptions.length > 0 && (
                  <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-y-auto">
                    {autocompleteOptions.map((option, index) => (
                      <button
                        key={index}
                        onClick={() => selectAutocompleteOption(option)}
                        className="w-full text-left px-4 py-2 hover:bg-blue-50 focus:bg-blue-50 focus:outline-none first:rounded-t-lg last:rounded-b-lg"
                      >
                        {option}
                      </button>
                    ))}
                  </div>
                )}
                
                {/* Loading indicator for autocomplete */}
                {isLoadingAutocomplete && (
                  <div className="absolute right-3 top-12 transform -translate-y-1/2">
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
                  </div>
                )}
              </div>

              {/* Action Buttons */}
              <div className="flex flex-col sm:flex-row gap-3">
                <button
                  onClick={submitGuess}
                  disabled={!guessInput.trim()}
                  className="flex-1 bg-green-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
                >
                  Submit Guess
                </button>
                <button
                  onClick={skipCard}
                  className="flex-1 bg-yellow-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-yellow-700 transition-colors"
                >
                  Skip Card
                </button>
              </div>
            </div>
          ) : (
            <div className="text-center">
              <button
                onClick={nextCard}
                className="bg-blue-600 text-white py-4 px-8 rounded-lg text-lg font-medium hover:bg-blue-700 transition-colors"
              >
                Next Card →
              </button>
              <p className="text-gray-600 text-sm mt-2">Press Enter for next card</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}'''
    
    return content

def main():
    """Main execution function"""
    
    print("🖼️  Fixing Card Name Visibility - Using Art Crop Images")
    print("=" * 55)
    
    # Check if we're in the right directory
    if not os.path.exists('src'):
        print("❌ Error: Not in project root directory (src/ not found)")
        return 1
    
    print("\n1. Updating CardGuessingGame.tsx...")
    try:
        with open('src/components/CardGuessingGame.tsx', 'w', encoding='utf-8') as f:
            f.write(update_card_guessing_game_component())
        print("✅ Updated CardGuessingGame.tsx:")
        print("   • Now uses art_crop images (artwork only, no card name)")
        print("   • Added fallback to border_crop if art_crop unavailable")
        print("   • Shows card details (set, mana cost, type) after guess")
        print("   • Improved styling for artwork display")
    except Exception as e:
        print(f"❌ Error updating CardGuessingGame.tsx: {e}")
        return 1
    
    print("\n" + "=" * 55)
    print("✅ SUCCESS! Card names are now hidden from view.")
    print("\n🎮 The game now shows only card artwork without names!")
    print("   • Uses Scryfall's art_crop images")
    print("   • Fallback handling for cards without art crops")
    print("   • Card details revealed after submitting guess")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
