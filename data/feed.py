import feedparser
import threading
import time

class Feed:
    def __init__(self, url):
        self._url = url
        self._items = []
        self._interval = 300
        self._lock = threading.Lock()
        self._running = True

        self._thread = threading.Thread(target=self.poll)
        self._thread.start()

    def poll(self):
        while self._running:
            feed = feedparser.parse(self._url)

            with self._lock:
                for e in feed.entries:
                    pub = e.published
                    if not any(item.published == pub for item in self._items):
                        self._items.append(e)

            for _ in range(300):
                if not self._running:
                    break
                time.sleep(1)

    def getItems(self):
        with self._lock:
            return list(self._items)

    def stopPoll(self):
        self._running = False
        self._thread.join()

class FeedManager:
    def __init__(self):
        self.feeds = {}

    def addFeed(self, name, url):
        if name in self.feeds:
            self.feeds[name]._url = url
            return
    
        feed = Feed(url)
        self.feeds[name] = feed

    def getFeedItems(self, name):
        if name not in self.feeds:
            raise ValueError(f"No feed with name {name} exists.")
        
        return self.feeds[name].getItems()
    
    def refreshFeeds(self):
        for name, feed in self.feeds.items():
            feed.stopPoll()
            new_feed = Feed(feed._url)
            self.feeds[name] = new_feed

    def stopAllFeeds(self):
        for feed in self.feeds.values():
            feed.stopPoll()

    def hasFeed(self, name):
        return name in self.feeds