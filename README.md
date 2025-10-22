# PaperCast: HuggingFace Podcast Automation

매일 아침 자동으로 Hugging Face 트렌딩 논문 Top 3를 수집하여 Gemini Pro로 요약하고, Google TTS로 음성 변환한 후 Google Cloud Storage에 업로드하여 공유 플랫폼에서 재생/다운로드 가능하게 만드는 자동화 팟캐스트 서비스입니다.

## Features

- 🤖 **자동 수집**: 매일 아침 6시(KST) Hugging Face 트렌딩 논문 Top 3 자동 수집
- 📝 **AI 요약**: Google Gemini Pro를 사용한 한국어 요약 생성
- 🎙️ **TTS 변환**: Google Cloud Text-to-Speech로 고품질 음성 생성
- ☁️ **클라우드 저장**: Google Cloud Storage에 MP3 파일 업로드
- 🌐 **웹 플랫폼**: GitHub Pages를 통한 팟캐스트 재생/다운로드
- 🔄 **완전 자동화**: GitHub Actions를 통한 무인 운영

## Quick Start

### Prerequisites

- Python 3.12 이상
- [uv](https://docs.astral.sh/uv/) (Python 패키지 매니저)
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
```bash
# uv를 사용한 실행 (권장)
uv run python run.py

# 또는 uv run으로 모듈 실행
uv run python -m src.main

# 또는 직접 실행
uv run python src/main.py

# 가상환경 활성화 후 실행 (선택사항)
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows
python run.py
```

> 💡 **권장**: `uv run python run.py` 사용 (가상환경 자동 관리)

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
src/
├── models/              # Data models (Paper, Podcast, ProcessingLog)
├── services/            # Core services
│   ├── collector.py     # Hugging Face paper collection
│   ├── summarizer.py    # Gemini Pro summarization
│   ├── tts.py           # Google TTS conversion
│   ├── uploader.py      # GCS upload
│   └── generator.py     # Static site generation
├── utils/               # Utilities (logger, retry, config)
└── main.py              # Main pipeline

tests/
├── unit/                # Unit tests
├── integration/         # Integration tests
└── contract/            # Contract tests

.github/workflows/
└── daily-podcast.yml    # GitHub Actions workflow

static-site/             # Generated static site
└── podcasts/            # Podcast metadata
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

