#!/usr/bin/env python3
"""
Implement Game Flow - Phase 2 Complete UI
MTG Quiz App - Replace JSON validation with proper game flow

This script creates:
1. InfoDisplay.tsx - Clean info panel (selected options + card count)
2. StartGameButton.tsx - Separate start button component
3. CardGuessingGame.tsx - Complete game with back button
4. Updates App.tsx - Game state management and layout switching

Features:
- Pre-game: Filters + Info + Start Button (responsive layout)
- Game: Full-width game interface with back to setup
- Start button disabled when no cards found
- Mobile-responsive single column layout

Run from project root: python python/implement_game_flow_phase2.py
"""

import os
import sys

def create_info_display_component():
    """Create clean info display component showing selected options and card count"""
    
    content = '''import React from 'react';
import type { ScryfallSearchResponse } from '../types';

interface InfoDisplayProps {
  searchResults: ScryfallSearchResponse | null;
  selectedFormat: string | null;
  selectedSet: string | null;
  isSearchLoading: boolean;
  searchError: string | null;
}

export default function InfoDisplay({ 
  searchResults, 
  selectedFormat, 
  selectedSet,
  isSearchLoading,
  searchError
}: InfoDisplayProps) {
  
  const formatDisplay = selectedFormat 
    ? selectedFormat.charAt(0).toUpperCase() + selectedFormat.slice(1)
    : 'All Formats';
    
  const setDisplay = selectedSet ? 'Specific Set Selected' : 'All Sets';
  
  const cardCount = searchResults?.total_cards || 0;

  return (
    <div className="p-6 bg-white rounded-lg shadow-lg">
      <h3 className="text-xl font-semibold text-gray-800 mb-4">Ready to Play</h3>
      
      {/* Current Selection */}
      <div className="space-y-3 mb-6">
        <div className="flex justify-between items-center">
          <span className="text-sm font-medium text-gray-600">Format:</span>
          <span className="text-sm text-gray-800 font-medium">{formatDisplay}</span>
        </div>
        
        <div className="flex justify-between items-center">
          <span className="text-sm font-medium text-gray-600">Sets:</span>
          <span className="text-sm text-gray-800 font-medium">{setDisplay}</span>
        </div>
        
        <hr className="border-gray-200" />
        
        <div className="flex justify-between items-center">
          <span className="text-sm font-medium text-gray-600">Available Cards:</span>
          {isSearchLoading ? (
            <div className="flex items-center">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
              <span className="text-sm text-gray-500">Loading...</span>
            </div>
          ) : searchError ? (
            <span className="text-sm text-red-600">Error loading</span>
          ) : (
            <span className="text-lg font-bold text-blue-600">
              {cardCount.toLocaleString()}
            </span>
          )}
        </div>
      </div>

      {/* Status Messages */}
      {cardCount === 0 && !isSearchLoading && !searchError && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-md p-3">
          <p className="text-sm text-yellow-800">
            <span className="font-medium">No cards available</span> with the current filter selection.
            Try adjusting your format or set selection.
          </p>
        </div>
      )}
      
      {searchError && (
        <div className="bg-red-50 border border-red-200 rounded-md p-3">
          <p className="text-sm text-red-800">
            <span className="font-medium">Error:</span> {searchError}
          </p>
        </div>
      )}
      
      {cardCount > 0 && !isSearchLoading && (
        <div className="bg-green-50 border border-green-200 rounded-md p-3">
          <p className="text-sm text-green-800">
            <span className="font-medium">Ready!</span> {cardCount.toLocaleString()} cards available for your quiz.
          </p>
        </div>
      )}
    </div>
  );
}'''
    
    return content

def create_start_game_button_component():
    """Create start game button component"""
    
    content = '''import React from 'react';
import type { ScryfallSearchResponse } from '../types';

interface StartGameButtonProps {
  searchResults: ScryfallSearchResponse | null;
  isSearchLoading: boolean;
  searchError: string | null;
  onStartGame: () => void;
}

export default function StartGameButton({ 
  searchResults, 
  isSearchLoading,
  searchError,
  onStartGame 
}: StartGameButtonProps) {
  
  const cardCount = searchResults?.total_cards || 0;
  const canStartGame = cardCount > 0 && !isSearchLoading && !searchError;

  return (
    <div className="p-6 bg-white rounded-lg shadow-lg">
      <button
        onClick={onStartGame}
        disabled={!canStartGame}
        className={`w-full py-4 px-6 rounded-lg font-semibold text-lg transition-all duration-200 ${
          canStartGame
            ? 'bg-blue-600 hover:bg-blue-700 text-white shadow-md hover:shadow-lg'
            : 'bg-gray-300 text-gray-500 cursor-not-allowed'
        }`}
      >
        {isSearchLoading ? (
          <div className="flex items-center justify-center">
            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-gray-500 mr-3"></div>
            Loading Cards...
          </div>
        ) : searchError ? (
          'Cannot Start - Error Loading Cards'
        ) : cardCount === 0 ? (
          'Cannot Start - No Cards Available'
        ) : (
          `Start Game (${cardCount.toLocaleString()} cards)`
        )}
      </button>
      
      {canStartGame && (
        <p className="text-center text-sm text-gray-600 mt-3">
          Press Enter or click to begin the card guessing game!
        </p>
      )}
    </div>
  );
}'''
    
    return content

def create_card_guessing_game_component():
    """Create the main card guessing game component"""
    
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
            
            {/* Card Image */}
            <div className="flex justify-center mb-6">
              <img
                src={getCardImageUrl(gameState.currentCard, 'normal')}
                alt="Magic card with hidden name"
                className="rounded-lg shadow-md max-w-full h-auto"
                style={{ maxHeight: '400px' }}
              />
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

def update_app_component():
    """Update the main App component to handle game state and layout switching"""
    
    content = '''import React, { useState } from 'react';
import FilterDropdowns from './components/FilterDropdowns';
import InfoDisplay from './components/InfoDisplay';
import StartGameButton from './components/StartGameButton';
import CardGuessingGame from './components/CardGuessingGame';
import type { ScryfallSearchResponse } from './types';
import './App.css';

function App() {
  // Filter state
  const [selectedFormat, setSelectedFormat] = useState<string | null>(null);
  const [selectedSet, setSelectedSet] = useState<string | null>(null);
  
  // Search results state
  const [searchResults, setSearchResults] = useState<ScryfallSearchResponse | null>(null);
  const [isSearchLoading, setIsSearchLoading] = useState(false);
  const [searchError, setSearchError] = useState<string | null>(null);
  
  // Game state
  const [isGameActive, setIsGameActive] = useState(false);

  const handleSearchResults = (results: ScryfallSearchResponse | null) => {
    setSearchResults(results);
  };

  const handleSearchLoading = (loading: boolean) => {
    setIsSearchLoading(loading);
  };

  const handleSearchError = (error: string | null) => {
    setSearchError(error);
  };

  const startGame = () => {
    setIsGameActive(true);
  };

  const backToSetup = () => {
    setIsGameActive(false);
  };

  // Game view - full screen
  if (isGameActive) {
    return (
      <CardGuessingGame
        selectedFormat={selectedFormat}
        selectedSet={selectedSet}
        onBackToSetup={backToSetup}
      />
    );
  }

  // Setup view - responsive layout
  return (
    <div className="min-h-screen bg-gray-100">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <header className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">
            MTG Card Name Learning Tool
          </h1>
          <p className="text-gray-600 max-w-2xl mx-auto">
            Test your Magic: The Gathering knowledge! Select your preferred format and set, 
            then start guessing card names from the images.
          </p>
        </header>

        {/* Responsive Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          
          {/* Left Column (Desktop) / Top Section (Mobile): Filters + Start Button */}
          <div className="space-y-6">
            <FilterDropdowns
              selectedFormat={selectedFormat}
              selectedSet={selectedSet}
              onFormatChange={setSelectedFormat}
              onSetChange={setSelectedSet}
              onSearchResults={handleSearchResults}
              onSearchLoading={handleSearchLoading}
              onSearchError={handleSearchError}
            />
            
            {/* Start Game Button - Below filters on desktop, after info on mobile */}
            <div className="hidden lg:block">
              <StartGameButton
                searchResults={searchResults}
                isSearchLoading={isSearchLoading}
                searchError={searchError}
                onStartGame={startGame}
              />
            </div>
          </div>

          {/* Right Column (Desktop) / Middle Section (Mobile): Info Display */}
          <div>
            <InfoDisplay
              searchResults={searchResults}
              selectedFormat={selectedFormat}
              selectedSet={selectedSet}
              isSearchLoading={isSearchLoading}
              searchError={searchError}
            />
          </div>
          
          {/* Start Game Button - Bottom on mobile */}
          <div className="lg:hidden">
            <StartGameButton
              searchResults={searchResults}
              isSearchLoading={isSearchLoading}
              searchError={searchError}
              onStartGame={startGame}
            />
          </div>
        </div>

        {/* Footer */}
        <footer className="mt-12 text-center text-gray-500 text-sm">
          <p>Learn Magic: The Gathering card names through interactive gameplay</p>
          <p>Using Scryfall API • Built with React + TypeScript + Tailwind CSS</p>
        </footer>
      </div>
    </div>
  );
}

export default App;'''
    
    return content

def update_filter_dropdowns_component():
    """Update FilterDropdowns to support the new callback props"""
    
    # Read the current FilterDropdowns component
    filter_path = 'src/components/FilterDropdowns.tsx'
    try:
        with open(filter_path, 'r', encoding='utf-8') as f:
            current_content = f.read()
    except FileNotFoundError:
        print(f"Error: {filter_path} not found")
        return False

    # Add the new callback props to the interface
    updated_content = current_content.replace(
        '''interface FilterDropdownsProps {
  selectedFormat: string | null;
  selectedSet: string | null;
  onFormatChange: (format: string | null) => void;
  onSetChange: (set: string | null) => void;
  onSearchResults: (results: ScryfallSearchResponse | null) => void;
}''',
        '''interface FilterDropdownsProps {
  selectedFormat: string | null;
  selectedSet: string | null;
  onFormatChange: (format: string | null) => void;
  onSetChange: (set: string | null) => void;
  onSearchResults: (results: ScryfallSearchResponse | null) => void;
  onSearchLoading: (loading: boolean) => void;
  onSearchError: (error: string | null) => void;
}'''
    )

    # Update the component parameters
    updated_content = updated_content.replace(
        '''export default function FilterDropdowns({
  selectedFormat,
  selectedSet,
  onFormatChange,
  onSetChange,
  onSearchResults
}: FilterDropdownsProps) {''',
        '''export default function FilterDropdowns({
  selectedFormat,
  selectedSet,
  onFormatChange,
  onSetChange,
  onSearchResults,
  onSearchLoading,
  onSearchError
}: FilterDropdownsProps) {'''
    )

    # Update the search effect to call the new callbacks
    updated_content = updated_content.replace(
        '''  // Search for cards whenever filters change
  useEffect(() => {
    const searchWithFilters = async () => {
      try {
        setIsSearchLoading(true);
        setSearchError(null);
        
        // Get first page of results with current filters
        const results = await searchCards(selectedFormat, selectedSet, 1);
        onSearchResults(results);
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Failed to search cards';
        setSearchError(errorMessage);
        console.error('Error searching cards:', error);
        onSearchResults(null);
      } finally {
        setIsSearchLoading(false);
      }
    };

    // Only search if we have at least one filter selected or if both are null (search all)
    searchWithFilters();
  }, [selectedFormat, selectedSet, onSearchResults]);''',
        '''  // Search for cards whenever filters change
  useEffect(() => {
    const searchWithFilters = async () => {
      try {
        setIsSearchLoading(true);
        setSearchError(null);
        onSearchLoading(true);
        onSearchError(null);
        
        // Get first page of results with current filters
        const results = await searchCards(selectedFormat, selectedSet, 1);
        onSearchResults(results);
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Failed to search cards';
        setSearchError(errorMessage);
        onSearchError(errorMessage);
        console.error('Error searching cards:', error);
        onSearchResults(null);
      } finally {
        setIsSearchLoading(false);
        onSearchLoading(false);
      }
    };

    // Only search if we have at least one filter selected or if both are null (search all)
    searchWithFilters();
  }, [selectedFormat, selectedSet, onSearchResults, onSearchLoading, onSearchError]);'''
    )

    try:
        with open(filter_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        return True
    except Exception as e:
        print(f"Error updating {filter_path}: {e}")
        return False

def main():
    """Main execution function"""
    
    print("🎮 Building Phase 2 Game Flow - Complete UI Implementation")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists('src'):
        print("❌ Error: Not in project root directory (src/ not found)")
        print("Please run this script from the mtg-quiz-app/ directory")
        return 1
    
    # Create components directory if it doesn't exist
    components_dir = 'src/components'
    if not os.path.exists(components_dir):
        os.makedirs(components_dir)
        print(f"✅ Created {components_dir} directory")
    
    success_count = 0
    total_tasks = 5
    
    # 1. Create InfoDisplay component
    print("\n1. Creating InfoDisplay.tsx...")
    try:
        with open('src/components/InfoDisplay.tsx', 'w', encoding='utf-8') as f:
            f.write(create_info_display_component())
        print("✅ Created InfoDisplay.tsx - Clean info panel with selected options + card count")
        success_count += 1
    except Exception as e:
        print(f"❌ Error creating InfoDisplay.tsx: {e}")
    
    # 2. Create StartGameButton component
    print("\n2. Creating StartGameButton.tsx...")
    try:
        with open('src/components/StartGameButton.tsx', 'w', encoding='utf-8') as f:
            f.write(create_start_game_button_component())
        print("✅ Created StartGameButton.tsx - Responsive start button with proper disabled state")
        success_count += 1
    except Exception as e:
        print(f"❌ Error creating StartGameButton.tsx: {e}")
    
    # 3. Create CardGuessingGame component
    print("\n3. Creating CardGuessingGame.tsx...")
    try:
        with open('src/components/CardGuessingGame.tsx', 'w', encoding='utf-8') as f:
            f.write(create_card_guessing_game_component())
        print("✅ Created CardGuessingGame.tsx - Full game interface with autocomplete + back button")
        success_count += 1
    except Exception as e:
        print(f"❌ Error creating CardGuessingGame.tsx: {e}")
    
    # 4. Update App.tsx
    print("\n4. Updating App.tsx...")
    try:
        with open('src/App.tsx', 'w', encoding='utf-8') as f:
            f.write(update_app_component())
        print("✅ Updated App.tsx - Game state management + responsive layout switching")
        success_count += 1
    except Exception as e:
        print(f"❌ Error updating App.tsx: {e}")
    
    # 5. Update FilterDropdowns component
    print("\n5. Updating FilterDropdowns.tsx...")
    if update_filter_dropdowns_component():
        print("✅ Updated FilterDropdowns.tsx - Added callback props for loading/error states")
        success_count += 1
    
    print("\n" + "=" * 60)
    print(f"🎯 Phase 2 Implementation Complete: {success_count}/{total_tasks} tasks successful")
    
    if success_count == total_tasks:
        print("\n🚀 SUCCESS! Ready to test the complete game flow:")
        print("   1. npm run dev")
        print("   2. Navigate to http://localhost:5173")
        print("   3. Test the responsive layout and game flow")
        print("\n✨ Features implemented:")
        print("   • Clean pre-game setup with info display")
        print("   • Responsive layout (desktop 2-col, mobile 1-col)")
        print("   • Start button positioned correctly per layout")
        print("   • Start button disabled when no cards available")
        print("   • Full-screen game interface with back button")
        print("   • Card guessing with autocomplete")
        print("   • Score tracking and game statistics")
    else:
        print(f"\n⚠️  {total_tasks - success_count} tasks failed. Check the errors above.")
        print("You may need to manually fix the failed components.")
    
    return 0 if success_count == total_tasks else 1

if __name__ == "__main__":
    sys.exit(main())
