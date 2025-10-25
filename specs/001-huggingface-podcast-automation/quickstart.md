# 빠른 시작 가이드: PaperCast API

**날짜**: 2025-01-27  
**기능**: 001-huggingface-podcast-automation  

## 개요

이 가이드는 PaperCast API를 로컬에서 실행하고 테스트하는 방법을 안내합니다.

## 사전 요구사항

- Python 3.11+
- Node.js 18+ (프론트엔드 개발 시)
- Git

## 1. 기존 파이프라인 실행 (에피소드 생성)

```bash
# 저장소 클론 (이미 했다면 생략)
cd /home/hanseungsoo/project/Python_Study/papercast

# 가상환경 활성화
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows

# 환경 변수 확인
cat .env  # GEMINI_API_KEY, GOOGLE_APPLICATION_CREDENTIALS 등

# 파이프라인 실행 (에피소드 생성)
python run.py
# 또는
python src/main.py

# 결과 확인
ls data/podcasts/  # JSON 파일 생성 확인
ls static-site/    # 정적 사이트 생성 확인
```

## 2. API 서버 실행

### Option A: FastAPI 직접 실행

```bash
# 1. API 폴더로 이동
cd papercast

# 2. FastAPI 서버 실행
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# 3. API 문서 확인
# 브라우저에서 http://localhost:8000/docs 접속

# 4. API 테스트
curl http://localhost:8000/api/health
curl http://localhost:8000/api/episodes/latest
```

### Option B: Vercel Dev (프론트엔드 포함)

```bash
# 1. 프론트엔드 폴더로 이동
cd frontend

# 2. 의존성 설치
npm install

# 3. Vercel 개발 서버 실행
vercel dev

# 4. 접속
# 브라우저에서 http://localhost:3000 접속
```

## 3. API 엔드포인트 테스트

### 헬스 체크

```bash
curl http://localhost:8000/api/health
```

**응답**:
```json
{
  "status": "healthy",
  "timestamp": "2025-01-27T12:00:00Z",
  "version": "1.0.0"
}
```

### 최신 에피소드 조회

```bash
curl http://localhost:8000/api/episodes/latest
```

**응답**:
```json
{
  "id": "2025-01-27",
  "title": "Daily Papers - 2025-01-27",
  "publication_date": "2025-01-27",
  "audio_url": "https://storage.googleapis.com/...",
  "duration_seconds": 627,
  "papers": [
    {
      "id": "2510.19338",
      "title": "Every Attention Matters",
      "authors": ["John Doe", "Jane Smith"],
      "summary": "이 논문은...",
      "url": "https://huggingface.co/papers/2510.19338"
    }
    // 2개 더...
  ]
}
```

### 에피소드 목록 조회

```bash
curl "http://localhost:8000/api/episodes?limit=10&offset=0"
```

### 특정 에피소드 조회

```bash
curl http://localhost:8000/api/episodes/2025-01-27
```

## 4. 개발 서버 실행 (기존)

기존 static-site 개발 서버도 계속 사용 가능합니다:

```bash
# 방법 1: Python HTTP 서버
cd papercast
python -m http.server 8080 --directory static-site

# 방법 2: Live Reload 서버
python scripts/dev-server.py

# 방법 3: 셸 스크립트
bash scripts/dev-server.sh
```

## 5. 프로젝트 구조 이해

```
papercast/
├── src/                     # 기존 파이프라인 (변경 없음)
│   └── main.py             # python run.py로 실행
│
├── api/                     # 신규 API (이번에 추가)
│   ├── main.py             # FastAPI 앱
│   └── routes/             # API 라우터
│
├── data/podcasts/           # 파이프라인이 생성한 JSON
│   └── 2025-01-27.json     # API가 읽음
│
└── static-site/             # 파이프라인이 생성한 HTML
    └── index.html          # 기존 방식으로 서빙
```

## 6. 일반적인 작업 흐름

### 에피소드 생성 후 API 테스트

```bash
# 1. 새 에피소드 생성
python run.py

# 2. API 서버 시작 (이미 실행 중이면 자동 리로드됨)
python -m uvicorn api.main:app --reload

# 3. 최신 에피소드 확인
curl http://localhost:8000/api/episodes/latest

# 4. 프론트엔드에서 확인
# http://localhost:3000 접속
```

### API 코드 수정 후 테스트

```bash
# 1. API 코드 수정 (api/main.py 또는 api/routes/*.py)

# 2. 자동 리로드 확인 (--reload 옵션으로 실행한 경우)
# "Application startup complete" 메시지 확인

# 3. 변경사항 테스트
curl http://localhost:8000/api/...

# 4. API 문서 확인
# http://localhost:8000/docs에서 변경사항 확인
```

## 7. 환경 변수

### 필수 환경 변수

```bash
# .env 파일
GEMINI_API_KEY=your_key_here
GOOGLE_APPLICATION_CREDENTIALS=./credentials/service-account.json
GCS_BUCKET_NAME=your_bucket_name
```

### API 전용 환경 변수 (선택)

```bash
# API 서버 설정
API_HOST=0.0.0.0
API_PORT=8000
API_CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# 데이터 디렉토리
PODCASTS_DIR=data/podcasts

# 캐싱
CACHE_TTL_SECONDS=3600
```

## 8. 트러블슈팅

### 에피소드가 없다는 오류

```bash
# 문제: API가 404 반환
# 원인: data/podcasts/ 폴더가 비어있음

# 해결: 에피소드 생성
python run.py
```

### 포트가 이미 사용 중

```bash
# 문제: uvicorn: [Errno 48] Address already in use

# 해결 1: 다른 포트 사용
python -m uvicorn api.main:app --reload --port 8001

# 해결 2: 기존 프로세스 종료
lsof -ti:8000 | xargs kill -9  # Linux/Mac
```

### CORS 오류

```bash
# 문제: 프론트엔드에서 API 호출 시 CORS 오류

# 해결: api/main.py에서 CORS 설정 확인
# CORS_ORIGINS에 프론트엔드 URL 추가
```

## 9. 다음 단계

### 로컬 개발

1. API 엔드포인트 추가
2. 프론트엔드 컴포넌트 개발
3. 테스트 작성

### 배포 준비

1. Vercel 계정 설정
2. GitHub에 푸시
3. Vercel에서 자동 배포

---

**빠른 시작 상태**: ✅ 완료  
**API 실행 확인**: ✅ 준비됨  
**프론트엔드 연결**: ✅ 준비됨
