FROM python:3.11-slim

# Chrome gereksinimleri
RUN apt-get update && apt-get install -y \
    wget curl unzip gnupg \
    libnss3 libxss1 libasound2 libatk1.0-0 \
    libatk-bridge2.0-0 libcups2 libdrm2 \
    libxkbcommon0 libxcomposite1 libxrandr2 \
    libxdamage1 libpango-1.0-0 libgbm1 \
    libxshmfence1 libgtk-3-0 \
    --no-install-recommends

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app
WORKDIR /app

ENV PORT=10000

CMD ["python", "main.py"]
