import React, { useState, useEffect } from 'react';
import { fetchSets, searchCardsMultipleSets } from '../services/scryfall';
import type { ScryfallSet, ScryfallSearchResponse } from '../types';
import InputModeSelector from './InputModeSelector';
import StartGameButton from './StartGameButton';

interface FilterDropdownsProps {
  selectedSets: string[];
  onSetsChange: (sets: string[]) => void;
  onSearchResults: (results: ScryfallSearchResponse | null) => void;
  onSearchLoading: (loading: boolean) => void;
  onSearchError: (error: string | null) => void;
  onBackToGame: (() => void) | null;
  inputMode: 'autocomplete' | 'plaintext' | 'multiplechoice';
  onInputModeChange: (mode: 'autocomplete' | 'plaintext' | 'multiplechoice') => void;
  searchResults: ScryfallSearchResponse | null;
  isSearchLoading: boolean;
  searchError: string | null;
  onStartGame: () => void;
}

export default function FilterDropdowns({
  selectedSets,
  onSetsChange,
  onSearchResults,
  onSearchLoading,
  onSearchError,
  onBackToGame,
  inputMode,
  onInputModeChange,
  searchResults,
  isSearchLoading,
  searchError,
  onStartGame
}: FilterDropdownsProps) {
  // Sets state
  const [sets, setSets] = useState<ScryfallSet[]>([]);
  const [isSetsLoading, setIsSetsLoading] = useState(false);
  const [setsError, setSetsError] = useState<string | null>(null);

  // Dropdown UI state
  const [searchInput, setSearchInput] = useState('');
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [highlightedIndex, setHighlightedIndex] = useState(-1);

  // Load sets on component mount
  useEffect(() => {
    loadSets();
  }, []);

  // Trigger search when selected sets change
  useEffect(() => {
    performSearch();
  }, [selectedSets]);

  const loadSets = async () => {
    try {
      setIsSetsLoading(true);
      setSetsError(null);
      
      const fetchedSets = await fetchSets();
      setSets(fetchedSets);
      
      console.log(`Loaded ${fetchedSets.length} sets`);
    } catch (error) {
      console.error('Failed to load sets:', error);
      setSetsError(error instanceof Error ? error.message : 'Failed to load sets');
    } finally {
      setIsSetsLoading(false);
    }
  };

  const performSearch = async () => {
    try {
      onSearchLoading(true);
      onSearchError(null);
      
      if (selectedSets.length === 0) {
        onSearchResults(null);
        return;
      }
      
      const results = await searchCardsMultipleSets(selectedSets);
      onSearchResults(results);
      
      console.log(`Search completed: ${results.total_cards} cards found`);
    } catch (error) {
      console.error('Search failed:', error);
      const errorMessage = error instanceof Error ? error.message : 'Search failed';
      onSearchError(errorMessage);
      onSearchResults(null);
    } finally {
      onSearchLoading(false);
    }
  };

  const handleSetSelect = (setCode: string) => {
    const isCurrentlySelected = selectedSets.includes(setCode);
    
    if (isCurrentlySelected) {
      // Remove set - keep dropdown open for easy multi-deselect
      onSetsChange(selectedSets.filter(code => code !== setCode));
      setHighlightedIndex(-1);
    } else {
      // Add set - close dropdown for mobile UX
      onSetsChange([...selectedSets, setCode]);
      setSearchInput('');
      setIsDropdownOpen(false);
      setHighlightedIndex(-1);
    }
  };

  const removeSet = (setCode: string) => {
    onSetsChange(selectedSets.filter(code => code !== setCode));
  };

  const clearAllSets = () => {
    onSetsChange([]);
    setSearchInput('');
    setIsDropdownOpen(false);
  };

  // Filter sets based on search input and exclude sets with 0 cards
  const filteredSets = sets.filter(set =>
    (set.name.toLowerCase().includes(searchInput.toLowerCase()) ||
     set.code.toLowerCase().includes(searchInput.toLowerCase())) &&
    set.card_count > 0
  );

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      {/* Game Setup Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
        <h2 className="text-xl font-bold text-gray-800">Game Setup</h2>
        {onBackToGame && (
          <button
            onClick={onBackToGame}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors text-sm"
          >
            ← Back to Game
          </button>
        )}
      </div>
      
      <div className="space-y-4">
        {/* Set Search/Select Dropdown */}
        <div className="relative">
          <label htmlFor="set-search" className="block text-sm font-medium text-gray-700 mb-2">
            Search and add Magic sets:
          </label>
          
          <div className="relative">
            <input
              id="set-search"
              type="text"
              value={searchInput}
              onChange={(e) => {
                setSearchInput(e.target.value);
                setIsDropdownOpen(true);
              }}
              onFocus={() => setIsDropdownOpen(true)}
              placeholder="Search for Magic sets..."
              className="w-full p-3 pr-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              disabled={isSetsLoading}
            />
            
            <button
              onClick={() => setIsDropdownOpen(!isDropdownOpen)}
              className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
            >
              {isDropdownOpen ? '▲' : '▼'}
            </button>
          </div>

          {/* Dropdown List */}
          {isDropdownOpen && !isSetsLoading && (
            <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-64 overflow-y-auto">
              {filteredSets.length > 0 ? (
                filteredSets.map((set, index) => {
                  const isSelected = selectedSets.includes(set.code);
                  return (
                    <button
                      key={set.code}
                      onClick={() => handleSetSelect(set.code)}
                      className={`w-full text-left px-4 py-3 border-b border-gray-100 hover:bg-blue-50 focus:outline-none transition-colors ${
                        isSelected ? 'bg-blue-50 text-blue-900' : 'text-gray-700'
                      } ${index === highlightedIndex ? 'bg-blue-100' : ''}`}
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="font-medium">
                            {set.name} <span className="text-sm text-gray-500">({set.code.toUpperCase()})</span>
                          </div>
                        </div>
                        {isSelected && (
                          <span className="text-blue-600 font-bold">✓</span>
                        )}
                      </div>
                    </button>
                  );
                })
              ) : (
                <div className="px-4 py-3 text-gray-500 text-center">
                  No sets found matching "{searchInput}"
                </div>
              )}
            </div>
          )}
        </div>

        {/* Selected Sets Display OR No Sets Message */}
        {selectedSets.length > 0 ? (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex flex-wrap items-center gap-2 mb-3">
              <span className="text-sm font-medium text-blue-800">Selected Sets:</span>
              {selectedSets.map(setCode => {
                const set = sets.find(s => s.code === setCode);
                return (
                  <div
                    key={setCode}
                    className="flex items-center gap-1 bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm"
                  >
                    <span>{set?.name || setCode.toUpperCase()}</span>
                    <button
                      onClick={() => removeSet(setCode)}
                      className="text-blue-600 hover:text-blue-800 font-bold ml-1"
                      title="Remove set"
                    >
                      ×
                    </button>
                  </div>
                );
              })}
            </div>
            <button
              onClick={clearAllSets}
              className="text-sm text-blue-600 hover:text-blue-800 underline"
            >
              Clear all sets
            </button>
          </div>
        ) : (
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 text-center">
            <p className="text-gray-600">
              Select one or more Magic sets to start playing. 
              Use the search box above to find specific sets.
            </p>
          </div>
        )}
        
        {/* Loading state for sets */}
        {isSetsLoading && (
          <div className="flex items-center text-blue-600">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
            <span className="text-sm">Loading Magic sets...</span>
          </div>
        )}
        
        {/* Error state for sets */}
        {setsError && (
          <div className="text-red-600 text-sm">
            ⚠️ {setsError}
          </div>
        )}

        {/* Multiple Choice Toggle */}
        <div className="mt-6 pt-6 border-t border-gray-200">
          <InputModeSelector 
            inputMode={inputMode}
            onInputModeChange={onInputModeChange}
          />
        </div>

        {/* Start Game Button */}
        <div className="mt-6 pt-6 border-t border-gray-200">
          <StartGameButton
            searchResults={searchResults}
            isSearchLoading={isSearchLoading}
            searchError={searchError}
            onStartGame={onStartGame}
          />
        </div>
      </div>
    </div>
  );
}