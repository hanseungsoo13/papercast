# Dockerfile

# 1. 파이썬 3.10(혹은 선호하는 버전) 환경을 가져옵니다.
FROM python:3.10-slim

# 2. 환경 변수 설정 (불필요한 로그 방지)
ENV PYTHONUNBUFFERED True

# 3. 작업 폴더를 /app으로 설정
WORKDIR /app

# 4. 필요한 라이브러리 목록을 먼저 복사하고 설치합니다.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. 나머지 모든 소스 코드(main.py)를 복사합니다.
COPY . .

# 6. Cloud Run이 서버를 시작할 때 실행할 명령어
# gunicorn을 사용해 8080 포트에서 main.py 안의 app을 실행합니다.
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "main:app"]