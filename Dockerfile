# Dockerfile for PaperCast API
FROM python:3.12-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 포트 설정
EXPOSE 8001

# 헬스 체크
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8001/api/health || exit 1

# Service Account 키 설정 (Cloud Run에서 자동으로 마운트됨)
RUN mkdir -p /app/credentials

# 애플리케이션 실행
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8001"]
