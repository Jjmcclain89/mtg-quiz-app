#!/usr/bin/env python3
"""
Fix Infinite Loop - Search Requests
MTG Quiz App - Fix the continuous API requests causing flickering

The issue: Added callback functions to useEffect dependency array which causes infinite re-renders
The fix: Remove callback functions from dependencies and use useCallback in parent

Run from project root: python python/fix_infinite_loop_search_requests.py
"""

import os
import sys

def fix_filter_dropdowns_component():
    """Fix the FilterDropdowns component to prevent infinite loop"""
    
    content = '''import React, { useState, useEffect } from 'react';
import { fetchFormats, fetchSets, filterSetsByFormat, searchCards } from '../services/scryfall';
import type { ScryfallSet, ScryfallSearchResponse } from '../types';

interface FilterDropdownsProps {
  selectedFormat: string | null;
  selectedSet: string | null;
  onFormatChange: (format: string | null) => void;
  onSetChange: (set: string | null) => void;
  onSearchResults: (results: ScryfallSearchResponse | null) => void;
  onSearchLoading: (loading: boolean) => void;
  onSearchError: (error: string | null) => void;
}

export default function FilterDropdowns({
  selectedFormat,
  selectedSet,
  onFormatChange,
  onSetChange,
  onSearchResults,
  onSearchLoading,
  onSearchError
}: FilterDropdownsProps) {
  // State for dropdown data
  const [formats, setFormats] = useState<string[]>([]);
  const [allSets, setAllSets] = useState<ScryfallSet[]>([]);
  const [filteredSets, setFilteredSets] = useState<ScryfallSet[]>([]);
  
  // Loading states
  const [isFormatsLoading, setIsFormatsLoading] = useState(true);
  const [isSetsLoading, setIsSetsLoading] = useState(true);
  const [isSearchLoading, setIsSearchLoading] = useState(false);
  
  // Error states
  const [formatsError, setFormatsError] = useState<string | null>(null);
  const [setsError, setSetsError] = useState<string | null>(null);
  const [searchError, setSearchError] = useState<string | null>(null);

  // Load formats on component mount
  useEffect(() => {
    const loadFormats = async () => {
      try {
        setIsFormatsLoading(true);
        setFormatsError(null);
        const formatsData = await fetchFormats();
        setFormats(formatsData);
      } catch (error) {
        setFormatsError(error instanceof Error ? error.message : 'Failed to load formats');
        console.error('Error loading formats:', error);
      } finally {
        setIsFormatsLoading(false);
      }
    };

    loadFormats();
  }, []);

  // Load sets on component mount
  useEffect(() => {
    const loadSets = async () => {
      try {
        setIsSetsLoading(true);
        setSetsError(null);
        const setsData = await fetchSets();
        setAllSets(setsData);
        setFilteredSets(setsData); // Initially show all sets
      } catch (error) {
        setSetsError(error instanceof Error ? error.message : 'Failed to load sets');
        console.error('Error loading sets:', error);
      } finally {
        setIsSetsLoading(false);
      }
    };

    loadSets();
  }, []);

  // Filter sets when format changes (now instant with static mapping)
  useEffect(() => {
    if (allSets.length === 0) return; // Wait for sets to load
    
    // Use static mapping for instant filtering (no loading state needed)
    const filtered = filterSetsByFormat(allSets, selectedFormat);
    setFilteredSets(filtered);
    
    // If current selected set is not in the filtered list, reset set selection
    if (selectedSet && selectedSet !== 'all') {
      const isSelectedSetStillValid = filtered.some(set => set.code === selectedSet);
      if (!isSelectedSetStillValid) {
        console.log(`Selected set ${selectedSet} not legal in ${selectedFormat}, resetting to all sets`);
        onSetChange(null);
      }
    }
  }, [selectedFormat, allSets, selectedSet, onSetChange]);

  // Search for cards whenever filters change - FIXED: Remove callback functions from dependencies
  useEffect(() => {
    const searchWithFilters = async () => {
      try {
        setIsSearchLoading(true);
        setSearchError(null);
        // Call parent callbacks
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
  }, [selectedFormat, selectedSet]); // FIXED: Only depend on the actual filter values

  const handleFormatChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const value = event.target.value;
    onFormatChange(value === 'all' ? null : value);
  };

  const handleSetChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const value = event.target.value;
    onSetChange(value === 'all' ? null : value);
  };

  return (
    <div className="space-y-6 p-6 bg-white rounded-lg shadow-lg">
      <h2 className="text-2xl font-bold text-gray-800 mb-4">Filter Card Pool</h2>
      
      {/* Format Dropdown */}
      <div className="space-y-2">
        <label htmlFor="format-select" className="block text-sm font-medium text-gray-700">
          Format
        </label>
        <select
          id="format-select"
          value={selectedFormat || 'all'}
          onChange={handleFormatChange}
          disabled={isFormatsLoading}
          className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
        >
          <option value="all">All Formats</option>
          {isFormatsLoading && (
            <option disabled>Loading formats...</option>
          )}
          {formatsError && (
            <option disabled>Error loading formats</option>
          )}
          {formats.map((format) => (
            <option key={format} value={format}>
              {format.charAt(0).toUpperCase() + format.slice(1)}
            </option>
          ))}
        </select>
        {formatsError && (
          <p className="text-sm text-red-600">{formatsError}</p>
        )}
      </div>

      {/* Set Dropdown */}
      <div className="space-y-2">
        <label htmlFor="set-select" className="block text-sm font-medium text-gray-700">
          Set/Expansion
          {selectedFormat && selectedFormat !== 'all' && (
            <span className="text-xs text-green-600 ml-1">
              (instantly filtered for {selectedFormat})
            </span>
          )}
        </label>
        <select
          id="set-select"
          value={selectedSet || 'all'}
          onChange={handleSetChange}
          disabled={isSetsLoading}
          className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
        >
          <option value="all">
            All Sets {selectedFormat && selectedFormat !== 'all' ? `(${filteredSets.length} legal in ${selectedFormat})` : `(${allSets.length} total)`}
          </option>
          {isSetsLoading && (
            <option disabled>Loading sets...</option>
          )}
          {setsError && (
            <option disabled>Error loading sets</option>
          )}
          {filteredSets.map((set) => (
            <option key={set.code} value={set.code}>
              {set.name} ({set.code.toUpperCase()})
            </option>
          ))}
        </select>
        {setsError && (
          <p className="text-sm text-red-600">{setsError}</p>
        )}
      </div>

      {/* Search Status */}
      <div className="pt-4 border-t border-gray-200">
        {isSearchLoading && (
          <div className="flex items-center text-blue-600">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
            Searching cards...
          </div>
        )}
        {searchError && (
          <p className="text-sm text-red-600">Search Error: {searchError}</p>
        )}
      </div>

      {/* Static Filtering Info */}
      {selectedFormat && selectedFormat !== 'all' && (
        <div className="bg-green-50 border border-green-200 rounded-md p-3">
          <p className="text-sm text-green-800">
            <span className="font-medium">⚡ Instant Filtering:</span> Sets filtered using static mapping for {selectedFormat} format.
            Showing {filteredSets.length} of {allSets.length} total sets (no API delay).
          </p>
        </div>
      )}
    </div>
  );
}'''
    
    return content

def fix_app_component():
    """Fix the App component to use useCallback for the callback functions"""
    
    content = '''import React, { useState, useCallback } from 'react';
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

def main():
    """Main execution function"""
    
    print("🔧 Fixing Infinite Loop - Search Requests")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('src'):
        print("❌ Error: Not in project root directory (src/ not found)")
        return 1
    
    success_count = 0
    total_tasks = 2
    
    # 1. Fix FilterDropdowns component
    print("\n1. Fixing FilterDropdowns.tsx...")
    try:
        with open('src/components/FilterDropdowns.tsx', 'w', encoding='utf-8') as f:
            f.write(fix_filter_dropdowns_component())
        print("✅ Fixed FilterDropdowns.tsx - Removed callback functions from useEffect dependencies")
        success_count += 1
    except Exception as e:
        print(f"❌ Error fixing FilterDropdowns.tsx: {e}")
    
    # 2. Fix App component
    print("\n2. Fixing App.tsx...")
    try:
        with open('src/App.tsx', 'w', encoding='utf-8') as f:
            f.write(fix_app_component())
        print("✅ Fixed App.tsx - Added useCallback to memoize callback functions")
        success_count += 1
    except Exception as e:
        print(f"❌ Error fixing App.tsx: {e}")
    
    print("\n" + "=" * 50)
    print(f"🎯 Fix Complete: {success_count}/{total_tasks} tasks successful")
    
    if success_count == total_tasks:
        print("\n✅ SUCCESS! The infinite loop has been fixed.")
        print("   • Removed callback functions from useEffect dependencies")
        print("   • Added useCallback to prevent unnecessary re-renders")
        print("   • Search requests should now only happen when filters change")
        print("\n🚀 The app should now work properly without flickering!")
    else:
        print(f"\n⚠️  {total_tasks - success_count} tasks failed. Check the errors above.")
    
    return 0 if success_count == total_tasks else 1

if __name__ == "__main__":
    sys.exit(main())
