FROM python:3.11-slim

# Chromium bağımlılıkları
RUN apt update && apt install -y \
    wget curl unzip gnupg \
    libnss3 libatk1.0-0 libcups2 libxkbcommon0 \
    libxcomposite1 libxrandr2 libxdamage1 \
    libpangocairo-1.0-0 libasound2 libxshmfence1 \
    libgbm1 libpango-1.0-0 libgtk-3-0

# Python paketleri
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Playwright Chromium yükle
RUN playwright install --with-deps chromium

COPY . /app
WORKDIR /app

# Render web service port 10000 kullanır
ENV PORT=10000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
