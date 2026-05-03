FROM mcr.microsoft.com/playwright/python:v1.48.0-jammy

WORKDIR /app

ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PIP_NO_CACHE_DIR=1 PLAYWRIGHT_BROWSERS_PATH=/ms-playwright DEBIAN_FRONTEND=noninteractive PORT=10000

RUN apt-get update && apt-get install -y wget gnupg ca-certificates && \
    wget -q -O /tmp/chrome-key.pub https://dl.google.com/linux/linux_signing_key.pub && \
    gpg --dearmor < /tmp/chrome-key.pub > /usr/share/keyrings/google-chrome.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && apt-get install -y google-chrome-stable && \
    rm -rf /var/lib/apt/lists/* /tmp/chrome-key.pub

COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 10000

CMD ["sh", "-c", "gunicorn app:app --worker-class gthread --workers 1 --threads 8 --timeout 0 --graceful-timeout 1800 --keep-alive 1800 --bind 0.0.0.0:${PORT:-10000} --access-logfile - --error-logfile -"]