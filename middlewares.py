import random, time, logging
from fake_useragent import UserAgent

log = logging.getLogger(__name__)


class RotateUserAgentMiddleware:
    def __init__(self, ua):
        self.ua = ua

    @classmethod
    def from_crawler(cls, crawler):
        return cls(UserAgent(browsers=["chrome", "firefox", "edge"],
                             os=["windows", "macos"]))

    def process_request(self, request):
        ua = self.ua.random
        request.headers["User-Agent"] = ua
        request.headers["sec-ch-ua"] = '"' + ua + '"'
        request.headers["sec-ch-ua-mobile"] = "?0"
        request.headers["sec-ch-ua-platform"] = '"Windows"'


class RandomProxyMiddleware:
    def __init__(self, proxies):
        self.proxies = proxies or []
        self.bad = {}
        self.max_fails = 3

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings.getlist("PROXY_LIST"))

    def _alive(self):
        return [p for p in self.proxies if self.bad.get(p, 0) < self.max_fails]

    def process_request(self, request):
        alive = self._alive()
        if not alive:
            return
        request.meta["proxy"] = random.choice(alive)

    def process_exception(self, request, exception):
        proxy = request.meta.get("proxy")
        if proxy:
            self.bad[proxy] = self.bad.get(proxy, 0) + 1
            log.warning("Proxy %s failed (%dx): %s", proxy, self.bad[proxy], exception)
            return request.replace(dont_filter=True)


class StealthHeadersMiddleware:
    def process_request(self, request):
        request.headers.setdefault(
            "Accept",
            "text/html,application/xhtml+xml,application/xml;q=0.9,"
            "image/avif,image/webp,*/*;q=0.8",
        )
        request.headers.setdefault("Accept-Language", "en-US,en;q=0.9")
        request.headers.setdefault("Accept-Encoding", "gzip, deflate, br")
        request.headers.setdefault("DNT", "1")
        request.headers.setdefault("Upgrade-Insecure-Requests", "1")
        request.headers.setdefault("Sec-Fetch-Dest", "document")
        request.headers.setdefault("Sec-Fetch-Mode", "navigate")
        request.headers.setdefault("Sec-Fetch-Site", "none")
        request.headers.setdefault("Sec-Fetch-User", "?1")
        if "Referer" not in request.headers and request.url.count("/") > 3:
            request.headers["Referer"] = "/".join(request.url.split("/")[:3]) + "/"


class BackoffRetryMiddleware:
    MAX_ATTEMPTS = 3

    def process_response(self, request, response):
        if response.status in (403, 429, 503):
            attempt = request.meta.get("backoff_attempt", 0) + 1
            if attempt <= self.MAX_ATTEMPTS:
                delay = 2 ** attempt
                log.warning("Blocked %s - backing off %ss (attempt %s)",
                            response.status, delay, attempt)
                time.sleep(delay)
                new_req = request.copy()
                new_req.meta["backoff_attempt"] = attempt
                new_req.dont_filter = True
                return new_req
        return response
