from bs4 import BeautifulSoup
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from log import logger  # 로그 모듈이 있다면 사용

# 개별 뉴스 크롤링 함수
def crawl_news(url, session=None):    
    session = session or requests.Session()
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = session.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # 4xx, 5xx 에러 발생 시 예외 처리

        soup = BeautifulSoup(response.content, 'html.parser')

        title = soup.find('title').get_text(strip=True) if soup.find('title') else "Title not found"
        content_div = soup.find('div', class_='news_cnt_detail_wrap')

        # 타이틀 정리
        if ' - 매일경제' in title:
            title = title.replace(' - 매일경제', '')
        if ' | 한국경제' in title:
            title = title.replace(' | 한국경제', '')

        # 본문 및 이미지 수집
        content_with_images = []
        image_urls = []
        if content_div:
            elements = content_div.find_all(['p', 'img'])
            image_counter = 1
            for element in elements:
                if element.name == 'p':
                    content_with_images.append(element.get_text(strip=True))
                elif element.name == 'img' and element.get('src'):
                    content_with_images.append(f"[사진{image_counter}]")
                    image_urls.append(element['src'])
                    image_counter += 1
        else:
            content_with_images = ["Content not found"]

        return {
            "title": title,
            "content": "\n".join(content_with_images),
            "images": image_urls,
            "url": url
        }

    except Exception as e:
        logger.warning(f"❌ 크롤링 실패: {url} - {e}")
        return {
            "title": "ERROR",
            "content": str(e),
            "images": [],
            "url": url
        }

# 병렬 뉴스 크롤링 함수
def crawl_multiple_news(urls, max_workers=10):
    # session = requests.Session()
    results = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # futures = [executor.submit(crawl_news, url, session) for url in urls]
        futures = [executor.submit(crawl_news, url) for url in urls]
        for future in as_completed(futures):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                logger.warning(f"❌ 스레드 처리 중 예외 발생: {e}")

    return results