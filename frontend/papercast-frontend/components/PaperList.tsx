'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { format } from 'date-fns';
import { ko } from 'date-fns/locale';

interface Paper {
  id: string;
  arxiv_id: string;
  title: string;
  summary: string;
  short_summary: string;
  url: string;
  thumbnail_url: string;
  authors: string[];
  published_date: string;
  upvotes: number;
}

interface EpisodeDetail {
  id: string;
  title: string;
  audio_url: string;
  created_at: string;
  papers: Paper[];
}

interface PaperListProps {
  selectedDate: Date | undefined;
  apiUrl: string;
}

export default function PaperList({ selectedDate, apiUrl }: PaperListProps) {
  const [episode, setEpisode] = useState<EpisodeDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!selectedDate) {
      setEpisode(null);
      return;
    }

    const fetchEpisode = async () => {
      setLoading(true);
      setError(null);
      try {
        const dateStr = format(selectedDate, 'yyyy-MM-dd');
        const res = await fetch(`${apiUrl}/episodes/${dateStr}`);
        
        if (res.status === 404) {
          setEpisode(null);
          setError('해당 날짜에 수집된 논문이 없습니다.');
          return;
        }
        
        if (!res.ok) {
          throw new Error('Failed to fetch episode');
        }
        
        const data = await res.json();
        setEpisode(data);
      } catch (err) {
        setError('논문 정보를 불러오는 중 오류가 발생했습니다.');
        setEpisode(null);
      } finally {
        setLoading(false);
      }
    };

    fetchEpisode();
  }, [selectedDate, apiUrl]);

  if (!selectedDate) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-8 text-center">
        <p className="text-gray-500 text-lg">날짜를 선택하면 해당 날짜의 논문 목록을 볼 수 있습니다.</p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-8 text-center">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <p className="mt-4 text-gray-600">논문 정보를 불러오는 중...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-8 text-center">
        <p className="text-red-500 text-lg">{error}</p>
      </div>
    );
  }

  if (!episode || !episode.papers || episode.papers.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-8 text-center">
        <p className="text-gray-500 text-lg">
          {format(selectedDate, 'yyyy년 MM월 dd일', { locale: ko })}에 수집된 논문이 없습니다.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="mb-6 pb-4 border-b border-gray-200">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">{episode.title}</h2>
        <p className="text-gray-600">
          {format(new Date(episode.created_at), 'yyyy년 MM월 dd일', { locale: ko })}
        </p>
        <Link
          href={`/episodes/${episode.id}`}
          className="inline-block mt-4 text-blue-600 hover:text-blue-800 font-medium"
        >
          전체 에피소드 보기 →
        </Link>
      </div>

      <div className="space-y-4">
        <h3 className="text-xl font-semibold text-gray-800 mb-4">
          논문 목록 ({episode.papers.length}개)
        </h3>
        {episode.papers.map((paper) => (
          <div
            key={paper.id}
            className="p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow"
          >
            <h4 className="text-lg font-semibold text-blue-700 mb-2 line-clamp-2">
              {paper.title}
            </h4>
            <div className="flex flex-wrap gap-4 text-sm text-gray-600 mb-3">
              <span>
                <strong>저자:</strong> {paper.authors.slice(0, 3).join(', ')}
                {paper.authors.length > 3 && ' 외'}
              </span>
              <span>
                <strong>게시일:</strong> {paper.published_date}
              </span>
              <span>
                <strong>추천:</strong> {paper.upvotes}
              </span>
            </div>
            <p className="text-gray-700 text-sm line-clamp-2 mb-3">
              {paper.short_summary}
            </p>
            <div className="flex gap-4">
              <a
                href={`https://arxiv.org/abs/${paper.arxiv_id}`}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:underline text-sm font-medium"
              >
                ArXiv 원문 →
              </a>
              <a
                href={paper.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-indigo-600 hover:underline text-sm font-medium"
              >
                Hugging Face →
              </a>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

