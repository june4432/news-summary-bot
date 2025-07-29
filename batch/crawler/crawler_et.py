import requests
import re
from bs4 import BeautifulSoup

# 전자신문 뉴스 크롤러
def crawl_et_news(url):
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
    title_tag = soup.find("h2", id="article_title_h2")
    title = title_tag.get_text(strip=True) if title_tag else "Title not found"

    content_parts = []
    image_urls = []
    image_count = 1

    # ✅ 본문 추출
    content_div = soup.find("div", class_="article_body", id="articleBody")
    if content_div:
        # 이미지 처리
        for img_figure in content_div.find_all("figure", class_="article_image"):
            img_tag = img_figure.find("img")
            if img_tag and img_tag.get("src"):
                # 이미지 URL 추가
                image_urls.append(img_tag["src"])
                
                # 캡션 추출
                caption_tag = img_figure.find("figcaption", class_="caption")
                caption = caption_tag.get_text(strip=True) if caption_tag else f"사진{image_count}"
                
                # 본문에 사진 표시 추가
                content_parts.append(f"[사진{image_count}: {caption}]")
                image_count += 1

        # 본문 텍스트 추출 (p 태그 내용)
        p_tag = content_div.find("p")
        if p_tag:
            # 이미지 figure는 제외하고 텍스트만 추출
            for figure in p_tag.find_all("figure"):
                figure.decompose()  # figure 태그 제거
            
            # span 태그 중 광고 관련 제거
            for span in p_tag.find_all("span", class_="ad_newsroom1234"):
                span.decompose()
            
            # <br /> 태그를 줄바꿈으로 변환하면서 텍스트 추출
            html_content = str(p_tag)
            # <br>, <br/>, <br /> 등 모든 형태의 br 태그를 줄바꿈으로 변환
            html_content = re.sub(r'<br\s*/?>', '\n', html_content, flags=re.IGNORECASE)
            
            # BeautifulSoup으로 다시 파싱해서 텍스트만 추출
            cleaned_soup = BeautifulSoup(html_content, "html.parser")
            text = cleaned_soup.get_text(separator="", strip=True)
            
            # 연속된 줄바꿈을 정리하고 문단 구분
            lines = []
            for line in text.split('\n'):
                line = line.strip()
                if line:  # 빈 줄이 아닌 경우만 추가
                    lines.append(line)
            
            # 줄바꿈으로 구분된 텍스트 생성
            text = '\n\n'.join(lines)
            content_parts.append(text)
        else:
            content_parts.append("Content not found")
    else:
        content_parts.append("Content not found")

    return {
        "title": title,
        "content": "\n".join(content_parts),
        "images": image_urls,
        "url": url
    } 