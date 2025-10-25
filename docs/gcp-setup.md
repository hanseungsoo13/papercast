# Google Cloud Platform 설정 가이드

PaperCast에서 필요한 GCP API 활성화 및 설정 방법입니다.

## 🔑 필요한 API

1. **Google Gemini API** (AI Studio에서 발급)
2. **Cloud Text-to-Speech API** (GCP)
3. **Cloud Storage API** (GCP)

---

## 📝 단계별 설정

### 1️⃣ GCP 프로젝트 생성

1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 새 프로젝트 생성 또는 기존 프로젝트 선택
3. 프로젝트 ID 확인 (예: `papercast-123456`)

---

### 2️⃣ API 활성화

#### Cloud Text-to-Speech API 활성화

**방법 1: 직접 링크**
```
https://console.developers.google.com/apis/api/texttospeech.googleapis.com/overview?project=YOUR_PROJECT_ID
```

**방법 2: 콘솔에서 수동**
1. GCP Console → **APIs & Services** → **Library**
2. "Cloud Text-to-Speech API" 검색
3. **ENABLE** 클릭
4. 활성화까지 1-2분 대기

#### Cloud Storage API 활성화

**방법 1: 직접 링크**
```
https://console.developers.google.com/apis/api/storage-api.googleapis.com/overview?project=YOUR_PROJECT_ID
```

**방법 2: 콘솔에서 수동**
1. GCP Console → **APIs & Services** → **Library**
2. "Cloud Storage API" 검색
3. **ENABLE** 클릭

---

### 3️⃣ Service Account 생성 및 권한 설정

#### Service Account 생성

1. GCP Console → **IAM & Admin** → **Service Accounts**
2. **CREATE SERVICE ACCOUNT** 클릭
3. 이름 입력: `papercast-bot`
4. 설명: "PaperCast automation service account"
5. **CREATE AND CONTINUE** 클릭

#### 역할(Role) 부여

다음 역할들을 추가하세요:

| 역할 | 이름 | 필요 이유 |
|------|------|----------|
| **Cloud Text-to-Speech User** | `roles/cloudtts.user` | 음성 생성 |
| **Storage Object Admin** | `roles/storage.objectAdmin` | MP3 업로드/관리 |
| **Storage Bucket Creator** | `roles/storage.buckets.create` | 버킷 생성 (선택) |

**설정 방법**:
1. "Select a role" 드롭다운 클릭
2. 위 역할들을 하나씩 추가
3. **CONTINUE** → **DONE**

#### JSON 키 생성

1. 생성된 Service Account 클릭
2. **KEYS** 탭 선택
3. **ADD KEY** → **Create new key**
4. **JSON** 선택 → **CREATE**
5. 다운로드된 JSON 파일 저장:
   ```bash
   mv ~/Downloads/papercast-*.json ~/project/Python_Study/papercast/credentials/service-account.json
   ```

---

### 4️⃣ Cloud Storage 버킷 생성

1. GCP Console → **Cloud Storage** → **Buckets**
2. **CREATE BUCKET** 클릭
3. 설정:
   - **Name**: `papercast-podcasts` (전역적으로 고유해야 함)
   - **Location type**: Region
   - **Location**: `asia-northeast3` (Seoul) - 가장 빠름
   - **Storage class**: Standard
   - **Access control**: Uniform
   - **Public access**: **Allow public access** (팟캐스트 공유용)
4. **CREATE** 클릭

#### 버킷 공개 설정

팟캐스트 파일을 공개적으로 접근 가능하게 만들기:

1. 생성한 버킷 클릭
2. **PERMISSIONS** 탭
3. **GRANT ACCESS** 클릭
4. 설정:
   - **New principals**: `allUsers`
   - **Role**: `Storage Object Viewer`
5. **SAVE** → 경고 확인 → **ALLOW PUBLIC ACCESS**

---

### 5️⃣ API 할당량 확인

#### Text-to-Speech 할당량

1. GCP Console → **APIs & Services** → **Enabled APIs**
2. **Cloud Text-to-Speech API** 클릭
3. **QUOTAS** 탭 확인

**무료 티어 한도**:
- Characters per month: 4,000,000 characters
- 일일 약 3개 논문 × 500자 × 30일 = 45,000자 (충분함)

#### Gemini API 할당량

1. [Google AI Studio](https://makersuite.google.com/) 접속
2. API 키 페이지에서 할당량 확인

**무료 티어 한도**:
- 60 requests per minute
- 일일 3개 논문 요약: 여유 있음

---

## ✅ 설정 확인

### 1. API 활성화 확인

```bash
# gcloud CLI 설치 후
gcloud services list --enabled --project=YOUR_PROJECT_ID | grep -E "(texttospeech|storage)"
```

출력:
```
storage-api.googleapis.com
texttospeech.googleapis.com
```

### 2. Service Account 권한 확인

```bash
gcloud projects get-iam-policy YOUR_PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:YOUR_SERVICE_ACCOUNT_EMAIL"
```

### 3. PaperCast 설정 검증

```bash
cd ~/project/Python_Study/papercast
python check_config.py
```

---

## 🚨 문제 해결

### "API has not been used" 오류

**증상**:
```
403 Cloud Text-to-Speech API has not been used in project...
```

**해결**:
1. 위의 직접 링크로 API 활성화
2. 활성화 후 **2-5분 대기**
3. 다시 실행

### "Permission denied" 오류

**증상**:
```
403 Permission denied
```

**해결**:
1. Service Account에 올바른 역할이 부여되었는지 확인
2. JSON 키 파일 경로가 올바른지 확인
3. 프로젝트 ID가 일치하는지 확인

### 버킷 이름 충돌

**증상**:
```
409 Bucket already exists
```

**해결**:
- 버킷 이름을 고유하게 변경 (예: `papercast-podcasts-YOUR_NAME`)

---

## 💰 비용 예상

### 무료 티어 사용 시

**Text-to-Speech**:
- 월 4백만 자 무료
- PaperCast 사용량: ~45,000자/월
- **비용: $0**

**Cloud Storage**:
- 5GB 무료
- MP3 파일: ~7MB/일 × 30일 = ~210MB
- **비용: $0**

**Gemini API**:
- 무료 티어: 60 req/min
- PaperCast 사용: 3 req/day
- **비용: $0**

### 예상 총 비용: **$0/월** (무료 티어 내)

---

## 🔗 유용한 링크

- [GCP Console](https://console.cloud.google.com/)
- [Cloud Text-to-Speech API](https://console.cloud.google.com/apis/library/texttospeech.googleapis.com)
- [Cloud Storage](https://console.cloud.google.com/storage)
- [Google AI Studio](https://makersuite.google.com/)
- [Service Accounts](https://console.cloud.google.com/iam-admin/serviceaccounts)
- [API 할당량](https://console.cloud.google.com/iam-admin/quotas)

---

## ✨ 설정 완료 후

```bash
# 1. 설정 검증
python check_config.py

# 2. 실행
python run.py

# 3. GitHub Actions 설정 (선택)
# README.md의 GitHub Actions 섹션 참고
```

모든 API가 활성화되고 Service Account가 올바르게 설정되었다면 PaperCast가 정상적으로 작동합니다! 🎉

