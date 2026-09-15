
# ─── Base image: Playwright + Chromium pre-installed ────────────
# Must match the `playwright` version in requirements.txt
FROM mcr.microsoft.com/playwright/python:v1.47.0-jammy

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    SCRAPY_SETTINGS_MODULE=settings \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# System deps (minimal — Playwright base already has most)
RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

# Python deps first (better layer caching)
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Project files
COPY . .

# Run as non-root
RUN useradd --create-home --shell /bin/bash scraper \
    && chown -R scraper:scraper /app
USER scraper

# Runtime dirs
RUN mkdir -p /app/output /app/logs

# Default command — override with `docker run ... python scripts/run_crawl.py <spider>`
ENTRYPOINT ["python", "scripts/run_crawl.py"]
CMD ["quotes_static"]
