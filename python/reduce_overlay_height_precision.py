#!/usr/bin/env python3
"""
Reduce Overlay Height for Precision
MTG Quiz App - Make overlay smaller vertically to stay within name area only

Fix: Reduce height so overlay doesn't bleed into artwork area
Keep: Current positioning and length that work well

Run from project root: python python/reduce_overlay_height_precision.py
"""

import os
import sys

def update_card_guessing_game_component():
    """Update CardGuessingGame with smaller overlay height"""
    
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

// Helper function to get card frame color for overlay (completely opaque)
function getCardFrameColor(card: ScryfallCard): string {
  // Determine overlay color based on card colors/type - fully opaque
  const colors = card.color_identity || [];
  
  if (colors.length === 0) {
    // Colorless/Artifact
    return '#C0C0C0'; // Light gray
  } else if (colors.length === 1) {
    // Mono-colored
    switch (colors[0]) {
      case 'W': return '#FFFBD5'; // White - cream
      case 'U': return '#0E68AB'; // Blue 
      case 'B': return '#150B00'; // Black
      case 'R': return '#D3202A'; // Red
      case 'G': return '#00733E'; // Green
      default: return '#F5F5DC'; // Default cream
    }
  } else {
    // Multi-colored
    return '#F4E164'; // Gold
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
            
            {/* Card Image with Name Overlay */}
            <div className="flex justify-center mb-6">
              <div className="relative inline-block">
                <img
                  src={getCardImageUrl(gameState.currentCard, 'normal')}
                  alt="Magic card with hidden name"
                  className="rounded-lg shadow-lg"
                  style={{ 
                    maxHeight: '500px',
                    width: 'auto',
                    height: 'auto'
                  }}
                />
                
                {/* Name Overlay - Only show when guess NOT submitted */}
                {!gameState.isGuessSubmitted && (
                  <div 
                    className="absolute"
                    style={{
                      // Precise positioning to stay within name area only
                      top: '5.5%',    // Same top position
                      left: '7%',     // Same left margin
                      right: '25%',   // Same length
                      height: '3.5%', // Reduced height (was 5.5%, now 3.5%)
                      backgroundColor: getCardFrameColor(gameState.currentCard),
                      // Completely opaque with subtle border
                      opacity: '1',   // Full opacity - no transparency
                      border: '1px solid rgba(0,0,0,0.15)',
                      borderRadius: '2px',
                      // Subtle shadow to blend with card
                      boxShadow: 'inset 0 1px 1px rgba(0,0,0,0.1)',
                    }}
                  />
                )}
                
                {/* Hint text overlay when guess is submitted */}
                {gameState.isGuessSubmitted && (
                  <div className="absolute top-2 left-2 right-2 bg-black bg-opacity-75 text-white p-2 rounded text-sm">
                    <p><span className="font-medium">Set:</span> {gameState.currentCard.set_name}</p>
                    {gameState.currentCard.mana_cost && (
                      <p><span className="font-medium">Cost:</span> {gameState.currentCard.mana_cost}</p>
                    )}
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
    
    print("📐 Reducing Overlay Height for Precision")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not os.path.exists('src'):
        print("❌ Error: Not in project root directory (src/ not found)")
        return 1
    
    print("\n1. Updating CardGuessingGame.tsx...")
    try:
        with open('src/components/CardGuessingGame.tsx', 'w', encoding='utf-8') as f:
            f.write(update_card_guessing_game_component())
        print("✅ Updated CardGuessingGame.tsx:")
        print("   • Reduced overlay height to 3.5% (was 5.5%)")
        print("   • Keeps same positioning and length")
        print("   • Should now stay within name area boundary")
        print("   • Won't bleed into artwork area")
    except Exception as e:
        print(f"❌ Error updating CardGuessingGame.tsx: {e}")
        return 1
    
    print("\n" + "=" * 40)
    print("✅ SUCCESS! Overlay height reduced for perfect fit.")
    print("\n📐 The overlay should now stay perfectly within the name area!")
    print("   • Smaller vertical size")
    print("   • No overlap into artwork")
    print("   • Clean, natural appearance")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
