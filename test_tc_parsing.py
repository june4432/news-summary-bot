#!/usr/bin/env python3
"""
TechCrunch 파싱 테스트 스크립트
방금 수정한 줄바꿈 문제가 해결되었는지 확인
"""

import sys
import os

# 프로젝트 루트를 Python path에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from batch.crawler.crawler_tc import crawl_tc_news

def test_tc_parsing():
    """테크크런치 파싱 테스트"""
    
    # 테스트할 URL
    url = "https://techcrunch.com/2025/08/03/inside-openais-quest-to-make-ai-do-anything-for-you/"
    
    print("🔍 TechCrunch 파싱 테스트 시작")
    print(f"📄 URL: {url}")
    print("="*80)
    
    try:
        # 크롤링 실행
        result = crawl_tc_news(url)
        
        print("📰 제목:")
        print(f"   {result['title']}")
        print()
        
        print("🔗 URL:")
        print(f"   {result['url']}")
        print()
        
        print("🖼️ 이미지 개수:")
        print(f"   {len(result['images'])}개")
        if result['images']:
            for i, img in enumerate(result['images'], 1):
                print(f"   {i}. {img}")
        print()
        
        print("📝 본문 내용 (전체):")
        print("-"*60)
        
        # 본문을 문장별로 나누어서 전체 출력
        content_lines = result['content'].split('\n\n')
        for i, line in enumerate(content_lines, 1):
            if line.strip():
                print(f"{i:2}. {line}")
                print()
        
        print("="*80)
        print("📊 파싱 결과 통계:")
        print(f"   - 제목 길이: {len(result['title'])} 글자")
        print(f"   - 본문 문장 수: {len(content_lines)} 개")
        print(f"   - 전체 본문 길이: {len(result['content'])} 글자")
        print(f"   - 이미지 수: {len(result['images'])} 개")
        
        # 줄바꿈 문제 체크 (실제 불완전한 문장만 체크)
        broken_sentences = []
        for line in content_lines:
            line_stripped = line.strip()
            if (line_stripped and len(line_stripped) < 20 and  # 매우 짧고
                not line_stripped.startswith('[사진') and  # 사진 태그가 아니고
                not line_stripped.endswith(('.', '!', '?')) and  # 문장 부호로 끝나지 않고
                line_stripped.count(' ') < 2):  # 단어가 2개 미만인 경우
                broken_sentences.append(line_stripped)
        
        if broken_sentences:
            print("\n⚠️ 불완전한 문장들 (줄바꿈 문제 가능성):")
            for sentence in broken_sentences:
                print(f"   - '{sentence}'")
        else:
            print("\n✅ 문장 파싱 양호 - 불완전한 문장이 발견되지 않았습니다!")
        
        # 추가 품질 체크
        avg_length = sum(len(line) for line in content_lines) / len(content_lines) if content_lines else 0
        print(f"\n📏 평균 문장 길이: {avg_length:.1f} 글자")
        
        complete_sentences = sum(1 for line in content_lines if line.strip().endswith(('.', '!', '?')))
        print(f"📄 완전한 문장 비율: {complete_sentences}/{len(content_lines)} ({complete_sentences/len(content_lines)*100:.1f}%)")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

def test_custom_url():
    """사용자가 입력한 URL로 테스트"""
    
    url = input("\n🔗 테스트할 TechCrunch URL을 입력하세요: ").strip()
    if not url:
        print("❌ URL이 입력되지 않았습니다.")
        return
    
    print(f"\n🔍 사용자 지정 URL 테스트: {url}")
    print("="*80)
    
    try:
        result = crawl_tc_news(url)
        print(f"📰 제목: {result['title']}")
        print(f"📝 본문 길이: {len(result['content'])} 글자")
        print(f"🖼️ 이미지 수: {len(result['images'])} 개")
        
        content_lines = result['content'].split('\n\n')
        print(f"📄 문장 수: {len(content_lines)} 개")
        
        if content_lines:
            print("\n📝 첫 번째 문장:")
            print(f"   {content_lines[0]}")
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    test_tc_parsing()
    
    # 추가 테스트 옵션
    while True:
        choice = input("\n다른 URL로 테스트하시겠습니까? (y/n): ").strip().lower()
        if choice in ['y', 'yes', 'ㅇ']:
            test_custom_url()
        else:
            break
    
    print("\n🎉 테스트 완료!")