import axios from 'axios';

// Ensure the API points to our running FastAPI backend
const API_BASE_URL = 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface Memory {
  id: number;
  title: string | null;
  url: string;
  content: string | null;
  summary: string | null;
  tags: string[] | null;
  importance_score: number | null;
  created_at: string;
}

export interface MemoryCreate {
  title?: string;
  url: string;
  content?: string;
}

export interface MemorySearchResponse {
  id: number;
  title: string | null;
  url: string;
  snippet: string | null;
  similarity_score: number;
  summary: string | null;
  tags: string[] | null;
  importance_score: number | null;
  created_at: string;
}

export interface ChatRequest {
  query: string;
}

export interface ChatResponse {
  answer: string;
  sources: MemorySearchResponse[];
}

export interface InsightsResponse {
  summary: string;
  created_at: string | null;
}

export const apiService = {
  getMemories: async (): Promise<Memory[]> => {
    const response = await apiClient.get<Memory[]>('/memory');
    return response.data;
  },

  getMemory: async (id: number): Promise<Memory> => {
    const response = await apiClient.get<Memory>(`/memory/${id}`);
    return response.data;
  },

  createMemory: async (data: MemoryCreate): Promise<Memory> => {
    const response = await apiClient.post<Memory>('/memory', data);
    return response.data;
  },

  deleteMemory: async (id: number): Promise<{ message: string }> => {
    const response = await apiClient.delete<{ message: string }>(`/memory/${id}`);
    return response.data;
  },

  deleteAllMemories: async (): Promise<{ message: string }> => {
    const response = await apiClient.delete<{ message: string }>('/memory');
    return response.data;
  },

  searchMemories: async (q: string, limit = 10): Promise<MemorySearchResponse[]> => {
    if (!q.trim()) return [];
    const response = await apiClient.get<MemorySearchResponse[]>('/search', {
      params: { q, limit },
    });
    return response.data;
  },

  chatWithMemories: async (query: string): Promise<ChatResponse> => {
    const response = await apiClient.post<ChatResponse>('/chat', { query });
    return response.data;
  },

  getInsights: async (): Promise<InsightsResponse> => {
    const response = await apiClient.get<InsightsResponse>('/insights');
    return response.data;
  },
};
