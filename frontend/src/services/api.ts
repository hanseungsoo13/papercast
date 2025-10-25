/**
 * API service for Daily Paper Cast frontend.
 */

import axios, { AxiosResponse } from 'axios';
import {
  Episode,
  EpisodeWithPapers,
  Paper,
  PaperWithEpisode,
  EpisodesResponse,
  PapersResponse,
  HealthStatus,
  ApiError
} from './types';

// API configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: false,
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  (error) => {
    console.error('API Response Error:', error);
    
    if (error.response) {
      // Server responded with error status
      const apiError: ApiError = {
        error: error.response.data?.error || 'UnknownError',
        message: error.response.data?.message || 'An error occurred',
        details: error.response.data?.details,
      };
      return Promise.reject(apiError);
    } else if (error.request) {
      // Request was made but no response received
      const apiError: ApiError = {
        error: 'NetworkError',
        message: 'Network error - please check your connection',
        details: null,
      };
      return Promise.reject(apiError);
    } else {
      // Something else happened
      const apiError: ApiError = {
        error: 'RequestError',
        message: 'Request failed to be sent',
        details: error.message,
      };
      return Promise.reject(apiError);
    }
  }
);

// API service functions
export const apiService = {
  // Health check
  async getHealth(): Promise<HealthStatus> {
    const response = await api.get<HealthStatus>('/health');
    return response.data;
  },

  // Episodes
  async getEpisodes(
    limit: number = 20,
    offset: number = 0
  ): Promise<Episode[]> {
    const response = await api.get<{episodes: Episode[]}>('/episodes', {
      params: { limit, offset },
    });
    return response.data.episodes;
  },

  async getLatestEpisode(): Promise<EpisodeWithPapers> {
    const response = await api.get<EpisodeWithPapers>('/episodes/latest');
    return response.data;
  },

  async getEpisode(id: string): Promise<EpisodeWithPapers> {
    const response = await api.get<EpisodeWithPapers>(`/episodes/${id}`);
    return response.data;
  },

  // Papers
  async getPapers(
    page: number = 1,
    limit: number = 20,
    episodeId?: number,
    search?: string
  ): Promise<PapersResponse> {
    const params: any = { page, limit };
    if (episodeId) params.episode_id = episodeId;
    if (search) params.search = search;

    const response = await api.get<PapersResponse>('/papers', { params });
    return response.data;
  },

  async getPaper(id: number): Promise<PaperWithEpisode> {
    const response = await api.get<PaperWithEpisode>(`/papers/${id}`);
    return response.data;
  },
};

// Utility functions
export const formatDuration = (seconds: number): string => {
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
};

export const formatFileSize = (bytes: number): string => {
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  if (bytes === 0) return '0 Bytes';
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
};

export const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
};

export const getArxivUrl = (arxivId: string): string => {
  return `https://arxiv.org/pdf/${arxivId}`;
};

export const getHuggingFaceUrl = (url: string): string => {
  return url;
};

export default apiService;
