### 📁 notion_writer.py
import requests
from datetime import datetime, timedelta, timezone
from batch.common.log import logger
from batch.common.config import notion_database_id, notion_token

# 데이터 베이스 안에 들어갈 속 글을 만든다.
def build_children_blocks_from_content(article):
    paragraphs = article["content"].split("\n")
    image_urls = article.get("images", [])
    blocks = []
    image_counter = 1

    # 🌍 영어 기사인 경우 원본 내용도 추가
    if article.get("language") == "english" and article.get("original_content"):
        blocks.append({
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{"type": "text", "text": {"content": "📄 번역된 내용"}}]
            }
        })

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
    
    # 🌍 영어 기사인 경우 원본 내용 추가
    if article.get("language") == "english" and article.get("original_content"):
        blocks.append({
            "object": "block",
            "type": "divider",
            "divider": {}
        })
        
        blocks.append({
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{"type": "text", "text": {"content": "🌍 원본 내용 (English)"}}]
            }
        })
        
        original_paragraphs = article["original_content"].split("\n")
        for paragraph in original_paragraphs:
            if paragraph.strip():
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": paragraph}}]
                    }
                })
    
    return blocks

# 노션에 데이터를 저장한다.
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
        },
        "신문사": {
            "select": {
                "name": article.get("source", "미지정")
            }
        },
        "광고성 여부": {
            "checkbox": article.get("is_ad", False)
        },
        "키워드": {
            "rich_text": [{"text": {"content": article['keyword']}}]
        },
        "분위기": {
            "select": {"name": article.get("mood", "미분류")}
        }
    }

    # 🌍 영어 기사인 경우 원본 제목과 내용도 저장
    if article.get("language") == "english":
        if article.get("original_title"):
            properties["원본 제목"] = {
                "rich_text": [{"text": {"content": article['original_title']}}]
            }
        
        if article.get("translated_title"):
            properties["번역된 제목"] = {
                "rich_text": [{"text": {"content": article['translated_title']}}]
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

# 저장되어 있는 기사 url을 가지고 온다.
def get_existing_urls_from_notion():
    url = f"https://api.notion.com/v1/databases/{notion_database_id}/query"
    headers = {
        "Authorization": f"Bearer {notion_token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }

    since = (datetime.utcnow() - timedelta(days=2)).isoformat()  # ✅ 최근 2일 기준

    body = {
        "filter": {
            "property": "스크랩 시간",  # ✅ 너의 DB에 있는 날짜 속성 이름
            "date": {
                "after": since
            }
        },
        "page_size": 100
    }

    existing_urls = set()
    has_more = True
    next_cursor = None

    while has_more:
        if next_cursor:
            body["start_cursor"] = next_cursor

        response = requests.post(url, headers=headers, json=body)
        data = response.json()

        for result in data.get("results", []):
            props = result.get("properties", {})
            url_prop = props.get("기사 링크", {}).get("url")  # ✅ 너가 사용하는 URL 필드명 유지
            if url_prop:
                existing_urls.add(url_prop)

        has_more = data.get("has_more", False)
        next_cursor = data.get("next_cursor", None)

    return existing_urls


# 메일에서 뉴스링크 클릭 시 - 본문 링크로 노션페이지id 가져오기
def get_page_id_by_url(article_url):
    #print(f"🔍 [조회 시작] URL 검색: {article_url}")
    #print(f"🔍 [조회 시작] URL 검색: {article_url}")

    url = f"https://api.notion.com/v1/databases/{notion_database_id}/query"
    headers = {
        "Authorization": f"Bearer {notion_token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }

    has_more = True
    next_cursor = None

    while has_more:
        payload = {"start_cursor": next_cursor} if next_cursor else {}

        response = requests.post(url, headers=headers, json=payload)
        data = response.json()
        #print("📦 Notion 응답 구조:\n", json.dumps(data, indent=2, ensure_ascii=False))

        for result in data.get("results", []):
            props = result.get("properties", {})
            stored_url = props.get("기사 링크", {}).get("url")

            #print(f"🔎 Notion URL 확인 중: {stored_url}")
            stored_url = props.get("기사 링크", {}).get("url")
            if stored_url and stored_url.rstrip('/') == article_url.rstrip('/'):
                print(f"🎯 매치 성공! page_id = {result['id']}")
                return result["id"]

        has_more = data.get("has_more", False)
        next_cursor = data.get("next_cursor", None)

    print(f"❌ 매치 실패 - URL이 DB에 존재하지 않음")
    return None

# 메일에서 뉴스링크 클릭 시 - 조회수 증가
def increment_view_count(page_id):
    print(f"🆙 조회수 증가 시도 중... 페이지 ID: {page_id}")

    headers = {
        "Authorization": f"Bearer {notion_token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }

    try:
        res = requests.get(f"https://api.notion.com/v1/pages/{page_id}", headers=headers)
        res.raise_for_status()
        props = res.json()["properties"]
        curr_raw = props.get("조회수", {}).get("number", 0)
        curr_count = curr_raw if curr_raw is not None else 0

        print(f"👁 기존 조회수: {curr_count}")

        data = {
            "properties": {
                "조회수": {"number": curr_count + 1}
            }
        }

        patch_res = requests.patch(f"https://api.notion.com/v1/pages/{page_id}", headers=headers, json=data)
        patch_res.raise_for_status()
        print(f"✅ 조회수 업데이트 완료! → {curr_count + 1}")

    except Exception as e:
        print(f"❌ 조회수 업데이트 실패: {e}")