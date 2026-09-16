FROM mcr.microsoft.com/playwright/python:v1.63.0-noble

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    SCRAPY_SETTINGS_MODULE=settings \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

RUN useradd --create-home --shell /bin/bash scraper \
    && chown -R scraper:scraper /app
USER scraper

RUN mkdir -p /app/output /app/logs

ENTRYPOINT ["python", "scripts/run_crawl.py"]
CMD ["quotes_static"]
