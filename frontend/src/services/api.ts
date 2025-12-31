/**
 * API client for backend communication
 */
import axios from 'axios';
import type { GenerateRequest } from '../types/events';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const healthCheck = async () => {
  const response = await api.get('/api/health');
  return response.data;
};

export const generateCodeSSE = (_request: GenerateRequest) => {
  return `${API_BASE_URL}/api/generate`;
};

export const sessionAPI = {
  listSessions: async () => {
    const response = await api.get('/api/sessions');
    return response.data;
  },

  getSession: async (sessionId: string) => {
    const response = await api.get(`/api/sessions/${sessionId}`);
    return response.data;
  },

  deleteSession: async (sessionId: string) => {
    await api.delete(`/api/sessions/${sessionId}`);
  }
};
