/**
 * Custom hook for Server-Sent Events (SSE) streaming
 */
import { useState, useCallback, useRef } from 'react';
import type { SSEEventData, GenerateRequest } from '../types/events';
import { generateCodeSSE } from '../services/api';

export interface UseSSEResult {
  events: SSEEventData[];
  isConnected: boolean;
  isComplete: boolean;
  error: string | null;
  startStream: (request: GenerateRequest) => void;
  stopStream: () => void;
}

export const useSSE = (): UseSSEResult => {
  const [events, setEvents] = useState<SSEEventData[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [isComplete, setIsComplete] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const eventSourceRef = useRef<EventSource | null>(null);

  const stopStream = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
      setIsConnected(false);
    }
  }, []);

  const startStream = useCallback((request: GenerateRequest) => {
    // Reset state
    setEvents([]);
    setIsComplete(false);
    setError(null);

    // Stop any existing stream
    stopStream();

    try {
      // Create POST request to get SSE stream
      const url = generateCodeSSE(request);

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

                  setEvents((prev) => [...prev, event]);

                  // Check for completion
                  if (currentEventType === 'complete') {
                    setIsComplete(true);
                    setIsConnected(false);
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
  }, [stopStream]);

  return {
    events,
    isConnected,
    isComplete,
    error,
    startStream,
    stopStream,
  };
};
