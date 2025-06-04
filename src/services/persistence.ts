// Game State Persistence Service
// Handles all localStorage operations for maintaining game state across browser sessions

import type { ScryfallCard, GameState } from '../types';

// =============================================================================
// PERSISTENCE CONFIGURATION
// =============================================================================

const STORAGE_KEY = 'mtg-quiz-app-state';
const STORAGE_VERSION = '1.0';

// =============================================================================
// TYPESCRIPT INTERFACES FOR PERSISTED STATE
// =============================================================================

export interface PersistedGameState {
  // App-level state
  selectedFormat: string | null;
  selectedSet: string | null;
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
  // App filters
  selectedFormat: null,
  selectedSet: null,
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
      hasCurrentCard: !!updatedState.currentCard
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
    
    // Check version compatibility  
    if (parsed.version !== STORAGE_VERSION) {
      console.warn(`Storage version mismatch (${parsed.version} vs ${STORAGE_VERSION}), using defaults`);
      return { ...DEFAULT_PERSISTED_STATE };
    }
    
    // Validate required fields and provide defaults for missing ones
    const loadedState: PersistedGameState = {
      ...DEFAULT_PERSISTED_STATE,
      ...parsed.data,
      version: STORAGE_VERSION // Ensure version is current
    };
    
    console.log('Game state loaded successfully:', {
      score: loadedState.score,
      streak: loadedState.streak,
      totalGuesses: loadedState.totalGuesses,
      isGameActive: loadedState.isGameActive,
      hasCurrentCard: !!loadedState.currentCard,
      selectedFormat: loadedState.selectedFormat,
      selectedSet: loadedState.selectedSet,
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
 * Reset game scores while preserving filter settings
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
 * Save only filter preferences
 */
export function saveFilterPreferences(format: string | null, set: string | null): boolean {
  return saveGameState({
    selectedFormat: format,
    selectedSet: set
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
    return saveGameState(importedState);
  } catch (error) {
    console.error('Failed to import game state:', error);
    return false;
  }
}
