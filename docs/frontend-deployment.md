# Vercel 프론트엔드 배포 가이드

## 🎯 개요

PaperCast의 Next.js 프론트엔드를 Vercel에 배포하여 백엔드 API와 연동합니다.

## 📋 사전 준비

### 1. Vercel 계정 및 CLI 설치

```bash
# Vercel CLI 설치
npm i -g vercel

# Vercel 로그인
vercel login
```

### 2. 백엔드 서버 배포 완료 확인

- Google Cloud Run에 백엔드 배포 완료
- 백엔드 URL 확인: `https://papercast-api-xxx-uc.a.run.app`
- API 테스트 완료

## 🚀 Vercel 배포 과정

### 1. Vercel 프로젝트 초기화

```bash
# frontend 디렉토리에서 실행
cd frontend

# Vercel 프로젝트 초기화
vercel

# 프로젝트 설정
? Set up and deploy "~/papercast/frontend"? [Y/n] y
? Which scope do you want to deploy to? [Your Account]
? Link to existing project? [N/y] n
? What's your project's name? papercast
? In which directory is your code located? ./
```

### 2. 환경 변수 설정

Vercel Dashboard에서 환경 변수 설정:

```bash
# Vercel Dashboard → Project → Settings → Environment Variables
NEXT_PUBLIC_API_URL=https://papercast-api-xxx-uc.a.run.app
```

또는 CLI로 설정:

```bash
# 환경 변수 추가
vercel env add NEXT_PUBLIC_API_URL
# 값 입력: https://papercast-api-xxx-uc.a.run.app
```

### 3. 프론트엔드 API 클라이언트 수정

`frontend/src/services/api.ts` 파일 수정:

```typescript
// frontend/src/services/api.ts
export class ApiService {
  // 프로덕션에서는 Vercel 환경 변수 사용
  private baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001/api';
  
  async getEpisodes(): Promise<EpisodeResponse[]> {
    const response = await fetch(`${this.baseUrl}/episodes`);
    return response.json();
  }
  
  async getEpisode(id: string): Promise<EpisodeDetailResponse> {
    const response = await fetch(`${this.baseUrl}/episodes/${id}`);
    return response.json();
  }
  
  async getPaper(id: string): Promise<PaperResponse> {
    const response = await fetch(`${this.baseUrl}/papers/${id}`);
    return response.json();
  }
}
```

### 4. Next.js 설정 확인

`frontend/next.config.js` 파일 확인:

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
  },
  // API 프록시 설정 (선택사항)
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL}/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
```

### 5. Vercel 배포

```bash
# 배포 실행
vercel --prod

# 또는 자동 배포 (Git 연동 시)
git push origin main
```

## 🔧 배포 후 설정

### 1. 도메인 확인

배포 완료 후 제공되는 URL 확인:
```
https://papercast.vercel.app
```

### 2. 기능 테스트

1. **홈페이지**: `https://papercast.vercel.app`
2. **아카이브**: `https://papercast.vercel.app/archive`
3. **에피소드 상세**: `https://papercast.vercel.app/episodes/2025-10-25`
4. **논문 상세**: `https://papercast.vercel.app/papers/2510.19600`

### 3. API 연동 확인

브라우저 개발자 도구에서 네트워크 탭 확인:
- API 호출이 백엔드 서버로 정상 전송되는지 확인
- CORS 오류가 없는지 확인

## 🚨 트러블슈팅

### 1. API 연결 오류

**문제**: 프론트엔드에서 백엔드 API 호출 실패

**해결**:
```bash
# 환경 변수 확인
vercel env ls

# 환경 변수 재설정
vercel env add NEXT_PUBLIC_API_URL
```

### 2. CORS 오류

**문제**: CORS policy 오류

**해결**: 백엔드 `api/main.py`에서 CORS 설정 확인:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://papercast.vercel.app",
        "https://*.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 3. 빌드 오류

**문제**: Vercel 빌드 실패

**해결**:
```bash
# 로컬에서 빌드 테스트
cd frontend
npm run build

# 빌드 로그 확인
vercel logs
```

### 4. 환경 변수 문제

**문제**: 환경 변수가 적용되지 않음

**해결**:
```bash
# 환경 변수 재배포
vercel env pull .env.local
vercel --prod
```

## 📝 배포 완료 후

### 1. GitHub Actions 업데이트

`.github/workflows/daily-podcast.yml`에서 Slack 알림 URL 업데이트:

```yaml
- name: Notify Slack
  if: success()
  uses: 8398a7/action-slack@v3
  with:
    status: success
    channel: '#papercast'
    text: |
      🎉 오늘의 AI 논문 팟캐스트가 완성되었습니다!
      
      📅 날짜: $(date +%Y-%m-%d)
      🎧 지금 바로 들어보세요: https://papercast.vercel.app
      📖 아카이브: https://papercast.vercel.app/archive
```

### 2. 커스텀 도메인 설정 (선택사항)

Vercel Dashboard에서 커스텀 도메인 설정:
1. Project → Settings → Domains
2. 도메인 추가
3. DNS 설정

### 3. 모니터링 설정

Vercel Analytics 활성화:
1. Project → Analytics
2. Web Analytics 활성화

## 🎉 배포 완료!

이제 다음 URL에서 PaperCast 서비스를 이용할 수 있습니다:

- **프론트엔드**: `https://papercast.vercel.app`
- **백엔드 API**: `https://papercast-api-xxx-uc.a.run.app`
- **API 문서**: `https://papercast-api-xxx-uc.a.run.app/docs`

---

**다음 단계**: [GitHub Actions 자동화 설정](github-actions-setup.md)
