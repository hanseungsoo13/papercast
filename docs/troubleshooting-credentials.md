# Google Cloud Credentials 문제 해결 가이드

## JSON 디코딩 오류 해결

### 문제 상황
```
json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
```

이 오류는 Google Cloud Service Account JSON이 base64로 인코딩되어 있을 때 발생합니다.

### 원인
- `GCP_SERVICE_ACCOUNT_KEY` 환경 변수가 base64로 인코딩된 JSON을 포함하고 있음
- GitHub Actions에서 base64 디코딩 과정에서 문제 발생
- JSON 파일이 올바르게 생성되지 않음

### 해결 방법

#### 1. Base64 인코딩 확인
Service Account JSON 파일을 올바르게 base64로 인코딩했는지 확인:

```bash
# JSON 파일을 base64로 인코딩
cat service-account-key.json | base64 -w 0

# 또는
base64 -w 0 < service-account-key.json
```

#### 2. Base64 디코딩 테스트
인코딩된 키가 올바른지 테스트:

```bash
# Base64 디코딩 후 JSON 유효성 검사
echo "YOUR_BASE64_STRING" | base64 --decode | python3 -m json.tool
```

#### 3. GitHub Actions Secret 확인
GitHub Repository → Settings → Secrets and variables → Actions에서:
- `GCP_SERVICE_ACCOUNT_KEY` Secret이 올바르게 설정되었는지 확인
- Secret 값이 base64 인코딩된 JSON인지 확인

#### 4. 로컬 테스트
프로젝트 루트에서 credential 테스트:

```bash
# 환경 변수 설정
export GCP_SERVICE_ACCOUNT_KEY="your_base64_encoded_key"

# 테스트 실행
python test_credentials.py
```

### 개선된 처리 방식

#### 자동 credential 설정
새로운 `src/utils/credentials.py` 모듈이 다음을 자동으로 처리합니다:

1. **Base64 디코딩**: 환경 변수에서 base64 키를 자동으로 디코딩
2. **JSON 검증**: 디코딩된 데이터가 유효한 JSON인지 확인
3. **파일 생성**: `credentials/service-account.json` 파일 자동 생성
4. **환경 변수 설정**: `GOOGLE_APPLICATION_CREDENTIALS` 자동 설정

#### GitHub Actions 워크플로우 개선
`.github/workflows/daily-podcast.yml`에서:

```yaml
- name: Set up Google Cloud credentials
  env:
    GCP_SERVICE_ACCOUNT_KEY: ${{ secrets.GCP_SERVICE_ACCOUNT_KEY }}
  run: |
    python -c "
    import os, sys
    sys.path.append('src')
    from utils.credentials import setup_gcp_credentials_from_base64
    
    if not setup_gcp_credentials_from_base64(os.getenv('GCP_SERVICE_ACCOUNT_KEY'), 'credentials/service-account.json'):
        sys.exit(1)
    "
```

### 문제 해결 체크리스트

- [ ] Service Account JSON 파일이 유효한지 확인
- [ ] Base64 인코딩이 올바른지 확인 (`base64 -w 0` 사용)
- [ ] GitHub Secret이 올바르게 설정되었는지 확인
- [ ] 로컬에서 `test_credentials.py` 실행 성공
- [ ] GitHub Actions 로그에서 credential 설정 단계 성공

### 추가 디버깅

#### 로그 확인
GitHub Actions에서 다음 로그를 확인:

```
🔑 Setting up GCP credentials using Python...
✅ GCP credentials setup successful
```

#### 수동 디버깅
문제가 지속되면 다음 명령어로 수동 확인:

```bash
# 1. Base64 키 확인
echo $GCP_SERVICE_ACCOUNT_KEY | wc -c

# 2. 디코딩 테스트
echo $GCP_SERVICE_ACCOUNT_KEY | base64 -d | head -c 100

# 3. JSON 유효성 검사
echo $GCP_SERVICE_ACCOUNT_KEY | base64 -d | python3 -m json.tool
```

### 지원되는 환경 변수

1. **GCP_SERVICE_ACCOUNT_KEY**: Base64 인코딩된 Service Account JSON
2. **GOOGLE_APPLICATION_CREDENTIALS**: 직접적인 JSON 파일 경로

시스템은 자동으로 어떤 방식을 사용할지 결정합니다.
