/**
 * Home page for Daily Paper Cast.
 * Displays the latest episode prominently with audio player and recent episodes list.
 */

import { useState, useEffect } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { Play, Pause, Download, Calendar, Clock, Users, ChevronDown, ChevronUp } from 'lucide-react';
import { apiService, formatDuration, formatFileSize, formatDate } from '../services/api';
import { EpisodeWithPapers, ApiError } from '../services/types';
import AudioPlayer from '../components/AudioPlayer';
import EpisodeCard from '../components/EpisodeCard';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import HeroSection from '../components/HeroSection';
import FeatureGrid from '../components/FeatureGrid';

export default function HomePage() {
  const [latestEpisode, setLatestEpisode] = useState<EpisodeWithPapers | null>(null);
  const [recentEpisodes, setRecentEpisodes] = useState<EpisodeWithPapers[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedPapers, setExpandedPapers] = useState<Set<string>>(new Set());

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);

        console.log('Fetching data from API...');
        
        // Fetch latest episode
        const latest = await apiService.getLatestEpisode();
        console.log('Latest episode:', latest);
        console.log('Latest episode papers:', latest.papers);
        if (latest.papers && latest.papers.length > 0) {
          console.log('First paper authors:', latest.papers[0].authors);
          console.log('First paper summary length:', latest.papers[0].summary?.length);
        }
        setLatestEpisode(latest);

        // Fetch recent episodes (excluding the latest one)
        const episodes = await apiService.getEpisodes(5, 0);
        console.log('Episodes:', episodes);
        const recent = episodes.filter(
          (episode) => episode.id !== latest.id
        );
        setRecentEpisodes(recent);
      } catch (err) {
        console.error('API Error:', err);
        const apiError = err as ApiError;
        setError(apiError.message || 'Failed to load episodes');
        
        // Set fallback data for development
        setLatestEpisode({
          id: '2025-10-21',
          title: 'Daily AI Papers - 2025-10-21',
          publication_date: '2025-10-21',
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
        });
        setRecentEpisodes([]);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

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

  return (
    <>
      <Head>
        <title>Daily Paper Cast - Latest AI Research Podcasts</title>
        <meta
          name="description"
          content="Listen to the latest AI research papers summarized in daily podcast episodes. Stay up-to-date with cutting-edge AI developments."
        />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 relative overflow-hidden">
        {/* Background Pattern */}
        <div className="absolute inset-0 opacity-30">
          <div className="w-full h-full bg-hero-pattern"></div>
        </div>
        {/* Hero Header */}
        <header className="relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-r from-blue-600/10 to-purple-600/10"></div>
          <div className="container-custom relative">
            <div className="flex justify-between items-center py-8">
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl flex items-center justify-center shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105">
                  <span className="text-white font-bold text-xl">🎙️</span>
                </div>
                <div>
                  <h1 className="text-3xl font-bold text-gray-900">
                    Daily Paper Cast
                  </h1>
                  <p className="text-gray-600 mt-1">
                    AI 연구 논문을 팟캐스트로 만나보세요
                  </p>
                </div>
              </div>
              <nav className="flex space-x-6">
                <Link
                  href="/archive"
                  className="btn-ghost hover:bg-blue-50 hover:text-blue-600 transition-all duration-200"
                >
                  아카이브
                </Link>
                <button 
                  className="btn-primary hover:shadow-glow transition-all duration-300"
                  onClick={() => {
                    alert('구독 기능은 곧 추가될 예정입니다! RSS 피드나 이메일 구독을 통해 알림을 받을 수 있습니다.');
                  }}
                >
                  구독하기
                </button>
              </nav>
            </div>
          </div>
        </header>

        {/* Hero Section */}
        <HeroSection
          title="오늘의 AI 연구 논문"
          description="매일 아침, 최신 AI 연구 논문을 한국어로 요약한 팟캐스트를 만나보세요"
          features={["실시간 업데이트", "🎧 고품질 오디오", "📄 논문 원문 링크"]}
        />

        <div className="container-custom section-padding">

          {/* Latest Episode */}
          {latestEpisode && (
            <section className="mb-16 animate-slide-up">
              <div className="card-gradient hover:shadow-2xl transition-all duration-300">
                <div className="p-8">
                  <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center space-x-3">
                      <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                      <h2 className="text-2xl font-bold text-gray-900">
                        최신 에피소드
                      </h2>
                    </div>
                    <span className="text-sm text-gray-500 flex items-center bg-white/80 backdrop-blur-sm px-3 py-1 rounded-full border border-white/20">
                      <Calendar className="w-4 h-4 mr-1" />
                      {formatDate(latestEpisode.publication_date)}
                    </span>
                  </div>

                  <h3 className="text-2xl font-bold text-gray-800 mb-6 leading-tight">
                    {latestEpisode.title}
                  </h3>

                  {/* Audio Player */}
                  <div className="mb-6">
                    <AudioPlayer
                      src={latestEpisode.audio_url}
                      title={latestEpisode.title}
                    />
                  </div>

                  {/* Episode Stats */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                    <div className="flex items-center text-sm text-gray-600">
                      <Clock className="w-4 h-4 mr-2" />
                      {latestEpisode.duration_seconds
                        ? formatDuration(latestEpisode.duration_seconds)
                        : 'Unknown duration'}
                    </div>
                    <div className="flex items-center text-sm text-gray-600">
                      <Users className="w-4 h-4 mr-2" />
                      {latestEpisode.papers.length} papers
                    </div>
                    <div className="flex items-center text-sm text-gray-600">
                      <Download className="w-4 h-4 mr-2" />
                      {latestEpisode.file_size_bytes
                        ? formatFileSize(latestEpisode.file_size_bytes)
                        : 'Unknown size'}
                    </div>
                  </div>

                  {/* Papers List */}
                  <div className="space-y-4">
                    <h4 className="text-lg font-semibold text-gray-800 flex items-center space-x-2">
                      <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
                      <span>이번 에피소드의 논문들</span>
                    </h4>
                    <div className="grid gap-4">
                      {latestEpisode.papers.map((paper, index) => (
                        <div
                          key={paper.id}
                          onClick={() => {
                            console.log('논문 카드 클릭됨:', paper.id);
                            window.location.href = `/papers/${paper.id}`;
                          }}
                          className="paper-item hover:border-blue-300 hover:shadow-md transition-all duration-200 block cursor-pointer"
                        >
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <div className="flex items-center space-x-2 mb-2">
                                <span className="w-6 h-6 bg-gradient-to-r from-blue-500 to-purple-500 text-white text-xs font-bold rounded-full flex items-center justify-center">
                                  {index + 1}
                                </span>
                                <h5 className="paper-title">
                                  {paper.title}
                                </h5>
                              </div>
                              <p className="paper-authors">
                                by {paper.authors && paper.authors.length > 0 ? paper.authors.join(', ') : 'Unknown'}
                              </p>
                              <div className="paper-summary">
                                <p className={expandedPapers.has(paper.id) ? '' : 'line-clamp-3'}>
                                  {paper.summary}
                                </p>
                                {paper.summary && paper.summary.length > 200 && (
                                  <button
                                    type="button"
                                    onClick={(e) => {
                                      console.log('더보기 버튼 클릭됨:', paper.id, '현재 상태:', expandedPapers.has(paper.id));
                                      e.preventDefault();
                                      e.stopPropagation();
                                      
                                      const newExpanded = new Set(expandedPapers);
                                      if (expandedPapers.has(paper.id)) {
                                        newExpanded.delete(paper.id);
                                        console.log('간략히 보기로 변경');
                                      } else {
                                        newExpanded.add(paper.id);
                                        console.log('더보기로 변경');
                                      }
                                      setExpandedPapers(newExpanded);
                                    }}
                                    className="mt-2 flex items-center space-x-1 text-blue-600 hover:text-blue-800 text-sm font-medium transition-colors bg-blue-50 hover:bg-blue-100 px-3 py-2 rounded-lg border border-blue-200 hover:border-blue-300 cursor-pointer"
                                    style={{ 
                                      zIndex: 20,
                                      position: 'relative',
                                      pointerEvents: 'auto'
                                    }}
                                  >
                                    <span>
                                      {expandedPapers.has(paper.id) ? '간략히 보기' : '더보기'}
                                    </span>
                                    {expandedPapers.has(paper.id) ? (
                                      <ChevronUp className="w-4 h-4" />
                                    ) : (
                                      <ChevronDown className="w-4 h-4" />
                                    )}
                                  </button>
                                )}
                              </div>
                            </div>
                            <div className="ml-4 flex flex-col items-end space-y-2">
                              <div className="flex items-center space-x-2">
                                <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded-full">
                                  👍 {paper.upvotes}
                                </span>
                              </div>
                              <div className="flex items-center space-x-2">
                                <div
                                  onClick={(e) => {
                                    console.log('원문 보기 링크 클릭됨:', paper.url);
                                    e.preventDefault();
                                    e.stopPropagation();
                                    e.nativeEvent.stopImmediatePropagation();
                                    window.open(paper.url, '_blank', 'noopener,noreferrer');
                                  }}
                                  onMouseDown={(e) => e.stopPropagation()}
                                  onMouseUp={(e) => e.stopPropagation()}
                                  style={{ 
                                    zIndex: 10,
                                    position: 'relative',
                                    cursor: 'pointer'
                                  }}
                                >
                                  <a
                                    href={paper.url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-blue-600 hover:text-blue-800 text-sm font-medium hover:underline transition-colors flex items-center space-x-1 bg-blue-50 hover:bg-blue-100 px-3 py-2 rounded-lg border border-blue-200 hover:border-blue-300 cursor-pointer"
                                    style={{ 
                                      zIndex: 10,
                                      position: 'relative'
                                    }}
                                  >
                                    <span>원문 보기</span>
                                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                                    </svg>
                                  </a>
                                </div>
                                <span className="text-xs text-gray-400">카드 클릭시 상세보기</span>
                              </div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </section>
          )}

          {/* Recent Episodes */}
          {recentEpisodes.length > 0 && (
            <section className="animate-fade-in">
              <div className="text-center mb-8">
                <h2 className="text-3xl font-bold text-gray-900 mb-4">
                  최근 에피소드
                </h2>
                <p className="text-lg text-gray-600 max-w-2xl mx-auto">
                  지난 에피소드들을 다시 들어보세요
                </p>
              </div>
              <div className="grid-responsive">
                {recentEpisodes.map((episode) => (
                  <EpisodeCard key={episode.id} episode={episode} />
                ))}
              </div>
              <div className="mt-12 text-center">
                <Link
                  href="/archive"
                  className="btn-primary hover:shadow-glow transition-all duration-300"
                >
                  모든 에피소드 보기
                </Link>
              </div>
            </section>
          )}

          {/* Feature Grid */}
          <FeatureGrid />
        </div>
      </main>
    </>
  );
}
