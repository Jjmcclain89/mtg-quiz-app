#!/usr/bin/env python3
"""
Optimize Hierarchical Format Mapping Script
Restructures format mappings to use hierarchical inheritance:
Standard → Pioneer → Modern → Legacy/Vintage
Now you only need to update Standard for new sets!
"""

import os
from pathlib import Path

def update_scryfall_service():
    """Update the Scryfall service to use hierarchical format mapping"""
    
    service_content = '''// Scryfall API Service Layer
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

// Main competitive MTG formats (ordered by size - smallest to largest)
const MTG_FORMATS = [
  'standard',
  'pioneer',
  'modern', 
  'legacy',
  'vintage'
];

// =============================================================================
// HIERARCHICAL FORMAT MAPPING (Optimized for Easy Maintenance)
// =============================================================================

/**
 * Hierarchical format mapping - each format includes all sets from smaller formats
 * To add a new set: just add it to STANDARD_SETS and it propagates automatically!
 * 
 * Format hierarchy: Standard → Pioneer → Modern → Legacy/Vintage
 */

// Standard - Current rotation (UPDATE THIS WHEN NEW SETS RELEASE)
const STANDARD_SETS = [
  'dmu', 'bro', 'one', 'mom', 'mat', 'woe', 'lci', 'mkm', 'otj', 'blb', 'dsk', 'fdn', 'dft'
];

// Pioneer additional sets (Return to Ravnica 2012 → pre-Standard)
const PIONEER_ADDITIONAL_SETS = [
  'rtr', 'gtc', 'dgm', 'm14', 'ths', 'bng', 'jou', 'm15', 'ktk', 'frf', 'dtk', 'ori',
  'bfz', 'ogw', 'soi', 'emn', 'kld', 'aer', 'akh', 'hou', 'xln', 'rix', 'dom', 'm19',
  'grn', 'rna', 'war', 'm20', 'eld', 'thb', 'iko', 'm21', 'znr', 'khm', 'stx', 'afr',
  'mid', 'vow', 'neo', 'snc'
];

// Modern additional sets (8th Edition 2003 → pre-Pioneer)  
const MODERN_ADDITIONAL_SETS = [
  '8ed', 'mrd', 'dst', '5dn', 'chk', 'bok', 'sok', '9ed', 'rav', 'gpt', 'dis',
  'csp', 'tsp', 'tsb', 'plc', 'fut', '10e', 'lrw', 'mor', 'shm', 'eve', 'ala',
  'con', 'arb', 'm10', 'zen', 'wwk', 'roe', 'm11', 'som', 'mbs', 'nph', 'm12',
  'isd', 'dka', 'avr', 'm13', 'mh2', 'ltr', 'mh3', 'clb'
];

// Legacy/Vintage additional sets (Alpha 1993 → pre-Modern)
const LEGACY_ADDITIONAL_SETS = [
  'lea', 'leb', '2ed', 'arn', 'atq', '3ed', 'leg', 'drk', 'fem', '4ed', 'ice',
  'hml', 'all', 'csp', 'mir', 'vis', 'wth', 'tmp', 'sth', 'exo', 'usg', 'ulg',
  'uds', '6ed', 'mmq', 'nem', 'pcy', 'inv', 'pls', 'apc', '7ed', 'ody', 'tor',
  'jud', 'ons', 'lgn', 'scg'
];

/**
 * Build format mappings hierarchically - each format inherits from smaller formats
 * This ensures consistency and makes maintenance easy
 */
const FORMAT_LEGAL_SETS: Record<string, string[]> = {
  // Standard - Base format (smallest)
  standard: [...STANDARD_SETS],
  
  // Pioneer - Standard + Pioneer additional sets
  pioneer: [...STANDARD_SETS, ...PIONEER_ADDITIONAL_SETS],
  
  // Modern - Pioneer + Modern additional sets  
  modern: [...STANDARD_SETS, ...PIONEER_ADDITIONAL_SETS, ...MODERN_ADDITIONAL_SETS],
  
  // Legacy - Modern + Legacy additional sets
  legacy: [...STANDARD_SETS, ...PIONEER_ADDITIONAL_SETS, ...MODERN_ADDITIONAL_SETS, ...LEGACY_ADDITIONAL_SETS],
  
  // Vintage - Same as Legacy (for most purposes)
  vintage: [...STANDARD_SETS, ...PIONEER_ADDITIONAL_SETS, ...MODERN_ADDITIONAL_SETS, ...LEGACY_ADDITIONAL_SETS]
};

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
// FORMAT OPERATIONS
// =============================================================================

/**
 * Get all available MTG formats
 * Returns the 5 main competitive formats
 */
export async function fetchFormats(): Promise<string[]> {
  try {
    // Add a small delay to simulate API call for consistent UX
    await delay(200);
    
    // Return the 5 main competitive formats
    return [...MTG_FORMATS];
  } catch (error) {
    console.error('Failed to get formats:', error);
    throw new ScryfallApiError('Failed to load MTG formats');
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
    // Sort sets by release date (newest first) for better UX
    return response.data.sort((a, b) => 
      new Date(b.released_at).getTime() - new Date(a.released_at).getTime()
    );
  } catch (error) {
    console.error('Failed to fetch sets:', error);
    throw new ScryfallApiError('Failed to load MTG sets');
  }
}

/**
 * Get sets that are legal in a specific format using hierarchical mapping
 * This provides instant results without slow API calls
 * @param format - MTG format (e.g., "standard", "modern")
 */
export function getLegalSetsForFormat(format: string): string[] {
  const legalSets = FORMAT_LEGAL_SETS[format.toLowerCase()];
  if (!legalSets) {
    console.warn(`No legal sets defined for format: ${format}`);
    return [];
  }
  
  console.log(`${format} format contains ${legalSets.length} legal sets`);
  return [...legalSets];
}

/**
 * Filter sets by format legality using hierarchical mapping (instant)
 * @param allSets - All available sets
 * @param format - Format to filter by (null means show all sets)
 */
export function filterSetsByFormat(allSets: ScryfallSet[], format: string | null): ScryfallSet[] {
  if (!format || format === 'all') {
    return allSets;
  }
  
  try {
    // Get set codes that are legal in this format (instant lookup)
    const legalSetCodes = getLegalSetsForFormat(format);
    
    if (legalSetCodes.length === 0) {
      console.warn(`No sets found for format ${format}, showing all sets`);
      return allSets;
    }
    
    // Filter the sets to only include those legal in the format
    const filteredSets = allSets.filter(set => legalSetCodes.includes(set.code));
    
    console.log(`Filtered ${allSets.length} sets down to ${filteredSets.length} sets for ${format} format`);
    
    return filteredSets;
    
  } catch (error) {
    console.error('Error filtering sets by format:', error);
    // Return all sets if filtering fails
    return allSets;
  }
}

// =============================================================================
// CARD SEARCH OPERATIONS
// =============================================================================

/**
 * Build search query from filter options
 */
function buildSearchQuery(format?: string | null, setCode?: string | null): string {
  const queryParts: string[] = [];
  
  if (format && format !== 'all') {
    queryParts.push(`format:${format}`);
  }
  
  if (setCode && setCode !== 'all') {
    queryParts.push(`set:${setCode}`);
  }
  
  // If no filters, search all cards
  return queryParts.length > 0 ? queryParts.join(' ') : '*';
}

/**
 * Search for cards with optional format and set filters
 * @param format - MTG format (e.g., "standard", "modern") or null for all formats
 * @param setCode - Set code (e.g., "neo", "mh2") or null for all sets
 * @param page - Page number for pagination (1-based)
 */
export async function searchCards(
  format?: string | null,
  setCode?: string | null,
  page: number = 1
): Promise<ScryfallSearchResponse> {
  const query = buildSearchQuery(format, setCode);
  const endpoint = `/cards/search?q=${encodeURIComponent(query)}&page=${page}`;
  
  try {
    return await makeRequest<ScryfallSearchResponse>(endpoint);
  } catch (error) {
    console.error('Failed to search cards:', error);
    throw new ScryfallApiError('Failed to search for cards');
  }
}

/**
 * Get a random card from the filtered card pool
 * Uses search with random page selection for better distribution
 */
export async function getRandomCard(
  format?: string | null,
  setCode?: string | null
): Promise<ScryfallCard> {
  try {
    // First, get the total number of cards to calculate random page
    const firstPage = await searchCards(format, setCode, 1);
    
    if (firstPage.total_cards === 0) {
      throw new ScryfallApiError('No cards found with the selected filters');
    }
    
    // Calculate random page (Scryfall returns ~175 cards per page)
    const cardsPerPage = firstPage.data.length;
    const totalPages = Math.ceil(firstPage.total_cards / cardsPerPage);
    const randomPage = Math.floor(Math.random() * totalPages) + 1;
    
    // Get random page
    const randomPageResponse = await searchCards(format, setCode, randomPage);
    
    if (randomPageResponse.data.length === 0) {
      throw new ScryfallApiError('No cards found on selected page');
    }
    
    // Pick random card from that page
    const randomIndex = Math.floor(Math.random() * randomPageResponse.data.length);
    return randomPageResponse.data[randomIndex];
    
  } catch (error) {
    console.error('Failed to get random card:', error);
    if (error instanceof ScryfallApiError) {
      throw error;
    }
    throw new ScryfallApiError('Failed to get random card');
  }
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
 * Check if a card is legal in a specific format
 */
export function isCardLegalInFormat(card: ScryfallCard, format: string): boolean {
  return card.legalities[format] === 'legal';
}

/**
 * Normalize card name for comparison (remove special characters, lowercase)
 */
export function normalizeCardName(name: string): string {
  return name
    .toLowerCase()
    .replace(/[^a-z0-9\\s]/g, '') // Remove special characters except spaces
    .replace(/\\s+/g, ' ') // Collapse multiple spaces
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
 * Get all available MTG formats for reference
 */
export function getAllFormats(): string[] {
  return [...MTG_FORMATS];
}

/**
 * Get all defined format-set mappings for reference
 */
export function getFormatSetMappings(): Record<string, string[]> {
  return { ...FORMAT_LEGAL_SETS };
}

/**
 * Add a new set to Standard (and automatically to all other formats)
 * This is the ONLY function you need to call when a new set releases!
 * @param setCode - New set code to add (e.g., 'mkc')
 */
export function addNewSetToStandard(setCode: string): void {
  if (!STANDARD_SETS.includes(setCode)) {
    STANDARD_SETS.push(setCode);
    
    // Rebuild all format mappings to include the new set
    FORMAT_LEGAL_SETS.standard = [...STANDARD_SETS];
    FORMAT_LEGAL_SETS.pioneer = [...STANDARD_SETS, ...PIONEER_ADDITIONAL_SETS];
    FORMAT_LEGAL_SETS.modern = [...STANDARD_SETS, ...PIONEER_ADDITIONAL_SETS, ...MODERN_ADDITIONAL_SETS];
    FORMAT_LEGAL_SETS.legacy = [...STANDARD_SETS, ...PIONEER_ADDITIONAL_SETS, ...MODERN_ADDITIONAL_SETS, ...LEGACY_ADDITIONAL_SETS];
    FORMAT_LEGAL_SETS.vintage = [...STANDARD_SETS, ...PIONEER_ADDITIONAL_SETS, ...MODERN_ADDITIONAL_SETS, ...LEGACY_ADDITIONAL_SETS];
    
    console.log(`Added ${setCode} to all formats. Standard now has ${STANDARD_SETS.length} sets.`);
  }
}

// =============================================================================
// ERROR EXPORT
// =============================================================================

export { ScryfallApiError };
export type { ApiError };
'''

    # Update the Scryfall service file
    service_file = Path('src/services/scryfall.ts')
    with open(service_file, 'w', encoding='utf-8') as f:
        f.write(service_content)
    
    print(f"✅ Updated Scryfall API service: {service_file}")

def main():
    """Main function to optimize hierarchical format mapping"""
    
    print("📊 Optimizing Hierarchical Format Mapping")
    print("=" * 60)
    
    # Verify we're in the right directory
    if not os.path.exists('package.json'):
        print("❌ Error: package.json not found!")
        print("   Make sure you're running this from the mtg-quiz-app/ root directory")
        return False
    
    # Verify the service file exists
    if not os.path.exists('src/services/scryfall.ts'):
        print("❌ Error: Scryfall API service not found!")
        print("   Please run the setup_scryfall_api_foundation.py script first")
        return False
    
    try:
        # Update the Scryfall service with hierarchical mapping
        update_scryfall_service()
        
        print("=" * 60)
        print("✅ Hierarchical Format Mapping Optimized!")
        print()
        print("📊 New Structure (Hierarchical Inheritance):")
        print("   • Standard (13 sets) ← BASE FORMAT")
        print("   • Pioneer = Standard + Pioneer additional (30+ sets)")
        print("   • Modern = Pioneer + Modern additional (50+ sets)")
        print("   • Legacy = Modern + Legacy additional (80+ sets)")
        print("   • Vintage = Same as Legacy (80+ sets)")
        print()
        print("🎯 Maintenance Benefits:")
        print("   • Add new set to STANDARD_SETS only")
        print("   • Automatically appears in ALL formats")
        print("   • No duplicate maintenance across formats")
        print("   • Guaranteed consistency between formats")
        print()
        print("⚡ Easy Updates:")
        print("   • Standard rotation: Update STANDARD_SETS array")
        print("   • New set release: Add to STANDARD_SETS")
        print("   • All other formats inherit automatically")
        print()
        print("🔧 Future Set Addition Example:")
        print("   When new set 'abc' releases:")
        print("   1. Add 'abc' to STANDARD_SETS array")
        print("   2. All formats automatically include it")
        print("   3. No other changes needed!")
        print()
        print("🧪 Test Your Optimization:")
        print("   1. Refresh browser")
        print("   2. Test all format + set combinations")
        print("   3. Verify set counts are accurate")
        print("   4. No functionality should change - just easier maintenance")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during optimization: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
