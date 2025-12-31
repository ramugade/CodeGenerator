import { create } from 'zustand';
import type { SSEEventData } from '../types/events';

interface MessageDTO {
  type: string;
  content: any;
  timestamp: string;
  order: number;
}

interface Session {
  id: string;
  title: string;
  created_at: string;
  total_tokens: number;
  total_cost_usd: number;
}

interface ChatState {
  currentSessionId: string | null;
  sessions: Session[];
  currentEvents: SSEEventData[];
  currentSessionCost: number;
  currentSessionTokens: number;

  setCurrentSession: (id: string | null) => void;
  setSessions: (sessions: Session[]) => void;
  addSession: (session: Session) => void;
  loadSessionHistory: (messages: MessageDTO[]) => void;
  addLiveEvent: (event: SSEEventData) => void;
  clearEvents: () => void;
  updateCurrentCost: (tokens: number, cost: number) => void;
  deleteSession: (sessionId: string) => void;
}

export const useChatStore = create<ChatState>((set) => ({
  currentSessionId: null,
  sessions: [],
  currentEvents: [],
  currentSessionCost: 0,
  currentSessionTokens: 0,

  setCurrentSession: (id) => set({ currentSessionId: id }),
  setSessions: (sessions) => set({ sessions }),
  addSession: (session) => set((state) => ({ sessions: [session, ...state.sessions] })),

  loadSessionHistory: (messages) => set({
    currentEvents: messages.map(msg => ({
      type: msg.type as any,
      data: msg.content
    }))
  }),

  addLiveEvent: (event) => set((state) => ({
    currentEvents: [...state.currentEvents, event]
  })),

  clearEvents: () => set({ currentEvents: [], currentSessionCost: 0, currentSessionTokens: 0 }),

  updateCurrentCost: (tokens, cost) => set({
    currentSessionTokens: tokens,
    currentSessionCost: cost
  }),

  deleteSession: (sessionId) => set((state) => ({
    sessions: state.sessions.filter(s => s.id !== sessionId),
    currentSessionId: state.currentSessionId === sessionId ? null : state.currentSessionId,
    currentEvents: state.currentSessionId === sessionId ? [] : state.currentEvents
  }))
}));
