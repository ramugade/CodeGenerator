import { useState, useEffect, useRef } from "react";
import { Sidebar } from "@/components/sidebar/Sidebar";
import { ChatHeader } from "@/components/header/ChatHeader";
import { Message } from "@/components/chat/Message";
import { FeedbackBanner } from "@/components/chat/FeedbackBanner";
import { ChatInput } from "@/components/chat/ChatInput";
import { useSSE } from "@/hooks/useSSE";
import { useChatStore } from "@/store/chatStore";
import type { GenerateRequest } from "@/types/events";

const Index = () => {
  const [mounted, setMounted] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  const { startStream } = useSSE();

  // Get state from store
  const {
    events,
    isConnected,
    isComplete,
    error,
    currentSessionId,
    currentSessionTokens,
    currentSessionCost,
    selectedModel,
    setSelectedModel,
    lastUserQuery,
    setLastUserQuery,
  } = useChatStore();

  useEffect(() => {
    // Enable dark mode
    document.documentElement.classList.add("dark");
    setMounted(true);
  }, []);

  // Auto-scroll to bottom when events change
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [events]);

  const handleSend = (message: string) => {
    // Save the last user query for regeneration
    setLastUserQuery(message);

    // Determine provider from model ID
    const provider = selectedModel.startsWith('gpt') ? 'openai' : 'anthropic';

    const request: GenerateRequest = {
      query: message,
      llm_provider: provider,
      session_id: currentSessionId || undefined,
      max_iterations: 5,
    };

    startStream(request);
  };

  const handleRegenerate = () => {
    if (lastUserQuery) {
      handleSend(lastUserQuery);
    }
  };

  // Filter out session_created and cost_update events
  const visibleEvents = events.filter(
    (event) => event.type !== "session_created" && event.type !== "cost_update"
  );

  if (!mounted) return null;

  return (
    <div className="flex h-screen bg-background">
      {/* Sidebar */}
      <Sidebar />

      {/* Main content */}
      <main className="flex-1 flex flex-col overflow-hidden">
        <ChatHeader
          cost={currentSessionCost}
          tokens={currentSessionTokens}
          selectedModel={selectedModel}
          onModelChange={setSelectedModel}
        />

        {/* Chat area */}
        <div className="flex-1 overflow-y-auto px-4 py-6 scrollbar-thin">
          <div className="max-w-3xl mx-auto">
            {visibleEvents.length === 0 && (
              <div className="flex items-center justify-center h-full text-muted-foreground">
                <div className="text-center">
                  <p className="text-lg font-medium mb-2">How can I help you today?</p>
                  <p className="text-sm text-muted-foreground/70">
                    Describe what you want to build and I'll generate the code for you
                  </p>
                </div>
              </div>
            )}

            {/* Render all events with appropriate components */}
            <div className="space-y-1">
              {visibleEvents.map((event, idx) => (
                <Message key={idx} event={event} onRegenerate={handleRegenerate} />
              ))}
            </div>

            {/* Show loading state */}
            {isConnected && !isComplete && (
              <div className="flex items-center gap-2 text-sm text-muted-foreground/70 py-4">
                <span className="flex gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-muted-foreground/50 animate-pulse" />
                  <span className="w-1.5 h-1.5 rounded-full bg-muted-foreground/40 animate-pulse delay-150" />
                  <span className="w-1.5 h-1.5 rounded-full bg-muted-foreground/30 animate-pulse delay-300" />
                </span>
              </div>
            )}

            {/* Show error */}
            {error && (
              <div className="text-destructive text-sm p-4 bg-destructive/10 rounded-lg">
                Error: {error}
              </div>
            )}

            {/* Feedback banner - only show when complete */}
            {isComplete && visibleEvents.length > 0 && <FeedbackBanner />}

            <div ref={bottomRef} />
          </div>
        </div>

        {/* Input area */}
        <ChatInput onSend={handleSend} />
      </main>
    </div>
  );
};

export default Index;
