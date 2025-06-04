import React from 'react';
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
}