import React, { useState, useEffect, useRef } from 'react';
import { fetchSets, searchCardsMultipleSets } from '../services/scryfall';
import type { ScryfallSet, ScryfallSearchResponse } from '../types';

interface FilterDropdownsProps {
  selectedSets: string[];
  onSetsChange: (sets: string[]) => void;
  onSearchResults: (results: ScryfallSearchResponse | null) => void;
  onSearchLoading: (loading: boolean) => void;
  onSearchError: (error: string | null) => void;
  onStartGame: () => void;
}

// Format preset mappings - simplified but accurate
const FORMAT_SETS = {
  standard: ['dmu', 'bro', 'one', 'mom', 'mat', 'woe', 'lci', 'mkm', 'otj', 'blb', 'dsk', 'fdn', 'dft'],
  pioneer: ['rtr', 'gtc', 'dgm', 'm14', 'ths', 'bng', 'jou', 'm15', 'ktk', 'frf', 'dtk', 'ori', 'bfz', 'ogw', 'soi', 'emn', 'kld', 'aer', 'akh', 'hou', 'xln', 'rix', 'dom', 'm19', 'grn', 'rna', 'war', 'm20', 'eld', 'thb', 'iko', 'm21', 'znr', 'khm', 'stx', 'afr', 'mid', 'vow', 'neo', 'snc', 'dmu', 'bro', 'one', 'mom', 'mat', 'woe', 'lci', 'mkm', 'otj', 'blb', 'dsk', 'fdn', 'dft'],
  modern: ['8ed', 'mrd', 'dst', '5dn', 'chk', 'bok', 'sok', '9ed', 'rav', 'gpt', 'dis', 'csp', 'tsp', 'tsb', 'plc', 'fut', '10e', 'lrw', 'mor', 'shm', 'eve', 'ala', 'con', 'arb', 'm10', 'zen', 'wwk', 'roe', 'm11', 'som', 'mbs', 'nph', 'm12', 'isd', 'dka', 'avr', 'm13', 'rtr', 'gtc', 'dgm', 'm14', 'ths', 'bng', 'jou', 'm15', 'ktk', 'frf', 'dtk', 'ori', 'bfz', 'ogw', 'soi', 'emn', 'kld', 'aer', 'akh', 'hou', 'xln', 'rix', 'dom', 'm19', 'grn', 'rna', 'war', 'm20', 'eld', 'thb', 'iko', 'm21', 'znr', 'khm', 'stx', 'afr', 'mid', 'vow', 'neo', 'snc', 'dmu', 'bro', 'one', 'mom', 'mat', 'woe', 'lci', 'mkm', 'otj', 'blb', 'dsk', 'fdn', 'dft', 'mh2', 'mh3'],
  legacy: ['lea', 'leb', '2ed', 'arn', 'atq', '3ed', 'leg', 'drk', 'fem', '4ed', 'ice', 'hml', 'all', 'mir', 'vis', 'wth', 'tmp', 'sth', 'exo', 'usg', 'ulg', 'uds', '6ed', 'mmq', 'nem', 'pcy', 'inv', 'pls', 'apc', '7ed', 'ody', 'tor', 'jud', 'ons', 'lgn', 'scg', '8ed', 'mrd', 'dst', '5dn', 'chk', 'bok', 'sok', '9ed', 'rav', 'gpt', 'dis', 'csp', 'tsp', 'tsb', 'plc', 'fut', '10e', 'lrw', 'mor', 'shm', 'eve', 'ala', 'con', 'arb', 'm10', 'zen', 'wwk', 'roe', 'm11', 'som', 'mbs', 'nph', 'm12', 'isd', 'dka', 'avr', 'm13', 'rtr', 'gtc', 'dgm', 'm14', 'ths', 'bng', 'jou', 'm15', 'ktk', 'frf', 'dtk', 'ori', 'bfz', 'ogw', 'soi', 'emn', 'kld', 'aer', 'akh', 'hou', 'xln', 'rix', 'dom', 'm19', 'grn', 'rna', 'war', 'm20', 'eld', 'thb', 'iko', 'm21', 'znr', 'khm', 'stx', 'afr', 'mid', 'vow', 'neo', 'snc', 'dmu', 'bro', 'one', 'mom', 'mat', 'woe', 'lci', 'mkm', 'otj', 'blb', 'dsk', 'fdn', 'dft'],
  vintage: ['lea', 'leb', '2ed', 'arn', 'atq', '3ed', 'leg', 'drk', 'fem', '4ed', 'ice', 'hml', 'all', 'mir', 'vis', 'wth', 'tmp', 'sth', 'exo', 'usg', 'ulg', 'uds', '6ed', 'mmq', 'nem', 'pcy', 'inv', 'pls', 'apc', '7ed', 'ody', 'tor', 'jud', 'ons', 'lgn', 'scg', '8ed', 'mrd', 'dst', '5dn', 'chk', 'bok', 'sok', '9ed', 'rav', 'gpt', 'dis', 'csp', 'tsp', 'tsb', 'plc', 'fut', '10e', 'lrw', 'mor', 'shm', 'eve', 'ala', 'con', 'arb', 'm10', 'zen', 'wwk', 'roe', 'm11', 'som', 'mbs', 'nph', 'm12', 'isd', 'dka', 'avr', 'm13', 'rtr', 'gtc', 'dgm', 'm14', 'ths', 'bng', 'jou', 'm15', 'ktk', 'frf', 'dtk', 'ori', 'bfz', 'ogw', 'soi', 'emn', 'kld', 'aer', 'akh', 'hou', 'xln', 'rix', 'dom', 'm19', 'grn', 'rna', 'war', 'm20', 'eld', 'thb', 'iko', 'm21', 'znr', 'khm', 'stx', 'afr', 'mid', 'vow', 'neo', 'snc', 'dmu', 'bro', 'one', 'mom', 'mat', 'woe', 'lci', 'mkm', 'otj', 'blb', 'dsk', 'fdn', 'dft']
};

export default function FilterDropdowns({
  selectedSets,
  onSetsChange,
  onSearchResults,
  onSearchLoading,
  onSearchError,
  onStartGame
}: FilterDropdownsProps) {
  // Sets state
  const [sets, setSets] = useState<ScryfallSet[]>([]);
  const [isSetsLoading, setIsSetsLoading] = useState(false);
  const [setsError, setSetsError] = useState<string | null>(null);
  

  
  // Searchable dropdown state
  const [searchInput, setSearchInput] = useState('');
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [highlightedIndex, setHighlightedIndex] = useState(-1);
  
  // Refs
  const inputRef = useRef<HTMLInputElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Load sets on component mount
  useEffect(() => {
    loadSets();
  }, []);

  // Trigger search when selected sets change
  useEffect(() => {
    performSearch();
  }, [selectedSets]);

  // Handle clicks outside to close dropdown
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsDropdownOpen(false);
        setSearchInput('');
        setHighlightedIndex(-1);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const loadSets = async () => {
    try {
      setIsSetsLoading(true);
      setSetsError(null);
      
      const fetchedSets = await fetchSets();
      
      // Filter out sets with 0 cards
      const setsWithCards = fetchedSets.filter(set => set.card_count > 0);
      
      setSets(setsWithCards);
      
      console.log(`Loaded ${setsWithCards.length} sets with cards`);
      
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
      
      const results = await searchCardsMultipleSets(selectedSets);
      onSearchResults(results);
      
      console.log(`Search completed: ${results.total_cards} cards found from ${selectedSets.length} sets`);
    } catch (error) {
      console.error('Search failed:', error);
      const errorMessage = error instanceof Error ? error.message : 'Search failed';
      onSearchError(errorMessage);
      onSearchResults(null);
    } finally {
      onSearchLoading(false);
    }
  };

  const handleInputChange = (value: string) => {
    setSearchInput(value);
    setIsDropdownOpen(true);
    setHighlightedIndex(-1);
  };

  const handleInputFocus = () => {
    setIsDropdownOpen(true);
  };

  const handleDropdownToggle = () => {
    setIsDropdownOpen(!isDropdownOpen);
    if (!isDropdownOpen) {
      inputRef.current?.focus();
    }
  };

  const handleSetSelect = (setCode: string) => {
    const isCurrentlySelected = selectedSets.includes(setCode);
    
    if (isCurrentlySelected) {
      // Set is already selected - remove it and KEEP dropdown open
      onSetsChange(selectedSets.filter(code => code !== setCode));
      // Keep dropdown open for easy multi-deselect
      setHighlightedIndex(-1);
    } else {
      // Set is not selected - add it and CLOSE dropdown (mobile-friendly)
      onSetsChange([...selectedSets, setCode]);
      // Close dropdown after adding (better mobile UX)
      setSearchInput('');
      setIsDropdownOpen(false);
      setHighlightedIndex(-1);
    }
  };

  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (!isDropdownOpen) {
      if (event.key === 'ArrowDown' || event.key === 'Enter') {
        event.preventDefault();
        setIsDropdownOpen(true);
      }
      return;
    }

    const filteredSets = getFilteredSets();

    if (event.key === 'ArrowDown') {
      event.preventDefault();
      setHighlightedIndex(prev => 
        prev < filteredSets.length - 1 ? prev + 1 : 0
      );
    } else if (event.key === 'ArrowUp') {
      event.preventDefault();
      setHighlightedIndex(prev => 
        prev > 0 ? prev - 1 : filteredSets.length - 1
      );
    } else if (event.key === 'Enter') {
      event.preventDefault();
      if (highlightedIndex >= 0 && highlightedIndex < filteredSets.length) {
        handleSetSelect(filteredSets[highlightedIndex].code);
      }
    } else if (event.key === 'Escape') {
      setIsDropdownOpen(false);
      setSearchInput('');
      setHighlightedIndex(-1);
    }
  };

  const handleRemoveSet = (setCodeToRemove: string) => {
    onSetsChange(selectedSets.filter(code => code !== setCodeToRemove));
  };

  const handleClearAll = () => {
    onSetsChange([]);
  };

  const handleFormatPreset = (format: keyof typeof FORMAT_SETS) => {
    const formatSets = FORMAT_SETS[format];
    // Filter to only include sets that actually exist in our loaded sets
    const availableSets = formatSets.filter(code => 
      sets.some(set => set.code === code)
    );
    onSetsChange(availableSets);
  };

  const getFilteredSets = () => {
    let filteredSets = sets;
    
    // Apply search filter
    if (searchInput.trim()) {
      const query = searchInput.toLowerCase();
      filteredSets = sets.filter(set => 
        set.name.toLowerCase().includes(query) ||
        set.code.toLowerCase().includes(query)
      );
    }
    
    return filteredSets;
  };



  const filteredSets = getFilteredSets();
  const canStartGame = selectedSets.length > 0;

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Game Settings</h2>
      
      <div className="space-y-6">
        
        {/* Format Presets */}
        <div>
          <h3 className="text-sm font-medium text-gray-700 mb-3">Format Presets:</h3>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => handleFormatPreset('standard')}
              className="px-3 py-2 text-sm bg-green-100 text-green-700 rounded-lg hover:bg-green-200 transition-colors"
            >
              Standard
            </button>
            <button
              onClick={() => handleFormatPreset('pioneer')}
              className="px-3 py-2 text-sm bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors"
            >
              Pioneer
            </button>
            <button
              onClick={() => handleFormatPreset('modern')}
              className="px-3 py-2 text-sm bg-purple-100 text-purple-700 rounded-lg hover:bg-purple-200 transition-colors"
            >
              Modern
            </button>
            <button
              onClick={() => handleFormatPreset('legacy')}
              className="px-3 py-2 text-sm bg-orange-100 text-orange-700 rounded-lg hover:bg-orange-200 transition-colors"
            >
              Legacy
            </button>
            <button
              onClick={() => handleFormatPreset('vintage')}
              className="px-3 py-2 text-sm bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors"
            >
              Vintage
            </button>
          </div>
        </div>

        {/* Searchable Set Dropdown */}
        <div className="relative" ref={dropdownRef}>
          <label htmlFor="set-search" className="block text-sm font-medium text-gray-700 mb-2">
            Search and Add Magic Sets:
          </label>
          
          <div className="relative">
            <input
              ref={inputRef}
              id="set-search"
              type="text"
              value={searchInput}
              onChange={(e) => handleInputChange(e.target.value)}
              onFocus={handleInputFocus}
              onKeyDown={handleKeyDown}
              placeholder="Choose a set to add..."
              disabled={isSetsLoading}
              className="w-full p-3 pr-10 text-lg border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
            />
            
            {/* Dropdown Arrow */}
            <button
              type="button"
              onClick={handleDropdownToggle}
              disabled={isSetsLoading}
              className="absolute inset-y-0 right-0 flex items-center px-3 disabled:cursor-not-allowed"
            >
              <svg
                className={`w-5 h-5 text-gray-400 transition-transform duration-200 ${
                  isDropdownOpen ? 'transform rotate-180' : ''
                }`}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>
          </div>
          
          {/* Dropdown */}
          {isDropdownOpen && (
            <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-y-auto">
              {isSetsLoading ? (
                <div className="p-4 text-center text-gray-500">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600 mx-auto mb-2"></div>
                  Loading sets...
                </div>
              ) : filteredSets.length > 0 ? (
                filteredSets.map((set, index) => {
                  const isSelected = selectedSets.includes(set.code);
                  const isHighlighted = index === highlightedIndex;
                  
                  return (
                    <button
                      key={set.code}
                      onClick={() => handleSetSelect(set.code)}
                      className={`w-full text-left px-4 py-3 transition-colors first:rounded-t-lg last:rounded-b-lg ${
                        isHighlighted 
                          ? 'bg-blue-200' 
                          : isSelected 
                            ? 'bg-blue-50 text-blue-800' 
                            : 'hover:bg-gray-50'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <span className={`font-medium ${isSelected ? 'text-blue-800' : 'text-gray-900'}`}>
                            {isSelected ? '✓ ' : ''}{set.name}
                          </span>
                          <span className="text-gray-500 text-sm ml-2">
                            ({set.code.toUpperCase()})
                          </span>
                        </div>
                      </div>
                    </button>
                  );
                })
              ) : (
                <div className="p-4 text-center text-gray-500">
                  {searchInput ? `No sets found matching "${searchInput}"` : 'No sets available'}
                </div>
              )}
            </div>
          )}
          
          {/* Loading state for sets */}
          {isSetsLoading && (
            <div className="mt-2 flex items-center text-blue-600">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
              <span className="text-sm">Loading Magic sets...</span>
            </div>
          )}
          

          
          {/* Error state for sets */}
          {setsError && (
            <div className="mt-2 text-red-600 text-sm">
              ⚠️ {setsError}
            </div>
          )}
        </div>

        {/* Selected Sets Display */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-lg font-medium text-gray-800">
              Selected Sets ({selectedSets.length})
            </h3>
            {selectedSets.length > 0 && (
              <button
                onClick={handleClearAll}
                className="text-sm text-red-600 hover:text-red-800 font-medium"
              >
                Clear All
              </button>
            )}
          </div>
          
          {selectedSets.length > 0 ? (
            <div className="flex flex-wrap gap-2">
              {selectedSets.map(setCode => {
                const set = sets.find(s => s.code === setCode);
                return (
                  <div
                    key={setCode}
                    className="inline-flex items-center bg-blue-100 text-blue-800 text-sm px-3 py-2 rounded-lg border border-blue-200"
                  >
                    <span className="font-medium">
                      {set ? set.name : setCode.toUpperCase()}
                    </span>
                    <button
                      onClick={() => handleRemoveSet(setCode)}
                      className="ml-2 text-blue-600 hover:text-blue-800 font-bold"
                      title="Remove this set"
                    >
                      ×
                    </button>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 text-center">
              <p className="text-gray-600">
                No sets selected. Use format presets or search for sets above.
              </p>
            </div>
          )}
        </div>

        {/* Start Game Button */}
        <div className="pt-4 border-t border-gray-200">
          <button
            onClick={onStartGame}
            disabled={!canStartGame}
            className={`w-full py-4 px-6 rounded-lg text-lg font-semibold transition-colors ${
              canStartGame
                ? 'bg-green-600 text-white hover:bg-green-700'
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }`}
          >
            {canStartGame ? 'Start Game' : 'Select Sets to Start'}
          </button>
        </div>
      </div>
    </div>
  );
}
