from .crawler_mk import crawl_mk_news
from .crawler_hk import crawl_hk_news
from .crawler_se import crawl_se_news
from .crawler_et import crawl_et_news
from .crawler_tc import crawl_tc_news

# url에 따라 크롤러를 분리하여 호출한다.
def crawl_news(url):
    if "mk.co.kr" in url:
        return crawl_mk_news(url)
    elif "hankyung.com" in url:
        return crawl_hk_news(url)
    elif "sedaily.com" in url:
        return crawl_se_news(url)
    elif "etnews.com" in url:
        return crawl_et_news(url)
    elif "techcrunch.com" in url:
        return crawl_tc_news(url)
    else:
        return {
            "title": "ERROR",
            "content": "지원되지 않는 URL입니다.",
            "images": [],
            "url": url
        }