FROM python:3.13-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    SCRAPY_SETTINGS_MODULE=settings \
    DEBIAN_FRONTEND=noninteractive \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

WORKDIR /app

# System deps for Chromium + fonts
RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates curl gnupg \
        # Chromium runtime libs
        libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 \
        libcups2 libdrm2 libdbus-1-3 libxkbcommon0 \
        libatspi2.0-0 libxcomposite1 libxdamage1 libxfixes3 \
        libxrandr2 libgbm1 libpango-1.0-0 libcairo2 libasound2 \
        # Fonts (avoid boxes rendering as tofu)
        fonts-liberation fonts-noto-color-emoji \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Install the Chromium build that matches THIS playwright pip version
RUN python -m playwright install chromium

COPY . .

RUN useradd --create-home --shell /bin/bash scraper \
    && chown -R scraper:scraper /app /ms-playwright
USER scraper

RUN mkdir -p /app/output /app/logs

ENTRYPOINT ["python", "scripts/run_crawl.py"]
CMD ["quotes_static"]
