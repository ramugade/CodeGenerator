/**
 * Custom hook for Server-Sent Events (SSE) streaming
 * Integrated with Zustand store for centralized state management
 */
import { useCallback, useRef } from 'react';
import type { SSEEventData, GenerateRequest } from '../types/events';
import { useChatStore } from '../store/chatStore';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface UseSSEResult {
  startStream: (request: GenerateRequest) => void;
  stopStream: () => void;
}

export const useSSE = (): UseSSEResult => {
  const eventSourceRef = useRef<EventSource | null>(null);

  // Get store actions
  const {
    setEvents,
    addEvent,
    setIsConnected,
    setIsComplete,
    setError,
    setCurrentSessionId,
    addSession,
    touchSession,
    updateCurrentCost,
  } = useChatStore();

  const stopStream = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
      setIsConnected(false);
    }
  }, [setIsConnected]);

  const startStream = useCallback((request: GenerateRequest) => {
    // Stop any existing stream
    stopStream();

    // Reset state and add user query event immediately to UI
    setIsComplete(false);
    setError(null);

    const userQueryEvent: SSEEventData = {
      type: 'user_query',
      data: {
        query: request.query,
        timestamp: new Date().toISOString()
      }
    };
    if (request.session_id) {
      addEvent(userQueryEvent);
    } else {
      setEvents([userQueryEvent]);
    }
    if (request.session_id) {
      touchSession(request.session_id);
    }

    try {
      const url = `${API_BASE_URL}/api/generate`;

      // Use fetch for POST with SSE
      fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      })
        .then(async (response) => {
          if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
          }

          setIsConnected(true);

          const reader = response.body?.getReader();
          const decoder = new TextDecoder();

          if (!reader) {
            throw new Error('No response body');
          }

          let buffer = '';
          let currentEventType: string | null = null;

          while (true) {
            const { done, value } = await reader.read();

            if (done) {
              setIsConnected(false);
              break;
            }

            // Decode chunk and add to buffer
            buffer += decoder.decode(value, { stream: true });

            // Process complete lines
            const lines = buffer.split('\n');
            buffer = lines.pop() || ''; // Keep incomplete line in buffer

            for (const line of lines) {
              const trimmedLine = line.trim();

              if (trimmedLine.startsWith('event:')) {
                currentEventType = trimmedLine.substring(6).trim();
              } else if (trimmedLine.startsWith('data:') && currentEventType) {
                const dataStr = trimmedLine.substring(5).trim();

                try {
                  const data = JSON.parse(dataStr);

                  // Add event to state
                  const event: SSEEventData = {
                    type: currentEventType as any,
                    data,
                  };

                  addEvent(event);

                  // Handle session_created event
                  if (currentEventType === 'session_created') {
                    const { session_id, title, created_at } = data;
                    setCurrentSessionId(session_id);
                    addSession({
                      id: session_id,
                      title,
                      created_at,
                      updated_at: created_at,
                      total_tokens: 0,
                      total_cost_usd: 0
                    });
                  }

                  // Handle cost_update event
                  if (currentEventType === 'cost_update') {
                    const { total_tokens, estimated_cost_usd } = data;
                    updateCurrentCost(total_tokens, estimated_cost_usd);
                  }

                  // Check for completion
                  if (currentEventType === 'complete') {
                    setIsComplete(true);
                    setIsConnected(false);
                    updateCurrentCost(
                      data.token_usage.total_tokens,
                      data.token_usage.estimated_cost_usd
                    );
                    reader.cancel();
                    break;
                  } else if (currentEventType === 'error') {
                    setError(data.error);
                    setIsConnected(false);
                    reader.cancel();
                    break;
                  }

                  currentEventType = null;
                } catch (e) {
                  console.error('Failed to parse SSE data:', dataStr, e);
                }
              }
            }
          }
        })
        .catch((err) => {
          console.error('SSE stream error:', err);
          setError(err.message);
          setIsConnected(false);
        });
    } catch (err: any) {
      console.error('Failed to start SSE stream:', err);
      setError(err.message);
      setIsConnected(false);
    }
  }, [stopStream, setEvents, setIsConnected, setIsComplete, setError, setCurrentSessionId, addSession, addEvent, touchSession, updateCurrentCost]);

  return {
    startStream,
    stopStream,
  };
};
