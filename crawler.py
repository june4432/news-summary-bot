from crawler_mk import crawl_mk_news
from crawler_hk import crawl_hk_news

def crawl_news(url):
    if "mk.co.kr" in url:
        return crawl_mk_news(url)
    elif "hankyung.com" in url:
        return crawl_hk_news(url)
    else:
        return {
            "title": "ERROR",
            "content": "지원되지 않는 URL입니다.",
            "images": [],
            "url": url
        }