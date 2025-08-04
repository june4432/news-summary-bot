#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

# 프로젝트 루트 디렉토리를 Python path에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from batch.crawler.crawler import crawl_news

def test_techcrunch():
    """TechCrunch 크롤러 테스트"""
    url = "https://techcrunch.com/2025/08/01/a-backlog-at-the-commerce-department-is-reportedly-stalling-nvidias-h20-chip-licenses/"
    
    print("🚀 TechCrunch 크롤링 테스트 시작...")
    print(f"📄 URL: {url}")
    print("-" * 80)
    
    try:
        result = crawl_news(url)
        
        print("✅ 크롤링 결과:")
        print(f"📰 제목: {result['title']}")
        print(f"📷 이미지 수: {len(result['images'])} 개")
        print(f"📝 본문 길이: {len(result['content'])} 글자")
        print("-" * 80)
        
        print("📄 본문 내용:")
        print(result['content'])
        print("-" * 80)
        
        if result['images']:
            print("📷 이미지 URL들:")
            for i, img_url in enumerate(result['images'], 1):
                print(f"  {i}. {img_url}")
        else:
            print("📷 이미지가 없습니다.")
            
        print("-" * 80)
        print("✅ 테스트 완료!")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_techcrunch() 