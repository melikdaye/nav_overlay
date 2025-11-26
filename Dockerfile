FROM python:3.11-slim

# Chrome dependencies
RUN apt-get update && apt-get install -y \
    wget curl unzip gnupg ca-certificates \
    libnss3 libxss1 libasound2 libatk1.0-0 \
    libatk-bridge2.0-0 libcups2 libdrm2 \
    libxkbcommon0 libxcomposite1 libxrandr2 \
    libxdamage1 libpango-1.0-0 libgbm1 \
    libxshmfence1 libgtk-3-0 \
    --no-install-recommends

# Install Google Chrome stable
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt-get install -y ./google-chrome-stable_current_amd64.deb \
    && rm google-chrome-stable_current_amd64.deb


##############################
# UNIVERSAL CHROMEDRIVER (3-stage fallback)
##############################

# Stage 1: Chrome for Testing - LatestStable
RUN echo "Trying ChromeDriver: Chrome-For-Testing LatestStable..." \
    && wget -q -O /tmp/chromedriver.zip \
         "https://storage.googleapis.com/chrome-for-testing-public/LatestStable/chromedriver-linux64.zip" \
    || true

# Stage 2: If file is empty, try universal driver (LATEST_RELEASE)
RUN if [ ! -s /tmp/chromedriver.zip ]; then \
        echo "Fallback 1: universal ChromeDriver (LATEST_RELEASE)" && \
        UNIVERSAL=$(wget -qO- https://chromedriver.storage.googleapis.com/LATEST_RELEASE) && \
        wget -q -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/$UNIVERSAL/chromedriver_linux64.zip" \
    ; fi || true

# Stage 3: If still empty → fallback stable version (120)
RUN if [ ! -s /tmp/chromedriver.zip ]; then \
        echo "Fallback 2: Trying ChromeDriver 120..." && \
        wget -q -O /tmp/chromedriver.zip \
           "https://chromedriver.storage.googleapis.com/120.0.6099.71/chromedriver_linux64.zip" \
    ; fi || true

# Final: Install whatever we got
RUN unzip /tmp/chromedriver.zip -d /usr/local/bin/ \
    && mv /usr/local/bin/chromedriver* /usr/local/bin/chromedriver \
    && chmod +x /usr/local/bin/chromedriver \
    && rm /tmp/chromedriver.zip || true


##############################

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app
WORKDIR /app

ENV PORT=10000

CMD ["python", "main.py"]
