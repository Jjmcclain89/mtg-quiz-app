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

// Cache for card names from selected sets
let cardNamesCache: { [key: string]: string[] } = {};
let cacheKey = '';

/**
 * Get autocomplete suggestions for card names from specific sets only
 * Uses local filtering from cached card names for better performance
 */
export async function getCardNameAutocompleteFromSets(query: string, setCodes: string[]): Promise<string[]> {
  if (!query || query.length < 2 || !setCodes || setCodes.length === 0) {
    return [];
  }
  
  try {
    // Create cache key from selected sets
    const currentCacheKey = setCodes.sort().join(',');
    
    // If cache is stale or doesn't exist, rebuild it
    if (cacheKey !== currentCacheKey || !cardNamesCache[currentCacheKey]) {
      console.log(`Building card names cache for ${setCodes.length} sets...`);
      
      // Get first page of cards from selected sets to build name cache
      const searchResponse = await searchCardsMultipleSets(setCodes, 1);
      
      if (searchResponse.total_cards === 0) {
        console.log('No cards found in selected sets, falling back to global autocomplete');
        return await getCardNameAutocomplete(query);
      }
      
      // Collect card names from multiple pages to build comprehensive cache
      const allCardNames = new Set<string>();
      
      // Add names from first page
      searchResponse.data.forEach(card => allCardNames.add(card.name));
      
      // If there are more pages, get a few more to build better cache
      if (searchResponse.has_more && searchResponse.total_cards > 175) {
        try {
          const page2 = await searchCardsMultipleSets(setCodes, 2);
          page2.data.forEach(card => allCardNames.add(card.name));
          
          if (page2.has_more) {
            const page3 = await searchCardsMultipleSets(setCodes, 3);
            page3.data.forEach(card => allCardNames.add(card.name));
          }
        } catch (error) {
          console.log('Could not fetch additional pages, using partial cache');
        }
      }
      
      // Cache the card names
      cardNamesCache[currentCacheKey] = Array.from(allCardNames).sort();
      cacheKey = currentCacheKey;
      
      console.log(`Cached ${cardNamesCache[currentCacheKey].length} unique card names from selected sets`);
    }
    
    // Filter cached names based on query
    const queryLower = query.toLowerCase();
    const matchingNames = cardNamesCache[currentCacheKey]
      .filter(name => name.toLowerCase().includes(queryLower))
      .sort((a, b) => {
        // Prioritize names that start with the query
        const aStarts = a.toLowerCase().startsWith(queryLower);
        const bStarts = b.toLowerCase().startsWith(queryLower);
        if (aStarts && !bStarts) return -1;
        if (!aStarts && bStarts) return 1;
        return a.localeCompare(b);
      })
      .slice(0, 8); // Limit to 8 suggestions
    
    console.log(`Found ${matchingNames.length} autocomplete matches in selected sets for "${query}"`);
    return matchingNames;
    
  } catch (error) {
    console.error('Set-specific autocomplete failed:', error);
    // Fallback to global autocomplete if caching fails
    console.log('Falling back to global autocomplete');
    return await getCardNameAutocomplete(query);
  }
}

// =============================================================================
// MULTIPLE CHOICE GENERATION
// =============================================================================

/**
 * Generate multiple choice options for a card
 * Uses smart algorithms to create plausible but incorrect options
 */
export async function generateMultipleChoiceOptions(
  correctCard: ScryfallCard,
  selectedSets: string[]
): Promise<{ text: string; isCorrect: boolean }[]> {
  try {
    console.log('Generating efficient multiple choice for:', correctCard.name);
    
    // Get one batch of random cards from the same search that found the correct card
    let availableCards: ScryfallCard[] = [];
    
    try {
      // Make ONE API call to get a bunch of cards
      const searchResponse = await searchCardsMultipleSets(selectedSets);
      availableCards = searchResponse.data || [];
      console.log('Got', availableCards.length, 'cards from single API call');
    } catch (error) {
      console.warn('Failed to get card pool, using fallbacks:', error);
    }
    
    // Remove the correct card from available options
    const wrongAnswerCandidates = availableCards.filter(card => card.name !== correctCard.name);
    
    // Pick 3 random wrong answers from the available cards
    const wrongAnswers: string[] = [];
    const shuffledCandidates = [...wrongAnswerCandidates];
    
    // Shuffle the array
    for (let i = shuffledCandidates.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [shuffledCandidates[i], shuffledCandidates[j]] = [shuffledCandidates[j], shuffledCandidates[i]];
    }
    
    // Take the first 3 unique cards as wrong answers
    for (const card of shuffledCandidates) {
      if (wrongAnswers.length >= 3) break;
      if (!wrongAnswers.includes(card.name)) {
        wrongAnswers.push(card.name);
      }
    }
    
    // Fill any remaining slots with fallbacks if needed
    const fallbacks = ['Lightning Bolt', 'Counterspell', 'Giant Growth', 'Sol Ring', 'Path to Exile'];
    for (const fallback of fallbacks) {
      if (wrongAnswers.length >= 3) break;
      if (fallback !== correctCard.name && !wrongAnswers.includes(fallback)) {
        wrongAnswers.push(fallback);
      }
    }
    
    // Create the options array
    const options = [
      { text: correctCard.name, isCorrect: true },
      { text: wrongAnswers[0] || 'Lightning Bolt', isCorrect: false },
      { text: wrongAnswers[1] || 'Counterspell', isCorrect: false },
      { text: wrongAnswers[2] || 'Giant Growth', isCorrect: false }
    ];
    
    console.log('Efficient multiple choice options:', options.map(o => o.text));
    
    // Shuffle the options so correct answer isn't always first
    return shuffleArray(options);
  } catch (error) {
    console.error('Error generating efficient multiple choice options:', error);
    
    // Ultra-safe fallback
    return [
      { text: correctCard.name, isCorrect: true },
      { text: 'Lightning Bolt', isCorrect: false },
      { text: 'Counterspell', isCorrect: false },
      { text: 'Giant Growth', isCorrect: false }
    ];
  }
}

function shuffleArray<T>(array: T[]): T[] {
  const shuffled = [...array];
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
  }
  return shuffled;
}
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
