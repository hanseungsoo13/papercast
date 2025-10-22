# Quickstart: HuggingFace Podcast Automation

**Feature**: 001-huggingface-podcast-automation  
**Date**: 2025-01-27  
**Purpose**: 개발 환경 설정 및 로컬 테스트 가이드

## Prerequisites

### Required Accounts & Services

1. **Google Cloud Platform Account**
   - Gemini API 활성화
   - Text-to-Speech API 활성화
   - Cloud Storage API 활성화
   - Service Account 생성 및 JSON 키 다운로드

2. **GitHub Account**
   - Repository 생성 또는 포크
   - GitHub Actions 활성화
   - GitHub Pages 또는 Cloudflare Pages 설정

3. **Development Tools**
   - Python 3.11 이상
   - Git
   - pip 또는 poetry

---

## Local Setup

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/papercast.git
cd papercast
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**requirements.txt**:
```
huggingface-hub>=0.20.0
google-generativeai>=0.3.0
google-cloud-texttospeech>=2.16.0
google-cloud-storage>=2.14.0
requests>=2.31.0
python-dotenv>=1.0.0
pydantic>=2.5.0
tenacity>=8.2.0
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-mock>=3.12.0
```

### 4. Environment Configuration

`.env` 파일 생성:

```bash
# Google Cloud
GEMINI_API_KEY=your_gemini_api_key_here
GOOGLE_APPLICATION_CREDENTIALS=./service-account-key.json
GCS_BUCKET_NAME=papercast-podcasts

# GitHub (for Actions)
GITHUB_TOKEN=your_github_token_here

# Configuration
TZ=Asia/Seoul
LOG_LEVEL=INFO
```

### 5. Google Cloud Service Account Setup

1. GCP Console에서 Service Account 생성
2. 다음 역할 부여:
   - Cloud Storage Admin
   - Text-to-Speech Admin
3. JSON 키 다운로드 → `service-account-key.json`
4. 파일 위치를 `.env`의 `GOOGLE_APPLICATION_CREDENTIALS`에 설정

---

## Running Locally

### Test Individual Components

#### 1. Test Paper Collection

```bash
python -m src.services.collector
```

Expected Output:
```
INFO: Fetching trending papers from Hugging Face...
INFO: Found 10 papers
INFO: Selected top 3 papers:
  1. [2401.12345] Efficient Transformers with Dynamic Attention
  2. [2401.12346] Multimodal Learning for Visual Question Answering
  3. [2401.12347] Zero-Shot Image Classification with CLIP
```

#### 2. Test Summarization

```bash
python -m src.services.summarizer --paper-id 2401.12345
```

Expected Output:
```
INFO: Generating summary for paper 2401.12345...
INFO: Summary generated (450 characters)
Summary: 이 논문은 동적 어텐션 메커니즘을 사용하여...
```

#### 3. Test Text-to-Speech

```bash
python -m src.services.tts --text "테스트 음성입니다" --output test.mp3
```

Expected Output:
```
INFO: Generating audio...
INFO: Audio saved to test.mp3 (size: 15 KB, duration: 2s)
```

#### 4. Test GCS Upload

```bash
python -m src.services.uploader --file test.mp3 --destination test/test.mp3
```

Expected Output:
```
INFO: Uploading test.mp3 to gs://papercast-podcasts/test/test.mp3...
INFO: Upload successful
INFO: Public URL: https://storage.googleapis.com/papercast-podcasts/test/test.mp3
```

### Run Full Pipeline

```bash
python src/main.py
```

Expected Output:
```
INFO: Starting podcast generation pipeline...
INFO: Step 1/5: Collecting papers...
INFO: Collected 3 papers
INFO: Step 2/5: Generating summaries...
INFO: Summaries generated for 3 papers
INFO: Step 3/5: Converting to speech...
INFO: Audio generated (duration: 8m 15s)
INFO: Step 4/5: Uploading to GCS...
INFO: Upload successful: https://storage.googleapis.com/papercast-podcasts/2025-01-27/episode.mp3
INFO: Step 5/5: Generating static site...
INFO: Site generated at static-site/
INFO: Pipeline completed successfully!
```

---

## Testing

### Run Unit Tests

```bash
pytest tests/unit/ -v
```

### Run Integration Tests

```bash
pytest tests/integration/ -v
```

### Run Contract Tests

```bash
pytest tests/contract/ -v --api-key $GEMINI_API_KEY
```

### Run with Coverage

```bash
pytest --cov=src --cov-report=html --cov-report=term
```

Expected Coverage:
```
---------- coverage: platform linux, python 3.11.5 -----------
Name                          Stmts   Miss  Cover
-------------------------------------------------
src/models/__init__.py            10      0   100%
src/services/collector.py         45      3    93%
src/services/summarizer.py        38      2    95%
src/services/tts.py               42      1    98%
src/services/uploader.py          35      2    94%
src/utils/logger.py               20      0   100%
src/utils/retry.py                15      1    93%
src/main.py                       80      8    90%
-------------------------------------------------
TOTAL                            285     17    94%
```

---

## GitHub Actions Setup

### 1. Add Repository Secrets

GitHub Repository → Settings → Secrets and variables → Actions

추가할 Secrets:
- `GEMINI_API_KEY`: Gemini API 키
- `GCP_SERVICE_ACCOUNT_KEY`: Service Account JSON (base64 encoded)
- `GCS_BUCKET_NAME`: `papercast-podcasts`

### 2. Workflow Configuration

`.github/workflows/daily-podcast.yml`:

```yaml
name: Daily Podcast Generation

on:
  schedule:
    - cron: '0 21 * * *'  # 매일 UTC 21:00 = KST 06:00
  workflow_dispatch:  # 수동 실행

jobs:
  generate-podcast:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Configure GCP credentials
        run: |
          echo "${{ secrets.GCP_SERVICE_ACCOUNT_KEY }}" | base64 -d > service-account-key.json
      
      - name: Run podcast generation
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          GOOGLE_APPLICATION_CREDENTIALS: ./service-account-key.json
          GCS_BUCKET_NAME: ${{ secrets.GCS_BUCKET_NAME }}
        run: |
          python src/main.py
      
      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./static-site
```

### 3. Manual Trigger

GitHub Repository → Actions → Daily Podcast Generation → Run workflow

---

## Static Site Deployment

### Option 1: GitHub Pages

1. Repository Settings → Pages
2. Source: Deploy from a branch
3. Branch: `gh-pages` / `root`
4. URL: `https://yourusername.github.io/papercast/`

### Option 2: Cloudflare Pages

1. Cloudflare Dashboard → Pages → Create a project
2. Connect to GitHub repository
3. Build settings:
   - Framework preset: None
   - Build command: `(leave empty)`
   - Build output directory: `static-site`
4. URL: `https://papercast.pages.dev/`

---

## Troubleshooting

### Issue: "API key not valid"

**Solution**:
- Gemini API 키 확인: https://makersuite.google.com/app/apikey
- `.env` 파일에 올바르게 설정되었는지 확인

### Issue: "Permission denied" (GCS)

**Solution**:
- Service Account에 적절한 권한이 부여되었는지 확인
- `GOOGLE_APPLICATION_CREDENTIALS` 경로가 올바른지 확인

### Issue: "Rate limit exceeded"

**Solution**:
- API 호출 빈도 줄이기
- 재시도 메커니즘 활용 (자동 처리됨)
- 무료 티어 한도 확인

### Issue: GitHub Actions 실행 실패

**Solution**:
- Actions 로그에서 오류 확인
- Secrets가 올바르게 설정되었는지 확인
- Workflow 파일 YAML 문법 확인

---

## Validation Checklist

실행 전 확인사항:

- [ ] Python 3.11 이상 설치됨
- [ ] 모든 의존성 설치됨 (`pip list` 확인)
- [ ] `.env` 파일 설정 완료
- [ ] Service Account JSON 키 다운로드 및 설정
- [ ] GCS 버킷 생성됨 (`papercast-podcasts`)
- [ ] GitHub Secrets 설정 완료
- [ ] 로컬 테스트 통과 (`pytest`)
- [ ] GitHub Actions 워크플로우 파일 커밋

---

## Next Steps

1. ✅ Local setup 완료
2. ✅ 각 컴포넌트 개별 테스트
3. ✅ 전체 파이프라인 로컬 실행
4. ✅ GitHub Actions 설정
5. ⏭️ `/speckit.tasks` 명령어로 구현 작업 목록 생성
6. ⏭️ TDD로 기능 구현 시작

---

## Useful Commands

```bash
# 가상환경 활성화
source venv/bin/activate

# 의존성 업데이트
pip install -r requirements.txt --upgrade

# 코드 포맷팅
black src/ tests/

# 린팅
pylint src/

# 타입 체크
mypy src/

# 테스트 실행 (빠른 모드)
pytest -x --tb=short

# 로그 확인
tail -f logs/papercast.log

# GCS 버킷 내용 확인
gsutil ls gs://papercast-podcasts/

# 정적 사이트 로컬 미리보기
python -m http.server 8000 --directory static-site
# 브라우저에서 http://localhost:8000 접속
```

