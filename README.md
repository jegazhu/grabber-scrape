# Stealth Scrape

A production-grade Python web scraping toolkit demonstrating:

| Capability | Where |
|---|---|
| Scrapy | spiders/ - static + JS-rendered targets |
| Proxy rotation | middlewares.RandomProxyMiddleware |
| Anti-bot navigation | UA rotation, stealth headers, exponential backoff |
| Headless browsers | scrapy-playwright + standalone Playwright + Selenium |
| MongoDB storage | pipelines.MongoPipeline - content-hash dedup |
| Containerized | Playwright base image, non-root runtime |
| CI/CD | Nightly crawl via GitHub Actions -> Atlas |

## Quickstart

    docker compose up --build

## Manual run

    pip install -r requirements.txt
    playwright install chromium
    python scripts/run_crawl.py quotes_js --mock

## Ethics

Respect robots.txt and site ToS. Practice targets used here
(toscrape.com, httpbin.org) are explicitly built for scraping.
