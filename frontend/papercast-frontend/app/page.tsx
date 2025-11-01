import Link from 'next/link';

// API URL (환경 변수로 빼는 것이 가장 좋습니다)
const API_URL = "https://podcast-backend-api-740616655373.asia-northeast3.run.app";

// 1. API 응답 데이터의 타입을 정의합니다 (TypeScript)
interface Episode {
  id: string; // '2025-10-27'
  title: string;
  audio_url: string;
  created_at: string;
}

// 2. API를 호출하는 함수
async function getEpisodes(): Promise<{ episodes: Episode[] }> {
  // Next.js 13+의 fetch는 기본적으로 SSG(정적 생성)처럼 작동합니다.
  const res = await fetch(`${API_URL}/episodes`);
  if (!res.ok) {
    throw new Error('Failed to fetch episodes');
  }
  return res.json();
}

// 3. 메인 페이지 컴포넌트 (async로 변경)
export default async function HomePage() {
  const { episodes } = await getEpisodes();

  return (
    <main className="container mx-auto max-w-3xl p-8">
      <h1 className="text-4xl font-bold mb-8 text-gray-900">
        PaperCast: AI 논문 요약
      </h1>

      <div className="space-y-6">
        {episodes
        .filter(episode => episode.id)
        .map((episode) => (
          // 4. 각 에피소드를 상세 페이지로 링크합니다.
          <Link
            href={`/episodes/${episode.id}`}
            key={episode.id}
            className="block p-6 bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow"
          >
            <h2 className="text-2xl font-semibold text-blue-700">{episode.title}</h2>
            <p className="text-gray-600 mt-2">
              게시일: {new Date(episode.created_at).toLocaleDateString()}
            </p>
          </Link>
        ))}
      </div>
    </main>
  );
}