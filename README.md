# PaperCast: AI 논문 팟캐스트 플랫폼

매일 아침 자동으로 Hugging Face 트렌딩 논문 Top 3를 수집하여 Gemini Pro로 요약하고, Google TTS로 음성 변환한 후 Google Cloud Storage에 업로드하여 웹 플랫폼에서 재생/다운로드 가능하게 만드는 풀스택 자동화 팟캐스트 서비스입니다.

## Features

- 🤖 **자동 수집**: 매일 아침 6시(KST) Hugging Face 트렌딩 논문 Top 3 자동 수집
- 📝 **AI 요약**: Google Gemini Pro를 사용한 한국어 요약 생성
- 📄 **3줄 요약**: 각 논문별 핵심 내용을 3줄로 간단 요약
- 🎙️ **TTS 변환**: Google Cloud Text-to-Speech로 고품질 음성 생성
- ☁️ **클라우드 저장**: Google Cloud Storage에 MP3 파일 업로드
- 🌐 **풀스택 웹 플랫폼**: FastAPI 백엔드 + Next.js 프론트엔드
- 📱 **반응형 UI**: 모바일/데스크톱 최적화된 사용자 인터페이스
- 🎵 **고급 오디오 플레이어**: 재생/일시정지, 볼륨 조절, 구간 이동
- 📄 **논문 뷰어**: ArXiv PDF 직접 링크 및 임베드 지원
- 🔗 **스마트 링크**: 논문 상세 페이지, 원문 링크, 에피소드 네비게이션
- 🔄 **완전 자동화**: GitHub Actions를 통한 무인 운영
- 📢 **Slack 알림**: 성공/실패 알림 및 웹페이지 링크 포함

## Quick Start

### 방법 1: GitHub Actions 자동 배포 (권장)

#### 1. GitHub Secrets 설정
Repository → Settings → Secrets and variables → Actions에서 다음 Secrets 설정:

| Secret Name | Description |
|-------------|-------------|
| `GEMINI_API_KEY` | Google Gemini API 키 |
| `GCP_SERVICE_ACCOUNT_KEY` | GCP Service Account JSON (base64) |
| `GCP_PROJECT_ID` | Google Cloud 프로젝트 ID |
| `GCS_BUCKET_NAME` | Google Cloud Storage 버킷 이름 |
| `DATABASE_URL` | PostgreSQL 데이터베이스 URL |
| `VERCEL_TOKEN` | Vercel API 토큰 |
| `VERCEL_ORG_ID` | Vercel 조직 ID |
| `VERCEL_PROJECT_ID` | Vercel 프로젝트 ID |
| `SLACK_WEBHOOK_URL` | Slack 웹훅 URL (선택사항) |

#### 2. 자동 배포 실행
- **매일 6시 KST**: 자동 실행
- **수동 실행**: Repository → Actions → Daily Podcast Generation → Run workflow

#### 3. 배포 결과 확인
- **프론트엔드**: `https://papercast.vercel.app`
- **백엔드**: `https://papercast-backend-xxx-uc.a.run.app`
- **API 문서**: `https://papercast-backend-xxx-uc.a.run.app/docs`

### 방법 2: 로컬 개발 환경

### Prerequisites

- Python 3.12 이상
- Node.js 18 이상
- [uv](https://docs.astral.sh/uv/) (Python 패키지 매니저)
- npm 또는 yarn (Node.js 패키지 매니저)
- Google Cloud Platform 계정
- GitHub 계정

### Installation

1. Clone the repository:
```bash
git clone https://github.com/hanseungsoo13/papercast.git
cd papercast
```

2. Install uv (if not already installed):
```bash
# Linux/Mac
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or via pip
pip install uv
```

3. Install dependencies with uv:
```bash
# 가상환경 자동 생성 및 의존성 설치
uv sync

# 또는 개발 의존성 포함 설치
uv sync --dev
```

4. Configure environment:

**프로젝트 루트에 `.env` 파일 생성**:
```bash
# .env 파일 생성
touch .env
```

**`.env` 파일에 다음 내용 입력**:
```bash
# Google Gemini API Key (필수)
# 발급: https://makersuite.google.com/app/apikey
GEMINI_API_KEY=your_gemini_api_key_here

# Google Cloud Service Account (필수)
# GCP Console에서 Service Account 생성 후 JSON 키 다운로드
GOOGLE_APPLICATION_CREDENTIALS=./credentials/service-account.json

# Google Cloud Storage Bucket Name (필수)
GCS_BUCKET_NAME=papercast-podcasts

# Optional: 기타 설정
TZ=Asia/Seoul
LOG_LEVEL=INFO
PAPERS_TO_FETCH=3
PODCAST_TITLE_PREFIX=Daily AI Papers
```

**Service Account JSON 키 저장**:
```bash
# credentials 디렉토리 생성
mkdir -p credentials

# GCP Console에서 다운로드한 JSON 키를 저장
# (예: service-account.json)
cp ~/Downloads/your-service-account-key.json credentials/service-account.json
```

5. **설정 검증** (권장):
```bash
# uv를 사용한 설정 검증
uv run python check_config.py

# 또는 직접 실행
python check_config.py
```

6. Run locally:

**풀스택 개발 서버 실행**:
```bash
# 통합 실행 스크립트 (권장)
./scripts/run-fullstack.sh

# 또는 개별 실행
# API 서버 (터미널 1)
uv run uvicorn api.main:app --host 0.0.0.0 --port 8001 --reload

# 프론트엔드 서버 (터미널 2)
cd frontend && npm run dev
```

**팟캐스트 생성 파이프라인 실행**:
```bash
# uv를 사용한 실행 (권장)
uv run python src/main.py

# 또는 직접 실행
uv run python -m src.main
```

> 💡 **개발 환경**: 풀스택 개발 시 `./scripts/run-fullstack.sh` 사용
> 💡 **팟캐스트 생성**: `uv run python src/main.py` 사용

## Testing

### Run Unit Tests
```bash
# uv를 사용한 단위 테스트 실행
uv run pytest tests/unit/ -v

# 커버리지 포함
uv run pytest tests/unit/ -v --cov=src --cov-report=html
```

### Run Contract Tests
```bash
# Contract 테스트 실행 (실제 API 호출 또는 Mock)
uv run pytest tests/contract/ -v --run-contract-tests

# Contract 테스트 스킵 (기본값)
uv run pytest tests/contract/ -v
```

### Run Integration Tests
```bash
# 통합 테스트 실행
uv run pytest tests/integration/ -v

# 전체 파이프라인 테스트만 실행
uv run pytest tests/integration/test_pipeline.py::TestPipelineIntegration::test_full_pipeline_end_to_end -v
```

### Run All Tests
```bash
# 모든 테스트 실행 (Contract 제외)
uv run pytest -v

# Contract 테스트 포함 모든 테스트
uv run pytest -v --run-contract-tests
```

### Test Coverage Report
테스트 실행 후 `htmlcov/index.html`을 브라우저로 열어 커버리지 리포트를 확인하세요.

## Configuration

> 💡 **자세한 설정 가이드**:
> - [API 키 설정 가이드](docs/API_SETUP.md) - Gemini API, Service Account 설정
> - [GCP 설정 가이드](docs/GCP_SETUP.md) - Text-to-Speech, Storage API 활성화 ⭐
> - [GitHub Actions 설정 가이드](docs/GITHUB_ACTIONS_SETUP.md) - 자동 실행 설정 ⭐⭐
> - [Slack 알림 설정 가이드](docs/SLACK_SETUP.md) - GitHub Actions → Slack 알림

### 빠른 설정

**자동 설정 스크립트 사용**:
```bash
# uv를 사용한 스크립트 실행
uv run ./setup_env.sh

# 또는 직접 실행
./setup_env.sh
```

이 스크립트는 `.env` 파일과 필요한 디렉토리를 자동으로 생성합니다.

### Required Environment Variables

- `GEMINI_API_KEY`: Google Gemini API key
- `GOOGLE_APPLICATION_CREDENTIALS`: Path to GCP service account JSON
- `GCS_BUCKET_NAME`: Google Cloud Storage bucket name

### Optional Variables

- `TZ`: Timezone (default: Asia/Seoul)
- `LOG_LEVEL`: Logging level (default: INFO)
- `PODCAST_TITLE_PREFIX`: Podcast title prefix
- `PAPERS_TO_FETCH`: Number of papers to fetch (default: 3)

## GitHub Actions Setup

### Required Secrets

GitHub Repository → Settings → Secrets and variables → Actions에서 다음 Secrets를 추가하세요:

| Secret Name | Description | How to Get |
|-------------|-------------|------------|
| `GEMINI_API_KEY` | Google Gemini API 키 | [Google AI Studio](https://makersuite.google.com/app/apikey)에서 발급 |
| `GCP_SERVICE_ACCOUNT_KEY` | GCP Service Account JSON (base64 encoded) | GCP Console에서 Service Account 생성 후 키 다운로드, `base64 -w 0 < key.json` 명령어로 인코딩 |
| `GCS_BUCKET_NAME` | Google Cloud Storage 버킷 이름 | 예: `papercast-podcasts` |
| `SLACK_WEBHOOK_URL` | Slack Webhook URL (선택사항) | [Slack API](https://api.slack.com/apps)에서 Incoming Webhook 생성 |

### Service Account 권한 설정

GCP Service Account에 다음 역할을 부여하세요:
- **Cloud Storage Admin**: MP3 파일 및 메타데이터 업로드
- **Cloud Text-to-Speech Admin**: 음성 변환

### 워크플로우 실행

1. **자동 실행**: 매일 오전 6시 (KST)에 자동으로 실행됩니다
2. **수동 실행**: 
   - GitHub Repository → Actions → Daily Podcast Generation
   - "Run workflow" 버튼 클릭

### 트러블슈팅

#### Secrets 설정 확인
```bash
# GitHub CLI를 사용하는 경우
gh secret list
```

#### 워크플로우 로그 확인
- Actions 탭에서 실패한 워크플로우 클릭
- 각 단계별 로그 확인

#### 일반적인 문제

1. **"API key not valid"**
   - Gemini API 키가 올바른지 확인
   - API 키 제한 설정 확인

2. **"Permission denied" (GCS)**
   - Service Account 권한 확인
   - 버킷 이름이 올바른지 확인

3. **"Quota exceeded"**
   - API 할당량 확인
   - 무료 티어 한도 확인

## Development

### Running Tests

```bash
# All tests with uv
uv run pytest

# Specific test types
uv run pytest tests/unit/ -m unit
uv run pytest tests/integration/ -m integration
uv run pytest tests/contract/ -m contract

# With coverage
uv run pytest --cov=src --cov-report=html
```

### Code Quality

```bash
# Format code with uv
uv run black src/ tests/

# Lint with uv
uv run pylint src/

# Type check with uv
uv run mypy src/

# 또는 uv를 사용한 개발 도구 실행
uv run --group dev black src/ tests/
uv run --group dev pylint src/
uv run --group dev mypy src/
```

## Project Structure

```
papercast/
├── src/                    # Core Python modules
│   ├── models/            # Data models (Paper, Podcast, ProcessingLog)
│   ├── services/          # Core services
│   │   ├── collector.py   # Hugging Face paper collection
│   │   ├── summarizer.py  # Gemini Pro summarization
│   │   ├── tts.py        # Google TTS conversion
│   │   ├── uploader.py   # GCS upload
│   │   └── generator.py  # Static site generation
│   ├── utils/             # Utilities (logger, retry, config)
│   └── main.py           # Main pipeline
├── api/                   # FastAPI backend
│   ├── routes/           # API endpoints
│   │   ├── health.py     # Health check endpoints
│   │   └── episodes.py   # Episode endpoints
│   ├── schemas.py        # Pydantic response schemas
│   ├── repository.py     # Data access layer
│   ├── dependencies.py   # FastAPI dependencies
│   └── main.py          # FastAPI app
├── frontend/              # Next.js frontend
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── pages/        # Next.js pages
│   │   ├── services/     # API client
│   │   └── styles/       # CSS styles
│   ├── package.json      # Node.js dependencies
│   └── next.config.js    # Next.js configuration
├── tests/                 # Test suite
│   ├── unit/            # Unit tests
│   ├── integration/     # Integration tests
│   ├── contract/        # Contract tests
│   └── api/             # API tests
├── scripts/              # Utility scripts
│   ├── run-fullstack.sh # Full-stack development server
│   ├── run-api.sh       # API server only
│   └── dev-regenerate.py # Site regeneration
├── .github/workflows/
│   └── daily-podcast.yml # GitHub Actions workflow
├── static-site/          # Generated static site
└── data/
    ├── papers/          # Collected papers
    └── podcasts/        # Generated podcasts
```

## License

MIT

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## Documentation

- [Implementation Plan](specs/001-huggingface-podcast-automation/plan.md)
- [Data Model](specs/001-huggingface-podcast-automation/data-model.md)
- [Quickstart Guide](specs/001-huggingface-podcast-automation/quickstart.md)
- [Task List](specs/001-huggingface-podcast-automation/tasks.md)