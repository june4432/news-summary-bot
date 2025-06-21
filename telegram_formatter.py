import re
from collections import defaultdict
from config import notion_url, newsletter_url

# ✅ Markdown V2 이스케이프 함수 (링크 포함 안전 처리)
def escape_markdown_v2(text: str) -> str:
    def escape(s):
        # MarkdownV2 에서 escape가 필요한 문자 전체 처리
        return re.sub(r'([\\_*~`()\[\]<>#+\-=|{}.!])', r'\\\1', s)

    def replace_link(match):
        label = escape(match.group(1))  # 라벨은 escape
        url = match.group(2)  # URL은 그대로 둠
        return f'[{label}]({url})'

    # 링크 먼저 escape (본문 보기 링크처럼)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', replace_link, text)

    # 나머지 텍스트 escape
    return escape(text)

# 제목용 escape (너무 과하지 않게)
def escape_title_markdown_v2(text: str) -> str:
    # *, _, ~, `, [, ], (, ), >, #, +, -, =, |, {, }, . 제외!
    # 실제 문제 되는 것만 골라서 처리 (*, _, ~, ` 등)
    return re.sub(r'([\\_*~`])', r'\\\1', text)

# ✅ 텔레그램 메시지 생성 함수
def build_telegram_message(news_data, max_articles=10, header=None):
    lines = []

    if header:
        lines.append(f"📢 *[{escape_markdown_v2(header)} 뉴스 요약]*\n")

    count = 1
    for article in news_data:
        if count > max_articles:
            break

        title = escape_title_markdown_v2(article.get("title", ""))
        emoji = article.get("emoji", "")
        summary = escape_markdown_v2(article.get("summary", ""))
        url = article.get("url", "")
        tags = article.get("tags", [])

        lines.append(f"*{escape_markdown_v2(str(count))}\\. {escape_markdown_v2(title)} {emoji}*")
        lines.append(f"{summary}")
        if tags:
            tag_line = " ".join(f"\\#{escape_markdown_v2(tag.replace(' ', ''))}" for tag in tags)
            lines.append(tag_line)
        if url:
            safe_full_url = escape_markdown_v2(f"{newsletter_url}/news-click?url={url}")
            lines.append(f"👉 [본문 보기]({safe_full_url})")

        lines.append("")
        count += 1

    # 푸터 링크
    footer_link = f"[지난 뉴스 전체 보기]({notion_url})"
    lines.append(f"📚 {footer_link}")
    return "\n".join(lines)