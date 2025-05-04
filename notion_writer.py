### 📁 notion_writer.py
import requests
from datetime import datetime, timedelta, timezone
from log import logger

def build_children_blocks_from_content(article):
    paragraphs = article["content"].split("\n")
    image_urls = article.get("images", [])
    blocks = []
    image_counter = 1

    for paragraph in paragraphs:
        if paragraph.strip().startswith(f"[사진{image_counter}]") and len(image_urls) >= image_counter:
            blocks.append({
                "object": "block",
                "type": "image",
                "image": {
                    "type": "external",
                    "external": {
                        "url": image_urls[image_counter - 1]
                    }
                }
            })
            image_counter += 1
        elif paragraph.strip():
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": paragraph}}]
                }
            })
    return blocks

def save_to_notion(article, notion_token, notion_database_id):
    url = "https://api.notion.com/v1/pages"

    headers = {
        "Authorization": f"Bearer {notion_token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }

    kst = timezone(timedelta(hours=9))
    scrap_time = datetime.now(kst).isoformat()

    properties = {
        "제목": {
            "title": [{"text": {"content": article['title']}}]
        },
        "요약": {
            "rich_text": [{"text": {"content": article['summary']}}]
        },
        "기사 링크": {
            "url": article['url']
        },
        "스크랩 시간": {
            "date": {"start": scrap_time}
        },
        "카테고리": {
            "select": {"name": article.get("category", "미분류")}
        }
    }

    if 'tags' in article and article['tags']:
        properties["태그"] = {
            "multi_select": [{"name": tag} for tag in article['tags']]
        }

    children = build_children_blocks_from_content(article)

    data = {
        "parent": {"database_id": notion_database_id},
        "icon": {
            "type": "emoji",
            "emoji": "📰"
        },        
        "properties": properties,
        "children": children
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        logger.info(f"✅ Notion 저장 성공: {article['title']}")
    else:
        logger.error(f"❌ Notion 저장 실패: {article['title']}", exc_info=True)
        logger.error(f"{response.status_code} {response.text}", exc_info=True)

def get_existing_urls_from_notion(notion_token, notion_database_id):
    url = f"https://api.notion.com/v1/databases/{notion_database_id}/query"
    headers = {
        "Authorization": f"Bearer {notion_token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    existing_urls = set()
    has_more = True
    next_cursor = None

    while has_more:
        body = {"start_cursor": next_cursor} if next_cursor else {}
        response = requests.post(url, headers=headers, json=body)
        data = response.json()

        for result in data.get("results", []):
            props = result.get("properties", {})
            url_prop = props.get("기사 링크", {}).get("url")
            if url_prop:
                existing_urls.add(url_prop)

        has_more = data.get("has_more", False)
        next_cursor = data.get("next_cursor", None)

    return existing_urls        