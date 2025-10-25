/**
 * Archive Page - 모든 에피소드 목록
 */

import { useState, useEffect } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { Calendar, Clock, Users, ArrowLeft } from 'lucide-react';
import { apiService, formatDuration, formatDate } from '../services/api';
import { Episode, ApiError } from '../services/types';
import EpisodeCard from '../components/EpisodeCard';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';

export default function ArchivePage() {
  const [episodes, setEpisodes] = useState<Episode[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchEpisodes = async () => {
      try {
        setLoading(true);
        setError(null);
        const episodesData = await apiService.getEpisodes(50, 0);
        setEpisodes(episodesData);
      } catch (err) {
        console.error('API Error:', err);
        const apiError = err as ApiError;
        setError(apiError.message || 'Failed to load episodes');
      } finally {
        setLoading(false);
      }
    };

    fetchEpisodes();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
        <LoadingSpinner size="lg" message="에피소드를 불러오는 중..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
        <ErrorMessage message={error} />
      </div>
    );
  }

  return (
    <>
      <Head>
        <title>Archive - Daily Paper Cast</title>
        <meta name="description" content="모든 AI 논문 팟캐스트 에피소드 아카이브" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
        {/* Header */}
        <header className="bg-white/80 backdrop-blur-lg border-b border-white/20">
          <div className="container-custom">
            <div className="flex items-center justify-between py-6">
              <div className="flex items-center space-x-4">
                <Link href="/" className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 transition-colors">
                  <ArrowLeft className="w-5 h-5" />
                  <span>홈으로</span>
                </Link>
                <div className="w-px h-6 bg-gray-300"></div>
                <div>
                  <h1 className="text-3xl font-bold text-gray-900">아카이브</h1>
                  <p className="text-gray-600 mt-1">모든 에피소드 보기</p>
                </div>
              </div>
              <div className="text-sm text-gray-500">
                총 {episodes.length}개 에피소드
              </div>
            </div>
          </div>
        </header>

        <div className="container-custom py-12">
          {episodes.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              {episodes.map((episode) => (
                <EpisodeCard key={episode.id} episode={episode} />
              ))}
            </div>
          ) : (
            <div className="text-center py-20">
              <div className="w-24 h-24 mx-auto mb-6 bg-gray-100 rounded-full flex items-center justify-center">
                <Calendar className="w-12 h-12 text-gray-400" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">아직 에피소드가 없습니다</h3>
              <p className="text-gray-600">첫 번째 에피소드가 생성되면 여기에 표시됩니다.</p>
            </div>
          )}
        </div>
      </main>
    </>
  );
}
