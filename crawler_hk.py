import requests
from bs4 import BeautifulSoup

def crawl_hk_news(url):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except Exception as e:
        return {
            "title": "ERROR",
            "content": f"요청 실패: {e}",
            "images": [],
            "url": url
        }

    soup = BeautifulSoup(response.content, "html.parser")

    # ✅ 제목
    title_tag = soup.find("h1", class_="headline")
    title = title_tag.get_text(strip=True) if title_tag else "Title not found"

    content_parts = []
    image_urls = []
    image_count = 1

    # ✅ 요약 박스 추출
    summary_boxes = soup.select(".article-body-wrap .summary")
    for box in summary_boxes:
        text = box.get_text(separator="\n", strip=True)
        if text:
            content_parts.append(text)

    # ✅ 본문 추출
    content_div = soup.find("div", id="articletxt")
    if content_div:
        # 이미지
        img_tag = content_div.find("img")
        if img_tag and img_tag.get("src"):
            content_parts.append(f"[사진{image_count}]")
            image_urls.append(img_tag["src"])
            image_count += 1

        # 본문 텍스트
        text = BeautifulSoup(content_div.decode_contents(), "html.parser").get_text(separator="\n", strip=True)
        content_parts.append(text)
    else:
        content_parts.append("Content not found")

    return {
        "title": title,
        "content": "\n".join(content_parts),
        "images": image_urls,
        "url": url
    }