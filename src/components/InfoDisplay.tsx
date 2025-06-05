import React from 'react';
import type { ScryfallSearchResponse } from '../types';

interface InfoDisplayProps {
  searchResults: ScryfallSearchResponse | null;
  selectedSets: string[];
  isSearchLoading: boolean;
  searchError: string | null;
}

export default function InfoDisplay({
  searchResults,
  selectedSets,
  isSearchLoading,
  searchError
}: InfoDisplayProps) {
  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h3 className="text-xl font-semibold text-gray-800 mb-4">Game Info</h3>
      
      <div className="space-y-4">
        {/* Sets Selection Status */}
        <div>
          <h4 className="font-medium text-gray-700 mb-2">Selected Sets:</h4>
          {selectedSets.length > 0 ? (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
              <p className="text-blue-800">
                <span className="font-medium">{selectedSets.length}</span> set{selectedSets.length !== 1 ? 's' : ''} selected
              </p>
              <p className="text-blue-600 text-sm mt-1">
                {selectedSets.slice(0, 3).map(code => code.toUpperCase()).join(', ')}
                {selectedSets.length > 3 && ` +${selectedSets.length - 3} more`}
              </p>
            </div>
          ) : (
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
              <p className="text-gray-600">No sets selected</p>
              <p className="text-gray-500 text-sm mt-1">
                Select one or more sets to see available cards
              </p>
            </div>
          )}
        </div>

        {/* Search Results */}
        <div>
          <h4 className="font-medium text-gray-700 mb-2">Available Cards:</h4>
          
          {isSearchLoading ? (
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
              <div className="flex items-center text-blue-600">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
                <span className="text-sm">Searching for cards...</span>
              </div>
            </div>
          ) : searchError ? (
            <div className="bg-red-50 border border-red-200 rounded-lg p-3">
              <p className="text-red-800 font-medium">Search Error</p>
              <p className="text-red-600 text-sm mt-1">{searchError}</p>
            </div>
          ) : searchResults ? (
            <div className="bg-green-50 border border-green-200 rounded-lg p-3">
              <p className="text-green-800 font-medium">
                {searchResults.total_cards.toLocaleString()} cards found
              </p>
              <p className="text-green-600 text-sm mt-1">
                Ready to start guessing card names!
              </p>
            </div>
          ) : (
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
              <p className="text-gray-600">No search performed yet</p>
              <p className="text-gray-500 text-sm mt-1">
                Select sets to see available cards
              </p>
            </div>
          )}
        </div>

        {/* Game Features */}
        <div>
          <h4 className="font-medium text-gray-700 mb-2">Game Features:</h4>
          <ul className="text-sm text-gray-600 space-y-1">
            <li>• Multiple input modes: Autocomplete and Multiple Choice</li>
            <li>• Real-time scoring and streak tracking</li>
            <li>• Mobile-optimized interface</li>
            <li>• Progress persistence across sessions</li>
            <li>• Smart card name matching</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
