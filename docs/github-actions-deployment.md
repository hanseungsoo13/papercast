# GitHub Actions 중심 배포 가이드

## 🎯 개요

PaperCast는 GitHub Actions를 통해 **완전 자동화된 배포 파이프라인**을 제공합니다. 매일 6시 KST에 자동으로 실행되어 논문 수집부터 배포까지 모든 과정을 처리합니다.

## 📋 배포 흐름

```
매일 6시 KST (21:00 UTC)
         ↓
┌─────────────────────────────────────┐
│        GitHub Actions 실행           │
└─────────────────────────────────────┘
         ↓
┌─────────────────────────────────────┐
│    1. 논문 수집 + AI 요약 생성       │
│    2. TTS 변환 + GCS 업로드         │
│    3. 데이터베이스 저장             │
└─────────────────────────────────────┘
         ↓
┌─────────────────────────────────────┐
│    4. 백엔드 배포 (Google Cloud Run)│
│    5. 프론트엔드 배포 (Vercel)      │
└─────────────────────────────────────┘
         ↓
┌─────────────────────────────────────┐
│    6. Slack 알림 전송               │
└─────────────────────────────────────┘
```

## 🚀 설정 방법

### 1. GitHub Secrets 설정

Repository → Settings → Secrets and variables → Actions에서 다음 Secrets를 설정:

| Secret Name | Description | How to Get |
|-------------|-------------|------------|
| `GEMINI_API_KEY` | Google Gemini API 키 | [Google AI Studio](https://makersuite.google.com/app/apikey) |
| `GCP_SERVICE_ACCOUNT_KEY` | GCP Service Account JSON (base64) | GCP Console → Service Account → 키 생성 → `base64 -w 0 < key.json` |
| `GCP_PROJECT_ID` | Google Cloud 프로젝트 ID | GCP Console → 프로젝트 선택 |
| `GCS_BUCKET_NAME` | Google Cloud Storage 버킷 이름 | GCS Console → 버킷 생성 |
| `DATABASE_URL` | PostgreSQL 데이터베이스 URL | Cloud SQL 또는 외부 DB |
| `FRONTEND_API_URL` | 백엔드 API URL (자동 설정됨) | Cloud Run 배포 후 자동 생성 |
| `FRONTEND_URL` | 프론트엔드 URL (자동 설정됨) | Vercel 배포 후 자동 생성 |
| `VERCEL_TOKEN` | Vercel API 토큰 | [Vercel Dashboard](https://vercel.com/account/tokens) |
| `VERCEL_ORG_ID` | Vercel 조직 ID | Vercel Dashboard → Settings → General |
| `VERCEL_PROJECT_ID` | Vercel 프로젝트 ID | Vercel Dashboard → Project → Settings |
| `SLACK_WEBHOOK_URL` | Slack 웹훅 URL (선택사항) | [Slack API](https://api.slack.com/apps) |

### 2. GCP Service Account 설정

```bash
# GCP Console에서 Service Account 생성
# 역할 부여:
# - Cloud Run Admin
# - Cloud Storage Admin  
# - Cloud SQL Admin
# - Cloud Build Editor

# JSON 키 다운로드 후 base64 인코딩
base64 -w 0 < service-account-key.json
```

### 3. Vercel 설정

```bash
# Vercel CLI 설치 및 로그인
npm i -g vercel
vercel login

# 프로젝트 초기화
cd frontend
vercel

# 토큰 및 ID 확인
vercel whoami
# VERCEL_TOKEN: vercel dashboard에서 생성
# VERCEL_ORG_ID: vercel dashboard → settings → general
# VERCEL_PROJECT_ID: vercel dashboard → project → settings
```

## 🔧 자동 배포 과정

### 1. 논문 수집 및 처리 (generate-podcast)

```yaml
- 논문 수집: Hugging Face에서 Top 3 논문
- AI 요약: Gemini Pro로 한국어 요약 생성
- 3줄 요약: 각 논문별 핵심 내용 요약
- TTS 변환: Google Cloud TTS로 음성 생성
- GCS 업로드: MP3 파일 및 메타데이터 저장
- DB 저장: PostgreSQL에 에피소드 및 논문 정보 저장
```

### 2. 백엔드 배포 (deploy-backend)

```yaml
- Docker 이미지 빌드: Google Cloud Build
- 이미지 푸시: Google Container Registry
- Cloud Run 배포: 자동 스케일링 서버리스
- 환경 변수 설정: DB, API 키, 버킷 이름
- 헬스 체크: API 엔드포인트 테스트
```

### 3. 프론트엔드 배포 (deploy-frontend)

```yaml
- 의존성 설치: npm ci
- 빌드: Next.js 프로덕션 빌드
- Vercel 배포: 자동 도메인 할당
- 환경 변수 설정: 백엔드 API URL 연결
- 프리뷰 배포: Pull Request별 프리뷰 생성
```

### 4. 알림 전송 (notify-success)

```yaml
- 성공 알림: Slack 채널에 웹사이트 링크 전송
- 실패 알림: 오류 로그 및 해결 방법 안내
- 링크 포함: 프론트엔드 URL, 아카이브 URL
```

## 🎯 배포 결과

### 자동 생성되는 URL

1. **백엔드 API**: `https://papercast-backend-xxx-uc.a.run.app`
2. **프론트엔드**: `https://papercast.vercel.app`
3. **API 문서**: `https://papercast-backend-xxx-uc.a.run.app/docs`

### 데이터 흐름

```
GitHub Actions
     ↓
논문 수집 → AI 요약 → TTS 변환
     ↓
GCS 업로드 → DB 저장
     ↓
백엔드 배포 → 프론트엔드 배포
     ↓
Slack 알림 → 사용자 접근
```

## 🚨 트러블슈팅

### 1. GitHub Actions 실패

**문제**: 워크플로우 실행 실패

**해결**:
```bash
# Actions 탭에서 실패한 워크플로우 확인
# 각 단계별 로그 확인
# Secrets 설정 재확인
```

### 2. 백엔드 배포 실패

**문제**: Cloud Run 배포 실패

**해결**:
```bash
# GCP Console → Cloud Run에서 서비스 확인
# 로그 확인: Cloud Run → 서비스 → 로그
# 환경 변수 확인: Cloud Run → 서비스 → 환경 변수
```

### 3. 프론트엔드 배포 실패

**문제**: Vercel 배포 실패

**해결**:
```bash
# Vercel Dashboard → Project → Deployments 확인
# 빌드 로그 확인
# 환경 변수 확인: Vercel → Project → Settings → Environment Variables
```

### 4. API 연결 실패

**문제**: 프론트엔드에서 백엔드 API 호출 실패

**해결**:
1. **CORS 설정 확인**: 백엔드에서 Vercel 도메인 허용
2. **환경 변수 확인**: `FRONTEND_API_URL`이 올바른지 확인
3. **네트워크 확인**: 브라우저 개발자 도구에서 실제 요청 URL 확인

## 📝 수동 실행

### 1. 전체 파이프라인 수동 실행

```bash
# GitHub Repository → Actions → Daily Podcast Generation
# "Run workflow" 버튼 클릭
```

### 2. 개별 단계 실행

```bash
# 논문 생성만 실행
# Repository → Actions → "Generate podcast episode" 워크플로우

# 배포만 실행  
# Repository → Actions → "Deploy backend/frontend" 워크플로우
```

## 🎉 완전 자동화!

이제 다음이 모두 자동으로 처리됩니다:

- ✅ **매일 6시 KST**: 자동 실행
- ✅ **논문 수집**: Hugging Face에서 최신 논문
- ✅ **AI 처리**: Gemini Pro 요약 + 3줄 요약 + TTS
- ✅ **클라우드 저장**: GCS에 MP3 및 메타데이터
- ✅ **백엔드 배포**: Google Cloud Run 자동 배포
- ✅ **프론트엔드 배포**: Vercel 자동 배포
- ✅ **알림 전송**: Slack으로 성공/실패 알림
- ✅ **웹사이트 접근**: 사용자가 즉시 새로운 에피소드 확인 가능

---

**다음 단계**: [모니터링 및 유지보수](monitoring-guide.md)
