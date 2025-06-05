// Game State Persistence Service - Multiple Sets Support
// Handles all localStorage operations for maintaining game state across browser sessions

import type { ScryfallCard, GameState } from '../types';

// =============================================================================
// PERSISTENCE CONFIGURATION
// =============================================================================

const STORAGE_KEY = 'mtg-quiz-app-state';
const STORAGE_VERSION = '3.0'; // Incremented for multiple sets version

// =============================================================================
// TYPESCRIPT INTERFACES FOR PERSISTED STATE
// =============================================================================

export interface PersistedGameState {
  // App-level state - multiple sets
  selectedSets: string[];
  isGameActive: boolean;
  
  // Game scores and progress
  score: number;
  streak: number;
  totalGuesses: number;
  
  // Current game state
  currentCard: ScryfallCard | null;
  isGuessSubmitted: boolean;
  lastGuess: string;
  isCorrectGuess: boolean | null;
  guessInput: string;
  
  // Metadata
  version: string;
  lastSaved: string;
}

interface StorageWrapper {
  data: PersistedGameState;
  version: string;
  timestamp: string;
}

// =============================================================================
// DEFAULT STATE
// =============================================================================

const DEFAULT_PERSISTED_STATE: PersistedGameState = {
  // App filters - multiple sets
  selectedSets: [],
  isGameActive: false,
  
  // Game progress
  score: 0,
  streak: 0,
  totalGuesses: 0,
  
  // Current game state
  currentCard: null,
  isGuessSubmitted: false,
  lastGuess: '',
  isCorrectGuess: null,
  guessInput: '',
  
  // Metadata
  version: STORAGE_VERSION,
  lastSaved: new Date().toISOString()
};

// =============================================================================
// STORAGE OPERATIONS
// =============================================================================

/**
 * Check if localStorage is available and working
 */
function isLocalStorageAvailable(): boolean {
  try {
    const test = '__localStorage_test__';
    localStorage.setItem(test, 'test');
    localStorage.removeItem(test);
    return true;
  } catch (error) {
    console.warn('localStorage is not available:', error);
    return false;
  }
}

/**
 * Save game state to localStorage
 */
export function saveGameState(state: Partial<PersistedGameState>): boolean {
  if (!isLocalStorageAvailable()) {
    console.warn('Cannot save game state: localStorage not available');
    return false;
  }
  
  try {
    // Get existing state or use defaults
    const existingState = loadGameState();
    
    // Merge with new state
    const updatedState: PersistedGameState = {
      ...existingState,
      ...state,
      version: STORAGE_VERSION,
      lastSaved: new Date().toISOString()
    };
    
    // Wrap with metadata
    const storageData: StorageWrapper = {
      data: updatedState,
      version: STORAGE_VERSION,
      timestamp: new Date().toISOString()
    };
    
    localStorage.setItem(STORAGE_KEY, JSON.stringify(storageData));
    
    console.log('Game state saved successfully:', {
      score: updatedState.score,
      streak: updatedState.streak,
      totalGuesses: updatedState.totalGuesses,
      isGameActive: updatedState.isGameActive,
      hasCurrentCard: !!updatedState.currentCard,
      selectedSetsCount: updatedState.selectedSets.length
    });
    
    return true;
  } catch (error) {
    console.error('Failed to save game state:', error);
    return false;
  }
}

/**
 * Load game state from localStorage
 */
export function loadGameState(): PersistedGameState {
  if (!isLocalStorageAvailable()) {
    console.warn('Cannot load game state: localStorage not available');
    return { ...DEFAULT_PERSISTED_STATE };
  }
  
  try {
    const storedData = localStorage.getItem(STORAGE_KEY);
    
    if (!storedData) {
      console.log('No stored game state found, using defaults');
      return { ...DEFAULT_PERSISTED_STATE };
    }
    
    const parsed: StorageWrapper = JSON.parse(storedData);
    
    // Validate storage format
    if (!parsed.data || !parsed.version) {
      console.warn('Invalid storage format, using defaults');
      return { ...DEFAULT_PERSISTED_STATE };
    }
    
    // Check version compatibility - reset if old version
    if (parsed.version !== STORAGE_VERSION) {
      console.warn(`Storage version mismatch (${parsed.version} vs ${STORAGE_VERSION}), using defaults`);
      return { ...DEFAULT_PERSISTED_STATE };
    }
    
    // Validate required fields and provide defaults for missing ones
    const loadedState: PersistedGameState = {
      ...DEFAULT_PERSISTED_STATE,
      ...parsed.data,
      // Ensure selectedSets is always an array
      selectedSets: Array.isArray(parsed.data.selectedSets) ? parsed.data.selectedSets : [],
      version: STORAGE_VERSION // Ensure version is current
    };
    
    console.log('Game state loaded successfully:', {
      score: loadedState.score,
      streak: loadedState.streak,
      totalGuesses: loadedState.totalGuesses,
      isGameActive: loadedState.isGameActive,
      hasCurrentCard: !!loadedState.currentCard,
      selectedSetsCount: loadedState.selectedSets.length,
      selectedSets: loadedState.selectedSets,
      lastSaved: loadedState.lastSaved
    });
    
    return loadedState;
  } catch (error) {
    console.error('Failed to load game state:', error);
    return { ...DEFAULT_PERSISTED_STATE };
  }
}

/**
 * Clear all stored game state
 */
export function clearGameState(): boolean {
  if (!isLocalStorageAvailable()) {
    console.warn('Cannot clear game state: localStorage not available');
    return false;
  }
  
  try {
    localStorage.removeItem(STORAGE_KEY);
    console.log('Game state cleared successfully');
    return true;
  } catch (error) {
    console.error('Failed to clear game state:', error);
    return false;
  }
}

/**
 * Reset game scores while preserving set selections
 */
export function resetGameScores(): boolean {
  const currentState = loadGameState();
  
  return saveGameState({
    score: 0,
    streak: 0,
    totalGuesses: 0,
    currentCard: null,
    isGuessSubmitted: false,
    lastGuess: '',
    isCorrectGuess: null,
    guessInput: '',
    isGameActive: false
  });
}

/**
 * Save set preferences (multiple sets)
 */
export function saveSetPreferences(sets: string[]): boolean {
  return saveGameState({
    selectedSets: [...sets] // Create copy to avoid reference issues
  });
}

/**
 * Save only game progress (scores, current card, etc.)
 */
export function saveGameProgress(gameState: GameState, guessInput: string): boolean {
  return saveGameState({
    score: gameState.score,
    streak: gameState.streak,
    totalGuesses: gameState.totalGuesses,
    currentCard: gameState.currentCard,
    isGuessSubmitted: gameState.isGuessSubmitted,
    lastGuess: gameState.lastGuess,
    isCorrectGuess: gameState.isCorrectGuess,
    guessInput: guessInput
  });
}

/**
 * Save game active status
 */
export function saveGameActiveStatus(isGameActive: boolean): boolean {
  return saveGameState({ isGameActive });
}

/**
 * Add a set to current selection
 */
export function addSetToSelection(setCode: string): boolean {
  const currentState = loadGameState();
  const currentSets = currentState.selectedSets || [];
  
  if (!currentSets.includes(setCode)) {
    return saveSetPreferences([...currentSets, setCode]);
  }
  
  return true; // Already in selection
}

/**
 * Remove a set from current selection
 */
export function removeSetFromSelection(setCode: string): boolean {
  const currentState = loadGameState();
  const currentSets = currentState.selectedSets || [];
  
  return saveSetPreferences(currentSets.filter(code => code !== setCode));
}

/**
 * Clear all set selections
 */
export function clearSetSelections(): boolean {
  return saveSetPreferences([]);
}

// =============================================================================
// UTILITY FUNCTIONS
// =============================================================================

/**
 * Get storage info for debugging
 */
export function getStorageInfo(): object {
  if (!isLocalStorageAvailable()) {
    return { available: false };
  }
  
  try {
    const storedData = localStorage.getItem(STORAGE_KEY);
    if (!storedData) {
      return { available: true, hasData: false };
    }
    
    const parsed = JSON.parse(storedData);
    return {
      available: true,
      hasData: true,
      version: parsed.version,
      timestamp: parsed.timestamp,
      dataSize: storedData.length,
      state: parsed.data
    };
  } catch (error) {
    return { available: true, hasData: false, error: error.message };
  }
}

/**
 * Export current state as JSON (for backup/debugging)
 */
export function exportGameState(): string {
  const state = loadGameState();
  return JSON.stringify(state, null, 2);
}

/**
 * Import state from JSON (for restore/debugging)
 */
export function importGameState(jsonData: string): boolean {
  try {
    const importedState = JSON.parse(jsonData);
    // Ensure selectedSets is an array
    if (importedState.selectedSets && !Array.isArray(importedState.selectedSets)) {
      importedState.selectedSets = [];
    }
    return saveGameState(importedState);
  } catch (error) {
    console.error('Failed to import game state:', error);
    return false;
  }
}
