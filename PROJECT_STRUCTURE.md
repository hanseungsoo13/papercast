# 📁 PaperCast 프로젝트 구조

> 프로젝트의 전체 구조와 각 파일/폴더의 역할

## 🎯 핵심 문서 (루트)

```
papercast/
├── README.md                 # 📖 프로젝트 소개 (외부 사용자용)
├── GETTING_STARTED.md        # ⚡ 5분 빠른 시작 가이드
├── DEVELOPER_GUIDE.md        # 🛠️ 개발자 명세서 (아키텍처, 개발 가이드)
├── TECHNICAL_STACK.md        # 🔧 기술 스택 & 배경지식
└── PROJECT_STRUCTURE.md      # 📁 이 파일
```

**역할 구분**:
- `README.md`: 첫 방문자가 보는 프로젝트 소개
- `GETTING_STARTED.md`: 빠르게 시작하고 싶은 사용자용
- `DEVELOPER_GUIDE.md`: 코드를 이해하고 개발하려는 개발자용
- `TECHNICAL_STACK.md`: 사용된 기술의 원리를 이해하고 싶은 사람용

---

## 📚 상세 문서 (docs/)

```
docs/
├── api-setup.md              # Gemini & GCP API 설정 가이드
├── gcp-setup.md              # Google Cloud Platform 설정
├── github-actions-setup.md   # GitHub Actions 자동화 설정
├── slack-setup.md            # Slack 알림 연동 (선택사항)
├── deployment.md             # 배포 및 운영 가이드
└── testing.md                # 테스트 전략 및 실행 방법
```

**특징**:
- 모든 파일명이 소문자-케밥-케이스
- 설정 관련 문서는 `-setup.md` 접미사
- 각 문서는 독립적으로 읽을 수 있도록 구성

---

## 🔧 스크립트 (scripts/)

```
scripts/
├── setup.sh                  # 환경 설정 자동화 스크립트
├── dev-server.sh             # 개발 서버 실행 스크립트
├── dev-server.py             # 라이브 리로드 개발 서버
├── dev-regenerate.py         # 사이트 재생성 (개발용)
└── make_bucket_public.py     # GCS 버킷 공개 설정
```

**사용법**:
```bash
# 환경 설정
bash scripts/setup.sh

# 개발 서버 시작
bash scripts/dev-server.sh

# 또는 Python으로 직접 실행
python scripts/dev-server.py
```

---

## 💻 소스 코드 (src/)

```
src/
├── models/                   # 데이터 모델 (Pydantic)
│   ├── paper.py             # Paper: 논문 정보
│   ├── podcast.py           # Podcast: 팟캐스트 메타데이터
│   └── processing_log.py    # ProcessingLog: 처리 로그
│
├── services/                 # 비즈니스 로직
│   ├── collector.py         # 논문 수집 (웹 스크래핑)
│   ├── summarizer.py        # AI 요약 (Gemini Pro)
│   ├── short_summarizer.py  # 3줄 요약 생성 (Gemini Pro)
│   ├── tts.py               # 음성 변환 (Google TTS)
│   ├── uploader.py          # 클라우드 업로드 (GCS)
│   └── generator.py       # 정적 사이트 생성
│
├── utils/                    # 유틸리티
│   ├── logger.py            # 로깅 설정
│   ├── config.py            # 환경 변수 관리
│   └── retry.py             # 재시도 로직 (tenacity)
│
└── main.py                   # 🎯 메인 파이프라인 오케스트레이션
```

**핵심 파일**:
- `main.py`: 전체 6단계 파이프라인 실행
- `services/`: 각 단계의 구체적인 로직
- `models/`: Pydantic을 사용한 타입 안전 데이터 모델

---

## 🧪 테스트 (tests/)

```
tests/
├── unit/                     # 단위 테스트
│   ├── test_collector.py
│   ├── test_summarizer.py
│   ├── test_tts.py
│   ├── test_uploader.py
│   ├── test_generator.py
│   ├── test_paper.py
│   └── test_processing_log.py
│
├── integration/              # 통합 테스트
│   └── test_pipeline.py
│
├── contract/                 # Contract 테스트 (외부 API)
│   ├── test_gemini_api.py
│   ├── test_google_tts_api.py
│   └── test_gcs_api.py
│
└── e2e/                      # E2E 테스트
    └── test_website.py
```

**실행 방법**:
```bash
pytest tests/unit/            # 단위 테스트만
pytest tests/integration/     # 통합 테스트만
pytest -v                     # 모든 테스트
```

---

## 📊 데이터 (data/)

```
data/
├── podcasts/                 # 팟캐스트 메타데이터 (JSON)
│   ├── 2025-10-21.json
│   ├── 2025-10-24.json
│   └── 2025-10-25.json
│
├── audio/                    # 로컬 MP3 파일 (임시)
│   └── {date}/
│       └── episode.mp3
│
└── logs/                     # 처리 로그
    └── pipeline_YYYYMMDD.log
```

**특징**:
- `podcasts/`: 각 날짜별 JSON 파일
- `audio/`: 업로드 전 임시 저장 (GCS 업로드 후 삭제 가능)
- `logs/`: 디버깅 및 모니터링용

---

## 🌐 웹사이트 (static-site/)

```
static-site/                  # 생성된 정적 웹사이트
├── index.html               # 메인 페이지 (에피소드 목록)
│
├── episodes/                # 개별 에피소드 페이지
│   ├── 2025-10-21.html
│   ├── 2025-10-24.html
│   └── 2025-10-25.html
│
├── assets/                  # 정적 자원
│   ├── css/
│   │   └── styles.css      # 전체 스타일시트
│   └── js/
│       └── script.js       # JavaScript (Split View 등)
│
└── podcasts/
    └── index.json          # API 엔드포인트 (메타데이터)
```

**배포**:
- GitHub Pages를 통해 자동 배포
- `gh-pages` 브랜치에 푸시됨
- `https://username.github.io/papercast`에서 접근

---

## ⚙️ 설정 파일

```
papercast/
├── .env                      # 환경 변수 (Git 제외)
├── .env.example             # 환경 변수 템플릿
├── requirements.txt          # Python 의존성
├── pyproject.toml           # Python 프로젝트 설정
├── uv.lock                  # uv 의존성 잠금 파일
├── pytest.ini               # pytest 설정
├── .gitignore               # Git 제외 파일
└── .cursorignore            # Cursor IDE 제외 파일
```

---

## 🔄 CI/CD (.github/)

```
.github/
└── workflows/
    └── daily-podcast.yml    # 매일 자동 실행 워크플로우
```

**동작**:
1. 매일 06:00 KST 자동 실행
2. 논문 수집 → 요약 → TTS → 업로드 → 사이트 생성
3. GitHub Pages 자동 배포

---

## 🔐 인증 (credentials/)

```
credentials/
└── service-account.json     # GCP 서비스 계정 키 (Git 제외)
```

**보안**:
- `.gitignore`에 추가되어 있음
- 절대 공개하지 말 것
- GitHub Secrets로 관리 권장

---

## 📦 기타 파일

```
papercast/
├── run.py                   # 파이프라인 실행 래퍼
├── main.py                  # 레거시 실행 파일 (→ run.py 사용 권장)
├── check_config.py          # 설정 검증 스크립트
└── LICENSE                  # MIT 라이선스
```

---

## 🗂️ 전체 디렉토리 트리

```
papercast/
│
├── 📖 문서 (루트)
│   ├── README.md
│   ├── GETTING_STARTED.md
│   ├── DEVELOPER_GUIDE.md
│   ├── TECHNICAL_STACK.md
│   └── PROJECT_STRUCTURE.md
│
├── 📚 docs/                  (상세 문서)
├── 🔧 scripts/               (유틸리티 스크립트)
├── 💻 src/                   (소스 코드)
├── 🧪 tests/                 (테스트)
├── 📊 data/                  (데이터)
├── 🌐 static-site/          (생성된 웹사이트)
├── ⚙️  .github/workflows/    (CI/CD)
└── 🔐 credentials/          (인증 정보)
```

---

## 🎯 파일 네이밍 컨벤션

### 문서 (Markdown)
- **루트 문서**: `SCREAMING_SNAKE_CASE.md` (예: `README.md`, `DEVELOPER_GUIDE.md`)
- **하위 문서**: `kebab-case.md` (예: `api-setup.md`, `github-actions-setup.md`)

### Python 파일
- **모듈**: `snake_case.py` (예: `collector.py`, `processing_log.py`)
- **스크립트**: `kebab-case.py` (예: `dev-regenerate.py`, `dev-server.py`)

### Shell 스크립트
- **모두**: `kebab-case.sh` (예: `setup.sh`, `dev-server.sh`)

---

## 🚀 일반적인 작업 흐름

### 1. 새 팟캐스트 생성
```
python run.py
  ↓ src/main.py
  ↓ services/ (6단계)
  ↓ data/podcasts/{date}.json
  ↓ static-site/
```

### 2. 개발 서버 실행
```
bash scripts/dev-server.sh
  ↓ scripts/dev-server.py
  ↓ http://localhost:8080
```

### 3. 사이트 재생성 (개발)
```
python scripts/dev-regenerate.py
  ↓ data/podcasts/*.json
  ↓ static-site/ (재생성)
```

### 4. 테스트 실행
```
pytest
  ↓ tests/unit/
  ↓ tests/integration/
  ↓ htmlcov/ (커버리지 리포트)
```

---

## 📝 빠른 참조

| 작업 | 명령어 | 참고 문서 |
|------|--------|-----------|
| 빠른 시작 | `python run.py` | [GETTING_STARTED.md](GETTING_STARTED.md) |
| 개발 서버 | `bash scripts/dev-server.sh` | [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) |
| 테스트 | `pytest` | [docs/testing.md](docs/testing.md) |
| 배포 | GitHub Actions 자동 | [docs/deployment.md](docs/deployment.md) |
| API 설정 | `.env` 파일 생성 | [docs/api-setup.md](docs/api-setup.md) |

---

**마지막 업데이트**: 2025-10-25  
**버전**: 1.0.0

