/**
 * Message list with auto-scroll
 */
import { useEffect, useRef } from 'react';
import type { SSEEventData } from '../../types/events';
import { Message } from './Message';

interface MessageListProps {
  events: SSEEventData[];
}

export const MessageList = ({ events }: MessageListProps) => {
  const bottomRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new events arrive
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [events]);

  if (events.length === 0) {
    return (
      <div className="flex items-center justify-center h-full text-gray-500">
        Enter a coding task to get started
      </div>
    );
  }

  return (
    <div className="space-y-4 pb-4">
      {events.map((event, idx) => (
        <Message key={idx} event={event} />
      ))}
      <div ref={bottomRef} />
    </div>
  );
};
