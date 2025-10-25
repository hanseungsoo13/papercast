#!/bin/bash

# PaperCast API 서버 실행 스크립트

echo "🚀 PaperCast API 서버를 시작합니다..."

# 프로젝트 루트로 이동
cd "$(dirname "$0")/.."

# 가상환경 확인
if [ ! -d ".venv" ]; then
    echo "❌ 가상환경이 없습니다. 'uv sync'를 먼저 실행하세요."
    exit 1
fi

# API 서버 실행
echo "📡 API 서버 시작 중..."
echo "📖 API 문서: http://localhost:8000/docs"
echo "🔍 ReDoc 문서: http://localhost:8000/redoc"
echo "🛑 종료하려면 Ctrl+C를 누르세요"
echo ""

uv run uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
