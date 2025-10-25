#!/bin/bash
# PaperCast 환경 설정 스크립트

echo "🚀 PaperCast 환경 설정을 시작합니다..."

# 1. .env 파일 생성
if [ -f ".env" ]; then
    echo "⚠️  .env 파일이 이미 존재합니다. 덮어쓸까요? (y/N)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo "❌ .env 파일 생성을 건너뜁니다."
    else
        create_env=true
    fi
else
    create_env=true
fi

if [ "$create_env" = true ]; then
    cat > .env << 'EOF'
# PaperCast Configuration
# 아래 값들을 실제 값으로 변경하세요

# Google Gemini API Key (필수)
# 발급: https://makersuite.google.com/app/apikey
GEMINI_API_KEY=your_gemini_api_key_here

# Google Cloud Service Account (필수)
# 경로를 실제 service account JSON 파일 경로로 변경
GOOGLE_APPLICATION_CREDENTIALS=./credentials/service-account.json

# Google Cloud Storage Bucket Name (필수)
# 실제 GCS 버킷 이름으로 변경
GCS_BUCKET_NAME=papercast-podcasts

# Optional: 추가 설정
TZ=Asia/Seoul
LOG_LEVEL=INFO
PAPERS_TO_FETCH=3
PODCAST_TITLE_PREFIX=Daily AI Papers
EOF
    echo "✅ .env 파일이 생성되었습니다!"
fi

# 2. credentials 디렉토리 생성
if [ ! -d "credentials" ]; then
    mkdir -p credentials
    echo "✅ credentials 디렉토리가 생성되었습니다!"
else
    echo "ℹ️  credentials 디렉토리가 이미 존재합니다."
fi

# 3. data 디렉토리 생성
if [ ! -d "data" ]; then
    mkdir -p data/podcasts data/logs
    echo "✅ data 디렉토리가 생성되었습니다!"
else
    echo "ℹ️  data 디렉토리가 이미 존재합니다."
fi

echo ""
echo "📝 다음 단계:"
echo "1. .env 파일을 열어서 실제 API 키를 입력하세요:"
echo "   nano .env"
echo ""
echo "2. GCP Service Account JSON 키를 다운로드하여 저장하세요:"
echo "   cp ~/Downloads/your-key.json credentials/service-account.json"
echo ""
echo "3. 설정이 완료되면 테스트해보세요:"
echo "   python src/main.py"
echo ""
echo "✨ 환경 설정이 완료되었습니다!"


