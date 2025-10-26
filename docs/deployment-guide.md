# PaperCast 전체 배포 가이드

## 🎯 개요

PaperCast는 **GitHub Actions를 통한 완전 자동화된 배포 파이프라인**을 제공합니다. 매일 6시 KST에 자동으로 실행되어 논문 수집부터 배포까지 모든 과정을 처리합니다.

> **💡 권장 방법**: GitHub Actions 자동 배포 (이 가이드)
> 
> **🔧 수동 배포**: [수동 배포 가이드](manual-deployment.md) 참조

## 📋 사전 준비

### 1. 필요한 계정 및 도구

- ✅ **Google Cloud Platform 계정**
- ✅ **Vercel 계정** (GitHub 연동 권장)
- ✅ **GitHub 계정**
- ✅ **Google Cloud CLI** 설치
- ✅ **Vercel CLI** 설치

### 2. 환경 변수 준비

```bash
# 필수 환경 변수
export GCP_PROJECT_ID="your-project-id"
export GEMINI_API_KEY="your-gemini-api-key"
export GCS_BUCKET_NAME="your-bucket-name"
export NEXT_PUBLIC_API_URL="https://papercast-api-xxx-uc.a.run.app"  # 백엔드 배포 후 설정
```

## 🚀 GitHub Actions 자동 배포

### 📋 배포 흐름

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

### 1단계: GitHub Secrets 설정

#### 1.1 Google Cloud 설정

```bash
# Google Cloud CLI 로그인
gcloud auth login

# 프로젝트 설정
gcloud config set project $GCP_PROJECT_ID

# 필요한 API 활성화
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

#### 1.2 백엔드 배포

```bash
# 자동 배포 스크립트 실행
./scripts/deploy-backend.sh

# 또는 수동 배포
gcloud builds submit --tag gcr.io/$GCP_PROJECT_ID/papercast-api
gcloud run deploy papercast-api \
  --image gcr.io/$GCP_PROJECT_ID/papercast-api \
  --platform managed \
  --region asia-northeast3 \
  --allow-unauthenticated \
  --port 8001 \
  --memory 1Gi \
  --cpu 1 \
  --max-instances 10 \
  --set-env-vars GEMINI_API_KEY=$GEMINI_API_KEY \
  --set-env-vars GCS_BUCKET_NAME=$GCS_BUCKET_NAME
```

#### 1.3 백엔드 URL 확인

```bash
# 배포된 서비스 URL 확인
SERVICE_URL=$(gcloud run services describe papercast-api --region asia-northeast3 --format="value(status.url)")
echo "백엔드 URL: $SERVICE_URL"

# API 테스트
curl $SERVICE_URL/api/health
```

### 2단계: 프론트엔드 배포 (Vercel)

#### 2.1 Vercel 설정

```bash
# Vercel CLI 로그인
vercel login

# 환경 변수 설정
export NEXT_PUBLIC_API_URL="$SERVICE_URL"
```

#### 2.2 프론트엔드 배포

```bash
# 자동 배포 스크립트 실행
./scripts/deploy-frontend.sh

# 또는 수동 배포
cd frontend
vercel --prod
```

#### 2.3 Vercel 환경 변수 설정

Vercel Dashboard에서 환경 변수 설정:
1. Project → Settings → Environment Variables
2. `NEXT_PUBLIC_API_URL` = `https://papercast-api-xxx-uc.a.run.app`

### 3단계: GitHub Actions 설정

#### 3.1 GitHub Secrets 설정

Repository → Settings → Secrets and variables → Actions:

| Secret Name | Value |
|-------------|-------|
| `GEMINI_API_KEY` | your-gemini-api-key |
| `GCP_SERVICE_ACCOUNT_KEY` | base64-encoded-service-account-json |
| `GCS_BUCKET_NAME` | your-bucket-name |
| `SLACK_WEBHOOK_URL` | your-slack-webhook-url |
| `FRONTEND_URL` | https://papercast.vercel.app |

#### 3.2 GitHub Actions 워크플로우 확인

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
      🎧 지금 바로 들어보세요: ${{ secrets.FRONTEND_URL }}
      📖 아카이브: ${{ secrets.FRONTEND_URL }}/archive
```

## 🔧 배포 후 설정

### 1. 도메인 확인

- **백엔드**: `https://papercast-api-xxx-uc.a.run.app`
- **프론트엔드**: `https://papercast.vercel.app`
- **API 문서**: `https://papercast-api-xxx-uc.a.run.app/docs`

### 2. 기능 테스트

1. **홈페이지**: 프론트엔드 URL 접속
2. **API 연동**: 네트워크 탭에서 API 호출 확인
3. **에피소드 페이지**: `/episodes/2025-10-25` 접속
4. **논문 상세**: `/papers/2510.19600` 접속

### 3. 자동화 테스트

```bash
# GitHub Actions 수동 실행
# Repository → Actions → Daily Podcast Generation → Run workflow
```

## 🚨 트러블슈팅

### 1. 백엔드 배포 실패

**문제**: Cloud Run 배포 실패

**해결**:
```bash
# 로그 확인
gcloud run services describe papercast-api --region asia-northeast3

# 재배포
gcloud run deploy papercast-api --image gcr.io/$GCP_PROJECT_ID/papercast-api
```

### 2. 프론트엔드 API 연결 실패

**문제**: CORS 오류 또는 API 연결 실패

**해결**:
1. 백엔드 CORS 설정 확인
2. Vercel 환경 변수 확인
3. 네트워크 탭에서 실제 요청 URL 확인

### 3. 환경 변수 문제

**문제**: 환경 변수가 적용되지 않음

**해결**:
```bash
# Vercel 환경 변수 재설정
vercel env add NEXT_PUBLIC_API_URL production
vercel --prod
```

## 📝 배포 완료 체크리스트

- [ ] 백엔드 Cloud Run 배포 완료
- [ ] 백엔드 API 테스트 통과
- [ ] 프론트엔드 Vercel 배포 완료
- [ ] 프론트엔드-백엔드 연동 테스트 통과
- [ ] GitHub Actions Secrets 설정 완료
- [ ] Slack 알림 테스트 완료
- [ ] 전체 시스템 테스트 완료

## 🎉 배포 완료!

이제 PaperCast 서비스가 완전히 배포되었습니다:

- **프론트엔드**: `https://papercast.vercel.app`
- **백엔드**: `https://papercast-api-xxx-uc.a.run.app`
- **자동화**: 매일 6시 KST에 GitHub Actions 실행
- **알림**: Slack으로 성공/실패 알림

---

**다음 단계**: [모니터링 및 유지보수 가이드](monitoring-guide.md)
