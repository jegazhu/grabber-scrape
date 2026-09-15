
#!/usr/bin/env python3
"""Run a Scrapy spider inside a fresh process. CI-friendly.

Usage:
    python scripts/run_crawl.py <spider_name> [--mongo-uri URI] [--mock]

Exit codes:
    0 = success (>=1 item scraped)
    1 = crawl error
    2 = zero items scraped (treated as failure in CI)
"""
import argparse, json, os, pathlib, sys, time

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("spider", help="Spider name, e.g. quotes_static or quotes_js")
    p.add_argument("--mongo-uri", default=os.environ.get("MONGO_URI", ""))
    p.add_argument("--mongo-db",  default=os.environ.get("MONGO_DB", "stealth_scrape"))
    p.add_argument("--mock", action="store_true",
                   help="Use in-memory mongomock instead of a real MongoDB")
    p.add_argument("--out", default="output")
    return p.parse_args()


def main():
    args = parse_args()
    os.environ["SCRAPY_SETTINGS_MODULE"] = "settings"

    out_dir = ROOT / args.out
    out_dir.mkdir(exist_ok=True)
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    feed = out_dir / f"{args.spider}_{stamp}.json"

    settings = get_project_settings()
    settings.set("FEEDS", {str(feed): {"format": "json", "overwrite": True}})

    if args.mongo_uri:
        settings.set("MONGO_URI", args.mongo_uri)
        settings.set("MONGO_DB", args.mongo_db)
        settings.set("MONGO_USE_MOCK", False)
    else:
        settings.set("MONGO_USE_MOCK", args.mock)

    proc = CrawlerProcess(settings)
    crawler = proc.create_crawler(args.spider)
    proc.crawl(crawler)
    proc.start()   # blocks, safe — we're in our own process

    stats = crawler.stats.get_stats()
    item_count = stats.get("item_scraped_count", 0)
    dupe_count = stats.get("mongo/duplicates", 0)
    insert_count = stats.get("mongo/inserted", 0)

    summary = {
        "spider":     args.spider,
        "items":      item_count,
        "inserted":   insert_count,
        "duplicates": dupe_count,
        "feed":       str(feed),
    }
    print("CRAWL_SUMMARY=" + json.dumps(summary))
    return 0 if item_count > 0 else 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"CRAWL_ERROR: {type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(1)
