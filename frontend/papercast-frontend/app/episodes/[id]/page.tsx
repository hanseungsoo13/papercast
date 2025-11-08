import { notFound } from 'next/navigation';
import Link from 'next/link';
import { format } from 'date-fns';
import { ko } from 'date-fns/locale';
import PaperThumbnail from '../../../components/PaperThumbnail';

// API URL
const API_URL = process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';

// 1. 상세 페이지에서 사용할 데이터 타입 정의 (백엔드 데이터에 맞게 확장)
interface Paper {
  id: string; // '2510.25616' (key로 사용)
  arxiv_id: string; // '2510.25616' (ArXiv 링크용)
  title: string;
  summary: string; // 긴 요약
  short_summary: string; // 짧은 요약 (3줄)
  url: string; // Hugging Face 링크
  thumbnail_url: string;
  authors: string[]; // 저자 배열
  published_date: string; // 'Oct 29'
  upvotes: number;
  // categories, collected_at, view_count 등은 요청대로 제외
}

interface EpisodeDetail {
  id: string;
  title: string;
  audio_url: string;
  created_at: string;
  papers: Paper[]; // Paper[] 타입 사용
}

// 2. API 호출 함수 (ID 기준) - 변경 없음
async function getEpisodeDetail(id: string): Promise<EpisodeDetail> {
  const res = await fetch(`${API_URL}/episodes/${id}`, {
    cache: 'no-store',
  });
  if (res.status === 404) {
    notFound();
  }
  if (!res.ok) {
    throw new Error('Failed to fetch episode detail');
  }
  return res.json();
}

// 3. 상세 페이지 컴포넌트 (UI/UX 개선)
export default async function EpisodeDetailPage(props: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await props.params;
  if (!id || id === 'undefined') {
    notFound();
  }
  const episode = await getEpisodeDetail(id);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto max-w-5xl px-4 sm:px-6 lg:px-8 py-8">
        {/* 뒤로가기 버튼 */}
        <Link
          href="/"
          className="inline-flex items-center gap-2 text-gray-700 hover:text-blue-600 mb-6 transition-colors group"
        >
          <svg
            className="w-5 h-5 transform group-hover:-translate-x-1 transition-transform"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M15 19l-7-7 7-7"
            />
          </svg>
          <span className="font-medium">홈으로 돌아가기</span>
        </Link>

        {/* 팟캐스트 헤더 및 플레이어 */}
        <div className="bg-white rounded-xl shadow-lg p-6 sm:p-8 mb-8">
          <div className="mb-6">
            <div className="flex items-center gap-2 mb-3">
              <span className="text-2xl">🎙️</span>
              <span className="text-sm font-semibold text-blue-600 uppercase tracking-wide">
                Episode
              </span>
            </div>
            <h1 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-3">
              {episode.title}
            </h1>
            <p className="text-gray-600 flex items-center gap-2">
              <svg
                className="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                />
              </svg>
              {format(new Date(episode.created_at), 'yyyy년 MM월 dd일 (EEEE)', {
                locale: ko,
              })}
            </p>
          </div>

          {/* 오디오 플레이어 */}
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-4 border border-blue-100">
            <audio
              controls
              className="w-full h-12"
              src={episode.audio_url}
              preload="metadata"
            >
              Your browser does not support the audio element.
            </audio>
          </div>
        </div>

        {/* 논문 목록 섹션 */}
        <div className="mb-6">
          <h2 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-2">
            📄 논문 요약
          </h2>
          <p className="text-gray-600 mb-6">
            총 {episode.papers.length}개의 논문이 포함되어 있습니다.
          </p>
        </div>

        <div className="space-y-6">
          {episode.papers.map((paper, index) => (
            <div
              key={paper.id}
              className="bg-white rounded-xl shadow-md hover:shadow-lg transition-shadow overflow-hidden"
            >
              <div className="p-6 sm:p-8">
                {/* 논문 헤더 */}
                <div className="flex flex-col sm:flex-row gap-6 mb-6">
                  {/* 썸네일 */}
                  <div className="flex-shrink-0">
                    <PaperThumbnail
                      src={paper.thumbnail_url}
                      alt={`${paper.title} thumbnail`}
                      className="w-full sm:w-40 h-auto object-cover rounded-lg border-2 border-gray-200 shadow-sm"
                    />
                  </div>

                  {/* 논문 메타 정보 */}
                  <div className="flex-1">
                    <div className="flex items-start gap-2 mb-3">
                      <span className="flex-shrink-0 w-8 h-8 bg-blue-100 text-blue-700 rounded-full flex items-center justify-center font-bold text-sm">
                        {index + 1}
                      </span>
                      <h3 className="text-xl sm:text-2xl font-bold text-gray-900 leading-tight">
                        {paper.title}
                      </h3>
                    </div>

                    <div className="space-y-2 mb-4">
                      <div className="flex items-start gap-2">
                        <span className="text-gray-500 text-sm font-medium min-w-[60px]">
                          저자:
                        </span>
                        <p className="text-gray-700 text-sm flex-1">
                          {paper.authors.length > 3
                            ? `${paper.authors.slice(0, 3).join(', ')} 외 ${
                                paper.authors.length - 3
                              }명`
                            : paper.authors.join(', ')}
                        </p>
                      </div>

                      <div className="flex flex-wrap gap-4 text-sm">
                        <div className="flex items-center gap-2 text-gray-600">
                          <svg
                            className="w-4 h-4"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                            />
                          </svg>
                          <span>{paper.published_date}</span>
                        </div>
                        <div className="flex items-center gap-2 text-gray-600">
                          <svg
                            className="w-4 h-4"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5"
                            />
                          </svg>
                          <span>{paper.upvotes} 추천</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* 요약 섹션 */}
                <div className="border-t border-gray-200 pt-6">
                  <h4 className="text-lg font-semibold text-gray-900 mb-3">
                    요약
                  </h4>
                  <div className="bg-gray-50 rounded-lg p-4 mb-4">
                    <p className="text-gray-700 whitespace-pre-line leading-relaxed">
                      {paper.short_summary}
                    </p>
                  </div>

                  {/* 전체 요약 토글 */}
                  <details className="group">
                    <summary className="cursor-pointer text-blue-600 hover:text-blue-800 font-medium select-none flex items-center gap-2 py-2">
                      <span>전체 요약 보기</span>
                      <svg
                        className="w-4 h-4 transform group-open:rotate-180 transition-transform"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M19 9l-7 7-7-7"
                        />
                      </svg>
                    </summary>
                    <div className="mt-4 p-4 bg-blue-50 rounded-lg border border-blue-100">
                      <p className="text-gray-700 whitespace-pre-line leading-relaxed">
                        {paper.summary}
                      </p>
                    </div>
                  </details>
                </div>

                {/* 링크 섹션 */}
                <div className="mt-6 pt-6 border-t border-gray-200 flex flex-wrap gap-4">
                  <a
                    href={`https://arxiv.org/abs/${paper.arxiv_id}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium text-sm shadow-sm hover:shadow-md"
                  >
                    <svg
                      className="w-4 h-4"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
                      />
                    </svg>
                    ArXiv 원문
                  </a>
                  <a
                    href={paper.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-medium text-sm shadow-sm hover:shadow-md"
                  >
                    <svg
                      className="w-4 h-4"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
                      />
                    </svg>
                    Hugging Face
                  </a>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* 하단 여백 및 홈으로 돌아가기 버튼 */}
        <div className="mt-12 text-center">
          <Link
            href="/"
            className="inline-flex items-center gap-2 px-6 py-3 bg-white text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium shadow-sm hover:shadow-md border border-gray-200"
          >
            <svg
              className="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"
              />
            </svg>
            홈으로 돌아가기
          </Link>
        </div>
      </div>
    </div>
  );
}
