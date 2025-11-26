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


# -------------------------------
# Install Chrome stable
# -------------------------------
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt-get install -y ./google-chrome-stable_current_amd64.deb \
    && rm google-chrome-stable_current_amd64.deb


# -------------------------------
# Install matching ChromeDriver (Chrome-for-Testing)
# -------------------------------
RUN CHROME_VERSION=$(google-chrome --version | awk '{print $3}') \
    && MAJOR_VERSION=$(echo $CHROME_VERSION | cut -d '.' -f 1) \
    && FULL_VERSION=$(curl -s https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json \
        | grep -o "\"version\": \"${MAJOR_VERSION}[^\"]*\"" | head -n 1 | cut -d '"' -f 4) \
    && echo "Chrome version: $CHROME_VERSION" \
    && echo "Matching driver version: $FULL_VERSION" \
    && wget -q -O /tmp/chromedriver.zip \
        https://storage.googleapis.com/chrome-for-testing-public/$FULL_VERSION/chromedriver-linux64.zip \
    && unzip /tmp/chromedriver.zip -d /usr/local/bin/ \
    && mv /usr/local/bin/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver \
    && chmod +x /usr/local/bin/chromedriver \
    && rm -rf /usr/local/bin/chromedriver-linux64 \
    && rm /tmp/chromedriver.zip


# -------------------------------
# Install python deps
# -------------------------------
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app
WORKDIR /app

ENV PORT=10000

CMD ["python", "main.py"]
