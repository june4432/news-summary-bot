#!/usr/bin/env python3
"""
노션 블록 생성 테스트 스크립트
TechCrunch 기사의 블록 구조가 요구사항에 맞게 생성되는지 확인
"""

import sys
import os

# 프로젝트 루트를 Python path에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from batch.notion_writer.notion_writer import build_children_blocks_from_content

def test_notion_blocks():
    """노션 블록 생성 테스트"""
    
    # 테스트용 TechCrunch 기사 데이터 (번역된 내용 포함)
    test_article = {
        "language": "english",
        "original_title": "Inside OpenAI's quest to make AI do anything for you",
        "original_content": "Shortly after Hunter Lightman joined OpenAI as a researcher in 2022, he watched his colleagues launch ChatGPT.\n\nMeanwhile, Lightman quietly worked on a team teaching OpenAI's models to solve high school math competitions.\n\nToday that team, known as MathGen, is considered instrumental to OpenAI's industry-leading effort.",
        "translated_title": "OpenAI의 AI가 당신을 위해 무엇이든 할 수 있도록 만드는 여정",
        "translated_content": "2022년 헌터 라이트만이 OpenAI의 연구원으로 합류한 직후, 그는 동료들이 ChatGPT를 출시하는 것을 지켜봤습니다.\n\n한편, 라이트만은 조용히 OpenAI의 모델들이 고등학교 수학 경시대회 문제를 해결하도록 가르치는 팀에서 일했습니다.\n\n오늘날 MathGen으로 알려진 그 팀은 OpenAI의 업계 선도적인 노력에 핵심적인 역할을 한다고 여겨집니다.",
        "title": "OpenAI의 AI가 당신을 위해 무엇이든 할 수 있도록 만드는 여정",  # main.py에서 번역된 제목으로 설정됨
        "content": "2022년 헌터 라이트만이 OpenAI의 연구원으로 합류한 직후, 그는 동료들이 ChatGPT를 출시하는 것을 지켜봤습니다.\n\n한편, 라이트만은 조용히 OpenAI의 모델들이 고등학교 수학 경시대회 문제를 해결하도록 가르치는 팀에서 일했습니다.\n\n오늘날 MathGen으로 알려진 그 팀은 OpenAI의 업계 선도적인 노력에 핵심적인 역할을 한다고 여겨집니다.",  # main.py에서 번역된 내용으로 설정됨
        "images": ["https://example.com/image1.jpg"],
        "url": "https://techcrunch.com/test-article"
    }
    
    print("🔍 노션 블록 생성 테스트 시작")
    print(f"📄 원문 제목: {test_article['original_title']}")
    print(f"📄 번역 제목: {test_article['translated_title']}")
    print("="*80)
    
    try:
        # 블록 생성 테스트
        blocks = build_children_blocks_from_content(test_article)
        
        print("📦 생성된 블록 요약:")
        print("-"*60)
        
        # H2 블록만 먼저 출력
        h2_count = 0
        for i, block in enumerate(blocks, 1):
            if block.get("type") == "heading_2":
                content = block["heading_2"]["rich_text"][0]["text"]["content"]
                h2_count += 1
                print(f"{i:2}. [H2] {content}")
        
        print(f"\n📄 전체 블록 개요:")
        block_summary = {}
        for block in blocks:
            block_type = block.get("type", "unknown")
            block_summary[block_type] = block_summary.get(block_type, 0) + 1
        
        for block_type, count in block_summary.items():
            print(f"   - {block_type}: {count}개")
        
        print(f"   - 총 블록 수: {len(blocks)}개")
        print("="*60)
        
        # 구조 검증
        print("\n✅ 구조 검증:")
        h2_blocks = [i for i, block in enumerate(blocks) if block.get("type") == "heading_2"]
        
        if len(h2_blocks) >= 2:
            print(f"   - 번역된 제목 H2: {blocks[h2_blocks[0]]['heading_2']['rich_text'][0]['text']['content']}")
            print(f"   - 원문 제목 H2: {blocks[h2_blocks[1]]['heading_2']['rich_text'][0]['text']['content']}")
            print("   ✅ 제목 구조 올바름")
        else:
            print("   ❌ H2 블록이 부족합니다")
        
        divider_exists = any(block.get("type") == "divider" for block in blocks)
        print(f"   - 구분선 존재: {'✅' if divider_exists else '❌'}")
        
        if len(blocks) <= 100:
            print(f"   - 블록 개수 제한: ✅ ({len(blocks)}/100)")
        else:
            print(f"   - 블록 개수 제한: ❌ ({len(blocks)}/100)")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_notion_blocks()