
import scrapy
from scrapy_playwright.page import PageMethod

class QuotesJSSpider(scrapy.Spider):
    name = "quotes_js"
    start_urls = ["https://quotes.toscrape.com/js/"]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                meta={
                    "playwright": True,
                    "playwright_include_page": False,
                    "playwright_page_methods": [
                        PageMethod("wait_for_load_state", "networkidle"),
                        PageMethod("wait_for_selector", "div.quote", timeout=45000),
                        # Uncomment to block images/css → faster:
                        # PageMethod("route", "**/*.{png,jpg,css}", lambda r: r.abort()),
                    ],
                },
                errback=self.errback,
            )

    async def errback(self, failure):
        page = failure.request.meta.get("playwright_page")
        if page:
            await page.close()

    def parse(self, response):
        for q in response.css("div.quote"):
            yield {
                "text":   q.css("span.text::text").get(),
                "author": q.css("small.author::text").get(),
                "tags":   q.css("div.tags a.tag::text").getall(),
                "source": "playwright",
            }
        nxt = response.css("li.next a::attr(href)").get()
        if nxt:
            yield response.follow(nxt, self.parse,
                                  meta={"playwright": True,
                                        "playwright_page_methods":
                                            [PageMethod("wait_for_selector", "div.quote")]})
