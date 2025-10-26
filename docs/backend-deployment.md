# 백엔드 서버 배포 가이드 (Google Cloud Run)

## 🎯 개요

PaperCast의 FastAPI 백엔드를 Google Cloud Run에 배포하여 Vercel 프론트엔드와 연동합니다.

## 📋 사전 준비

### 1. Google Cloud Platform 설정

```bash
# Google Cloud CLI 설치 (이미 설치되어 있다면 스킵)
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# 프로젝트 설정
gcloud config set project YOUR_PROJECT_ID
gcloud auth login
```

### 2. 필요한 API 활성화

```bash
# Cloud Run API 활성화
gcloud services enable run.googleapis.com

# Container Registry API 활성화
gcloud services enable containerregistry.googleapis.com
```

## 🚀 배포 과정

### 1. Dockerfile 생성

프로젝트 루트에 `Dockerfile` 생성:

```dockerfile
# Dockerfile
FROM python:3.12-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 포트 설정
EXPOSE 8001

# 애플리케이션 실행
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8001"]
```

### 2. .dockerignore 생성

```dockerignore
# .dockerignore
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
.git/
.github/
.gitignore
README.md
docs/
tests/
frontend/
node_modules/
.next/
static-site/
data/
logs/
*.log
.DS_Store
Thumbs.db
```

### 3. Cloud Run 배포

```bash
# Docker 이미지 빌드 및 푸시
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/papercast-api

# Cloud Run에 배포
gcloud run deploy papercast-api \
  --image gcr.io/YOUR_PROJECT_ID/papercast-api \
  --platform managed \
  --region asia-northeast3 \
  --allow-unauthenticated \
  --port 8001 \
  --memory 1Gi \
  --cpu 1 \
  --max-instances 10 \
  --set-env-vars GEMINI_API_KEY=your_gemini_api_key \
  --set-env-vars GCS_BUCKET_NAME=your_bucket_name
```

### 4. 환경 변수 설정

Cloud Run 서비스에 환경 변수 설정:

```bash
# 환경 변수 업데이트
gcloud run services update papercast-api \
  --region asia-northeast3 \
  --set-env-vars GEMINI_API_KEY=your_gemini_api_key \
  --set-env-vars GCS_BUCKET_NAME=your_bucket_name \
  --set-env-vars GOOGLE_APPLICATION_CREDENTIALS=/app/credentials/service-account.json
```

### 5. 서비스 계정 키 설정

```bash
# 서비스 계정 키를 Cloud Run에 업로드
gcloud run services update papercast-api \
  --region asia-northeast3 \
  --update-secrets GCP_SERVICE_ACCOUNT_KEY=your-secret-name:latest
```

## 🔧 배포 후 설정

### 1. 도메인 확인

배포 완료 후 제공되는 URL 확인:
```
https://papercast-api-xxx-uc.a.run.app
```

### 2. API 테스트

```bash
# 헬스 체크
curl https://papercast-api-xxx-uc.a.run.app/api/health

# 에피소드 목록
curl https://papercast-api-xxx-uc.a.run.app/api/episodes
```

### 3. CORS 설정 확인

`api/main.py`에서 CORS 설정이 올바른지 확인:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # 로컬 개발
        "https://papercast.vercel.app",  # Vercel 배포 URL
        "https://*.vercel.app",  # Vercel 프리뷰 URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 🚨 트러블슈팅

### 1. 메모리 부족 오류
```bash
# 메모리 증가
gcloud run services update papercast-api \
  --region asia-northeast3 \
  --memory 2Gi
```

### 2. 타임아웃 오류
```bash
# 타임아웃 증가
gcloud run services update papercast-api \
  --region asia-northeast3 \
  --timeout 300
```

### 3. 환경 변수 확인
```bash
# 현재 환경 변수 확인
gcloud run services describe papercast-api \
  --region asia-northeast3 \
  --format="value(spec.template.spec.template.spec.containers[0].env[].name,spec.template.spec.template.spec.containers[0].env[].value)"
```

## 📝 배포 완료 후

1. **백엔드 URL 확인**: `https://papercast-api-xxx-uc.a.run.app`
2. **API 문서 확인**: `https://papercast-api-xxx-uc.a.run.app/docs`
3. **프론트엔드 환경 변수 설정**: `NEXT_PUBLIC_API_URL` 업데이트
4. **Vercel 배포**: 백엔드 URL을 사용하여 프론트엔드 배포

---

**다음 단계**: [Vercel 프론트엔드 배포 가이드](frontend-deployment.md)
