import React, { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import {
    getRandomCardFromSets,
    getCardNameAutocomplete,
    getCardNameAutocompleteFromSets,
    getCardImageUrl,
    cardNamesMatch,
    generateMultipleChoiceOptions,
} from '../services/scryfall';
import {
    loadGameState,
    saveGameProgress,
    resetGameScores,
} from '../services/persistence';
import type { ScryfallCard, GameState } from '../types';
import MultipleChoiceInput from './MultipleChoiceInput';

interface CardGuessingGameProps {
    selectedSets: string[];
    inputMode: 'autocomplete' | 'plaintext' | 'multiplechoice';
    onBackToSetup: () => void;
}

// Mobile detection utility
function isMobileDevice(): boolean {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
        navigator.userAgent
    );
}

// Helper function to get card frame color for overlay (completely opaque)
function getCardFrameColor(card: ScryfallCard): string {
    // Determine overlay color based on card colors/type - fully opaque
    const colors = card.color_identity || [];

    if (colors.length === 0) {
        // Colorless/Artifact
        return '#C0C0C0'; // Light gray
    } else if (colors.length === 1) {
        // Mono-colored
        switch (colors[0]) {
            case 'W':
                return '#FFFBD5'; // White - cream
            case 'U':
                return '#0E68AB'; // Blue
            case 'B':
                return '#150B00'; // Black
            case 'R':
                return '#D3202A'; // Red
            case 'G':
                return '#00733E'; // Green
            default:
                return '#F5F5DC'; // Default cream
        }
    } else {
        // Multi-colored
        return '#F4E164'; // Gold
    }
}


// Memoized version of MultipleChoiceInput to prevent unnecessary re-renders
const MemoizedMultipleChoiceInput = React.memo(MultipleChoiceInput, (prevProps, nextProps) => {
    // Only re-render if the props that actually matter have changed
    return (
        prevProps.isCorrect === nextProps.isCorrect &&
        prevProps.correctAnswer === nextProps.correctAnswer &&
        JSON.stringify(prevProps.options) === JSON.stringify(nextProps.options)
    );
});

export default function CardGuessingGame({
    selectedSets,
    inputMode,
    onBackToSetup,
}: CardGuessingGameProps) {
    // Game state (will be restored from localStorage)
    const [gameState, setGameState] = useState<GameState>({
        currentCard: null,
        isLoading: false,
        isGuessSubmitted: false,
        lastGuess: '',
        isCorrectGuess: null,
        score: 0,
        streak: 0,
        totalGuesses: 0,
        inputMode: inputMode,
        multipleChoiceOptions: [],
        selectedChoice: null,
    });

    // Input state (will be restored from localStorage)
    const [guessInput, setGuessInput] = useState('');

    // Autocomplete state (not persisted - ephemeral)
    const [autocompleteOptions, setAutocompleteOptions] = useState<string[]>(
        []
    );
    const [showAutocomplete, setShowAutocomplete] = useState(false);
    const [isLoadingAutocomplete, setIsLoadingAutocomplete] = useState(false);
    const [highlightedIndex, setHighlightedIndex] = useState<number>(-1);

    // Multiple choice state
    const [selectedChoice, setSelectedChoice] = useState<string | null>(null);

    // State restoration tracking
    const [isStateRestored, setIsStateRestored] = useState(false);

    // Refs
    const inputRef = useRef<HTMLInputElement>(null);

    // Update game state when inputMode prop changes
    useEffect(() => {
        setGameState((prev) => ({ ...prev, inputMode }));
    }, [inputMode]);

    // Regenerate multiple choice options when switching to multiple choice mode
    // Only run this when inputMode changes to multiplechoice, not on every state change
    useEffect(() => {
        const regenerateOptionsIfNeeded = async () => {
            // Only regenerate if we're switching TO multiple choice mode and don't have options
            if (
                inputMode === 'multiplechoice' &&
                gameState.currentCard &&
                (!gameState.multipleChoiceOptions ||
                    gameState.multipleChoiceOptions.length === 0) &&
                !gameState.isGuessSubmitted &&
                selectedSets.length > 0
            ) {
                console.log(
                    'Regenerating multiple choice options for mode switch...'
                );

                try {
                    const options = await generateMultipleChoiceOptions(
                        gameState.currentCard,
                        selectedSets
                    );
                    setGameState((prev) => ({
                        ...prev,
                        multipleChoiceOptions: options,
                    }));
                    console.log(
                        'Successfully regenerated multiple choice options:',
                        options
                    );
                } catch (error) {
                    console.error(
                        'Failed to regenerate multiple choice options:',
                        error
                    );
                    // Fallback options
                    const fallbackOptions = [
                        { text: gameState.currentCard.name, isCorrect: true },
                        { text: 'Lightning Bolt', isCorrect: false },
                        { text: 'Counterspell', isCorrect: false },
                        { text: 'Giant Growth', isCorrect: false }
                    ];
                    setGameState((prev) => ({
                        ...prev,
                        multipleChoiceOptions: fallbackOptions,
                    }));
                }
            }
        };

        regenerateOptionsIfNeeded();
    }, [
        inputMode,
        gameState.currentCard?.id, // Only check card ID, not full object
        gameState.isGuessSubmitted,
        // Remove multipleChoiceOptions from dependencies to prevent re-render loop
    ]);

    // Restore game state from localStorage on mount
    useEffect(() => {
        try {
            const persistedState = loadGameState();

            // Restore game progress
            setGameState({
                currentCard: persistedState.currentCard,
                isLoading: false,
                isGuessSubmitted: persistedState.isGuessSubmitted,
                lastGuess: persistedState.lastGuess,
                isCorrectGuess: persistedState.isCorrectGuess,
                score: persistedState.score,
                streak: persistedState.streak,
                totalGuesses: persistedState.totalGuesses,
                inputMode: inputMode, // Use current prop
                multipleChoiceOptions:
                    persistedState.multipleChoiceOptions || [],
                selectedChoice: persistedState.selectedChoice || null,
            });

            // Restore input state
            setGuessInput(persistedState.guessInput);
            setSelectedChoice(persistedState.selectedChoice || null);

            setIsStateRestored(true);

            console.log('Game state restored from localStorage:', {
                score: persistedState.score,
                streak: persistedState.streak,
                totalGuesses: persistedState.totalGuesses,
                hasCurrentCard: !!persistedState.currentCard,
                isGuessSubmitted: persistedState.isGuessSubmitted,
                inputMode: inputMode,
            });

            // If no current card was saved, load a new one
            if (!persistedState.currentCard) {
                loadNewCard();
            }
        } catch (error) {
            console.error('Failed to restore game state:', error);
            setIsStateRestored(true);
            loadNewCard(); // Start fresh on restoration failure
        }
    }, []);

    // Auto-save game progress whenever gameState or guessInput changes
    useEffect(() => {
        if (isStateRestored) {
            const stateToSave = {
                ...gameState,
                selectedChoice: selectedChoice,
            };
            saveGameProgress(stateToSave, guessInput);
        }
    }, [gameState, guessInput, selectedChoice, isStateRestored]);

    // Mobile UX: Input focus is manual to keep card image visible  // Focus input when new card loads (desktop only - prevent mobile keyboard popup)
    useEffect(() => {
        if (
            gameState.currentCard &&
            !gameState.isGuessSubmitted &&
            inputRef.current
        ) {
            // Only auto-focus on non-mobile devices and autocomplete mode to prevent keyboard covering card
            if (!isMobileDevice() && inputMode === 'autocomplete') {
                inputRef.current.focus();
            }
        }
    }, [gameState.currentCard, gameState.isGuessSubmitted, inputMode]);

    // Reset highlighted index when autocomplete options change
    useEffect(() => {
        setHighlightedIndex(-1);
    }, [autocompleteOptions]);

    // Autocomplete functionality - immediate response (no debounce)
    useEffect(() => {
        // Only run autocomplete for autocomplete mode
        if (inputMode !== 'autocomplete') {
            setShowAutocomplete(false);
            setAutocompleteOptions([]);
            setHighlightedIndex(-1);
            return;
        }

        // Don't show autocomplete if guess is submitted or input is empty
        if (gameState.isGuessSubmitted || guessInput.length < 2) {
            setShowAutocomplete(false);
            setAutocompleteOptions([]);
            setHighlightedIndex(-1);
            return;
        }

        // Make autocomplete request immediately
        const fetchAutocomplete = async () => {
            try {
                setIsLoadingAutocomplete(true);
                const suggestions = await getCardNameAutocompleteFromSets(
                    guessInput,
                    selectedSets
                );
                setAutocompleteOptions(suggestions.slice(0, 8)); // Limit to 8 suggestions
                setShowAutocomplete(suggestions.length > 0);
            } catch (error) {
                console.error('Autocomplete error:', error);
                setAutocompleteOptions([]);
                setShowAutocomplete(false);
            } finally {
                setIsLoadingAutocomplete(false);
            }
        };

        fetchAutocomplete();
    }, [guessInput, gameState.isGuessSubmitted, inputMode]);

    const loadNewCard = async () => {
        try {
            setGameState((prev) => ({ ...prev, isLoading: true }));

            // Use multiple sets for card selection
            const card = await getRandomCardFromSets(selectedSets);

            // Generate multiple choice options if in multiple choice mode
            let multipleChoiceOptions: { text: string; isCorrect: boolean }[] = [];
            if (inputMode === 'multiplechoice') {
                try {
                    multipleChoiceOptions = await generateMultipleChoiceOptions(
                        card,
                        selectedSets
                    );
                } catch (error) {
                    console.error(
                        'Failed to generate multiple choice options:',
                        error
                    );
                    // Fallback options
                    multipleChoiceOptions = [
                        { text: card.name, isCorrect: true },
                        { text: 'Lightning Bolt', isCorrect: false },
                        { text: 'Counterspell', isCorrect: false },
                        { text: 'Giant Growth', isCorrect: false }
                    ];
                }
            }

            setGameState((prev) => ({
                ...prev,
                currentCard: card,
                isLoading: false,
                isGuessSubmitted: false,
                lastGuess: '',
                isCorrectGuess: null,
                multipleChoiceOptions,
                selectedChoice: null,
            }));

            // Reset input states
            setGuessInput('');
            setSelectedChoice(null);
            setShowAutocomplete(false);
            setAutocompleteOptions([]);
            setHighlightedIndex(-1);
        } catch (error) {
            console.error('Error loading card:', error);
            setGameState((prev) => ({
                ...prev,
                isLoading: false,
                currentCard: null,
            }));
        }
    };

    const submitGuess = () => {
        if (!gameState.currentCard) return;

        let guessToCheck = '';
        let displayGuess = '';

        if (inputMode === 'multiplechoice') {
            if (!selectedChoice) return;
            guessToCheck = selectedChoice;
            displayGuess = selectedChoice;
        } else {
            if (!guessInput.trim()) return;
            guessToCheck = guessInput;
            displayGuess = guessInput;
        }

        const isCorrect = cardNamesMatch(
            guessToCheck,
            gameState.currentCard.name
        );

        setGameState((prev) => ({
            ...prev,
            isGuessSubmitted: true,
            lastGuess: displayGuess,
            isCorrectGuess: isCorrect,
            score: isCorrect ? prev.score + 1 : prev.score,
            streak: isCorrect ? prev.streak + 1 : 0,
            totalGuesses: prev.totalGuesses + 1,
            selectedChoice:
                inputMode === 'multiplechoice' ? selectedChoice : null,
        }));

        setShowAutocomplete(false);
        setHighlightedIndex(-1);
    };

    const skipCard = () => {
        if (!gameState.currentCard) return;

        setGameState((prev) => ({
            ...prev,
            isGuessSubmitted: true,
            lastGuess: '',
            isCorrectGuess: false,
            streak: 0,
            totalGuesses: prev.totalGuesses + 1,
            selectedChoice: null,
        }));

        setShowAutocomplete(false);
        setHighlightedIndex(-1);
        setSelectedChoice(null);
    };

    const nextCard = () => {
        loadNewCard();
    };

    const resetScores = () => {
        resetGameScores();
        setGameState((prev) => ({
            ...prev,
            score: 0,
            streak: 0,
            totalGuesses: 0,
            currentCard: null,
            isGuessSubmitted: false,
            lastGuess: '',
            isCorrectGuess: null,
            multipleChoiceOptions: [],
            selectedChoice: null,
        }));
        setGuessInput('');
        setSelectedChoice(null);
        loadNewCard();
    };

    const handleInputChange = (value: string) => {
        setGuessInput(value);
    };

    const handleChoiceSelect = useCallback((choice: string) => {
        // Set the selected choice and immediately submit
        setSelectedChoice(choice);

        // Auto-submit the guess
        if (!gameState.currentCard) return;

        const isCorrect = cardNamesMatch(choice, gameState.currentCard.name);

        setGameState((prev) => ({
            ...prev,
            isGuessSubmitted: true,
            lastGuess: choice,
            isCorrectGuess: isCorrect,
            score: isCorrect ? prev.score + 1 : prev.score,
            streak: isCorrect ? prev.streak + 1 : 0,
            totalGuesses: prev.totalGuesses + 1,
            selectedChoice: choice,
        }));

        setShowAutocomplete(false);
        setHighlightedIndex(-1);
    }, [gameState.currentCard]);

    const handleKeyDown = (event: React.KeyboardEvent) => {
        // Only handle keyboard events for autocomplete mode
        if (inputMode !== 'autocomplete') return;

        // Handle autocomplete navigation
        if (showAutocomplete && autocompleteOptions.length > 0) {
            if (event.key === 'ArrowDown') {
                event.preventDefault();
                setHighlightedIndex((prev) =>
                    prev < autocompleteOptions.length - 1 ? prev + 1 : 0
                );
                return;
            }

            if (event.key === 'ArrowUp') {
                event.preventDefault();
                setHighlightedIndex((prev) =>
                    prev > 0 ? prev - 1 : autocompleteOptions.length - 1
                );
                return;
            }

            if (event.key === 'Enter' && highlightedIndex >= 0) {
                event.preventDefault();
                selectAutocompleteOption(autocompleteOptions[highlightedIndex]);
                return;
            }
        }

        // Handle normal game actions
        if (event.key === 'Enter') {
            if (gameState.isGuessSubmitted) {
                nextCard();
            } else {
                submitGuess();
            }
        } else if (event.key === 'Escape') {
            setShowAutocomplete(false);
            setHighlightedIndex(-1);
        }
    };

    const selectAutocompleteOption = (option: string) => {
        setGuessInput(option);
        setShowAutocomplete(false);
        setHighlightedIndex(-1);
        if (inputRef.current && !isMobileDevice()) {
            inputRef.current.focus();
        }
    };

    // Calculate accuracy percentage
    const accuracy =
        gameState.totalGuesses > 0
            ? Math.round((gameState.score / gameState.totalGuesses) * 100)
            : 0;

    // Show loading while restoring state
    if (!isStateRestored) {
        return (
            <div className='min-h-screen bg-gray-100 flex items-center justify-center'>
                <div className='bg-white rounded-lg shadow-lg p-8 text-center'>
                    <div className='animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4'></div>
                    <p className='text-xl text-gray-600'>
                        Restoring your game...
                    </p>
                </div>
            </div>
        );
    }

    if (gameState.isLoading) {
        return (
            <div className='min-h-screen bg-gray-100 flex items-center justify-center'>
                <div className='bg-white rounded-lg shadow-lg p-8 text-center'>
                    <div className='animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4'></div>
                    <p className='text-xl text-gray-600'>
                        Loading your next card...
                    </p>
                </div>
            </div>
        );
    }

    if (!gameState.currentCard) {
        return (
            <div className='min-h-screen bg-gray-100 flex items-center justify-center'>
                <div className='bg-white rounded-lg shadow-lg p-8 text-center max-w-md'>
                    <h3 className='text-2xl font-semibold text-gray-700 mb-4'>
                        No Card Available
                    </h3>
                    <p className='text-gray-600 mb-6'>
                        Unable to load a card from the selected sets. This might
                        be a temporary issue, or there may be no cards available
                        in your current selection.
                    </p>
                    <div className='space-y-3'>
                        <button
                            onClick={loadNewCard}
                            className='w-full bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors'
                        >
                            Try Again
                        </button>
                        <button
                            onClick={onBackToSetup}
                            className='w-full bg-gray-600 text-white px-6 py-3 rounded-lg hover:bg-gray-700 transition-colors'
                        >
                            Back to Setup
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className='min-h-screen bg-gray-100'>
            <div className='container mx-auto px-4 py-8 max-w-4xl'>
                {/* Input Section - TOP PRIORITY for mobile interaction */}
                <div className='bg-white rounded-lg shadow-lg p-4 sm:p-6 mb-4 sm:mb-6'>
                    {!gameState.isGuessSubmitted ? (
                        <div className='space-y-4'>
                            {/* Render different inputs based on mode */}
                            {inputMode === 'multiplechoice' ? (
                                <MemoizedMultipleChoiceInput
                                    options={gameState.multipleChoiceOptions || []}
                                    onChoiceSelect={handleChoiceSelect}
                                    isCorrect={gameState.isCorrectGuess}
                                    correctAnswer={gameState.currentCard.name}
                                />
                            ) : (
                                <>
                                    {/* Text Input (Autocomplete or Plain Text) */}
                                    <div className='relative'>
                                        <label
                                            htmlFor='guess-input'
                                            className='block text-xs sm:text-sm font-medium text-gray-700 mb-1 sm:mb-2'
                                        >
                                            Enter card name:
                                        </label>
                                        <input
                                            ref={inputRef}
                                            id='guess-input'
                                            type='text'
                                            value={guessInput}
                                            onChange={(e) =>
                                                handleInputChange(
                                                    e.target.value
                                                )
                                            }
                                            onKeyDown={handleKeyDown}
                                            placeholder='Start typing a card name...'
                                            autoComplete='off'
                                            className='w-full p-2 sm:p-4 text-base sm:text-lg border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
                                        />

                                        {/* Autocomplete Dropdown - Only for autocomplete mode */}
                                        {inputMode === 'autocomplete' &&
                                            showAutocomplete &&
                                            autocompleteOptions.length > 0 && (
                                                <div className='absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-y-auto'>
                                                    {autocompleteOptions.map(
                                                        (option, index) => (
                                                            <button
                                                                key={index}
                                                                onClick={() =>
                                                                    selectAutocompleteOption(
                                                                        option
                                                                    )
                                                                }
                                                                className={`w-full text-left px-4 py-2 focus:outline-none first:rounded-t-lg last:rounded-b-lg transition-colors ${
                                                                    index ===
                                                                    highlightedIndex
                                                                        ? 'bg-blue-100 text-blue-900'
                                                                        : 'hover:bg-blue-50'
                                                                }`}
                                                            >
                                                                {option}
                                                            </button>
                                                        )
                                                    )}
                                                </div>
                                            )}

                                        {/* Loading indicator for autocomplete */}
                                        {inputMode === 'autocomplete' &&
                                            isLoadingAutocomplete && (
                                                <div className='absolute right-3 top-12 transform -translate-y-1/2'>
                                                    <div className='animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600'></div>
                                                </div>
                                            )}
                                    </div>

                                    {/* Navigation Instructions - Only for autocomplete mode */}
                                    {inputMode === 'autocomplete' &&
                                        showAutocomplete &&
                                        autocompleteOptions.length > 0 && (
                                            <div className='text-sm text-gray-600'>
                                                Use ↑↓ arrow keys to navigate,
                                                Enter to select, Escape to close
                                            </div>
                                        )}

                                    {/* Action Buttons - Mobile Optimized */}
                                    <div className='flex flex-row gap-3'>
                                        <button
                                            onClick={submitGuess}
                                            disabled={!guessInput.trim()}
                                            className='flex-1 bg-green-600 text-white py-2 px-3 sm:py-3 sm:px-6 rounded-lg text-sm sm:text-base font-medium hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors'
                                        >
                                            Submit Guess
                                        </button>
                                        <button
                                            onClick={skipCard}
                                            className='flex-1 bg-yellow-600 text-white py-2 px-3 sm:py-3 sm:px-6 rounded-lg text-sm sm:text-base font-medium hover:bg-yellow-700 transition-colors'
                                        >
                                            Skip Card
                                        </button>
                                    </div>
                                </>
                            )}
                        </div>
                    ) : (
                        <div className='text-center'>
                            <button
                                onClick={nextCard}
                                className='bg-blue-600 text-white py-4 px-8 rounded-lg text-lg font-medium hover:bg-blue-700 transition-colors'
                            >
                                Next Card →
                            </button>
                            <p className='text-gray-600 text-sm mt-2'>
                                Press Enter for next card
                            </p>
                        </div>
                    )}
                </div>

                {/* Card Display - MAIN CONTENT */}
                <div className='bg-white rounded-lg shadow-lg p-4 sm:p-6 mb-4 sm:mb-6'>
                    <div className='text-center'>
                        <h2 className='hidden sm:block text-2xl font-bold text-gray-800 mb-6'>
                            What's the name of this card?
                        </h2>

                        {/* Card Image with Name Overlay */}
                        <div className='flex justify-center mb-4 sm:mb-6'>
                            <div className='relative inline-block'>
                                <img
                                    src={getCardImageUrl(
                                        gameState.currentCard,
                                        'normal'
                                    )}
                                    alt='Magic card with hidden name'
                                    className='rounded-lg shadow-lg'
                                    style={{
                                        maxHeight: '500px',
                                        width: 'auto',
                                        height: 'auto',
                                    }}
                                />

                                {/* Name Overlay - Only show when guess NOT submitted */}
                                {!gameState.isGuessSubmitted && (
                                    <div
                                        className='absolute'
                                        style={{
                                            // Positioning to fully cover name text
                                            top: '5.5%', // Same top position
                                            left: '7%', // Same left margin
                                            right: '25%', // Same length
                                            height: '4.2%', // Current working height
                                            backgroundColor: getCardFrameColor(
                                                gameState.currentCard
                                            ),
                                            // Completely opaque with subtle border
                                            opacity: '1', // Full opacity - no transparency
                                            border: '1px solid rgba(0,0,0,0.15)',
                                            borderRadius: '2px',
                                            // Subtle shadow to blend with card
                                            boxShadow:
                                                'inset 0 1px 1px rgba(0,0,0,0.1)',
                                        }}
                                    />
                                )}
                            </div>
                        </div>

                        {/* Game Result Display */}
                        {gameState.isGuessSubmitted && (
                            <div className='mb-6'>
                                {gameState.isCorrectGuess ? (
                                    <div className='bg-green-50 border border-green-200 rounded-lg p-4'>
                                        <h3 className='text-xl font-bold text-green-800'>
                                            ✅ Correct!
                                        </h3>
                                        <p className='text-green-700'>
                                            The card is{' '}
                                            <span className='font-bold'>
                                                {gameState.currentCard.name}
                                            </span>
                                        </p>
                                        <p className='text-green-600 text-sm mt-1'>
                                            From{' '}
                                            {gameState.currentCard.set_name} (
                                            {gameState.currentCard.set.toUpperCase()}
                                            )
                                        </p>
                                    </div>
                                ) : (
                                    <div className='bg-red-50 border border-red-200 rounded-lg p-4'>
                                        <h3 className='text-xl font-bold text-red-800'>
                                            {gameState.lastGuess
                                                ? '❌ Incorrect'
                                                : '⏭️ Skipped'}
                                        </h3>
                                        <p className='text-red-700'>
                                            The card is{' '}
                                            <span className='font-bold'>
                                                {gameState.currentCard.name}
                                            </span>
                                        </p>
                                        <p className='text-red-600 text-sm mt-1'>
                                            From{' '}
                                            {gameState.currentCard.set_name} (
                                            {gameState.currentCard.set.toUpperCase()}
                                            )
                                        </p>
                                        {gameState.lastGuess && (
                                            <p className='text-red-600 text-sm mt-1'>
                                                Your guess: "
                                                {gameState.lastGuess}"
                                            </p>
                                        )}
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                </div>

                {/* Stats + Back Button Panel - Unified White Background */}
                <div className='bg-white rounded-lg shadow-lg p-6 mb-6'>
                    <div className='flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6'>
                        {/* Score Display */}
                        <div className='flex justify-center lg:justify-start'>
                            <div className='flex items-center space-x-8 text-center'>
                                <div className='flex flex-col items-center'>
                                    <div className='text-2xl font-bold text-green-600'>
                                        {gameState.score}
                                    </div>
                                    <div className='text-sm text-gray-600'>
                                        Correct
                                    </div>
                                </div>
                                <div className='flex flex-col items-center'>
                                    <div className='text-2xl font-bold text-red-600'>
                                        {gameState.totalGuesses -
                                            gameState.score}
                                    </div>
                                    <div className='text-sm text-gray-600'>
                                        Incorrect
                                    </div>
                                </div>
                                <div className='flex flex-col items-center'>
                                    <div className='text-2xl font-bold text-blue-600'>
                                        {gameState.streak}
                                    </div>
                                    <div className='text-sm text-gray-600'>
                                        Streak
                                    </div>
                                </div>
                                <div className='flex flex-col items-center'>
                                    <div className='text-2xl font-bold text-gray-600'>
                                        {accuracy}%
                                    </div>
                                    <div className='text-sm text-gray-600'>
                                        Accuracy
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Action Buttons - Inside Same Panel */}
                        <div className='lg:flex-shrink-0'>
                            <div className='flex flex-col sm:flex-row gap-3 lg:text-right'>
                                <button
                                    onClick={resetScores}
                                    className='bg-orange-600 text-white px-4 py-2 rounded-lg hover:bg-orange-700 transition-colors text-sm'
                                    title='Reset all scores and start fresh'
                                >
                                    Reset Scores
                                </button>
                                <button
                                    onClick={onBackToSetup}
                                    className='bg-gray-600 text-white px-6 py-3 rounded-lg hover:bg-gray-700 transition-colors'
                                >
                                    ← Back to Setup
                                </button>
                            </div>
                        </div>
                    </div>

                    {/* Game Info */}
                    <div className='mt-4 pt-4 border-t border-gray-200'>
                        <div className='flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2'>
                            <p className='text-sm text-gray-600'>
                                Playing with {selectedSets.length} set
                                {selectedSets.length !== 1 ? 's' : ''}:{' '}
                                <span className='font-medium'>
                                    {selectedSets
                                        .slice(0, 3)
                                        .map((code) => code.toUpperCase())
                                        .join(', ')}
                                    {selectedSets.length > 3 &&
                                        ` +${selectedSets.length - 3} more`}
                                </span>
                            </p>
                            <p className='text-sm text-gray-600'>
                                <span className='font-medium'>Input Mode:</span>{' '}
                                {inputMode === 'autocomplete' &&
                                    '💭 Autocomplete'}
                                {inputMode === 'plaintext' && '✏️ Plain Text'}
                                {inputMode === 'multiplechoice' &&
                                    '🎯 Multiple Choice'}
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
