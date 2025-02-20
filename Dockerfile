# Python 3.11 이미지를 기반으로 사용
FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필요한 의존성 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Playwright 설치를 위한 의존성
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxcb1 \
    libxkbcommon0 \
    libatspi2.0-0 \
    libx11-6 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# requirements.txt 복사 및 패키지 설치
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install streamlit

# Playwright 브라우저 설치
RUN playwright install chromium

# 애플리케이션 코드 복사
COPY . .

# 로그 디렉토리 생성
RUN mkdir -p /app/logs

# 실행 스크립트 생성
RUN echo '#!/bin/bash\n\
exec streamlit run main.py --server.address=0.0.0.0 2>&1 | tee -a /app/logs/app.log' > /app/start.sh \
    && chmod +x /app/start.sh

# 포트 설정
EXPOSE 8501

# 실행 명령
CMD ["/app/start.sh"] 