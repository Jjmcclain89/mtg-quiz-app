import React from 'react';
import type { ScryfallSearchResponse } from '../types';

interface JsonDisplayProps {
  searchResults: ScryfallSearchResponse | null;
  selectedFormat: string | null;
  selectedSet: string | null;
}

export default function JsonDisplay({ searchResults, selectedFormat, selectedSet }: JsonDisplayProps) {
  if (!searchResults) {
    return (
      <div className="p-6 bg-gray-50 rounded-lg">
        <h3 className="text-lg font-semibold text-gray-700 mb-2">Search Results</h3>
        <p className="text-gray-500">No search results available</p>
      </div>
    );
  }

  return (
    <div className="p-6 bg-gray-50 rounded-lg">
      <h3 className="text-lg font-semibold text-gray-700 mb-4">Search Results Validation</h3>
      
      {/* Current Filters */}
      <div className="mb-4 p-4 bg-white rounded border">
        <h4 className="font-medium text-gray-700 mb-2">Current Filters:</h4>
        <div className="space-y-1 text-sm">
          <p><span className="font-medium">Format:</span> {selectedFormat || 'All Formats'}</p>
          <p><span className="font-medium">Set:</span> {selectedSet || 'All Sets'}</p>
        </div>
      </div>

      {/* Search Summary */}
      <div className="mb-4 p-4 bg-blue-50 rounded border border-blue-200">
        <h4 className="font-medium text-blue-800 mb-2">Search Summary:</h4>
        <div className="space-y-1 text-sm text-blue-700">
          <p><span className="font-medium">Total Cards Found:</span> {searchResults.total_cards.toLocaleString()}</p>
          <p><span className="font-medium">Cards on This Page:</span> {searchResults.data.length}</p>
          <p><span className="font-medium">Has More Pages:</span> {searchResults.has_more ? 'Yes' : 'No'}</p>
        </div>
      </div>

      {/* Sample Cards */}
      <div className="mb-4">
        <h4 className="font-medium text-gray-700 mb-2">Sample Cards (First 3):</h4>
        <div className="space-y-2">
          {searchResults.data.slice(0, 3).map((card, index) => (
            <div key={card.id} className="p-3 bg-white rounded border text-sm">
              <div className="font-medium text-gray-800">{card.name}</div>
              <div className="text-gray-600">
                {card.set_name} ({card.set.toUpperCase()}) • {card.type_line}
              </div>
              <div className="text-gray-500">
                Rarity: {card.rarity} • CMC: {card.cmc}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Raw JSON (collapsed by default) */}
      <details className="mt-4">
        <summary className="cursor-pointer font-medium text-gray-700 hover:text-gray-900">
          View Raw JSON Response (Click to expand)
        </summary>
        <div className="mt-2 p-4 bg-white border rounded">
          <pre className="text-xs text-gray-600 overflow-auto max-h-96">
            {JSON.stringify(searchResults, null, 2)}
          </pre>
        </div>
      </details>
    </div>
  );
}
