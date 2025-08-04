#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'batch', 'crawler'))

from crawler_et import crawl_et_news

def test_etnews_crawler():
    # 테스트할 URL
    test_url = "https://www.etnews.com/20250729000290"
    
    print("🔍 전자신문 크롤러 테스트 시작...")
    print(f"📰 URL: {test_url}")
    print("-" * 80)
    
    # 크롤링 실행
    result = crawl_et_news(test_url)
    
    # 결과 출력
    print(f"📰 제목: {result['title']}")
    print("-" * 80)
    
    print(f"📷 이미지 개수: {len(result['images'])}")
    for i, img_url in enumerate(result['images'], 1):
        print(f"  [사진{i}] {img_url}")
    print("-" * 80)
    
    print("📝 본문 내용:")
    print(result['content'])
    print("-" * 80)
    
    print(f"🔗 원본 URL: {result['url']}")
    
    # 크롤링 성공 여부 확인
    if result['title'] != "ERROR" and result['title'] != "Title not found":
        print("\n✅ 크롤링 성공!")
        
        # 사진 표시 형태 확인
        if "[사진1]" in result['content']:
            print("✅ 사진 표시 형태도 올바름: [사진1] 형태로 표시됨")
        else:
            print("⚠️ 사진 표시 형태 확인 필요")
    else:
        print("\n❌ 크롤링 실패!")
        
    return result

if __name__ == "__main__":
    test_etnews_crawler() 