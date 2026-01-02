/**
 * Centralized chat state management using Zustand
 */
import { create } from 'zustand';
import type { SSEEventData } from '../types/events';

interface Session {
  id: string;
  title: string;
  created_at: string;
  updated_at?: string;
  total_tokens: number;
  total_cost_usd: number;
}

interface ChatStore {
  // Sessions
  sessions: Session[];
  currentSessionId: string | null;

  // Events (messages)
  events: SSEEventData[];

  // Cost tracking
  currentSessionTokens: number;
  currentSessionCost: number;

  // Connection state
  isConnected: boolean;
  isComplete: boolean;
  error: string | null;

  // Selected model
  selectedModel: string;

  // Last user query for regeneration
  lastUserQuery: string | null;

  // Actions
  setSessions: (sessions: Session[]) => void;
  addSession: (session: Session) => void;
  deleteSession: (sessionId: string) => void;
  setCurrentSession: (sessionId: string | null) => void;

  setEvents: (events: SSEEventData[]) => void;
  addEvent: (event: SSEEventData) => void;
  clearEvents: () => void;

  updateCurrentCost: (tokens: number, cost: number) => void;

  setIsConnected: (isConnected: boolean) => void;
  setIsComplete: (isComplete: boolean) => void;
  setError: (error: string | null) => void;

  setSelectedModel: (model: string) => void;
  setLastUserQuery: (query: string | null) => void;
}

export const useChatStore = create<ChatStore>((set) => ({
  // Initial state
  sessions: [],
  currentSessionId: null,
  events: [],
  currentSessionTokens: 0,
  currentSessionCost: 0,
  isConnected: false,
  isComplete: false,
  error: null,
  selectedModel: 'gpt-3.5-turbo',
  lastUserQuery: null,

  // Session actions
  setSessions: (sessions) => set({ sessions }),

  addSession: (session) => set((state) => ({
    sessions: [session, ...state.sessions]
  })),

  deleteSession: (sessionId) => set((state) => ({
    sessions: state.sessions.filter(s => s.id !== sessionId),
    currentSessionId: state.currentSessionId === sessionId ? null : state.currentSessionId,
    events: state.currentSessionId === sessionId ? [] : state.events
  })),

  setCurrentSession: (sessionId) => set({
    currentSessionId: sessionId,
    events: [],
    currentSessionTokens: 0,
    currentSessionCost: 0,
    isComplete: false,
    error: null
  }),

  // Event actions
  setEvents: (events) => set({ events }),

  addEvent: (event) => set((state) => ({
    events: [...state.events, event]
  })),

  clearEvents: () => set({
    events: [],
    currentSessionTokens: 0,
    currentSessionCost: 0,
    isComplete: false,
    error: null
  }),

  // Cost tracking
  updateCurrentCost: (tokens, cost) => set({
    currentSessionTokens: tokens,
    currentSessionCost: cost
  }),

  // Connection state
  setIsConnected: (isConnected) => set({ isConnected }),
  setIsComplete: (isComplete) => set({ isComplete }),
  setError: (error) => set({ error }),

  // Model selection
  setSelectedModel: (model) => set({ selectedModel }),

  // Last user query
  setLastUserQuery: (query) => set({ lastUserQuery: query }),
}));
