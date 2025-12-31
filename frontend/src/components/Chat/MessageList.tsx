/**
 * Message list with auto-scroll
 */
import { useEffect, useRef } from 'react';
import type { SSEEventData } from '../../types/events';
import { Message } from './Message';
import { ThinkingIndicator } from '../Common/ThinkingIndicator';

interface MessageListProps {
  events: SSEEventData[];
  isConnected?: boolean;
}

export const MessageList = ({ events, isConnected }: MessageListProps) => {
  const bottomRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new events arrive
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [events]);

  if (events.length === 0) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="w-16 h-16 rounded-full bg-gradient-to-br from-purple-500 to-blue-500
                          flex items-center justify-center mx-auto mb-4 shadow-lg">
            <span className="text-3xl">🤖</span>
          </div>
          <h2 className="text-xl font-semibold text-gray-700 dark:text-gray-300 mb-2">
            AI Code Generator
          </h2>
          <p className="text-gray-500 dark:text-gray-500">
            Enter a coding task to get started
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto w-full">
      <div className="space-y-0">
        {events.map((event, idx) => (
          <Message key={idx} event={event} />
        ))}
        {isConnected && <ThinkingIndicator />}
        <div ref={bottomRef} />
      </div>
    </div>
  );
};
