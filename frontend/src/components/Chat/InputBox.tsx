/**
 * Chat input box
 */
import { useState } from 'react';

interface InputBoxProps {
  onSubmit: (query: string) => void;
  disabled: boolean;
}

export const InputBox = ({ onSubmit, disabled }: InputBoxProps) => {
  const [query, setQuery] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim() && !disabled) {
      onSubmit(query.trim());
      setQuery('');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="p-6">
      <div className="max-w-4xl mx-auto">
        <div className="flex gap-3">
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Describe what you want to build... (e.g., 'Write a function that calculates factorial')"
            disabled={disabled}
            rows={3}
            className="flex-1 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100
                       border border-gray-300 dark:border-gray-700 rounded-xl px-4 py-3
                       focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
                       disabled:opacity-50 disabled:cursor-not-allowed resize-none
                       placeholder:text-gray-400 dark:placeholder:text-gray-500"
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSubmit(e);
              }
            }}
          />
          <button
            type="submit"
            disabled={disabled || !query.trim()}
            className="px-8 py-3 bg-gradient-to-r from-blue-600 to-purple-600
                       hover:from-blue-700 hover:to-purple-700
                       disabled:from-gray-400 disabled:to-gray-500
                       disabled:cursor-not-allowed text-white rounded-xl
                       font-semibold transition-all duration-200 shadow-sm
                       hover:shadow-md disabled:shadow-none"
          >
            {disabled ? 'Generating...' : 'Generate'}
          </button>
        </div>
        <div className="text-xs text-gray-500 dark:text-gray-500 mt-2.5 ml-1">
          Press Enter to send, Shift+Enter for new line
        </div>
      </div>
    </form>
  );
};
