# API 키 설정 가이드

PaperCast를 실행하기 위해 필요한 API 키와 설정을 안전하게 관리하는 방법입니다.

## 🔐 보안 원칙

**절대로 API 키를 코드에 직접 넣지 마세요!**

✅ **권장**: `.env` 파일 사용 (Git에 커밋되지 않음)  
❌ **금지**: 코드에 하드코딩, export 명령어로 환경변수 설정

---

## 📝 빠른 시작

### 1️⃣ 자동 설정 스크립트 실행

```bash
./setup_env.sh
```

이 스크립트는 자동으로:
- `.env` 파일 생성
- `credentials/` 디렉토리 생성
- `data/` 디렉토리 생성

### 2️⃣ API 키 발급 및 설정

#### Google Gemini API Key

1. [Google AI Studio](https://makersuite.google.com/app/apikey) 접속
2. "Create API Key" 클릭
3. 생성된 키를 복사
4. `.env` 파일 열기:
   ```bash
   nano .env
   ```
5. `GEMINI_API_KEY` 값에 붙여넣기:
   ```bash
   GEMINI_API_KEY=your_actual_api_key_here
   ```

#### Google Cloud Service Account

1. [GCP Console](https://console.cloud.google.com/) 접속
2. 프로젝트 선택 또는 생성
3. **IAM & Admin** → **Service Accounts** 이동
4. "Create Service Account" 클릭
5. 이름 입력 (예: `papercast-bot`)
6. 역할 부여:
   - **Cloud Storage Admin**
   - **Cloud Text-to-Speech Admin**
7. "Create Key" → JSON 선택
8. 다운로드된 JSON 파일을 저장:
   ```bash
   mv ~/Downloads/your-project-xxxxx.json credentials/service-account.json
   ```
9. `.env` 파일에서 경로 확인:
   ```bash
   GOOGLE_APPLICATION_CREDENTIALS=./credentials/service-account.json
   ```

#### Google Cloud Storage Bucket

1. GCP Console → **Cloud Storage** → **Buckets**
2. "Create Bucket" 클릭
3. 이름 입력 (예: `papercast-podcasts`)
4. 지역 선택 (예: `asia-northeast3` - 서울)
5. `.env` 파일에 버킷 이름 입력:
   ```bash
   GCS_BUCKET_NAME=papercast-podcasts
   ```

---

## 📂 파일 구조

```
papercast/
├── .env                          # API 키 저장 (Git 무시됨!)
├── credentials/                  # 인증 파일 저장 (Git 무시됨!)
│   └── service-account.json     # GCP Service Account 키
├── setup_env.sh                 # 환경 설정 스크립트
└── src/
    └── utils/
        └── config.py            # .env 파일 자동 로드
```

---

## 🛡️ 보안 체크리스트

- [ ] `.env` 파일이 `.gitignore`에 포함되어 있는지 확인
- [ ] `credentials/` 디렉토리가 `.gitignore`에 포함되어 있는지 확인
- [ ] `.env` 파일을 절대 Git에 커밋하지 않기
- [ ] Service Account JSON 키를 안전하게 보관
- [ ] API 키가 노출되면 즉시 폐기하고 재발급

---

## 🧪 설정 검증

### 설정 확인 테스트

```python
# Python에서 직접 테스트
python -c "from src.utils.config import config; print(config.validate())"
```

출력:
- `True`: 모든 설정 완료 ✅
- `False`: 설정 누락 ❌

### 상세 설정 확인

```python
python -c "from src.utils.config import config; print(config)"
```

출력 예시:
```
Config(gcs_bucket=papercast-podcasts, timezone=Asia/Seoul, papers_to_fetch=3)
```

---

## 🚀 실행

설정이 완료되면:

```bash
python src/main.py
```

프로그램이 자동으로:
1. `.env` 파일을 읽음
2. API 키 검증
3. 필요한 디렉토리 생성
4. 팟캐스트 생성 시작

---

## ❓ 문제 해결

### "Missing required configuration" 에러

**원인**: `.env` 파일이 없거나 필수 값이 비어있음

**해결**:
```bash
# .env 파일이 있는지 확인
ls -la .env

# .env 파일 내용 확인 (API 키는 표시되지 않음)
cat .env | grep -v "^#" | grep "="
```

### "Google credentials file not found" 에러

**원인**: Service Account JSON 파일 경로가 잘못됨

**해결**:
```bash
# credentials 디렉토리 확인
ls -la credentials/

# .env 파일의 경로와 실제 파일 경로가 일치하는지 확인
cat .env | grep GOOGLE_APPLICATION_CREDENTIALS
```

### Gemini API 오류

**원인**: API 키가 잘못되었거나 할당량 초과

**해결**:
1. [Google AI Studio](https://makersuite.google.com/app/apikey)에서 키 재확인
2. 할당량 확인 (무료: 60 requests/minute)

### GCS 업로드 오류

**원인**: Service Account 권한 부족 또는 버킷이 없음

**해결**:
1. GCP Console → IAM에서 권한 확인
2. GCS에서 버킷 존재 여부 확인
3. Service Account가 버킷에 접근 가능한지 확인

---

## 💡 팁

### 여러 환경 관리

개발/테스트/프로덕션 환경을 분리하려면:

```bash
# 개발 환경
.env.development

# 프로덕션 환경  
.env.production
```

사용:
```python
from src.utils.config import Config

# 특정 환경 파일 로드
config = Config(env_file=".env.development")
```

### API 키 회전 (Rotation)

주기적으로 API 키를 교체하세요:

1. 새 키 발급
2. `.env` 파일 업데이트
3. 서비스 재시작
4. 이전 키 폐기

---

## 📚 추가 자료

- [Google Gemini API 문서](https://ai.google.dev/docs)
- [Google Cloud TTS 문서](https://cloud.google.com/text-to-speech/docs)
- [Google Cloud Storage 문서](https://cloud.google.com/storage/docs)
- [python-dotenv 문서](https://github.com/theskumar/python-dotenv)


