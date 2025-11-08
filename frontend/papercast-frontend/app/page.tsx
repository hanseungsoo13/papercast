import HomePageClient from '../components/HomePageClient';

// API URL (환경 변수로 빼는 것이 가장 좋습니다)
const API_URL = process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';

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
  const res = await fetch(`${API_URL}/episodes`, {
    cache: 'no-store', // 최신 데이터를 가져오기 위해
  });
  if (!res.ok) {
    throw new Error('Failed to fetch episodes');
  }
  return res.json();
}

// 3. 메인 페이지 컴포넌트 (async로 변경)
export default async function HomePage() {
  const { episodes } = await getEpisodes();
  
  // 사용 가능한 날짜 목록 추출
  const availableDates = episodes
    .filter(episode => episode.id)
    .map(episode => episode.id);

  return (
    <HomePageClient 
      availableDates={availableDates} 
      apiUrl={API_URL}
    />
  );
}