import React from 'react';
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
}