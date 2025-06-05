import React from 'react';

interface InputModeSelectorProps {
  inputMode: 'autocomplete' | 'plaintext' | 'multiplechoice';
  onInputModeChange: (mode: 'autocomplete' | 'plaintext' | 'multiplechoice') => void;
}

export default function InputModeSelector({ inputMode, onInputModeChange }: InputModeSelectorProps) {
  const isMultipleChoice = inputMode === 'multiplechoice';

  const handleToggle = () => {
    // Toggle between autocomplete and multiple choice
    onInputModeChange(isMultipleChoice ? 'autocomplete' : 'multiplechoice');
  };

  return (
    <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
        <div className="font-medium text-gray-800">Multiple Choice</div>
        
        <label className="relative inline-flex items-center cursor-pointer">
          <input
            type="checkbox"
            checked={isMultipleChoice}
            onChange={handleToggle}
            className="sr-only peer"
          />
          <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
        </label>
    </div>
  );
}
