import React from 'react';

interface MultipleChoiceOption {
  text: string;
  isCorrect: boolean;
}

interface MultipleChoiceInputProps {
  options: MultipleChoiceOption[];
  onChoiceSelect: (choice: string) => void;
  isCorrect: boolean | null;
  correctAnswer: string;
}

export default function MultipleChoiceInput({ 
  options, 
  onChoiceSelect, 
  isCorrect, 
  correctAnswer 
}: MultipleChoiceInputProps) {
  console.log('MultipleChoiceInput rendered with options:', options);
  console.log('isCorrect:', isCorrect, 'correctAnswer:', correctAnswer);
  
  // Safety check
  if (!options || !Array.isArray(options) || options.length === 0) {
    console.error('Invalid options passed to MultipleChoiceInput:', options);
    return (
      <div className="text-red-600">
        Error: No multiple choice options available
      </div>
    );
  }

  // Determine if a choice has been made (game is in "result" state)
  const hasChoiceBeenMade = isCorrect !== null;

  return (
    <div className="grid grid-cols-2 gap-3">
      {options.map((option, index) => {
        // Safety check for each option
        if (!option || typeof option.text !== 'string') {
          console.error('Invalid option at index', index, ':', option);
          return (
            <button
              key={index}
              className="p-4 border border-gray-300 rounded-lg bg-gray-100"
              disabled
            >
              Invalid Option
            </button>
          );
        }

        const isThisTheCorrectAnswer = option.text === correctAnswer;
        
        let buttonClass = "p-4 border-2 rounded-lg font-medium transition-all text-left ";
        
        if (hasChoiceBeenMade) {
          // A choice has been made - show results
          if (isThisTheCorrectAnswer) {
            // This is the correct answer - always show green when revealed
            buttonClass += "border-green-500 bg-green-100 text-green-800";
          } else {
            // This is a wrong answer - show gray when revealed
            buttonClass += "border-gray-300 bg-gray-100 text-gray-600";
          }
        } else {
          // No choice made yet - show interactive button (all options look the same)
          buttonClass += "border-gray-300 bg-white hover:border-blue-500 hover:bg-blue-50 cursor-pointer";
        }

        return (
          <button
            key={index}
            onClick={() => !hasChoiceBeenMade && onChoiceSelect(option.text)}
            className={buttonClass}
            disabled={hasChoiceBeenMade}
          >
            {option.text}
            {hasChoiceBeenMade && isThisTheCorrectAnswer && (
              <span className="ml-2 text-green-600">✓</span>
            )}
          </button>
        );
      })}
    </div>
  );
}
