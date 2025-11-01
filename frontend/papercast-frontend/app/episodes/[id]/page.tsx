import { notFound } from 'next/navigation';

// API URL
const API_URL = "https://podcast-backend-api-740616655373.asia-northeast3.run.app";

// 1. 상세 페이지에서 사용할 데이터 타입 정의
interface Paper {
  id: string;
  title: string;
  summary: string;
  short_summary: string;
  url: string;
  thumbnail_url: string;
}

interface EpisodeDetail {
  id: string;
  title: string;
  audio_url: string;
  created_at: string;
  papers: Paper[];
}

// 2. API 호출 함수 (ID 기준)
async function getEpisodeDetail(id: string): Promise<EpisodeDetail> {
  const res = await fetch(`${API_URL}/episodes/${id}`, {
    cache: 'no-store'
  });
  if (res.status === 404) {
    notFound(); // 404 페이지를 렌더링합니다.
  }
  if (!res.ok) {
    throw new Error('Failed to fetch episode detail');
  }
  return res.json();
}

// 3. 상세 페이지 컴포넌트
export default async function EpisodeDetailPage({ params }: { params: { id: string } }) {
    if (!params.id || params.id === 'undefined') {
        notFound();
      }
    const episode = await getEpisodeDetail(params.id);

  return (
    <main className="container mx-auto max-w-3xl p-8">
      {/* 팟캐스트 제목 및 플레이어 */}
      <div className="bg-white p-8 rounded-lg shadow-xl mb-12">
        <h1 className="text-4xl font-bold mb-4 text-gray-900">{episode.title}</h1>
        <p className="text-gray-500 mb-6">
          {new Date(episode.created_at).toLocaleDateString()}
        </p>
        <audio controls className="w-full" src={episode.audio_url}>
          Your browser does not support the audio element.
        </audio>
      </div>

      {/* 논문 목록 */}
      <h2 className="text-3xl font-semibold mb-6 text-gray-800">
        오늘의 논문 요약
      </h2>
      <div className="space-y-8">
        {episode.papers.map((paper) => (
          <div key={paper.id} className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-2xl font-semibold text-blue-700 mb-3">{paper.title}</h3>
            <p className="text-gray-700 whitespace-pre-line mb-4">
              {paper.summary}
            </p>
            <a
              href={paper.url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:underline font-medium"
            >
              원문 보러가기 &rarr;
            </a>
          </div>
        ))}
      </div>
    </main>
  );
}