/**
 * Home page for Daily Paper Cast.
 * Displays the latest episode prominently with audio player and recent episodes list.
 */

import { useState, useEffect } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { Play, Pause, Download, Calendar, Clock, Users } from 'lucide-react';
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

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);

        console.log('Fetching data from API...');
        
        // Fetch latest episode
        const latest = await apiService.getLatestEpisode();
        console.log('Latest episode:', latest);
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
          papers: [
            {
              id: '2510.19338',
              title: 'Every Attention Matters',
              authors: ['John Doe', 'Jane Smith'],
              url: 'https://huggingface.co/papers/2510.19338',
              upvotes: 142,
              collected_at: '2025-10-20T16:07:59.488472+00:00'
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

      <main className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
        {/* Hero Header */}
        <header className="relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-r from-blue-600/10 to-purple-600/10"></div>
          <div className="container-custom relative">
            <div className="flex justify-between items-center py-8">
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl flex items-center justify-center">
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
                  className="btn-ghost"
                >
                  아카이브
                </Link>
                <button className="btn-primary">
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
              <div className="card-gradient">
                <div className="p-8">
                  <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center space-x-3">
                      <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                      <h2 className="text-2xl font-bold text-gray-900">
                        최신 에피소드
                      </h2>
                    </div>
                    <span className="text-sm text-gray-500 flex items-center bg-gray-100 px-3 py-1 rounded-full">
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
                    <h4 className="text-lg font-semibold text-gray-800">
                      Papers in this episode:
                    </h4>
                    <div className="grid gap-4">
                      {latestEpisode.papers.map((paper, index) => (
                        <div
                          key={paper.id}
                          className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                        >
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <h5 className="font-medium text-gray-900 mb-2">
                                {index + 1}. {paper.title}
                              </h5>
                              <p className="text-sm text-gray-600 mb-2">
                                by {paper.authors.join(', ')}
                              </p>
                              <p className="text-sm text-gray-700 line-clamp-2">
                                {paper.summary}
                              </p>
                            </div>
                            <div className="ml-4 flex flex-col items-end space-y-2">
                              <span className="text-xs text-gray-500">
                                👍 {paper.upvotes}
                              </span>
                              <a
                                href={paper.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                              >
                                View Paper →
                              </a>
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
            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-6">
                Recent Episodes
              </h2>
              <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                {recentEpisodes.map((episode) => (
                  <EpisodeCard key={episode.id} episode={episode} />
                ))}
              </div>
              <div className="mt-8 text-center">
                <Link
                  href="/archive"
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 transition-colors"
                >
                  View All Episodes
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
