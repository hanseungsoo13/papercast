# 🛠️ PaperCast 개발자 가이드

> **목적**: 이 프로젝트의 아키텍처, 설계 원칙, 개발 방법을 이해하기 위한 개발자 명세서

## 📋 목차

1. [프로젝트 개요](#프로젝트-개요)
2. [아키텍처](#아키텍처)
3. [데이터 흐름](#데이터-흐름)
4. [핵심 컴포넌트](#핵심-컴포넌트)
5. [개발 환경 설정](#개발-환경-설정)
6. [테스트 전략](#테스트-전략)
7. [배포 프로세스](#배포-프로세스)
8. [유지보수 가이드](#유지보수-가이드)

---

## 🎯 프로젝트 개요

### 목적
매일 Hugging Face 트렌딩 논문 Top 3를 자동으로 수집하여 한국어로 요약하고, TTS로 변환한 후 웹에서 재생 가능한 팟캐스트로 제공

### 핵심 기능
- **자동화**: GitHub Actions를 통한 매일 자동 실행
- **AI 처리**: Gemini Pro 요약 + Google TTS 음성 변환
- **웹 플랫폼**: 정적 사이트 생성 + GitHub Pages 호스팅
- **사용자 경험**: 오디오 플레이어 + PDF 뷰어 통합

### 기술 스택 요약
- **백엔드**: Python 3.12+ (FastAPI)
- **프론트엔드**: Next.js 14 + React 18 + TypeScript
- **AI/ML**: Google Gemini Pro, Google Cloud TTS
- **스토리지**: Google Cloud Storage
- **호스팅**: Vercel (프론트엔드), Google Cloud Run (백엔드)
- **자동화**: GitHub Actions
- **데이터**: JSON 파일 기반 (NoSQL)

---

## 🏗️ 아키텍처

### 전체 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                    GitHub Actions (스케줄러)                  │
│                    매일 6AM KST 자동 실행                     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  PodcastPipeline (main.py)                   │
│                      6단계 파이프라인                         │
└─────────────────────────────────────────────────────────────┘
         │
         ├─ Step 1: PaperCollector      (논문 수집)
         │          ↓ Hugging Face 웹 스크래핑
         │          ↓ BeautifulSoup 파싱
         │
         ├─ Step 2: Summarizer          (요약 생성)
         │          ↓ Gemini Pro API 호출
         │          ↓ 한국어 요약 (200자 이내)
         │
         ├─ Step 3: TTSConverter         (음성 변환)
         │          ↓ Google Cloud TTS API
         │          ↓ MP3 파일 생성 (로컬)
         │
         ├─ Step 4: GCSUploader          (클라우드 업로드)
         │          ↓ Google Cloud Storage
         │          ↓ 공개 URL 생성
         │
         ├─ Step 5: Podcast.save()       (메타데이터 저장)
         │          ↓ data/podcasts/{date}.json
         │
         └─ Step 6: StaticSiteGenerator  (웹사이트 생성)
                    ↓ HTML/CSS/JS 생성
                    ↓ static-site/ 디렉토리
                    ↓ GitHub Pages 자동 배포
```

### 풀스택 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                        │
│  • React 18 + TypeScript                                    │
│  • Server-Side Rendering                                    │
│  • API 프록시 (FastAPI 연동)                                │
│  • 반응형 UI + 오디오 플레이어                               │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    API Layer (FastAPI)                       │
│  • RESTful API 엔드포인트                                    │
│  • Pydantic 데이터 검증                                      │
│  • JSON 파일 기반 데이터 저장소                              │
│  • CORS 설정                                                │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  Core Pipeline (Python)                     │
│  • 논문 수집 + AI 요약 + TTS 변환                            │
│  • Google Cloud Storage 업로드                              │
│  • 정적 사이트 생성                                          │
└─────────────────────────────────────────────────────────────┘
```

### 컴포넌트 다이어그램

```
papercast/
├── src/                       # Core Python modules
│   ├── models/               # 데이터 모델 (Pydantic)
│   │   ├── paper.py          # Paper: 논문 정보
│   │   ├── podcast.py        # Podcast: 팟캐스트 메타데이터
│   │   └── processing_log.py # ProcessingLog: 처리 로그
│   ├── services/             # 비즈니스 로직
│   │   ├── collector.py      # 논문 수집 (웹 스크래핑)
│   │   ├── summarizer.py     # AI 요약 (Gemini Pro)
│   │   ├── tts.py           # 음성 변환 (Google TTS)
│   │   ├── uploader.py      # 클라우드 업로드 (GCS)
│   │   └── generator.py      # 정적 사이트 생성
│   ├── utils/                # 유틸리티
│   │   ├── logger.py         # 로깅 설정
│   │   ├── config.py         # 환경 변수 관리
│   │   └── retry.py          # 재시도 로직
│   └── main.py               # 파이프라인 오케스트레이션
├── api/                      # FastAPI backend
│   ├── routes/              # API 엔드포인트
│   │   ├── health.py        # 헬스 체크
│   │   └── episodes.py      # 에피소드 API
│   ├── schemas.py           # Pydantic 응답 스키마
│   ├── repository.py        # 데이터 접근 레이어
│   ├── dependencies.py      # FastAPI 의존성
│   └── main.py              # FastAPI 앱
├── frontend/                 # Next.js frontend
│   ├── src/
│   │   ├── components/       # React 컴포넌트
│   │   │   ├── AudioPlayer.tsx
│   │   │   ├── EpisodeCard.tsx
│   │   │   └── LoadingSpinner.tsx
│   │   ├── pages/           # Next.js 페이지
│   │   │   └── index.tsx    # 홈페이지
│   │   ├── services/        # API 클라이언트
│   │   │   ├── api.ts       # API 서비스
│   │   │   └── types.ts     # TypeScript 타입
│   │   └── styles/          # CSS 스타일
│   ├── package.json         # Node.js 의존성
│   └── next.config.js       # Next.js 설정
└── tests/                   # 테스트 스위트
    ├── unit/               # 단위 테스트
    ├── integration/        # 통합 테스트
    ├── contract/           # 계약 테스트
    └── api/                # API 테스트
```

---

## 🔄 데이터 흐름

### Step-by-Step 데이터 변환

#### 1. 논문 수집 (Raw HTML → Paper 객체)

```python
# Input: Hugging Face HTML
<article data-paper-id="2510.19338">
    <h3>Every Attention Matters</h3>
    <div class="authors">
        <a>Author 1</a>, <a>Author 2</a>
    </div>
    <p class="abstract">We propose...</p>
</article>

# Process: collector.py
def _parse_paper_from_html(self, article_elem) -> Paper:
    title = article_elem.find('h3').text.strip()
    authors = [a.text.strip() for a in article_elem.find_all('a')]
    abstract = article_elem.find('p', class_='abstract').text.strip()
    arxiv_id = self._extract_arxiv_id(article_elem)
    
    return Paper(
        id=arxiv_id,
        title=title,
        authors=authors,
        abstract=abstract,
        arxiv_id=arxiv_id,
        url=f"https://huggingface.co/papers/{arxiv_id}"
    )

# Output: Paper 객체
Paper(
    id="2510.19338",
    title="Every Attention Matters",
    authors=["Author 1", "Author 2"],
    abstract="We propose...",
    arxiv_id="2510.19338",
    url="https://huggingface.co/papers/2510.19338"
)
```

#### 2. 요약 생성 (Paper → Paper + Summary)

```python
# Input: Paper 객체 (요약 없음)
paper = Paper(title="...", abstract="...")

# Process: summarizer.py
prompt = f"""
다음 논문을 200자 이내로 한국어로 요약하세요:
제목: {paper.title}
초록: {paper.abstract}
"""

response = genai.GenerativeModel('gemini-pro').generate_content(prompt)
summary = response.text[:200]

# Output: Paper + summary
paper.summary = "이 논문은 대규모 언어 모델의 추론 성능을..."
```

#### 3. TTS 변환 (Text → MP3)

```python
# Input: 논문 요약 텍스트
script = f"""
오늘의 첫 번째 논문은 {paper.title}입니다.
{paper.summary}
"""

# Process: tts.py
synthesis_input = texttospeech.SynthesisInput(text=script)
voice = texttospeech.VoiceSelectionParams(
    language_code="ko-KR",
    name="ko-KR-Neural2-A"
)
audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.MP3
)

response = tts_client.synthesize_speech(
    input=synthesis_input,
    voice=voice,
    audio_config=audio_config
)

# Output: MP3 파일
with open("data/audio/2025-10-25/episode.mp3", "wb") as f:
    f.write(response.audio_content)
```

#### 4. 클라우드 업로드 (Local MP3 → Public URL)

```python
# Input: 로컬 MP3 파일
local_path = "data/audio/2025-10-25/episode.mp3"

# Process: uploader.py
blob_name = "2025-10-25/episode.mp3"
bucket = storage_client.bucket(bucket_name)
blob = bucket.blob(blob_name)
blob.upload_from_filename(local_path)
blob.make_public()

# Output: 공개 URL
public_url = f"https://storage.googleapis.com/{bucket_name}/{blob_name}"
# "https://storage.googleapis.com/papers_ethan/2025-10-25/episode.mp3"
```

#### 5. 메타데이터 저장 (Podcast → JSON)

```python
# Input: Podcast 객체
podcast = Podcast(
    id="2025-10-25",
    title="Daily AI Papers - 2025-10-25",
    papers=[paper1, paper2, paper3],
    audio_file_path="https://storage.googleapis.com/.../episode.mp3",
    audio_duration=627,
    audio_size=5026816
)

# Process: podcast.save()
podcast_dict = podcast.dict()
with open(f"data/podcasts/{podcast.id}.json", "w") as f:
    json.dump(podcast_dict, f, ensure_ascii=False, indent=2)

# Output: JSON 파일
{
  "id": "2025-10-25",
  "audio_file_path": "https://storage.googleapis.com/.../episode.mp3",
  "papers": [...]
}
```

#### 6. 웹사이트 생성 (JSON → HTML)

```python
# Input: Podcast JSON 파일들
podcasts = load_podcasts_from_json("data/podcasts/")

# Process: generator.py
def _generate_episode_page(self, podcast):
    html = f'''
    <audio controls>
        <source src="{podcast.audio_file_path}">
    </audio>
    
    {self._generate_paper_cards(podcast.papers)}
    '''
    
    with open(f"static-site/episodes/{podcast.id}.html", "w") as f:
        f.write(html)

# Output: 정적 HTML 파일
static-site/
├── index.html
├── episodes/
│   └── 2025-10-25.html
└── assets/
    ├── css/styles.css
    └── js/script.js
```

---

## 🔧 핵심 컴포넌트 상세

### 1. PaperCollector (논문 수집기)

**파일**: `src/services/collector.py`

**역할**: Hugging Face 논문 페이지에서 Top 3 논문 스크래핑

**핵심 로직**:
```python
class PaperCollector:
    def fetch_papers(self, target_date: str = None) -> List[Paper]:
        """어제 날짜의 Top 3 논문 수집"""
        
        # 1. 날짜 계산 (어제)
        date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        
        # 2. Hugging Face 페이지 요청
        url = f"https://huggingface.co/papers/date/{date}"
        response = requests.get(url)
        
        # 3. HTML 파싱
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = soup.find_all('article', limit=3)
        
        # 4. Paper 객체 생성
        papers = []
        for article in articles:
            paper = self._parse_paper_from_html(article)
            papers.append(paper)
        
        return papers
    
    def _extract_arxiv_id(self, article) -> str:
        """ArXiv ID 추출 (예: 2510.19338)"""
        # data-paper-id 속성에서 추출
        return article.get('data-paper-id', '')
```

**에러 처리**:
- `@retry(max_attempts=3)`: 네트워크 오류 시 재시도
- BeautifulSoup 파싱 실패 시 로깅 및 스킵

---

### 2. Summarizer (요약 생성기)

**파일**: `src/services/summarizer.py`

**역할**: Gemini Pro를 사용한 한국어 요약 생성

**핵심 로직**:
```python
class Summarizer:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    
    def summarize_paper(self, paper: Paper) -> str:
        """논문을 200자 이내로 요약"""
        
        prompt = f"""
        다음 AI 논문을 200자 이내로 한국어로 요약해주세요:
        
        제목: {paper.title}
        저자: {', '.join(paper.authors[:3])}
        초록: {paper.abstract[:500]}
        
        요약 형식:
        - 핵심 내용
        - 연구 방법
        - 기대 효과
        """
        
        response = self.model.generate_content(prompt)
        summary = response.text.strip()
        
        # 길이 제한 (200자)
        if len(summary) > 200:
            summary = summary[:197] + "..."
        
        return summary
```

**프롬프트 엔지니어링**:
- 명확한 지시사항 (한국어, 200자 제한)
- 구조화된 출력 요청 (핵심 내용, 방법, 효과)
- 컨텍스트 제한 (초록 500자까지만 사용)

---

### 3. TTSConverter (음성 변환기)

**파일**: `src/services/tts.py`

**역할**: Google Cloud TTS를 사용한 MP3 생성

**핵심 로직**:
```python
class TTSConverter:
    def __init__(self, credentials_path: str):
        self.client = texttospeech.TextToSpeechClient.from_service_account_json(
            credentials_path
        )
    
    def convert_to_speech(self, papers: List[Paper]) -> str:
        """요약문을 음성으로 변환"""
        
        # 1. 스크립트 생성
        script = self._generate_script(papers)
        
        # 2. TTS 요청 구성
        synthesis_input = texttospeech.SynthesisInput(text=script)
        voice = texttospeech.VoiceSelectionParams(
            language_code="ko-KR",
            name="ko-KR-Neural2-A",  # Neural2: 자연스러운 음성
            ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=1.0,  # 일반 속도
            pitch=0.0           # 기본 피치
        )
        
        # 3. 음성 합성
        response = self.client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )
        
        # 4. MP3 저장
        output_path = f"data/audio/{date}/episode.mp3"
        with open(output_path, "wb") as f:
            f.write(response.audio_content)
        
        return output_path
    
    def _generate_script(self, papers: List[Paper]) -> str:
        """자연스러운 팟캐스트 스크립트 생성"""
        script = "안녕하세요, 오늘의 AI 논문 팟캐스트입니다.\n\n"
        
        for i, paper in enumerate(papers, 1):
            script += f"{i}번째 논문은 {paper.title}입니다. "
            script += f"{paper.summary}\n\n"
        
        script += "오늘의 AI 논문 소개를 마치겠습니다. 감사합니다."
        return script
```

**최적화**:
- Neural2 보이스 사용 (더 자연스러운 음성)
- 적절한 속도와 피치 설정
- 문장 사이 자연스러운 pause

---

### 4. StaticSiteGenerator (사이트 생성기)

**파일**: `src/services/generator.py`

**역할**: 정적 HTML/CSS/JS 웹사이트 생성

**핵심 로직**:
```python
class StaticSiteGenerator:
    def generate_site(self, podcasts: List[Podcast]):
        """전체 사이트 생성"""
        
        # 1. 디렉토리 생성
        self._create_directories()
        
        # 2. 메인 페이지 (에피소드 목록)
        self._generate_index_page(podcasts)
        
        # 3. 개별 에피소드 페이지
        for podcast in podcasts:
            self._generate_episode_page(podcast)
        
        # 4. JSON API
        self._generate_podcast_index(podcasts)
        
        # 5. CSS/JS
        self._generate_styles()
        self._generate_scripts()
    
    def _generate_episode_page(self, podcast: Podcast):
        """에피소드 상세 페이지 생성"""
        
        # 오디오 플레이어 HTML
        audio_html = f'''
        <audio id="podcast-audio" controls>
            <source src="{podcast.audio_file_path}" type="audio/mpeg">
        </audio>
        '''
        
        # 논문 카드 HTML
        papers_html = self._generate_paper_cards(podcast.papers)
        
        # Split View HTML (PDF 뷰어)
        split_view_html = self._generate_split_view()
        
        # 전체 HTML 조합
        html = self._build_html_template(
            title=podcast.title,
            audio=audio_html,
            papers=papers_html,
            split_view=split_view_html
        )
        
        # 파일 저장
        output_path = self.output_dir / f"episodes/{podcast.id}.html"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)
```

**중요 설계 결정**:
1. **완전 정적**: 백엔드 서버 불필요
2. **CDN 친화적**: 모든 리소스가 정적 파일
3. **오프라인 호환**: Service Worker 추가 가능
4. **SEO 최적화**: 메타 태그 포함

---

## 💻 개발 환경 설정

### 로컬 개발 환경

#### 1. 프로젝트 클론 및 의존성 설치

```bash
# 1. 저장소 클론
git clone https://github.com/hanseungsoo13/papercast.git
cd papercast

# 2. Python 가상환경 생성 (Python 3.11+)
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows

# 3. 의존성 설치
pip install -r requirements.txt

# 또는 uv 사용 (권장)
pip install uv
uv sync
```

#### 2. 환경 변수 설정

```bash
# .env 파일 생성
cat > .env << EOF
# Gemini API Key
GEMINI_API_KEY=your_gemini_api_key_here

# Google Cloud 인증
GOOGLE_APPLICATION_CREDENTIALS=./credentials/service-account.json

# GCS 버킷
GCS_BUCKET_NAME=papercast-podcasts

# 기타 설정
TZ=Asia/Seoul
LOG_LEVEL=INFO
EOF

# GCP 서비스 계정 키 저장
mkdir -p credentials
# service-account.json 파일을 credentials/ 폴더에 저장
```

#### 3. 개발 서버 실행

```bash
# 방법 1: 전체 파이프라인 실행 (처음 한 번)
python run.py

# 방법 2: 개발 서버만 실행
python dev_server.py

# 방법 3: 사이트 재생성 + 서버 실행
python scripts/dev-regenerate.py
python dev_server.py
```

### IDE 설정 (VSCode/Cursor)

**.vscode/settings.json**:
```json
{
  "python.defaultInterpreterPath": ".venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "python.testing.pytestEnabled": true,
  "python.testing.unittestEnabled": false,
  "editor.formatOnSave": true,
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true,
    ".pytest_cache": true
  }
}
```

---

## 🧪 테스트 전략

### 테스트 계층

```
tests/
├── unit/                      # 단위 테스트 (개별 함수/클래스)
│   ├── test_collector.py     # PaperCollector 테스트
│   ├── test_summarizer.py    # Summarizer 테스트
│   ├── test_tts.py            # TTSConverter 테스트
│   └── test_generator.py     # StaticSiteGenerator 테스트
│
├── integration/               # 통합 테스트 (컴포넌트 간 상호작용)
│   └── test_pipeline.py      # 전체 파이프라인 테스트
│
├── contract/                  # Contract 테스트 (외부 API)
│   ├── test_gemini_api.py    # Gemini Pro API 테스트
│   ├── test_google_tts.py    # Google TTS API 테스트
│   └── test_gcs.py            # GCS API 테스트
│
└── e2e/                       # E2E 테스트 (웹사이트)
    └── test_website.py        # 생성된 웹사이트 테스트
```

### 테스트 실행

```bash
# 전체 테스트
pytest

# 단위 테스트만
pytest tests/unit/ -v

# 커버리지 포함
pytest --cov=src --cov-report=html

# 특정 테스트 파일
pytest tests/unit/test_collector.py -v

# 특정 테스트 함수
pytest tests/unit/test_collector.py::test_fetch_papers -v
```

### Mock 사용 예시

```python
# tests/unit/test_collector.py
from unittest.mock import Mock, patch
import pytest

@patch('requests.get')
def test_fetch_papers_success(mock_get):
    """논문 수집 성공 테스트"""
    
    # Mock HTML 응답 설정
    mock_response = Mock()
    mock_response.text = """
    <article data-paper-id="2510.19338">
        <h3>Test Paper Title</h3>
        <div class="authors">
            <a>Author One</a>
            <a>Author Two</a>
        </div>
        <p class="abstract">This is a test abstract.</p>
    </article>
    """
    mock_get.return_value = mock_response
    
    # 테스트 실행
    collector = PaperCollector()
    papers = collector.fetch_papers("2025-10-25")
    
    # 검증
    assert len(papers) == 1
    assert papers[0].title == "Test Paper Title"
    assert len(papers[0].authors) == 2
```

---

## 🚀 배포 프로세스

### GitHub Actions 워크플로우

**파일**: `.github/workflows/daily-podcast.yml`

```yaml
name: Daily Podcast Generation

on:
  schedule:
    - cron: '0 21 * * *'  # 매일 6AM KST
  workflow_dispatch:

jobs:
  generate-and-deploy:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Setup credentials
        env:
          GCP_KEY: ${{ secrets.GCP_SERVICE_ACCOUNT_KEY }}
        run: |
          echo "$GCP_KEY" | base64 -d > credentials/service-account.json
      
      - name: Run pipeline
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          GOOGLE_APPLICATION_CREDENTIALS: credentials/service-account.json
          GCS_BUCKET_NAME: ${{ secrets.GCS_BUCKET_NAME }}
        run: python run.py
      
      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./static-site
          publish_branch: gh-pages
```

### 배포 흐름

```
1. GitHub Actions 트리거 (매일 6AM)
   ↓
2. 전체 파이프라인 실행 (논문 수집 → 사이트 생성)
   ↓
3. static-site/ 디렉토리 생성
   ↓
4. gh-pages 브랜치에 자동 푸시
   ↓
5. GitHub Pages가 자동 배포
   ↓
6. https://username.github.io/papercast 에서 접근 가능
```

---

## 🔧 유지보수 가이드

### 로그 확인

```bash
# 로컬 로그
cat data/logs/pipeline_YYYYMMDD.log

# GitHub Actions 로그
# Repository → Actions → 워크플로우 선택 → 로그 확인
```

### 에러 대응

#### 1. 논문 수집 실패
```python
# collector.py에서 에러 발생 시
# 원인: Hugging Face HTML 구조 변경
# 해결: HTML 셀렉터 업데이트

# 디버깅
response = requests.get(url)
with open('debug.html', 'w') as f:
    f.write(response.text)
# HTML 구조 확인 후 파싱 로직 수정
```

#### 2. API 할당량 초과
```bash
# Gemini Pro: 60 requests/minute
# Google TTS: 100 requests/minute
# GCS: 5000 writes/day

# 해결: 재시도 로직 + 백오프
@retry(max_attempts=3, backoff_factor=2)
def api_call():
    pass
```

#### 3. 사이트 생성 실패
```bash
# 원인: JSON 파일 손상
# 해결: 백업에서 복구

cp data/podcasts/2025-10-25.json.backup \
   data/podcasts/2025-10-25.json

python scripts/dev-regenerate.py
```

### 성능 최적화

#### 1. 병렬 처리
```python
# 현재: 순차 처리
for paper in papers:
    summary = summarizer.summarize(paper)

# 개선: 병렬 처리
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=3) as executor:
    summaries = list(executor.map(summarizer.summarize, papers))
```

#### 2. 캐싱
```python
# 당일 데이터 캐싱
import functools

@functools.lru_cache(maxsize=128)
def fetch_papers(date: str):
    # 같은 날짜 요청 시 캐시 사용
    pass
```

---

## 📚 추가 리소스

### 코드 스타일 가이드
- PEP 8 준수
- Black 포맷터 사용
- 타입 힌트 권장

### Git 커밋 컨벤션
```
feat: 새 기능 추가
fix: 버그 수정
docs: 문서 변경
style: 코드 포맷팅
refactor: 리팩토링
test: 테스트 추가/수정
chore: 빌드/설정 변경
```

### 참고 문서
- [TECHNICAL_STACK.md](TECHNICAL_STACK.md) - 기술 스택 상세
- [docs/deployment.md](docs/deployment.md) - 배포 가이드
- [docs/testing.md](docs/testing.md) - 테스트 가이드

---

## 🤝 기여하기

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

**마지막 업데이트**: 2025-10-25
**버전**: 1.0.0

