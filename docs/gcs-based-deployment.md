# GCS 기반 데이터 저장 배포 가이드

## 🎯 개요

PaperCast는 **Google Cloud Storage (GCS)를 중앙 데이터 저장소**로 사용하여 완전한 클라우드 기반 아키텍처를 제공합니다.

## 📋 데이터 저장 구조

### ❌ **기존 문제점**
```
GitHub Actions 실행
         ↓
로컬 JSON 파일 생성 (data/podcasts/*.json)
         ↓
GitHub Actions 종료 → 데이터 손실
         ↓
백엔드 배포 → 데이터 없음
```

### ✅ **GCS 기반 해결책**
```
GitHub Actions 실행
         ↓
논문 수집 + AI 처리 + TTS 생성
         ↓
GCS에 모든 데이터 저장
├── podcasts/2025-01-23.json (메타데이터)
├── podcasts/2025-01-23/episode.mp3 (오디오)
└── podcasts/2025-01-23/metadata.json (상세 정보)
         ↓
백엔드 배포 → GCS에서 직접 데이터 읽기
```

## 🏗️ 아키텍처

### 1. 데이터 흐름

```
┌─────────────────────────────────────┐
│        GitHub Actions               │
│    (매일 6시 KST 자동 실행)         │
└─────────────────────────────────────┘
         ↓
┌─────────────────────────────────────┐
│    1. 논문 수집 (Hugging Face)      │
│    2. AI 요약 생성 (Gemini Pro)     │
│    3. TTS 변환 (Google Cloud TTS)   │
└─────────────────────────────────────┘
         ↓
┌─────────────────────────────────────┐
│        Google Cloud Storage         │
│    (중앙 데이터 저장소)              │
│                                     │
│  papercast-podcasts/                │
│  ├── podcasts/                      │
│  │   ├── 2025-01-23.json           │
│  │   ├── 2025-01-24.json           │
│  │   └── 2025-01-25.json           │
│  └── episodes/                      │
│      ├── 2025-01-23/                │
│      │   ├── episode.mp3            │
│      │   └── metadata.json          │
│      └── 2025-01-24/                │
│          ├── episode.mp3            │
│          └── metadata.json          │
└─────────────────────────────────────┘
         ↓
┌─────────────────────────────────────┐
│        백엔드 (Cloud Run)            │
│    GCS에서 직접 데이터 읽기          │
└─────────────────────────────────────┘
         ↓
┌─────────────────────────────────────┐
│        프론트엔드 (Vercel)           │
│    백엔드 API 호출                   │
└─────────────────────────────────────┘
```

### 2. GCS 데이터 구조

```
papercast-podcasts/
├── podcasts/                          # 에피소드 메타데이터
│   ├── 2025-01-23.json               # 에피소드 기본 정보
│   ├── 2025-01-24.json
│   └── 2025-01-25.json
└── episodes/                         # 에피소드 상세 데이터
    ├── 2025-01-23/
    │   ├── episode.mp3                # 오디오 파일
    │   └── metadata.json              # 상세 메타데이터
    ├── 2025-01-24/
    │   ├── episode.mp3
    │   └── metadata.json
    └── 2025-01-25/
        ├── episode.mp3
        └── metadata.json
```

## 🔧 구현 세부사항

### 1. GCS Repository 패턴

```python
# api/repository_gcs.py
class GCSPodcastRepository:
    def __init__(self, bucket_name: str, credentials_path: Optional[str] = None):
        self.bucket_name = bucket_name
        self.client = storage.Client(credentials=credentials)
        self.bucket = self.client.bucket(bucket_name)
    
    def find_all(self) -> List[Podcast]:
        """GCS에서 모든 팟캐스트 조회"""
        blobs = self.client.list_blobs(self.bucket_name, prefix="podcasts/")
        # JSON 파일들을 날짜 역순으로 정렬하여 반환
    
    def find_by_id(self, podcast_id: str) -> Optional[Podcast]:
        """GCS에서 특정 팟캐스트 조회"""
        blob_name = f"podcasts/{podcast_id}.json"
        blob = self.bucket.blob(blob_name)
        # GCS에서 직접 JSON 데이터 로드
```

### 2. 데이터 저장 과정

```python
# src/main.py
def _save_podcast_to_gcs(self, podcast: Podcast) -> str:
    """팟캐스트 메타데이터를 GCS에 저장"""
    destination = f"podcasts/{podcast.id}.json"
    metadata_url = self.uploader.upload_json(podcast.to_dict(), destination)
    return metadata_url
```

### 3. API 엔드포인트

```python
# api/routes/episodes.py
@router.get("/episodes", response_model=List[EpisodeResponse])
async def get_episodes(repo: GCSPodcastRepository = Depends(get_repository)):
    """GCS에서 에피소드 목록 조회"""
    podcasts = repo.find_all()
    return [EpisodeResponse.from_podcast(podcast) for podcast in podcasts]
```

## 🚀 배포 과정

### 1. GitHub Actions 실행

```yaml
# .github/workflows/daily-podcast.yml
- name: Generate podcast episode
  env:
    GCS_BUCKET_NAME: ${{ secrets.GCS_BUCKET_NAME }}
    GOOGLE_APPLICATION_CREDENTIALS: ./credentials/service-account.json
    GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
  run: |
    python src/main.py  # GCS에 모든 데이터 저장
```

### 2. 백엔드 배포

```yaml
- name: Deploy to Cloud Run
  run: |
    gcloud run deploy papercast-backend \
      --set-env-vars="GCS_BUCKET_NAME=${{ secrets.GCS_BUCKET_NAME }}" \
      --set-secrets="GCP_SERVICE_ACCOUNT_KEY=${{ secrets.GCP_SERVICE_ACCOUNT_KEY }}:latest"
```

### 3. 프론트엔드 배포

```yaml
- name: Deploy to Vercel
  env:
    NEXT_PUBLIC_API_URL: ${{ secrets.FRONTEND_API_URL }}
  run: |
    vercel --prod
```

## 🔍 데이터 접근 방식

### 1. 백엔드에서 GCS 데이터 읽기

```python
# Cloud Run에서 실행되는 백엔드
# 환경 변수: GCS_BUCKET_NAME, GOOGLE_APPLICATION_CREDENTIALS

repository = CachedGCSPodcastRepository(
    bucket_name=os.getenv("GCS_BUCKET_NAME"),
    credentials_path=os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
)

# GCS에서 직접 데이터 조회
episodes = repository.find_all()
```

### 2. API 응답 예시

```json
// GET /api/episodes
{
  "episodes": [
    {
      "id": "2025-01-23",
      "title": "Daily AI Papers - 2025-01-23",
      "audio_url": "https://storage.googleapis.com/papercast-podcasts/episodes/2025-01-23/episode.mp3",
      "papers_count": 3,
      "created_at": "2025-01-23T06:00:00Z"
    }
  ]
}
```

## 🎯 주요 장점

### 1. **완전한 클라우드 기반**
- ✅ **중앙 집중식 데이터**: GCS에 모든 데이터 저장
- ✅ **확장성**: 무제한 데이터 저장 가능
- ✅ **가용성**: 99.9% 가용성 보장

### 2. **GitHub Actions 최적화**
- ✅ **데이터 지속성**: Actions 종료 후에도 데이터 유지
- ✅ **백엔드 독립성**: 배포 시 데이터 손실 없음
- ✅ **자동화**: 완전 자동화된 파이프라인

### 3. **성능 최적화**
- ✅ **캐싱**: Repository 레벨에서 캐싱
- ✅ **CDN**: GCS 글로벌 CDN 활용
- ✅ **병렬 처리**: 여러 요청 동시 처리

## 📝 설정 요구사항

### 1. GitHub Secrets

| Secret Name | Description |
|-------------|-------------|
| `GCS_BUCKET_NAME` | GCS 버킷 이름 |
| `GCP_SERVICE_ACCOUNT_KEY` | GCP Service Account JSON (base64) |
| `GCP_PROJECT_ID` | Google Cloud 프로젝트 ID |

### 2. GCS 버킷 설정

```bash
# GCS 버킷 생성
gsutil mb gs://papercast-podcasts

# 버킷 권한 설정
gsutil iam ch serviceAccount:papercast-service@project.iam.gserviceaccount.com:objectAdmin gs://papercast-podcasts
```

### 3. Service Account 권한

```json
{
  "role": "roles/storage.objectAdmin",
  "resource": "projects/PROJECT_ID/buckets/papercast-podcasts"
}
```

## 🎉 완전한 클라우드 아키텍처!

이제 PaperCast는 **완전한 클라우드 기반 서비스**가 되었습니다:

- ✅ **데이터**: GCS에 중앙 집중식 저장
- ✅ **처리**: GitHub Actions에서 자동 생성
- ✅ **서빙**: Cloud Run에서 GCS 데이터 직접 서빙
- ✅ **프론트엔드**: Vercel에서 자동 배포
- ✅ **자동화**: 매일 6시 KST 완전 자동 실행

---

**다음 단계**: [모니터링 및 유지보수](monitoring-guide.md)
