import feedparser

def get_latest_news_urls(rss_url, limit=10):
    feed = feedparser.parse(rss_url)
    return [entry.link for entry in feed.entries[:limit]]