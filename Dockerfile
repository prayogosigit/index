# Gunakan base image Python slim
FROM python:3.11-slim

# Install dependencies sistem yang diperlukan oleh Pillow & instagrapi
RUN apt-get update && apt-get install -y \
    build-essential \
    libjpeg-dev \
    zlib1g-dev \
    libffi-dev \
    libxml2-dev \
    libxslt1-dev \
    libssl-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set workdir
WORKDIR /app

# Salin requirement dan script
COPY requirements.txt .
COPY auto_like.py .

# Install library Python
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /app/session
# Jalankan script saat container dijalankan
CMD ["python", "auto_like.py"]
