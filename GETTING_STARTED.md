# 🚀 빠른 시작 가이드

> PaperCast를 5분 안에 시작하는 방법

## 📋 사전 준비

1. Python 3.11+ 설치
2. Git 설치
3. Google Gemini API 키 ([발급받기](https://makersuite.google.com/app/apikey))
4. Google Cloud 계정 (무료 티어 가능)

---

## ⚡ 3단계로 시작하기

### 1️⃣ 설치

```bash
# 저장소 클론
git clone https://github.com/hanseungsoo13/papercast.git
cd papercast

# 의존성 설치
pip install -r requirements.txt
```

### 2️⃣ 환경 설정

```bash
# 설정 스크립트 실행 (대화형)
bash scripts/setup.sh

# 또는 수동으로 .env 파일 생성
cat > .env << EOF
GEMINI_API_KEY=your_key_here
GOOGLE_APPLICATION_CREDENTIALS=./credentials/service-account.json
GCS_BUCKET_NAME=your-bucket-name
EOF
```

### 3️⃣ 실행

```bash
# 팟캐스트 생성
python run.py

# 개발 서버 시작
bash scripts/dev-server.sh

# 브라우저에서 http://localhost:8080 접속
```

---

## 🎯 다음 단계

### 개발자라면
→ [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) - 아키텍처와 개발 가이드

### 기술에 관심있다면
→ [TECHNICAL_STACK.md](TECHNICAL_STACK.md) - 사용된 기술 상세 설명

### 배포하고 싶다면
→ [docs/deployment.md](docs/deployment.md) - GitHub Pages 자동 배포

---

## ❓ 문제 해결

### "API key not valid"
→ [docs/api-setup.md](docs/api-setup.md) 참고

### "Permission denied" (GCS)
→ [docs/gcp-setup.md](docs/gcp-setup.md) 참고

### 기타 문제
→ [GitHub Issues](https://github.com/hanseungsoo13/papercast/issues)

---

## 📚 전체 문서

- [README.md](README.md) - 프로젝트 개요
- [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) - 개발자 가이드
- [TECHNICAL_STACK.md](TECHNICAL_STACK.md) - 기술 스택
- [docs/](docs/) - 상세 문서

---

**즐거운 AI 논문 팟캐스트 여행 되세요!** 🎧✨

