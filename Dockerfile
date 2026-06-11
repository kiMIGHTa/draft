FROM pytorch/pytorch:latest

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    git \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir \
    setuptools==79.0.1 \
    wheel \
    packaging


RUN pip install --no-cache-dir --no-build-isolation -r requirements.txt

COPY . .

RUN mkdir -p /app/data/audio && chmod 777 /app/data/audio

ENV FLASK_APP=app.py
ENV PYTHONUNBUFFERED=1

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

CMD ["gunicorn", "-b", "0.0.0.0:5000", "--timeout", "300", "--workers", "1", "app:app"]