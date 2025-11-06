import { notFound } from 'next/navigation';

// API URL
const API_URL = process.env.API_URL;

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
    <main className="container mx-auto max-w-3xl p-8">
      {/* 팟캐스트 제목 및 플레이어 (변경 없음) */}
      <div className="bg-white p-8 rounded-lg shadow-xl mb-12">
        <h1 className="text-4xl font-bold mb-4 text-gray-900">
          {episode.title}
        </h1>
        <p className="text-gray-500 mb-6">
          {new Date(episode.created_at).toLocaleDateString()}
        </p>
        <audio controls className="w-full" src={episode.audio_url}>
          Your browser does not support the audio element.
        </audio>
      </div>

      {/* 논문 목록 (대대적 수정) */}
      <h2 className="text-3xl font-semibold mb-6 text-gray-800">
        오늘의 논문 요약
      </h2>
      <div className="space-y-8">
        {episode.papers.map((paper) => (
          <div
            key={paper.id}
            className="bg-white p-6 rounded-lg shadow-md overflow-hidden"
          >
            <div className="flex flex-col sm:flex-row gap-6">
              {/* 썸네일 (신규) */}
              <div className="flex-shrink-0">
                <img
                  src={paper.thumbnail_url}
                  alt={`${paper.title} thumbnail`}
                  className="w-full sm:w-32 h-auto object-cover rounded-md border"
                />
              </div>

              {/* 논문 메타 정보 (신규) */}
              <div className="flex-1">
                <h3 className="text-2xl font-semibold text-blue-700 mb-2">
                  {paper.title}
                </h3>
                <p className="text-sm text-gray-600 mb-2">
                  <strong>Authors:</strong> {paper.authors.join(', ')}
                </p>
                <div className="flex gap-4 text-sm text-gray-500 mb-4">
                  <span>
                    <strong>Published:</strong> {paper.published_date}
                  </span>
                  <span>
                    <strong>Upvotes:</strong> {paper.upvotes}
                  </span>
                </div>
              </div>
            </div>

            {/* 요약 섹션 (수정) */}
            <div className="mt-4">
              {/* 짧은 요약 (기본 노출) */}
              <p className="text-gray-700 whitespace-pre-line mb-4">
                {paper.short_summary}
              </p>

              {/* 긴 요약 (토글) */}
              <details className="text-gray-700">
                <summary className="cursor-pointer text-blue-600 hover:underline font-medium select-none">
                  전체 요약 보기
                </summary>
                <p className="whitespace-pre-line mt-3 p-4 bg-gray-50 rounded-md border">
                  {paper.summary}
                </p>
              </details>
            </div>

            {/* 링크 섹션 (수정) */}
            <div className="mt-6 pt-4 border-t border-gray-200 flex flex-wrap gap-x-6 gap-y-2">
              <a
                href={`https://arxiv.org/abs/${paper.arxiv_id}`}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:underline font-medium"
              >
                원문 보러가기 (ArXiv) &rarr;
              </a>
              <a
                href={paper.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-indigo-600 hover:underline font-medium text-sm"
              >
                Hugging Face &rarr;
              </a>
            </div>
          </div>
        ))}
      </div>
    </main>
  );
}