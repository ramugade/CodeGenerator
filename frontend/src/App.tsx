/**
 * AI-Powered Python Code Generator - Main App
 */
import { useState } from 'react';
import { useSSE } from './hooks/useSSE';
import { MessageList } from './components/Chat/MessageList';
import { InputBox } from './components/Chat/InputBox';
import type { GenerateRequest } from './types/events';

function App() {
  const { events, isConnected, isComplete, error, startStream } = useSSE();
  const [llmProvider, setLlmProvider] = useState<'openai' | 'anthropic'>('openai');

  const handleGenerate = (query: string) => {
    const request: GenerateRequest = {
      query,
      llm_provider: llmProvider,
      max_iterations: 5,
    };

    startStream(request);
  };

  return (
    <div className="flex flex-col h-screen bg-gray-950 text-gray-100">
      {/* Header */}
      <header className="border-b border-gray-800 bg-gray-900 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-blue-400">AI Code Generator</h1>
            <p className="text-sm text-gray-400">Natural language → Working Python code</p>
          </div>

          <div className="flex items-center gap-4">
            {/* Connection Status */}
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${
                isConnected ? 'bg-green-500 animate-pulse' :
                error ? 'bg-red-500' :
                isComplete ? 'bg-blue-500' : 'bg-gray-500'
              }`} />
              <span className="text-sm text-gray-400">
                {isConnected ? 'Generating...' :
                 error ? 'Error' :
                 isComplete ? 'Complete' : 'Ready'}
              </span>
            </div>

            {/* LLM Provider Selector */}
            <div className="flex items-center gap-2">
              <label className="text-sm text-gray-400">Provider:</label>
              <select
                value={llmProvider}
                onChange={(e) => setLlmProvider(e.target.value as 'openai' | 'anthropic')}
                disabled={isConnected}
                className="bg-gray-800 text-gray-100 rounded px-3 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <option value="openai">OpenAI GPT-4</option>
                <option value="anthropic">Anthropic Claude</option>
              </select>
            </div>
          </div>
        </div>
      </header>

      {/* Error Display */}
      {error && !isConnected && (
        <div className="bg-red-900/20 border-b border-red-500/30 px-6 py-3">
          <div className="text-red-400 text-sm">❌ Error: {error}</div>
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-4">
        <MessageList events={events} />
      </div>

      {/* Input */}
      <InputBox onSubmit={handleGenerate} disabled={isConnected} />
    </div>
  );
}

export default App;
