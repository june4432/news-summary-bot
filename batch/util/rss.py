import feedparser
import json
from batch.common.config import rss_sources_file, rss_batch_count

# RSS Source에서 RSS URL 목록을 가지고 온다.
def load_rss_sources():
    with open(rss_sources_file, "r", encoding="utf-8") as f:
        sources = json.load(f)
    grouped = {}
    for item in sources:
        grouped.setdefault(item["source"], []).append(item["category"])
    return grouped

# RSS URL을 통해서 최근 10개의 기사 목록을 가져오는 기능
def get_latest_news_urls(rss_url, limit=int(rss_batch_count)):
    feed = feedparser.parse(rss_url)
    return [entry.link for entry in feed.entries[:limit]]
