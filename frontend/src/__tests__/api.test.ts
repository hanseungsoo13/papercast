/**
 * API service tests for frontend
 */

import { apiService } from '../services/api';
import { EpisodeWithPapers, EpisodesResponse } from '../services/types';

// Mock axios
jest.mock('axios');
const axios = require('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('API Service', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('getHealth', () => {
    it('should return health status', async () => {
      const mockHealth = {
        status: 'healthy',
        timestamp: '2025-01-27T12:00:00Z',
        version: '1.0.0'
      };

      mockedAxios.create.mockReturnValue({
        get: jest.fn().mockResolvedValue({ data: mockHealth }),
        interceptors: {
          request: { use: jest.fn() },
          response: { use: jest.fn() }
        }
      } as any);

      const result = await apiService.getHealth();
      expect(result).toEqual(mockHealth);
    });
  });

  describe('getEpisodes', () => {
    it('should return episodes with pagination', async () => {
      const mockEpisodes: EpisodesResponse = {
        episodes: [
          {
            id: '2025-01-27',
            title: 'Daily Papers - 2025-01-27',
            publication_date: '2025-01-27',
            audio_url: 'https://example.com/audio.mp3',
            papers_count: 3,
            created_at: '2025-01-27T06:00:00Z'
          }
        ],
        total: 1,
        limit: 20,
        offset: 0
      };

      mockedAxios.create.mockReturnValue({
        get: jest.fn().mockResolvedValue({ data: mockEpisodes }),
        interceptors: {
          request: { use: jest.fn() },
          response: { use: jest.fn() }
        }
      } as any);

      const result = await apiService.getEpisodes(20, 0);
      expect(result).toEqual(mockEpisodes);
    });
  });

  describe('getLatestEpisode', () => {
    it('should return latest episode with papers', async () => {
      const mockEpisode: EpisodeWithPapers = {
        id: '2025-01-27',
        title: 'Daily Papers - 2025-01-27',
        publication_date: '2025-01-27',
        audio_url: 'https://example.com/audio.mp3',
        papers_count: 3,
        created_at: '2025-01-27T06:00:00Z',
        papers: [
          {
            id: '2510.19338',
            title: 'Every Attention Matters',
            authors: ['John Doe', 'Jane Smith'],
            url: 'https://huggingface.co/papers/2510.19338',
            upvotes: 142,
            collected_at: '2025-01-27T05:00:00Z'
          }
        ]
      };

      mockedAxios.create.mockReturnValue({
        get: jest.fn().mockResolvedValue({ data: mockEpisode }),
        interceptors: {
          request: { use: jest.fn() },
          response: { use: jest.fn() }
        }
      } as any);

      const result = await apiService.getLatestEpisode();
      expect(result).toEqual(mockEpisode);
    });
  });

  describe('getEpisode', () => {
    it('should return specific episode by ID', async () => {
      const mockEpisode: EpisodeWithPapers = {
        id: '2025-01-27',
        title: 'Daily Papers - 2025-01-27',
        publication_date: '2025-01-27',
        audio_url: 'https://example.com/audio.mp3',
        papers_count: 3,
        created_at: '2025-01-27T06:00:00Z',
        papers: []
      };

      mockedAxios.create.mockReturnValue({
        get: jest.fn().mockResolvedValue({ data: mockEpisode }),
        interceptors: {
          request: { use: jest.fn() },
          response: { use: jest.fn() }
        }
      } as any);

      const result = await apiService.getEpisode('2025-01-27');
      expect(result).toEqual(mockEpisode);
    });
  });
});
