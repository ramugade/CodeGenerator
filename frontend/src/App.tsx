/**
 * AI-Powered Python Code Generator - Main App
 */
import { useState, useEffect } from 'react';
import { useSSE } from './hooks/useSSE';
import { MessageList } from './components/Chat/MessageList';
import { InputBox } from './components/Chat/InputBox';
import { Sidebar } from './components/Common/Sidebar';
import { CostCounter } from './components/Common/CostCounter';
import { ModelSelector } from './components/Common/ModelSelector';
import { ThemeToggle } from './components/Common/ThemeToggle';
import { useChatStore } from './store/chatStore';
import { sessionAPI } from './services/api';
import { DEFAULT_MODELS } from './config/models';
import type { GenerateRequest } from './types/events';

function App() {
  console.log('🎨 NEW UI LOADED - Theme system active!');
  const { events, isConnected, isComplete, error, startStream } = useSSE();
  const [llmProvider, setLlmProvider] = useState<'openai' | 'anthropic'>('anthropic');
  const [selectedModel, setSelectedModel] = useState<string>(DEFAULT_MODELS.anthropic);

  const {
    currentSessionId,
    currentEvents,
    loadSessionHistory,
    addLiveEvent,
    clearEvents,
    updateCurrentCost
  } = useChatStore();

  // Load history when session changes
  useEffect(() => {
    if (currentSessionId) {
      sessionAPI.getSession(currentSessionId).then(session => {
        loadSessionHistory(session.messages || []);
        updateCurrentCost(session.total_tokens, session.total_cost_usd);
      });
    } else {
      clearEvents();
    }
  }, [currentSessionId, loadSessionHistory, clearEvents, updateCurrentCost]);

  // Append live SSE events to history
  useEffect(() => {
    events.forEach(event => {
      if (!currentEvents.find(e => e === event)) {
        addLiveEvent(event);
      }
    });
  }, [events, currentEvents, addLiveEvent]);

  const handleGenerate = (query: string) => {
    // Add user query to events
    const userQueryEvent = {
      type: 'user_query' as const,
      data: {
        query,
        timestamp: new Date().toISOString()
      }
    };
    addLiveEvent(userQueryEvent);

    const request: GenerateRequest = {
      query,
      llm_provider: llmProvider,
      session_id: currentSessionId || undefined,
      max_iterations: 5,
    };

    startStream(request);
  };

  const handleModelChange = (modelId: string, provider: 'openai' | 'anthropic') => {
    setSelectedModel(modelId);
    setLlmProvider(provider);
  };

  return (
    <div className="flex h-screen bg-white dark:bg-gray-950 text-gray-900 dark:text-gray-100 transition-colors">
      <Sidebar />

      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="border-b border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-900 px-8 py-5 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-500 to-purple-600 bg-clip-text text-transparent">
                AI Code Generator
              </h1>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-0.5">
                Natural language → Working Python code
              </p>
            </div>

            <div className="flex items-center gap-6">
              {/* Cost Counter */}
              <CostCounter />

              {/* Connection Status */}
              <div className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${
                  isConnected ? 'bg-green-500 animate-pulse' :
                  error ? 'bg-red-500' :
                  isComplete ? 'bg-blue-500' : 'bg-gray-400'
                }`} />
                <span className="text-sm text-gray-500 dark:text-gray-400">
                  {isConnected ? 'Generating...' :
                   error ? 'Error' :
                   isComplete ? 'Complete' : 'Ready'}
                </span>
              </div>

              {/* Model Selector */}
              <ModelSelector
                selectedModel={selectedModel}
                onChange={handleModelChange}
                disabled={isConnected}
              />

              {/* Theme Toggle */}
              <ThemeToggle />
            </div>
          </div>
        </header>

        {/* Error Display */}
        {error && !isConnected && (
          <div className="bg-red-50 dark:bg-red-900/20 border-b border-red-200 dark:border-red-500/30 px-8 py-4">
            <div className="text-red-600 dark:text-red-400 text-sm font-medium">
              ❌ Error: {error}
            </div>
          </div>
        )}

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-8 py-6 bg-gray-50 dark:bg-gray-950">
          <MessageList events={currentEvents} isConnected={isConnected} />
        </div>

        {/* Input */}
        <div className="border-t border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900">
          <InputBox onSubmit={handleGenerate} disabled={isConnected} />
        </div>
      </div>
    </div>
  );
}

export default App;
