FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt /app/

RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt

COPY app_utils /app/app_utils

COPY pages /app/pages

COPY Home.py /app/Home.py

COPY main_page.css /app/main_page.css

CMD ["streamlit", "run", "Home.py", "--server.port=8501", "--server.address=0.0.0.0"]