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
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Game Information</h2>
      
      <div className="space-y-4">
        
        {/* Current Selection Summary */}
        <div className="bg-gray-50 rounded-lg p-4">
          <h3 className="font-semibold text-gray-800 mb-2">Card Pool:</h3>
          <div className="text-gray-600">
            {selectedSets.length > 0 ? (
              <p>
                <span className="text-blue-600 font-medium">
                  {selectedSets.length} set{selectedSets.length !== 1 ? 's' : ''} selected
                </span>
              </p>
            ) : (
              <p className="text-orange-600">
                No sets selected - please choose sets to create your card pool
              </p>
            )}
          </div>
        </div>

        {/* Search Results */}
        {isSearchLoading && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-center">
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600 mr-3"></div>
              <div>
                <h3 className="font-semibold text-blue-800">Searching Cards...</h3>
                <p className="text-blue-600 text-sm">Finding cards from your selected sets</p>
              </div>
            </div>
          </div>
        )}

        {searchError && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <h3 className="font-semibold text-red-800 mb-2">Search Error</h3>
            <p className="text-red-600 text-sm">{searchError}</p>
          </div>
        )}

        {searchResults && !isSearchLoading && !searchError && selectedSets.length > 0 && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <h3 className="font-semibold text-green-800 mb-2">Ready to Play!</h3>
            <div className="text-green-700 space-y-2">
              <p className="text-lg font-medium">
                {searchResults.total_cards.toLocaleString()} cards available
              </p>
              <p className="text-sm">
                Cards from {selectedSets.length} selected set{selectedSets.length !== 1 ? 's' : ''}
              </p>
              {searchResults.has_more && (
                <p className="text-xs text-green-600">
                  Large card pools provide excellent variety!
                </p>
              )}
            </div>
          </div>
        )}

        {/* How to Play */}
        <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-4">
          <h3 className="font-semibold text-indigo-800 mb-2">How to Play</h3>
          <ul className="text-indigo-700 text-sm space-y-1 list-disc list-inside">
            <li>Card images appear with names hidden</li>
            <li>Type the card name with autocomplete help</li>
            <li>Build your score and accuracy</li>
            <li>Skip cards if you're not sure</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
