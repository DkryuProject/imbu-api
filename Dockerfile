# 베이스 이미지
FROM python:3.10
# 작업 디렉토리 설정
WORKDIR /imbuAPI
# 종속성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY .env .env
# FastAPI 애플리케이션 복사
COPY . .
# 서버 실행 명령어
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
