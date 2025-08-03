import requests
import re
from bs4 import BeautifulSoup

# TechCrunch 뉴스 크롤러
def crawl_tc_news(url):
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

    # ✅ 제목 추출
    title_tag = soup.find("h1", class_="wp-block-post-title")
    if not title_tag:
        # 다른 패턴의 제목 태그 시도
        title_tag = soup.find("h1") or soup.find("title")
    
    title = title_tag.get_text(strip=True) if title_tag else "Title not found"
    
    # TechCrunch에서 사이트명 제거
    if "| TechCrunch" in title:
        title = title.replace("| TechCrunch", "").strip()

    content_parts = []
    image_urls = []
    image_count = 1

    # ✅ 본문 추출 - TechCrunch 구조에 맞춰 div.entry-content에서 추출
    content_div = soup.select_one("div.entry-content")
    
    if content_div:
        # 대표 이미지만 처리 (wp-block-post-featured-image 클래스)
        featured_image_figure = soup.find("figure", class_="wp-block-post-featured-image")
        if featured_image_figure:
            img_tag = featured_image_figure.find("img")
            if img_tag and img_tag.get("src"):
                src = img_tag.get("src")
                alt = img_tag.get("alt", "Featured Image")
                
                image_urls.append(src)
                # 본문에 사진 표시 추가
                content_parts.append(f"[사진{image_count}]")
                image_count += 1

        # 본문 텍스트 추출 - 직접 텍스트 추출
        # 불필요한 요소들 제거
        for unwanted in content_div.find_all([
            "script", "style", "aside", "nav", "header", "footer",
            "figure", "img"  # 이미지는 이미 처리했으므로 제거
        ]):
            unwanted.decompose()
        
        # 전체 텍스트를 가져온 후 정리
        full_text = content_div.get_text(separator="\n", strip=True)
        
        # 줄바꿈으로 분리해서 의미있는 문장들만 추출
        lines = []
        for line in full_text.split('\n'):
            line = line.strip()
            # 의미있는 텍스트만 포함 (길이 체크 및 특정 패턴 제외)
            if (line and len(line) > 15 and 
                not line.lower().startswith(('image credits:', 'posted:', 'topics')) and
                not line.endswith('ago') and
                not line.isdigit()):
                lines.append(line)
        
        # 중복 제거하면서 순서 유지
        seen = set()
        unique_lines = []
        for line in lines:
            if line not in seen:
                seen.add(line)
                unique_lines.append(line)
        
        content_parts.extend(unique_lines)
    
    # 본문이 추출되지 않은 경우 대안 시도
    if not content_parts or (len(content_parts) == 1 and content_parts[0] == ""):
        # 전체 article 태그에서 추출 시도
        article = soup.find("article")
        if article:
            # 헤더, 푸터, 사이드바 등 제거
            for unwanted in article.find_all(["header", "footer", "aside", "nav", "script", "style"]):
                unwanted.decompose()
            
            paragraphs = article.find_all("p")
            for p in paragraphs:
                text = p.get_text(strip=True)
                if text and len(text) > 10:
                    content_parts.append(text)

    # 최종적으로 내용이 없으면 기본 메시지
    if not content_parts:
        content_parts = ["Content not found"]

    return {
        "title": title,
        "content": "\n\n".join(content_parts),
        "images": image_urls,
        "url": url
    } 