/**
 * Episode Detail Page
 */

import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Head from 'next/head';
import Link from 'next/link';
import { ArrowLeft, Calendar, Clock, Download, Users, ExternalLink, Star, MessageCircle } from 'lucide-react';
import { apiService, formatDuration, formatFileSize, formatDate } from '../../services/api';
import { EpisodeWithPapers, ApiError } from '../../services/types';
import AudioPlayer from '../../components/AudioPlayer';
import LoadingSpinner from '../../components/LoadingSpinner';
import ErrorMessage from '../../components/ErrorMessage';

export default function EpisodeDetail() {
  const router = useRouter();
  const { id } = router.query;
  
  const [episode, setEpisode] = useState<EpisodeWithPapers | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;

    const fetchEpisode = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // For now, we'll use mock data since we don't have a specific episode endpoint
        // In a real app, you'd call: const episode = await apiService.getEpisode(id as string);
        
        // Mock episode data
        const mockEpisode: EpisodeWithPapers = {
          id: id as string,
          title: `Daily AI Papers - ${id}`,
          publication_date: id as string,
          audio_url: 'https://storage.googleapis.com/papers_ethan/2025-10-21/episode.mp3',
          papers_count: 3,
          created_at: '2025-10-20T16:07:59.488472+00:00',
          duration_seconds: 1800, // 30 minutes
          file_size_bytes: 15728640, // 15MB
          papers: [
            {
              id: '2510.19338',
              title: 'Every Attention Matters: A Novel Attention Mechanism for Deep Learning',
              authors: ['John Doe', 'Jane Smith', 'Bob Johnson'],
              url: 'https://huggingface.co/papers/2510.19338',
              upvotes: 142,
              collected_at: '2025-10-20T16:07:59.488472+00:00',
              summary: 'This paper introduces a novel attention mechanism that improves the performance of transformer models by considering every attention head in the network.'
            },
            {
              id: '2510.19339',
              title: 'Neural Architecture Search for Efficient Models',
              authors: ['Alice Brown', 'Charlie Wilson'],
              url: 'https://huggingface.co/papers/2510.19339',
              upvotes: 89,
              collected_at: '2025-10-20T16:07:59.488472+00:00',
              summary: 'We present a new approach to neural architecture search that finds more efficient models with better performance.'
            },
            {
              id: '2510.19340',
              title: 'Multi-Modal Learning with Vision and Language',
              authors: ['David Lee', 'Emma Davis', 'Frank Miller'],
              url: 'https://huggingface.co/papers/2510.19340',
              upvotes: 156,
              collected_at: '2025-10-20T16:07:59.488472+00:00',
              summary: 'This work explores how to effectively combine vision and language models for better understanding of visual content.'
            }
          ]
        };
        
        setEpisode(mockEpisode);
      } catch (err) {
        console.error('Error fetching episode:', err);
        const apiError = err as ApiError;
        setError(apiError.message || 'Failed to load episode');
      } finally {
        setLoading(false);
      }
    };

    fetchEpisode();
  }, [id]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <ErrorMessage message={error} />
      </div>
    );
  }

  if (!episode) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <ErrorMessage message="Episode not found" />
      </div>
    );
  }

  return (
    <>
      <Head>
        <title>{episode.title} - Daily Paper Cast</title>
        <meta name="description" content={`Listen to ${episode.title} - Latest AI research papers summarized in Korean`} />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
        {/* Header */}
        <header className="bg-white/80 backdrop-blur-sm border-b border-gray-200 sticky top-0 z-50">
          <div className="container-custom">
            <div className="flex items-center justify-between py-4">
              <div className="flex items-center space-x-4">
                <Link 
                  href="/"
                  className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 transition-colors"
                >
                  <ArrowLeft className="w-5 h-5" />
                  <span>뒤로가기</span>
                </Link>
                <div className="h-6 w-px bg-gray-300"></div>
                <h1 className="text-lg font-semibold text-gray-900 truncate">
                  {episode.title}
                </h1>
              </div>
              <div className="flex items-center space-x-4">
                <Link href="/archive" className="btn-ghost">
                  아카이브
                </Link>
                <button className="btn-primary">
                  구독하기
                </button>
              </div>
            </div>
          </div>
        </header>

        <div className="container-custom py-8">
          {/* Episode Header */}
          <div className="card-gradient mb-8">
            <div className="p-8">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center space-x-3">
                  <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                  <h2 className="text-2xl font-bold text-gray-900">
                    에피소드 상세정보
                  </h2>
                </div>
                <span className="text-sm text-gray-500 flex items-center bg-white/80 backdrop-blur-sm px-3 py-1 rounded-full border border-white/20">
                  <Calendar className="w-4 h-4 mr-1" />
                  {formatDate(episode.publication_date)}
                </span>
              </div>

              <h3 className="text-3xl font-bold text-gray-800 mb-6 leading-tight">
                {episode.title}
              </h3>

              {/* Episode Stats */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
                <div className="flex items-center text-sm text-gray-600 bg-white/50 rounded-lg p-3">
                  <Clock className="w-5 h-5 mr-2 text-blue-500" />
                  <span className="font-medium">
                    {episode.duration_seconds ? formatDuration(episode.duration_seconds) : 'Unknown duration'}
                  </span>
                </div>
                <div className="flex items-center text-sm text-gray-600 bg-white/50 rounded-lg p-3">
                  <Users className="w-5 h-5 mr-2 text-purple-500" />
                  <span className="font-medium">{episode.papers.length} 논문</span>
                </div>
                <div className="flex items-center text-sm text-gray-600 bg-white/50 rounded-lg p-3">
                  <Download className="w-5 h-5 mr-2 text-green-500" />
                  <span className="font-medium">
                    {episode.file_size_bytes ? formatFileSize(episode.file_size_bytes) : 'Unknown size'}
                  </span>
                </div>
              </div>

              {/* Audio Player */}
              <div className="mb-8">
                <AudioPlayer
                  src={episode.audio_url}
                  title={episode.title}
                />
              </div>
            </div>
          </div>

          {/* Papers Section */}
          <div className="mb-8">
            <div className="flex items-center space-x-3 mb-6">
              <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
              <h2 className="text-2xl font-bold text-gray-900">
                논문 목록
              </h2>
              <span className="text-sm text-gray-500 bg-gray-100 px-2 py-1 rounded-full">
                {episode.papers.length}개 논문
              </span>
            </div>

            <div className="grid gap-6">
              {episode.papers.map((paper, index) => (
                <div
                  key={paper.id}
                  className="paper-item hover:border-blue-300 hover:shadow-lg transition-all duration-200"
                >
                  <div className="p-6">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-1">
                        <div className="flex items-center space-x-3 mb-3">
                          <span className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-500 text-white text-sm font-bold rounded-full flex items-center justify-center">
                            {index + 1}
                          </span>
                          <h3 className="text-xl font-bold text-gray-900">
                            {paper.title}
                          </h3>
                        </div>
                        
                        <div className="flex items-center space-x-4 text-sm text-gray-600 mb-3">
                          <div className="flex items-center space-x-1">
                            <Users className="w-4 h-4" />
                            <span>{paper.authors.join(', ')}</span>
                          </div>
                          <div className="flex items-center space-x-1">
                            <Star className="w-4 h-4 text-yellow-500" />
                            <span>{paper.upvotes} upvotes</span>
                          </div>
                        </div>
                        
                        <p className="text-gray-700 mb-4 leading-relaxed">
                          {paper.summary}
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4">
                        <a
                          href={paper.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="btn-primary flex items-center space-x-2"
                        >
                          <ExternalLink className="w-4 h-4" />
                          <span>논문 원문 보기</span>
                        </a>
                        <button className="btn-secondary flex items-center space-x-2">
                          <MessageCircle className="w-4 h-4" />
                          <span>논평 보기</span>
                        </button>
                      </div>
                      
                      <div className="text-xs text-gray-500">
                        ID: {paper.id}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Navigation */}
          <div className="flex justify-between items-center">
            <Link href="/" className="btn-secondary">
              홈으로 돌아가기
            </Link>
            <Link href="/archive" className="btn-primary">
              다른 에피소드 보기
            </Link>
          </div>
        </div>
      </main>
    </>
  );
}
