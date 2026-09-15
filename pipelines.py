import hashlib, logging
from pymongo.errors import DuplicateKeyError

log = logging.getLogger(__name__)
_MOCK_CLIENT = None


def _get_mock_client():
    global _MOCK_CLIENT
    if _MOCK_CLIENT is None:
        import mongomock
        _MOCK_CLIENT = mongomock.MongoClient()
        log.info("Created in-memory mongomock client (singleton)")
    return _MOCK_CLIENT


def _content_hash(item):
    key = str(item.get("text", "") or "") + "|" + str(item.get("author", "") or "")
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:24]


class MongoPipeline:
    def __init__(self, uri, db, collection, use_mock):
        self.uri = uri
        self.db_name = db
        self.coll_name = collection
        self.use_mock = use_mock
        self.client = None
        self.collection = None
        self.inserted = 0
        self.duplicates = 0
        self.errors = 0

    @classmethod
    def from_crawler(cls, crawler):
        s = crawler.settings
        return cls(
            uri=s.get("MONGO_URI"),
            db=s.get("MONGO_DB"),
            collection=s.get("MONGO_COLLECTION"),
            use_mock=s.getbool("MONGO_USE_MOCK", False),
        )

    def open_spider(self, spider):
        if self.use_mock:
            self.client = _get_mock_client()
            log.info("MongoPipeline -> mongomock (in-memory)")
        else:
            from pymongo import MongoClient
            self.client = MongoClient(self.uri, serverSelectionTimeoutMS=5000)
            self.client.admin.command("ping")
            log.info("MongoPipeline -> %s", self.uri)

        self.collection = self.client[self.db_name][self.coll_name]
        self.collection.create_index("author")
        self.collection.create_index("tags")

    def close_spider(self, spider):
        stats = spider.crawler.stats
        stats.set_value("mongo/inserted",   self.inserted)
        stats.set_value("mongo/duplicates", self.duplicates)
        stats.set_value("mongo/errors",     self.errors)
        log.info("MongoPipeline summary - inserted=%s duplicates=%s errors=%s",
                 self.inserted, self.duplicates, self.errors)
        if not self.use_mock and self.client is not None:
            self.client.close()

    def process_item(self, item, spider):
        record = dict(item)
        record["_id"] = _content_hash(record)
        try:
            self.collection.insert_one(record)
            self.inserted += 1
        except DuplicateKeyError:
            self.duplicates += 1
        except Exception as e:
            self.errors += 1
            log.error("Insert error for %s: %s", record.get("_id"), e)
        return item
