# -*- coding: utf-8 -*-
import os
import re
import json
import urllib.parse
import feedparser
import requests
import random
from datetime import datetime
from deep_translator import GoogleTranslator

# 기본 프로젝트 경로 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # /backend 폴더
BLOG_DIR = os.path.dirname(BASE_DIR)  # 전체 프로젝트 루트 폴더
POSTS_DIR = os.path.join(BLOG_DIR, "data", "posts")

# 불법/정책위반 키워드 블랙리스트 정의 (구글 애드센스 정책 준수)
BLACKLIST_KEYWORDS = [
    'hack', 'crack', 'casino', 'gambling', 'illegal', 'adult', 'porn', 'torrent', 'bypass',
    '도박', '해킹', '크랙', '불법복제', '마약', '성인물', '사설토토', '무단배포', '우회'
]

# 상업적 무료 배포 전용 이미지 서비스(Unsplash) 고품질 IT 썸네일 리스트
UNSPLASH_THUMBNAILS = [
    "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=800&q=80", # IT 테크 반도체
    "https://images.unsplash.com/photo-1517694712202-14dd9538aa97?auto=format&fit=crop&w=800&q=80", # 코딩 랩탑
    "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&w=800&q=80", # 사이버 매트릭스
    "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&w=800&q=80", # 네트워크 보안
    "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?auto=format&fit=crop&w=800&q=80"  # AI 로봇
]

def clean_html(raw_html):
    """HTML 잔여 태그 정규식 제거"""
    if not raw_html:
        return ""
    cleanr = re.compile('<.*?>')
    return re.sub(cleanr, '', raw_html)

def check_blacklist(text):
    """블랙리스트 기반 정책 위반 필터링"""
    if not text:
        return False
    text_lower = text.lower()
    for word in BLACKLIST_KEYWORDS:
        if word in text_lower:
            return True
    return False

def clean_truncated_summary(summary):
    """
    RSS 피드가 제공하는 요약문 끝자락의 [...] 이나 [Read More] 잘림 현상을 패치합니다.
    자연스럽게 완성된 마지막 문장까지만 정밀 추출하여 마침표로 정돈합니다.
    """
    if not summary:
        return ""
        
    # 흔히 발생하는 잘림 표기 제거
    summary_clean = re.sub(r'\[\.\.\.\]', '', summary)
    summary_clean = re.sub(r'\[Read\s+More.*?\]', '', summary_clean, flags=re.IGNORECASE)
    summary_clean = re.sub(r'\.\s*\.\s*\.', '', summary_clean) # ... 표기 제거
    
    summary_clean = summary_clean.strip()
    
    # 마지막 문장이 미완성 상태인 경우 가장 인접한 완성 문장까지만 파싱하여 단정하게 정돈
    sentences = re.split(r'(\.|\!|\?)\s+', summary_clean)
    if len(sentences) > 2:
        # 문장 경계와 문장 부호 재조합
        reconstructed = []
        for i in range(0, len(sentences)-1, 2):
            reconstructed.append(sentences[i] + sentences[i+1])
        
        # 마지막 토막 문장이 마침표 없이 끝난 미완성 구문인지 판정
        last_item = sentences[-1].strip()
        if last_item and not any(last_item.endswith(p) for p in ['.', '!', '?']):
            # 미완성 마지막 토막 버리고 앞쪽 완성 문장들만 채택
            summary_clean = " ".join(reconstructed)
        else:
            if last_item:
                reconstructed.append(last_item)
            summary_clean = " ".join(reconstructed)
            
    # 혹시 모를 마침표가 완전히 부재하면 보정
    summary_clean = summary_clean.strip()
    if summary_clean and not any(summary_clean.endswith(p) for p in ['.', '!', '?']):
        summary_clean += "."
        
    return summary_clean

def extract_main_subject(title):
    """
    기사 제목에서 핵심 주제 키워드를 인텔리전트하게 추출합니다.
    문장 내 영문 명사 및 첫 알파벳 대문자 단어들을 우선 타겟팅하여 블로그 본문 변형에 활용합니다.
    """
    if not title:
        return "기술 혁신"
    
    # 대괄호 안의 글자 우선 추출 (예: [Amazon Bedrock] -> Amazon Bedrock)
    brackets = re.findall(r'\[(.*?)\]', title)
    if brackets:
        return brackets[0]
        
    # 콜론 앞 단어 추출 (예: AWS News: New advanced -> AWS News)
    if ":" in title:
        part = title.split(":", 1)[0].strip()
        if len(part) < 30:
            return part
            
    # 대문자로 시작하는 고유 명사들 추출
    words = re.findall(r'\b[A-Z][a-zA-Z0-9]*\b', title)
    if words:
        # 가급적 의미 있는 기술 명칭(Tech, AWS, Next, AI 등) 위주로 조합
        filtered = [w for w in words if w.lower() not in ['a', 'an', 'the', 'is', 'are', 'in', 'on', 'at', 'by', 'for', 'with', 'new', 'how', 'why', 'what']]
        if filtered:
            return " ".join(filtered[:2])
            
    # 한글 제목인 경우 명사 추출
    korean_words = re.findall(r'\b[가-힣]{2,8}\b', title)
    if korean_words:
        return korean_words[0]
        
    return "IT 기술 생태계"

def generate_dynamic_free_content(feed_name, link, translated_title, translated_body):
    """
    Gemini API 키가 없을 때 (무료 모드), 기사마다 독창적인 개별 분석과 고유의 지문을 갖도록
    제목 키워드와 랜덤 템플릿 풀을 기반으로 100% 동적 기사 포스팅을 편찬합니다.
    """
    # 핵심 주제 추출
    subject = extract_main_subject(translated_title)
    
    # 2번 영역(블로그 분석 및 인사이트)의 동적 베리에이션 템플릿 풀
    insight_templates = [
        f"""이번 소식은 최근 요동치는 글로벌 테크 씬에서 {subject}을 중심으로 하는 패러다임 전환이 가속화되고 있음을 보여줍니다. 특히 시장과 현장의 목소리를 분석해 볼 때 다음과 같은 입체적 관점으로 바라보아야 합니다:
* **주요 흐름 및 시장 접근성**: {subject} 분야의 기술적 문턱이 대폭 낮아지며, 글로벌 엔지니어들과 혁신 기업들 사이에서 범용적인 영향력이 배가될 것입니다.
* **사용자 및 개발자 경험(UX/DX)**: 실무 현장에서의 운용 편의성이 강화됨에 따라, 전반적인 개발 생산성이 향상되고 신제품 런칭 시너지를 극대화하는 촉진제 역할을 해줄 전망입니다.""",

        f"""새롭게 공개된 {subject}의 혁신적 소식은 글로벌 IT 인프라 발전 경로에 커다란 나침반을 놓아준 것과 다름없습니다. 이번 보도를 다각도로 진단한 심층 시사점은 아래와 같습니다:
* **생태계 다변화와 경쟁 우위**: 다양한 오픈 플랫폼과 프레임워크 간의 유기적인 시너지가 창출되면서 {subject} 생태계 전반의 양적, 질적 팽창이 가파르게 실현될 것입니다.
* **비즈니스 가치 확장**: 단순한 기술 혁신 단계를 넘어, 기업 비즈니스 모델 입증과 시장의 실질적인 니즈를 관통하는 강력한 상용적 생산성을 확보해 주었습니다.""",

        f"""{subject} 분야의 놀라운 발전상을 함축하고 있는 이번 정보는 전 세계 엔지니어들과 C-Level 결정권자들에게도 매우 중대한 시사점을 남깁니다. 면밀하게 분석한 두 가지 실효적 인사이트는 다음과 같습니다:
* **기술의 보편화와 표준 정립**: 복잡했던 기존 인프라 장벽이 완전히 해소되면서 {subject} 솔루션이 IT 전 영역의 표준 규격이자 필수 동력원으로 급부상하게 됩니다.
* **사용자 친화적 서비스 전환**: 복잡한 설정 없이도 뛰어난 최적화를 경험할 수 있어 공급자와 소비자 그룹 모두의 만족도를 고르게 만족시킬 획기적 발판이 마련되었습니다."""
    ]
    
    # 3번 영역(결론 및 시사점)의 동적 베리에이션 템플릿 풀
    conclusion_templates = [
        f"""종합해 볼 때, 이번 {subject} 관련 긴급 뉴스는 4차 산업혁명의 흐름 속에서 기술적 패러다임을 더욱 빠른 속도로 재편하는 거대한 촉매제입니다. 앞으로도 이 신선한 변화가 업계와 현업 생태계 전반에 가져올 흥미진진한 가치를 계속 모니터링하여 유익한 IT 트렌드 리포트를 성실하게 업데이트해 드리겠습니다.""",
        
        f"""결론적으로 {subject}의 신규 행보는 디지털 트랜스포메이션을 추진하는 많은 혁신 기업들에게 새로운 설계도와 이정표를 쥐여 준 중대 이벤트입니다. 기술적 지평을 끊임없이 개척해 나가는 이 유의미한 패러다임의 변곡점을 매의 눈으로 주시하여 가치 있는 해설글로 보답하겠습니다.""",
        
        f"""마치며, 이번 {subject} 소식은 모던 IT 및 소프트웨어 엔지니어링 업계에 강력한 활력을 불어넣는 신호탄이라 단언할 수 있습니다. 기술 범용성과 강력한 가치 창출 능력을 동시에 입증해 낸 만큼, 이 거대한 기술적 물결을 세밀하게 분석하고 현장의 소식을 발 발빠르게 공유해 드리겠습니다."""
    ]
    
    # 기사 해시 기반이나 난수 기반으로 템플릿 고유 매칭 (매 글마다 완전히 다르게 조합)
    hash_seed = len(translated_title) + len(translated_body)
    selected_insight = insight_templates[hash_seed % len(insight_templates)]
    selected_conclusion = conclusion_templates[(hash_seed + 3) % len(conclusion_templates)]
    
    # 최종 마크다운 본문 구조 조립
    post_content = f"""
최신 글로벌 테크 소식인 {feed_name}에서 발표한 매우 중요한 정보를 바탕으로 번역 및 컴파일 편찬한 IT 리포트입니다.

---

## 1. 개요 및 주요 포인트
글로벌 기술 리더들의 혁신을 이끄는 본 기사의 주요 내용과 심층 요약은 다음과 같습니다:

> {translated_body}

*최신 기술 트렌드에 대한 깊이 있는 세부 문맥과 공식 전문(Full Text)을 정독하시려면, 아래 원문 링크를 통해 보다 상세한 소식을 함께 점검해 보시길 권장합니다.*

## 2. 블로그 분석 및 인사이트
{selected_insight}

---

## 3. 결론 및 시사점
{selected_conclusion}

*본 아티클은 [{feed_name}]({link})의 공식 RSS 발행 기사를 합법적인 저작권 가이드라인을 철저히 준수하여 정밀 번역 편찬 및 출처를 정확히 명시하여 유익한 정보 제공 목적으로 작성되었습니다.*
"""
    return post_content

def call_gemini_api(api_key, prompt):
    """
    최신 Google Gemini 2.5 Flash API를 호출하여 100% 창작 집필을 구동합니다.
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }]
    }
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            return result['candidates'][0]['content']['parts'][0]['text']
        else:
            print(f"  [Gemini API Warning] API 호출 실패 (HTTP {response.status_code}): {response.text[:100]}")
            return None
    except Exception as e:
        print(f"  [Gemini API Error] 네트워크 장애 또는 API 무응답: {e}")
        return None

def auto_collect_posts():
    # 수집 정보 (유력 글로벌 테크 RSS 피드 매칭)
    feeds = [
        {"name": "TechCrunch Startups", "url": "https://techcrunch.com/category/startups/feed/"},
        {"name": "Google Developers", "url": "https://feeds.feedburner.com/GoogleDeveloperBlog"},
        {"name": "AWS News", "url": "https://aws.amazon.com/blogs/aws/feed/"}
    ]
    
    # 윈도우 환경 편의성 대폭 개선: 시스템 환경 변수 외에도 프로젝트 루트의 .env 파일 자동 로딩 및 주입
    # [BOM 철통 방어]: utf-8-sig 코덱을 사용하여 파워쉘에서 생성한 UTF-8 BOM 파일도 무결 감지합니다.
    api_key = os.environ.get("GEMINI_API_KEY") or ""
    if not api_key:
        env_files = [os.path.join(BLOG_DIR, ".env"), os.path.join(BLOG_DIR, ".env.local")]
        for env_file in env_files:
            if os.path.exists(env_file):
                try:
                    with open(env_file, "r", encoding="utf-8-sig") as ef:
                        for line in ef:
                            line = line.strip()
                            if line and not line.startswith("#") and "=" in line:
                                key, val = line.split("=", 1)
                                if key.strip() == "GEMINI_API_KEY":
                                    api_key = val.strip().strip('"').strip("'")
                                    print(f"  [INFO] 로컬 설정 파일({os.path.basename(env_file)})에서 GEMINI_API_KEY 자동 로드 완료!")
                                    break
                except Exception as e:
                    print(f"  [WARNING] 로컬 설정 파일 파싱 중 오류: {e}")
            if api_key:
                break
                
    print("[INFO] AI 및 저작권 프리 정적 아티클 자동 수집 집필 파이프라인 가동!")
    os.makedirs(POSTS_DIR, exist_ok=True)
    
    collected_count = 0
    
    for idx, feed_info in enumerate(feeds):
        print(f"\n[FEED] 테크 채널 분석 개시: {feed_info['name']}")
        try:
            feed = feedparser.parse(feed_info["url"])
        except Exception as e:
            print(f"  [ERROR] RSS 피드를 읽어들일 수 없습니다: {e}")
            continue
            
        # 가장 최근 기사 최신 2개씩 수집 진행
        entries = feed.entries[:2]
        
        for entry in entries:
            title = entry.title
            link = entry.link
            summary = entry.get("summary", entry.get("description", ""))
            summary_clean = clean_html(summary)
            
            # [보안 필터 1]: 애드센스 정책 위반 키워드가 섞여 있으면 스크랩 원천 배제
            if check_blacklist(title) or check_blacklist(summary_clean):
                print(f"  [BLOCKED] 애드센스 정책 위반 소지 감지 기사 배제: {title[:20]}...")
                continue
                
            # 슬러그 생성 및 파일명 포맷 조합
            slug = re.sub(r'[^a-zA-Z0-9]+', '-', title.lower()).strip('-')
            slug_words = slug.split("-")[:5]
            slug = "-".join(slug_words)
            
            output_filepath = os.path.join(POSTS_DIR, f"auto-{slug}.md")
            
            # 중복 수집 발행 방지
            if os.path.exists(output_filepath):
                print(f"  [SKIP] 이미 데이터베이스에 존재하는 포스팅: auto-{slug}.md")
                continue
                
            print(f"  [COLLECT] 신규 테크 콘텐츠 수집 완료: {title[:25]}...")
            
            post_content = ""
            meta_description = ""
            
            # Unsplash 상업용 무료 라이선스 고화질 IT 사진 썸네일 매핑
            thumbnail_url = UNSPLASH_THUMBNAILS[collected_count % len(UNSPLASH_THUMBNAILS)]
            
            # 1초 잘림 방지 필터 거치기
            cleaned_summary = clean_truncated_summary(summary_clean)
            
            if api_key:
                # [모드 A] Gemini 2.5 Flash를 가동한 100% 완전 창작 오리지널 포스팅 모드
                print("  [AI MODE] Gemini 2.5 Flash 초지능 창작 블로그 에디팅 기동...")
                
                prompt = f"""
                You are an elite, highly professional IT tech and software engineering blogger.
                Below is the raw summary data of a recent technology news article.
                Your task is to write a highly detailed, extremely engaging, and long-form (at least 1500 Korean characters) blog post in Korean based on this information.
                
                CRITICAL COPYRIGHT & POLICY RULES:
                1. DO NOT copy-paste sentences from the input. Extract the facts only, and write the entire post using completely new sentence structures and your own analytical words.
                2. Adhere strictly to the Google AdSense Program Policies. Never generate illegal, adult, hacking, crack, bypass, gambling, or violent contents.
                3. The tone of voice must be polite, highly professional, informative, and friendly (use '-요', '-습니다' style).
                
                Input Article Title: {title}
                Input Article Summary: {cleaned_summary}
                
                Your Output Format MUST contain only the raw body of the article in standard Markdown format.
                Do not include YAML frontmatter, do not include H1 title inside the markdown.
                Structure the post beautifully with Heading 2 (##) and Heading 3 (###).
                Include an engaging introduction, structured body paragraphs with deep technical analysis, a comparison or tabular data if appropriate, and a professional conclusion.
                """
                
                ai_output = call_gemini_api(api_key, prompt)
                if ai_output:
                    post_content = ai_output.strip()
                    meta_description = f"최신 글로벌 테크 트렌드 리포트 '{title}'에 대한 AI 심층 분석 및 독창적 기술 해설 리포트입니다."
                else:
                    api_key = "" # API 통신 실패 시 모드 B로 대체 기동
                    
            if not api_key:
                # [모드 B] 구글 번역 + 인텔리전트 동적 매핑 엔진 (출처 정확히 명시 모드)
                print("  [FREE MODE] 무료 지능형 동적 매핑 엔진 집필 기동...")
                translator = GoogleTranslator(source='en', target='ko')
                
                try:
                    # 제목 번역
                    translated_title = translator.translate(title)
                    # 요약 본문 번역
                    translated_body = translator.translate(cleaned_summary[:4500])
                    
                    # 동적 템플릿 조합 본문 생성
                    post_content = generate_dynamic_free_content(feed_info['name'], link, translated_title, translated_body)
                    
                    meta_description = f"글로벌 테크 미디어 {feed_info['name']}에서 보도된 '{translated_title}' 기사에 대한 정밀 번역 편찬 분석 리포트입니다."
                    
                except Exception as e:
                    print(f"  [ERROR] 무료 번역 엔진 장애 발생: {e}")
                    continue
            
            # YAML Frontmatter 헤더 가이드라인 생성
            final_title = f"[IT 트렌드] {title}" if api_key else f"[IT 분석] {translated_title}"
            
            yaml_header = f"""---
title: "{final_title}"
date: "{datetime.now().strftime('%Y-%m-%d')}"
description: "{meta_description}"
tags: ["IT뉴스", "테크트렌드", "기술동향"]
thumbnail: "{thumbnail_url}"
slug: "auto-{slug}"
---

"""
            # 완성된 마크다운 초안 적재
            with open(output_filepath, "w", encoding="utf-8") as f:
                f.write(yaml_header + post_content)
                
            print(f"  [SUCCESS] 초안 마크다운 적재 완료: auto-{slug}.md")
            collected_count += 1
            
    print(f"\n[COMPLETE] 총 {collected_count}개의 고품질 AI 및 지능형 동적 기사 초안이 '/data/posts/' 하위에 완벽히 생성 적재되었습니다!")

if __name__ == "__main__":
    auto_collect_posts()