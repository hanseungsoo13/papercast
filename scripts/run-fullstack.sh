#!/bin/bash

# PaperCast 풀스택 개발 서버 실행 스크립트
# API 서버와 프론트엔드를 동시에 실행

echo "🚀 PaperCast 풀스택 개발 서버를 시작합니다..."

# 프로젝트 루트로 이동
cd "$(dirname "$0")/.."

# API 서버 실행 (백그라운드)
echo "📡 API 서버 시작 중..."
uv run uvicorn api.main:app --host 0.0.0.0 --port 8001 --reload &
API_PID=$!

# API 서버 시작 대기
echo "⏳ API 서버 시작 대기 중..."
sleep 5

# API 서버 상태 확인
if curl -s http://localhost:8001/api/health > /dev/null; then
    echo "✅ API 서버가 정상적으로 시작되었습니다"
    echo "📖 API 문서: http://localhost:8001/docs"
else
    echo "❌ API 서버 시작 실패"
    kill $API_PID 2>/dev/null
    exit 1
fi

# 프론트엔드 서버 실행
echo "🌐 프론트엔드 서버 시작 중..."
cd frontend
npm run dev &
FRONTEND_PID=$!

# 서버 종료 처리
cleanup() {
    echo ""
    echo "🛑 서버를 종료합니다..."
    kill $API_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

echo ""
echo "🎉 풀스택 개발 서버가 시작되었습니다!"
echo "📡 API 서버: http://localhost:8001"
echo "📖 API 문서: http://localhost:8001/docs"
echo "🌐 프론트엔드: http://localhost:3000"
echo ""
echo "🛑 종료하려면 Ctrl+C를 누르세요"
echo ""

# 대기
wait
