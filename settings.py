BOT_NAME = "stealth_scrape"
SPIDER_MODULES = ["spiders"]
NEWSPIDER_MODULE = "spiders"

ROBOTSTXT_OBEY = True
CONCURRENT_REQUESTS = 8
CONCURRENT_REQUESTS_PER_DOMAIN = 4
DOWNLOAD_DELAY = 1.2
DOWNLOAD_DELAY_JITTER = 0.5
COOKIES_ENABLED = True
RETRY_ENABLED = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [403, 429, 500, 502, 503, 504]

DOWNLOADER_MIDDLEWARES = {
    "middlewares.RotateUserAgentMiddleware": 400,
    "middlewares.RandomProxyMiddleware": 410,
    "middlewares.StealthHeadersMiddleware": 420,
    "middlewares.BackoffRetryMiddleware": 550,
}

DOWNLOAD_HANDLERS = {
    "http":  "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
PLAYWRIGHT_BROWSER_TYPE = "chromium"
PLAYWRIGHT_LAUNCH_OPTIONS = {
    "headless": True,
    "args": ["--no-sandbox", "--disable-blink-features=AutomationControlled"],
}
PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT = 30000

ITEM_PIPELINES = {
    "pipelines.MongoPipeline": 300,
}
MONGO_URI        = "mongodb://localhost:27017"
MONGO_DB         = "stealth_scrape"
MONGO_COLLECTION = "quotes"
MONGO_USE_MOCK   = True

PROXY_LIST = []
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
