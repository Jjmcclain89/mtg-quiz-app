// TypeScript type definitions for MTG Quiz App
// Based on Scryfall API documentation: https://scryfall.com/docs/api

// =============================================================================
// SCRYFALL API RESPONSE TYPES
// =============================================================================

export interface ScryfallCard {
  id: string;
  name: string;
  mana_cost?: string;
  cmc: number;
  type_line: string;
  oracle_text?: string;
  set: string;
  set_name: string;
  rarity: string;
  image_uris?: {
    small: string;
    normal: string;
    large: string;
    png: string;
    art_crop: string;
    border_crop: string;
  };
  card_faces?: Array<{
    name: string;
    image_uris?: {
      small: string;
      normal: string;
      large: string;
      png: string;
      art_crop: string;
      border_crop: string;
    };
  }>;
  legalities: {
    [format: string]: 'legal' | 'not_legal' | 'restricted' | 'banned';
  };
  color_identity?: string[];
}

export interface ScryfallSearchResponse {
  object: 'list';
  total_cards: number;
  has_more: boolean;
  next_page?: string;
  data: ScryfallCard[];
}

export interface ScryfallSet {
  id: string;
  code: string;
  name: string;
  set_type: string;
  released_at: string;
  card_count: number;
  digital: boolean;
  nonfoil_only: boolean;
  foil_only: boolean;
}

export interface ScryfallSetsResponse {
  object: 'list';
  data: ScryfallSet[];
}

export interface ScryfallAutocompleteResponse {
  object: 'catalog';
  data: string[];
}

// =============================================================================
// APPLICATION STATE TYPES
// =============================================================================

export interface GameSettings {
  selectedFormat: string | null;
  selectedSet: string | null;
  inputMode: 'autocomplete' | 'plaintext' | 'multiplechoice';
  difficultyLevel: 'easy' | 'medium' | 'hard' | 'expert';
}

export interface GameState {
  currentCard: ScryfallCard | null;
  isLoading: boolean;
  isGuessSubmitted: boolean;
  lastGuess: string;
  isCorrectGuess: boolean | null;
  score: number;
  streak: number;
  totalGuesses: number;
  inputMode: 'autocomplete' | 'plaintext' | 'multiplechoice';
  multipleChoiceOptions?: string[];
  selectedChoice?: string;
}

export interface FilterOptions {
  formats: string[];
  sets: ScryfallSet[];
  isFormatsLoading: boolean;
  isSetsLoading: boolean;
  formatsError: string | null;
  setsError: string | null;
}

// =============================================================================
// MULTIPLE CHOICE TYPES
// =============================================================================

export interface MultipleChoiceOption {
  text: string;
  isCorrect: boolean;
  cardId?: string;
}

export interface MultipleChoiceState {
  options: MultipleChoiceOption[];
  selectedIndex: number | null;
  isSubmitted: boolean;
}

// =============================================================================
// PERSISTENCE TYPES
// =============================================================================

export interface PersistedGameState {
  // App-level state
  selectedFormat: string | null;
  selectedSet: string | null;
  isGameActive: boolean;
  inputMode: 'autocomplete' | 'plaintext' | 'multiplechoice';
  
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
  multipleChoiceOptions?: string[];
  selectedChoice?: string;
  
  // Metadata
  version: string;
  lastSaved: string;
}

export interface StorageMeta {
  version: string;
  timestamp: string;
  dataSize?: number;
}

export interface GameStateSnapshot {
  state: PersistedGameState;
  meta: StorageMeta;
}

// =============================================================================
// API ERROR TYPES
// =============================================================================

export interface ScryfallError {
  object: 'error';
  code: string;
  status: number;
  warnings?: string[];
  details: string;
}

export interface ApiError {
  message: string;
  status?: number;
  code?: string;
  details?: string;
}

// =============================================================================
// UTILITY TYPES
// =============================================================================

export type LoadingState = 'idle' | 'loading' | 'success' | 'error';

export interface LoadingStates {
  formats: LoadingState;
  sets: LoadingState;
  cards: LoadingState;
  autocomplete: LoadingState;
}

// =============================================================================
// PERSISTENCE UTILITY TYPES
// =============================================================================

export type PersistenceOperation = 'save' | 'load' | 'clear' | 'reset';

export interface PersistenceResult {
  success: boolean;
  operation: PersistenceOperation;
  data?: any;
  error?: string;
}

export interface StorageInfo {
  available: boolean;
  hasData?: boolean;
  version?: string;
  timestamp?: string;
  dataSize?: number;
  error?: string;
}
