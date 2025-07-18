import requests
from bs4 import BeautifulSoup, NavigableString, Tag
import re

def is_noise(text):
    """본문이 아닌 광고/스크립트 잡음 제거"""
    noise_keywords = [
        "googletag", "dable", "function(", "cmd.push",
        "setService", "renderWidget", "plugin.min.js",
        "iframe", "script"
    ]
    return any(keyword in text for keyword in noise_keywords)

def clean_article_content_with_images(article_div, start_index=1):
    """
    본문 텍스트 + 이미지 위치 [사진N] 삽입 + 이미지 URL 수집
    """
    content_parts = []
    image_urls = []
    image_count = start_index

    for elem in article_div.descendants:
        if isinstance(elem, Tag):
            if elem.get("class") in [["art_rel"], ["article_copy"]]:
                continue

            if elem.name == "img" and elem.get("src"):
                image_urls.append(elem["src"])
                content_parts.append(f"[사진{image_count}]")
                image_count += 1

        elif isinstance(elem, NavigableString):
            text = elem.strip()
            if text and text != "viewer" and not is_noise(text):
                content_parts.append(text)

    return content_parts, image_urls

def convert_start_block_to_markdown(text):
    """
    start_block\n━\n소제목\nend_block → ### 소제목
    """
    pattern = re.compile(r'start_block\s*[\n\r]+━[\n\r]+(.*?)\s*[\n\r]+end_block', re.DOTALL)

    def repl(match):
        subtitle = match.group(1).strip()
        return f"### {subtitle}"

    return re.sub(pattern, repl, text).strip()

def extract_summary_paragraphs(soup):
    """
    article_summary 안의 <p> 태그들 텍스트 추출
    """
    summary_div = soup.find("div", class_="article_summary")
    if not summary_div:
        return []

    paragraphs = summary_div.find_all("p")
    return [p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)]

def crawl_se_news(url):
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

    soup = BeautifulSoup(response.text, "html.parser")

    # ✅ 제목
    title_tag = soup.find("meta", property="og:title")
    title = title_tag["content"] if title_tag else "제목 없음"

    # ✅ 기사 요약문 + 본문 텍스트 + 이미지
    content_parts = []
    image_urls = []

    # ✨ 요약문 먼저 삽입
    summary_parts = extract_summary_paragraphs(soup)
    content_parts.extend(summary_parts)

    # ✨ 본문 내용
    article_div = soup.find("div", class_="article_view")
    if article_div:
        inner_content, inner_images = clean_article_content_with_images(article_div, start_index=1)
        content_parts += inner_content
        image_urls += inner_images
    else:
        content_parts.append("본문 영역을 찾을 수 없습니다.")

    # ✅ 소제목 변환
    content = "\n".join(content_parts)
    content = convert_start_block_to_markdown(content)

    return {
        "title": title,
        "content": content,
        "images": image_urls,
        "url": url
    }