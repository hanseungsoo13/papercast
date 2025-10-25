# 🔧 PaperCast 기술 스택 & 배경지식

> **목적**: 이 프로젝트에서 사용된 기술들의 상세 설명과 이해에 필요한 배경지식 정리

## 📋 목차

1. [기술 스택 개요](#기술-스택-개요)
2. [Python 생태계](#python-생태계)
3. [AI/ML 서비스](#aiml-서비스)
4. [클라우드 서비스](#클라우드-서비스)
5. [웹 기술](#웹-기술)
6. [자동화 & CI/CD](#자동화--cicd)
7. [개발 도구](#개발-도구)
8. [아키텍처 패턴](#아키텍처-패턴)

---

## 🎯 기술 스택 개요

### Full Stack Diagram

```
┌────────────────────────────────────────────────────────────┐
│                      Frontend                               │
│  • Vanilla JavaScript (ES6+)                               │
│  • HTML5 + CSS3                                            │
│  • Responsive Design                                        │
│  • No Framework (정적 사이트)                               │
└────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────────┐
│                     Backend/Logic                           │
│  • Python 3.11+                                            │
│  • Pydantic (데이터 검증)                                   │
│  • BeautifulSoup4 (웹 스크래핑)                            │
│  • Requests (HTTP 클라이언트)                               │
└────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────────┐
│                    AI/ML Services                           │
│  • Google Gemini Pro (텍스트 요약)                         │
│  • Google Cloud TTS (음성 합성)                            │
└────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────────┐
│                  Cloud Infrastructure                       │
│  • Google Cloud Storage (파일 저장)                        │
│  • GitHub Pages (웹 호스팅)                                │
│  • GitHub Actions (CI/CD)                                  │
└────────────────────────────────────────────────────────────┘
```

---

## 🐍 Python 생태계

### Python 3.11+

**왜 Python인가?**
- 풍부한 AI/ML 라이브러리 생태계
- 간결한 문법으로 빠른 개발
- Google Cloud API 공식 지원
- 웹 스크래핑 도구 풍부

**Python 3.11의 주요 특징**:
```python
# 1. 더 나은 에러 메시지
# Before (Python 3.10)
# TypeError: unsupported operand type(s) for +: 'int' and 'str'

# After (Python 3.11)
# TypeError: unsupported operand type(s) for +: 'int' and 'str'
#   File "main.py", line 5
#     result = 10 + "hello"
#              ~~ ^ ~~~~~~~

# 2. 성능 향상 (10-60% 빠름)
# 3. Exception Groups
try:
    # multiple operations
    pass
except* ValueError as e:
    # handle ValueError
    pass
except* TypeError as e:
    # handle TypeError
    pass
```

---

### Pydantic (데이터 검증)

**역할**: 런타임 데이터 검증 및 타입 힌트 활용

**핵심 개념**:
```python
from pydantic import BaseModel, Field, HttpUrl
from typing import List
from datetime import datetime

class Paper(BaseModel):
    """논문 데이터 모델"""
    
    # 필수 필드
    id: str = Field(..., description="논문 ID")
    title: str = Field(..., min_length=1, max_length=500)
    
    # 타입 검증
    authors: List[str] = Field(default_factory=list)
    url: HttpUrl  # URL 형식 자동 검증
    
    # 범위 검증
    upvotes: int = Field(default=0, ge=0)  # >= 0
    
    # 길이 제한
    summary: str = Field(None, max_length=1000)
    
    # 날짜/시간
    collected_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        # JSON 직렬화 설정
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            HttpUrl: lambda v: str(v)
        }

# 사용 예시
paper = Paper(
    id="2510.19338",
    title="Every Attention Matters",
    authors=["Author 1", "Author 2"],
    url="https://huggingface.co/papers/2510.19338",
    upvotes=142
)

# 검증 실패 시 자동으로 ValidationError 발생
try:
    invalid_paper = Paper(
        id="",  # ❌ 빈 문자열
        title="A" * 600,  # ❌ 너무 긺
        url="not-a-url"  # ❌ URL 형식 아님
    )
except ValidationError as e:
    print(e.json())
```

**장점**:
- ✅ 자동 타입 변환
- ✅ 런타임 검증
- ✅ JSON 직렬화/역직렬화
- ✅ IDE 자동완성 지원

---

### BeautifulSoup4 (웹 스크래핑)

**역할**: HTML 파싱 및 데이터 추출

**핵심 개념**:
```python
from bs4 import BeautifulSoup
import requests

# 1. HTML 가져오기
response = requests.get("https://huggingface.co/papers/date/2025-10-25")
html = response.text

# 2. BeautifulSoup 객체 생성
soup = BeautifulSoup(html, 'html.parser')

# 3. 요소 찾기
# CSS 선택자 사용
articles = soup.select('article[data-paper-id]')

# 태그 이름으로 찾기
title = soup.find('h3', class_='paper-title')

# 여러 요소 찾기
authors = soup.find_all('a', class_='author-link')

# 4. 데이터 추출
paper_id = article.get('data-paper-id')  # 속성 값
title_text = title.text.strip()  # 텍스트 내용
author_names = [a.text.strip() for a in authors]  # 리스트 컴프리헨션

# 5. 네비게이션
parent = title.parent  # 부모 요소
siblings = title.find_next_siblings()  # 형제 요소
```

**파싱 전략**:
```python
# 견고한 파싱을 위한 패턴
def safe_find_text(soup, selector, default=""):
    """안전하게 텍스트 추출"""
    element = soup.select_one(selector)
    return element.text.strip() if element else default

def safe_find_attr(element, attr, default=""):
    """안전하게 속성 추출"""
    return element.get(attr, default) if element else default

# 사용
title = safe_find_text(article, 'h3.paper-title', default="Unknown")
paper_id = safe_find_attr(article, 'data-paper-id', default="")
```

---

### Requests (HTTP 클라이언트)

**역할**: HTTP 요청 처리

**핵심 사용법**:
```python
import requests
from tenacity import retry, stop_after_attempt, wait_exponential

# 1. 기본 GET 요청
response = requests.get('https://api.example.com/data')

# 2. 헤더 설정
headers = {
    'User-Agent': 'PaperCast/1.0',
    'Accept': 'application/json'
}
response = requests.get(url, headers=headers)

# 3. 타임아웃 설정
response = requests.get(url, timeout=30)  # 30초

# 4. 재시도 로직 (tenacity 사용)
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def fetch_with_retry(url):
    response = requests.get(url, timeout=30)
    response.raise_for_status()  # 4xx, 5xx 에러 시 예외 발생
    return response

# 5. 세션 사용 (연결 재사용)
session = requests.Session()
session.headers.update({'User-Agent': 'PaperCast/1.0'})

response1 = session.get(url1)  # 연결 생성
response2 = session.get(url2)  # 연결 재사용 (빠름)
```

---

## 🤖 AI/ML 서비스

### Google Gemini Pro (텍스트 생성)

**역할**: 논문 초록을 한국어로 요약

**핵심 개념**:
```python
import google.generativeai as genai

# 1. API 설정
genai.configure(api_key="YOUR_API_KEY")

# 2. 모델 초기화
model = genai.GenerativeModel('gemini-pro')

# 3. 프롬프트 작성 (중요!)
prompt = """
당신은 AI 논문 전문가입니다.
다음 논문을 200자 이내로 한국어로 요약해주세요.

제목: {title}
초록: {abstract}

요약 형식:
- 핵심 기여: (한 문장)
- 방법론: (한 문장)
- 결과: (한 문장)
"""

# 4. 생성 (스트리밍 가능)
response = model.generate_content(prompt)
summary = response.text

# 5. 스트리밍 생성
for chunk in model.generate_content(prompt, stream=True):
    print(chunk.text, end='')
```

**프롬프트 엔지니어링 팁**:
```python
# ❌ 나쁜 프롬프트
"이 논문 요약해줘"

# ✅ 좋은 프롬프트
"""
역할: AI 논문 전문가
작업: 논문 요약
제약: 200자 이내, 한국어, 전문 용어 최소화
형식: 핵심 기여, 방법론, 결과
톤: 간결하고 명확하게

입력:
제목: {title}
초록: {abstract}

출력 형식:
- 핵심: ...
- 방법: ...
- 결과: ...
"""
```

**비용 최적화**:
- Gemini Pro: 무료 티어 60 requests/minute
- 입력 토큰 길이 제한 (초록 500자까지만)
- 캐싱 활용 (같은 날짜 재요청 방지)

---

### Google Cloud Text-to-Speech

**역할**: 텍스트를 자연스러운 음성으로 변환

**핵심 개념**:
```python
from google.cloud import texttospeech

# 1. 클라이언트 초기화
client = texttospeech.TextToSpeechClient.from_service_account_json(
    'credentials/service-account.json'
)

# 2. 입력 텍스트 준비
synthesis_input = texttospeech.SynthesisInput(
    text="안녕하세요, 오늘의 AI 논문 팟캐스트입니다."
)

# 3. 음성 설정
voice = texttospeech.VoiceSelectionParams(
    language_code="ko-KR",
    name="ko-KR-Neural2-A",  # Neural2: 더 자연스러움
    ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
)

# 4. 오디오 설정
audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.MP3,
    speaking_rate=1.0,  # 0.25 ~ 4.0 (1.0 = 정상 속도)
    pitch=0.0,          # -20.0 ~ 20.0 (0.0 = 기본 피치)
    volume_gain_db=0.0  # -96.0 ~ 16.0 (0.0 = 기본 볼륨)
)

# 5. 음성 합성
response = client.synthesize_speech(
    input=synthesis_input,
    voice=voice,
    audio_config=audio_config
)

# 6. MP3 저장
with open('output.mp3', 'wb') as f:
    f.write(response.audio_content)
```

**SSML 사용 (고급)**:
```python
# SSML: Speech Synthesis Markup Language
ssml_text = """
<speak>
  <prosody rate="slow" pitch="-2st">
    안녕하세요, 오늘의 AI 논문 팟캐스트입니다.
  </prosody>
  
  <break time="500ms"/>
  
  <prosody rate="medium">
    첫 번째 논문은 <emphasis level="strong">Every Attention Matters</emphasis>입니다.
  </prosody>
  
  <break time="1s"/>
  
  <prosody rate="fast">
    이 논문은 Transformer 모델의 성능을 개선합니다.
  </prosody>
</speak>
"""

synthesis_input = texttospeech.SynthesisInput(ssml=ssml_text)
```

**비용**:
- Standard 음성: $4 per 1M characters
- Neural2 음성: $16 per 1M characters
- 월 4M characters 무료

---

## ☁️ 클라우드 서비스

### Google Cloud Storage

**역할**: MP3 파일 저장 및 공개 URL 제공

**핵심 개념**:
```python
from google.cloud import storage

# 1. 클라이언트 초기화
client = storage.Client.from_service_account_json(
    'credentials/service-account.json'
)

# 2. 버킷 접근
bucket = client.bucket('papercast-podcasts')

# 3. 파일 업로드
blob = bucket.blob('2025-10-25/episode.mp3')
blob.upload_from_filename('local/path/episode.mp3')

# 4. 공개 URL 설정
blob.make_public()
public_url = blob.public_url
# https://storage.googleapis.com/papercast-podcasts/2025-10-25/episode.mp3

# 5. 메타데이터 설정
blob.metadata = {
    'title': 'Daily AI Papers - 2025-10-25',
    'duration': '627'
}
blob.patch()

# 6. 파일 존재 확인
if blob.exists():
    print(f"File size: {blob.size} bytes")
```

**버킷 설정**:
```bash
# gsutil 사용
gsutil mb -c STANDARD -l asia-northeast3 gs://papercast-podcasts

# 공개 읽기 권한
gsutil iam ch allUsers:objectViewer gs://papercast-podcasts

# 라이프사이클 정책 (90일 후 삭제)
gsutil lifecycle set lifecycle.json gs://papercast-podcasts
```

**lifecycle.json**:
```json
{
  "rule": [
    {
      "action": {"type": "Delete"},
      "condition": {"age": 90}
    }
  ]
}
```

---

### GitHub Pages

**역할**: 정적 웹사이트 무료 호스팅

**핵심 개념**:
- `gh-pages` 브랜치의 내용을 자동으로 호스팅
- 커스텀 도메인 지원
- HTTPS 자동 제공
- CDN 통합

**설정 방법**:
```bash
# 1. gh-pages 브랜치 생성
git checkout --orphan gh-pages
git rm -rf .
echo "Hello, GitHub Pages!" > index.html
git add index.html
git commit -m "Initial commit"
git push origin gh-pages

# 2. Repository Settings → Pages
# Source: Deploy from a branch
# Branch: gh-pages / (root)

# 3. 접속
# https://username.github.io/papercast
```

**GitHub Actions 자동 배포**:
```yaml
- name: Deploy to GitHub Pages
  uses: peaceiris/actions-gh-pages@v3
  with:
    github_token: ${{ secrets.GITHUB_TOKEN }}
    publish_dir: ./static-site
    publish_branch: gh-pages
```

---

## 🌐 웹 기술

### Vanilla JavaScript (프레임워크 없음)

**왜 프레임워크를 사용하지 않았나?**
- 정적 사이트에 프레임워크 오버헤드 불필요
- 번들 크기 최소화 (빠른 로딩)
- 빌드 프로세스 불필요
- 간단한 인터랙션만 필요

**핵심 기능 구현**:

#### 1. Split View (PDF 뷰어)
```javascript
// 상태 관리
let splitViewActive = false;
let currentPaperIndex = -1;

function toggleSplitView(paperIndex) {
  const paper = papersData[paperIndex];
  const container = document.getElementById('split-view-container');
  
  if (splitViewActive && currentPaperIndex === paperIndex) {
    // 닫기
    closeSplitView();
  } else {
    // 열기
    openSplitView(paper, paperIndex);
  }
}

function openSplitView(paper, paperIndex) {
  splitViewActive = true;
  currentPaperIndex = paperIndex;
  
  // PDF iframe 설정
  const pdfUrl = `https://arxiv.org/pdf/${paper.arxiv_id}`;
  document.getElementById('pdf-iframe').src = pdfUrl;
  
  // 컨테이너 표시
  container.setAttribute('data-active', 'true');
  container.setAttribute('aria-hidden', 'false');
}
```

#### 2. 오디오 플레이어 제어
```javascript
const audio = document.getElementById('podcast-audio');

// 재생/일시정지
audio.addEventListener('play', () => {
  console.log('Playing');
});

audio.addEventListener('pause', () => {
  console.log('Paused');
});

// 진행 상황 업데이트
audio.addEventListener('timeupdate', () => {
  const progress = (audio.currentTime / audio.duration) * 100;
  updateProgressBar(progress);
});
```

#### 3. 키보드 단축키
```javascript
document.addEventListener('keydown', (e) => {
  // Escape: Split View 닫기
  if (e.key === 'Escape' && splitViewActive) {
    closeSplitView();
  }
  
  // Ctrl+S: Split View 토글
  if (e.ctrlKey && e.key === 's') {
    e.preventDefault();
    toggleSplitView(0);
  }
  
  // Space: 재생/일시정지
  if (e.key === ' ' && e.target === document.body) {
    e.preventDefault();
    audio.paused ? audio.play() : audio.pause();
  }
});
```

---

### CSS3 (반응형 디자인)

**핵심 기술**:

#### 1. CSS Variables (테마 시스템)
```css
:root {
  --primary-color: #6366f1;
  --secondary-color: #8b5cf6;
  --background-color: #f8fafc;
  --text-primary: #1e293b;
  --text-secondary: #64748b;
  --border-color: #e2e8f0;
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
  --radius-md: 12px;
}

/* 사용 */
.button {
  background-color: var(--primary-color);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-md);
}
```

#### 2. Grid Layout (반응형 그리드)
```css
.episodes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

/* 모바일 */
@media (max-width: 768px) {
  .episodes-grid {
    grid-template-columns: 1fr;
  }
}
```

#### 3. Flexbox (레이아웃)
```css
.paper-card {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.paper-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: auto; /* 하단 고정 */
}
```

---

## 🔄 자동화 & CI/CD

### GitHub Actions

**핵심 개념**:
```yaml
# 트리거 설정
on:
  schedule:
    - cron: '0 21 * * *'  # UTC 21:00 = KST 06:00
  workflow_dispatch:      # 수동 실행 가능
  push:
    branches: [main]      # main 브랜치 푸시 시

# 작업 정의
jobs:
  generate-podcast:
    runs-on: ubuntu-latest
    timeout-minutes: 30
    
    steps:
      # 체크아웃
      - uses: actions/checkout@v4
      
      # Python 설정
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      # 환경 변수
      - name: Set env
        run: |
          echo "GEMINI_API_KEY=${{ secrets.GEMINI_API_KEY }}" >> $GITHUB_ENV
      
      # 실행
      - name: Run pipeline
        run: python run.py
```

**Secrets 관리**:
```bash
# GitHub CLI로 설정
gh secret set GEMINI_API_KEY --body "your-api-key"
gh secret set GCS_BUCKET_NAME --body "papercast-podcasts"

# 또는 Web UI: Repository → Settings → Secrets
```

---

## 🛠️ 개발 도구

### uv (Python 패키지 매니저)

**왜 uv인가?**
- pip보다 10-100배 빠름
- 의존성 잠금 파일 (`uv.lock`)
- 가상환경 자동 관리

```bash
# 설치
curl -LsSf https://astral.sh/uv/install.sh | sh

# 프로젝트 초기화
uv init

# 의존성 추가
uv add pydantic requests beautifulsoup4

# 의존성 설치
uv sync

# 스크립트 실행
uv run python main.py
```

---

### pytest (테스트 프레임워크)

**핵심 기능**:
```python
# 기본 테스트
def test_addition():
    assert 1 + 1 == 2

# Fixture 사용
@pytest.fixture
def sample_paper():
    return Paper(
        id="test-123",
        title="Test Paper"
    )

def test_paper_creation(sample_paper):
    assert sample_paper.id == "test-123"

# 파라미터화
@pytest.mark.parametrize("input,expected", [
    ("hello", 5),
    ("world", 5),
    ("pytest", 6)
])
def test_length(input, expected):
    assert len(input) == expected

# Mock 사용
from unittest.mock import Mock, patch

@patch('requests.get')
def test_api_call(mock_get):
    mock_get.return_value.status_code = 200
    # 테스트 로직
```

---

## 🏛️ 아키텍처 패턴

### Pipeline Pattern (파이프라인 패턴)

**개념**: 데이터를 여러 단계로 처리

```python
class PodcastPipeline:
    def run(self):
        # 각 단계를 순차적으로 실행
        papers = self.step1_collect()
        papers_with_summary = self.step2_summarize(papers)
        audio_path = self.step3_tts(papers_with_summary)
        audio_url = self.step4_upload(audio_path)
        podcast = self.step5_save(papers_with_summary, audio_url)
        self.step6_generate_site(podcast)
```

**장점**:
- 각 단계 독립적 테스트 가능
- 에러 발생 지점 명확
- 로깅 및 모니터링 용이

---

### Repository Pattern (저장소 패턴)

**개념**: 데이터 접근 로직 캡슐화

```python
class PodcastRepository:
    def save(self, podcast: Podcast):
        """팟캐스트를 JSON으로 저장"""
        path = f"data/podcasts/{podcast.id}.json"
        with open(path, 'w') as f:
            json.dump(podcast.dict(), f)
    
    def find_by_id(self, podcast_id: str) -> Podcast:
        """ID로 팟캐스트 찾기"""
        path = f"data/podcasts/{podcast_id}.json"
        with open(path, 'r') as f:
            data = json.load(f)
        return Podcast.from_dict(data)
    
    def find_all(self) -> List[Podcast]:
        """모든 팟캐스트 찾기"""
        podcasts = []
        for file in Path("data/podcasts").glob("*.json"):
            podcast = self.find_by_id(file.stem)
            podcasts.append(podcast)
        return podcasts
```

---

### Factory Pattern (팩토리 패턴)

**개념**: 객체 생성 로직 캡슐화

```python
class ServiceFactory:
    @staticmethod
    def create_collector() -> PaperCollector:
        return PaperCollector()
    
    @staticmethod
    def create_summarizer() -> Summarizer:
        api_key = os.getenv('GEMINI_API_KEY')
        return Summarizer(api_key=api_key)
    
    @staticmethod
    def create_tts() -> TTSConverter:
        credentials = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        return TTSConverter(credentials_path=credentials)
```

---

## 📚 학습 리소스

### Python
- [Python 공식 문서](https://docs.python.org/3/)
- [Real Python](https://realpython.com/)
- [Python Patterns](https://python-patterns.guide/)

### AI/ML
- [Gemini API 문서](https://ai.google.dev/docs)
- [Google Cloud TTS 문서](https://cloud.google.com/text-to-speech/docs)
- [Prompt Engineering Guide](https://www.promptingguide.ai/)

### 웹 개발
- [MDN Web Docs](https://developer.mozilla.org/)
- [Web.dev](https://web.dev/)
- [CSS-Tricks](https://css-tricks.com/)

### DevOps
- [GitHub Actions 문서](https://docs.github.com/en/actions)
- [GitHub Pages 문서](https://docs.github.com/en/pages)

---

**마지막 업데이트**: 2025-10-25
**버전**: 1.0.0

