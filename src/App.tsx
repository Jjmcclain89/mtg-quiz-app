import React, { useState, useCallback, useEffect } from 'react';
import FilterDropdowns from './components/FilterDropdowns';


import CardGuessingGame from './components/CardGuessingGame';
import { 
  loadGameState, 
  saveSetPreference, 
  saveGameActiveStatus 
} from './services/persistence';
import type { ScryfallSearchResponse } from './types';
import './App.css';

function App() {
  // Initialize state from localStorage
  const [isStateLoaded, setIsStateLoaded] = useState(false);
  
  // Filter state - multiple sets support
  const [selectedSets, setSelectedSets] = useState<string[]>([]);
  
  // Input mode state
  const [inputMode, setInputMode] = useState<'autocomplete' | 'plaintext' | 'multiplechoice'>('multiplechoice');
  
  // Search results state
  const [searchResults, setSearchResults] = useState<ScryfallSearchResponse | null>(null);
  const [isSearchLoading, setIsSearchLoading] = useState(false);
  const [searchError, setSearchError] = useState<string | null>(null);
  
  // Game state
  const [isGameActive, setIsGameActive] = useState(false);

  // Load persisted state on component mount
  useEffect(() => {
    try {
      const persistedState = loadGameState();
      
      // Restore game active status
      setIsGameActive(persistedState.isGameActive);
      
      // Restore input mode
      setInputMode(persistedState.inputMode || 'multiplechoice');
      
      setIsStateLoaded(true);
      
      console.log('App state restored from localStorage');
    } catch (error) {
      console.error('Failed to restore app state:', error);
      setIsStateLoaded(true); // Continue with defaults
    }
  }, []);

  // Save game active status when it changes
  useEffect(() => {
    if (isStateLoaded) {
      saveGameActiveStatus(isGameActive);
    }
  }, [isGameActive, isStateLoaded]);

  // Memoized callback functions to prevent infinite re-renders
  const handleSearchResults = useCallback((results: ScryfallSearchResponse | null) => {
    setSearchResults(results);
  }, []);

  const handleSearchLoading = useCallback((loading: boolean) => {
    setIsSearchLoading(loading);
  }, []);

  const handleSearchError = useCallback((error: string | null) => {
    setSearchError(error);
  }, []);

  const startGame = useCallback(() => {
    setIsGameActive(true);
  }, []);

  const backToSetup = useCallback(() => {
    setIsGameActive(false);
  }, []);

  // Show loading state while restoring from localStorage
  if (!isStateLoaded) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="bg-white rounded-lg shadow-lg p-8 text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-xl text-gray-600">Loading your game...</p>
        </div>
      </div>
    );
  }

  // Game view - full screen
  if (isGameActive) {
    return (
      <CardGuessingGame
        selectedSets={selectedSets}
        inputMode={inputMode}
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
          <h1 className="text-2xl font-bold text-gray-800">
            MTG Card Name Learning Tool
          </h1>
        </header>

        {/* Unified Layout */}
        <div className="max-w-2xl mx-auto">
          <FilterDropdowns
            selectedSets={selectedSets}
            onSetsChange={setSelectedSets}
            onSearchResults={handleSearchResults}
            onSearchLoading={handleSearchLoading}
            onSearchError={handleSearchError}
            onBackToGame={null}
            inputMode={inputMode}
            onInputModeChange={setInputMode}
            searchResults={searchResults}
            isSearchLoading={isSearchLoading}
            searchError={searchError}
            onStartGame={startGame}
          />
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

export default App;
