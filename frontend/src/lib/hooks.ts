import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiService, MemoryCreate } from './api';

export const queryKeys = {
  memories: ['memories'] as const,
  memory: (id: number) => ['memory', id] as const,
  search: (q: string, limit: number) => ['search', q, limit] as const,
  insights: ['insights'] as const,
};

export function useMemories() {
  return useQuery({
    queryKey: queryKeys.memories,
    queryFn: apiService.getMemories,
  });
}

export function useMemory(id: number) {
  return useQuery({
    queryKey: queryKeys.memory(id),
    queryFn: () => apiService.getMemory(id),
    enabled: !!id && !isNaN(id),
  });
}

export function useCreateMemory() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: MemoryCreate) => apiService.createMemory(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.memories });
      queryClient.invalidateQueries({ queryKey: queryKeys.insights });
    },
  });
}

export function useDeleteMemory() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => apiService.deleteMemory(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.memories });
      queryClient.removeQueries({ queryKey: queryKeys.memory(id) });
      queryClient.invalidateQueries({ queryKey: queryKeys.insights });
    },
  });
}

export function useDeleteAllMemories() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: apiService.deleteAllMemories,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.memories });
      queryClient.invalidateQueries({ queryKey: queryKeys.insights });
    },
  });
}

export function useSearch(q: string, limit = 15) {
  return useQuery({
    queryKey: queryKeys.search(q, limit),
    queryFn: () => apiService.searchMemories(q, limit),
    enabled: q.trim().length > 0,
  });
}

export function useInsights() {
  return useQuery({
    queryKey: queryKeys.insights,
    queryFn: apiService.getInsights,
  });
}

export function useChat() {
  return useMutation({
    mutationFn: (query: string) => apiService.chatWithMemories(query),
  });
}
