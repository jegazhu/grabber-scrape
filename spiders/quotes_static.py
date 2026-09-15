
import scrapy

class QuotesSpider(scrapy.Spider):
    name = "quotes_static"
    start_urls = ["https://quotes.toscrape.com/"]

    custom_settings = {"DOWNLOAD_DELAY": 0.5}

    def parse(self, response):
        for q in response.css("div.quote"):
            yield {
                "text":   q.css("span.text::text").get(),
                "author": q.css("small.author::text").get(),
                "tags":   q.css("div.tags a.tag::text").getall(),
            }
        nxt = response.css("li.next a::attr(href)").get()
        if nxt:
            yield response.follow(nxt, self.parse)
