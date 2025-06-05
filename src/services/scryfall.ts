// Scryfall API Service Layer - Multiple Sets Support
// Handles all interactions with the Scryfall API for MTG card data

import type {
  ScryfallCard,
  ScryfallSearchResponse,
  ScryfallSet,
  ScryfallSetsResponse,
  ScryfallAutocompleteResponse,
  ScryfallError,
  ApiError
} from '../types';

// =============================================================================
// CONFIGURATION
// =============================================================================

const SCRYFALL_API_BASE = 'https://api.scryfall.com';
const REQUEST_DELAY = 100; // 100ms delay between requests to respect rate limits

// Simple request delay to avoid hitting rate limits
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

// =============================================================================
// ERROR HANDLING
// =============================================================================

class ScryfallApiError extends Error {
  public status: number;
  public code: string;
  public details: string;

  constructor(error: ScryfallError | string, status: number = 500) {
    if (typeof error === 'string') {
      super(error);
      this.status = status;
      this.code = 'unknown';
      this.details = error;
    } else {
      super(error.details);
      this.status = error.status;
      this.code = error.code;
      this.details = error.details;
    }
    this.name = 'ScryfallApiError';
  }
}

// =============================================================================
// HTTP CLIENT
// =============================================================================

async function makeRequest<T>(endpoint: string): Promise<T> {
  const url = `${SCRYFALL_API_BASE}${endpoint}`;
  
  try {
    await delay(REQUEST_DELAY);
    
    const response = await fetch(url);
    const data = await response.json();
    
    if (!response.ok) {
      // Scryfall returns error objects for API errors
      if (data.object === 'error') {
        throw new ScryfallApiError(data as ScryfallError);
      }
      throw new ScryfallApiError(
        `HTTP ${response.status}: ${response.statusText}`,
        response.status
      );
    }
    
    return data;
  } catch (error) {
    if (error instanceof ScryfallApiError) {
      throw error;
    }
    
    // Handle network errors, JSON parsing errors, etc.
    if (error instanceof Error) {
      throw new ScryfallApiError(`Network error: ${error.message}`);
    }
    
    throw new ScryfallApiError('Unknown error occurred');
  }
}

// =============================================================================
// SET OPERATIONS
// =============================================================================

/**
 * Fetch all MTG sets from Scryfall
 * Returns detailed information about each set including name, code, release date
 */
export async function fetchSets(): Promise<ScryfallSet[]> {
  try {
    const response = await makeRequest<ScryfallSetsResponse>('/sets');
    
    // Filter to only include core and expansion sets, then sort by release date
    const filteredSets = response.data
      .filter((set: ScryfallSet) => {
        return set.set_type === 'core' || set.set_type === 'expansion';
      })
      .sort((a: ScryfallSet, b: ScryfallSet) => 
        new Date(b.released_at).getTime() - new Date(a.released_at).getTime()
      );
    
    console.log(`Filtered ${response.data.length} total sets down to ${filteredSets.length} core/expansion sets`);
    
    return filteredSets;
  } catch (error) {
    console.error('Failed to fetch sets:', error);
    throw new ScryfallApiError('Failed to load MTG sets');
  }
}

// =============================================================================
// CARD SEARCH OPERATIONS
// =============================================================================

/**
 * Build search query for multiple sets
 */
function buildMultipleSetQuery(setCodes: string[]): string {
  if (!setCodes || setCodes.length === 0) {
    // No sets selected - return empty query that will give 0 results
    return 'set:___NONE___'; // This will return no results
  }
  
  if (setCodes.length === 1) {
    // Single set
    return `set:${setCodes[0]}`;
  }
  
  // Multiple sets - use OR operator
  const setQueries = setCodes.map(code => `set:${code}`);
  return `(${setQueries.join(' OR ')})`;
}

/**
 * Search for cards from multiple sets
 * @param setCodes - Array of set codes to search in
 * @param page - Page number for pagination (1-based)
 */
export async function searchCardsMultipleSets(
  setCodes: string[],
  page: number = 1
): Promise<ScryfallSearchResponse> {
  
  // If no sets selected, return empty result immediately
  if (!setCodes || setCodes.length === 0) {
    return {
      object: 'list',
      total_cards: 0,
      has_more: false,
      data: []
    };
  }
  
  const query = buildMultipleSetQuery(setCodes);
  const endpoint = `/cards/search?q=${encodeURIComponent(query)}&page=${page}`;
  
  try {
    console.log(`Searching cards from ${setCodes.length} sets:`, setCodes);
    return await makeRequest<ScryfallSearchResponse>(endpoint);
  } catch (error) {
    console.error('Failed to search cards from multiple sets:', error);
    throw new ScryfallApiError('Failed to search for cards');
  }
}

/**
 * Legacy function for compatibility - redirects to single set search
 */
export async function searchCards(
  format?: string | null, // Ignored but kept for compatibility
  setCode?: string | null,
  page: number = 1
): Promise<ScryfallSearchResponse> {
  const setCodes = setCode ? [setCode] : [];
  return searchCardsMultipleSets(setCodes, page);
}

/**
 * Get a random card from the selected sets
 * Uses search with random page selection for better distribution
 */
export async function getRandomCardFromSets(setCodes: string[]): Promise<ScryfallCard> {
  try {
    if (!setCodes || setCodes.length === 0) {
      throw new ScryfallApiError('No sets selected for random card selection');
    }
    
    // First, get the total number of cards to calculate random page
    const firstPage = await searchCardsMultipleSets(setCodes, 1);
    
    if (firstPage.total_cards === 0) {
      throw new ScryfallApiError('No cards found in the selected sets');
    }
    
    // Calculate random page (Scryfall returns ~175 cards per page)
    const cardsPerPage = firstPage.data.length;
    const totalPages = Math.ceil(firstPage.total_cards / cardsPerPage);
    const randomPage = Math.floor(Math.random() * totalPages) + 1;
    
    // Get random page
    const randomPageResponse = await searchCardsMultipleSets(setCodes, randomPage);
    
    if (randomPageResponse.data.length === 0) {
      throw new ScryfallApiError('No cards found on selected page');
    }
    
    // Pick random card from that page
    const randomIndex = Math.floor(Math.random() * randomPageResponse.data.length);
    const selectedCard = randomPageResponse.data[randomIndex];
    
    console.log(`Selected random card: ${selectedCard.name} from ${selectedCard.set_name}`);
    return selectedCard;
    
  } catch (error) {
    console.error('Failed to get random card from sets:', error);
    if (error instanceof ScryfallApiError) {
      throw error;
    }
    throw new ScryfallApiError('Failed to get random card');
  }
}

/**
 * Legacy function for compatibility - redirects to multiple sets version
 */
export async function getRandomCard(
  format?: string | null, // Ignored but kept for compatibility
  setCode?: string | null
): Promise<ScryfallCard> {
  const setCodes = setCode ? [setCode] : [];
  return getRandomCardFromSets(setCodes);
}

// =============================================================================
// AUTOCOMPLETE OPERATIONS
// =============================================================================

/**
 * Get autocomplete suggestions for card names
 * @param query - Partial card name to search for
 */
export async function getCardNameAutocomplete(query: string): Promise<string[]> {
  if (!query || query.length < 2) {
    return [];
  }
  
  const endpoint = `/cards/autocomplete?q=${encodeURIComponent(query)}`;
  
  try {
    const response = await makeRequest<ScryfallAutocompleteResponse>(endpoint);
    return response.data;
  } catch (error) {
    console.error('Failed to get autocomplete suggestions:', error);
    // Don't throw for autocomplete failures - just return empty array
    return [];
  }
}

// =============================================================================
// UTILITY FUNCTIONS
// =============================================================================

/**
 * Get the best image URL for a card (handles double-faced cards)
 */
export function getCardImageUrl(card: ScryfallCard, size: 'small' | 'normal' | 'large' = 'normal'): string {
  // Handle double-faced cards (use front face)
  if (card.card_faces && card.card_faces[0]?.image_uris) {
    return card.card_faces[0].image_uris[size];
  }
  
  // Handle regular cards
  if (card.image_uris) {
    return card.image_uris[size];
  }
  
  throw new Error('No image available for this card');
}

/**
 * Normalize card name for comparison (remove special characters, lowercase)
 */
export function normalizeCardName(name: string): string {
  return name
    .toLowerCase()
    .replace(/[^a-z0-9\s]/g, '') // Remove special characters except spaces
    .replace(/\s+/g, ' ') // Collapse multiple spaces
    .trim();
}

/**
 * Check if two card names match (handles slight variations)
 */
export function cardNamesMatch(guess: string, correctName: string): boolean {
  const normalizedGuess = normalizeCardName(guess);
  const normalizedCorrect = normalizeCardName(correctName);
  
  return normalizedGuess === normalizedCorrect;
}

/**
 * Get cards count for multiple sets (for info display)
 */
export async function getCardCountForSets(setCodes: string[]): Promise<number> {
  try {
    if (!setCodes || setCodes.length === 0) {
      return 0;
    }
    
    const firstPage = await searchCardsMultipleSets(setCodes, 1);
    return firstPage.total_cards;
  } catch (error) {
    console.error('Failed to get card count for sets:', error);
    return 0;
  }
}

// =============================================================================
// ERROR EXPORT
// =============================================================================

export { ScryfallApiError };
export type { ApiError };
