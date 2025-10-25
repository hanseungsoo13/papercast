/**
 * TypeScript type definitions for Daily Paper Cast API.
 */

export interface Episode {
  id: string;
  title: string;
  publication_date: string;
  audio_url: string;
  script?: string;
  duration_seconds?: number;
  file_size_bytes?: number;
  papers_count: number;
  created_at: string;
}

export interface Paper {
  id: string;
  title: string;
  authors: string[];
  summary?: string;
  url: string;
  arxiv_id?: string;
  abstract?: string;
  categories?: string[];
  upvotes: number;
  thumbnail_url?: string;
  published_date?: string;
  collected_at: string;
}

export interface EpisodeWithPapers extends Episode {
  papers: Paper[];
}

export interface PaperWithEpisode extends Paper {
  episode: Episode;
}

export interface Pagination {
  page: number;
  limit: number;
  total: number;
  pages: number;
  has_next: boolean;
  has_prev: boolean;
}

export interface EpisodesResponse {
  episodes: Episode[];
  total: number;
  limit: number;
  offset: number;
}

export interface PapersResponse {
  papers: Paper[];
  pagination: Pagination;
}

export interface ApiError {
  error: string;
  message: string;
  details?: any;
}

export interface HealthStatus {
  status: 'healthy' | 'degraded' | 'unhealthy';
  timestamp: string;
  version: string;
}
