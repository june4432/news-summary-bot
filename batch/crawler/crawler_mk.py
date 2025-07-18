from bs4 import BeautifulSoup
import requests
import datetime
from batch.common.log import logger

#매일경제 뉴스 크롤러
def crawl_mk_news(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    title = soup.find('title').get_text(strip=True) if soup.find('title') else "Title not found"
    content_div = soup.find('div', class_='news_cnt_detail_wrap')
    
    if ' - 매일경제' in title:
        title = title.replace(' - 매일경제', '')

    if ' | 한국경제' in title:
        title = title.replace(' | 한국경제', '')

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