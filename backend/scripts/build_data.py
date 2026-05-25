import os
import json
import yaml
import markdown
from datetime import datetime
from deep_translator import GoogleTranslator

# 기본 프로젝트 절대 경로 동적 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # /backend 폴더
BLOG_DIR = os.path.dirname(BASE_DIR)  # 전체 프로젝트 루트 폴더
POSTS_DIR = os.path.join(BLOG_DIR, "data", "posts")

# 산출물을 Next.js 내부 소스 트리인 frontend/src/data/posts.json에 자동 누적
OUTPUT_FILE = os.path.join(BLOG_DIR, "frontend", "src", "data", "posts.json")

# 지원하는 다국어 목록 지정 (ko: 한국어, en: 영어, ja: 일본어)
LANGUAGES = ['ko', 'en', 'ja']

def translate_markdown(markdown_text, target_lang):
    """
    마크다운 특수 기호와 코드 블록(```)을 철저하게 방어하며 본문을 번역하는 엔진입니다.
    """
    if not markdown_text.strip() or target_lang == 'ko':
        return markdown_text
        
    print(f"  [TRANSLATE] 번역 요청 처리 중 (언어: ko -> {target_lang})")
    
    # deep-translator 구글 엔진 인스턴스 소집
    translator = GoogleTranslator(source='ko', target=target_lang)
    
    paragraphs = markdown_text.split("\n")
    translated_paragraphs = []
    
    in_code_block = False
    
    for p in paragraphs:
        # 코드 블록 경계선 감지 및 상태 전환
        if p.strip().startswith("```"):
            in_code_block = not in_code_block
            translated_paragraphs.append(p)
            continue
            
        # 코드 블록 내부의 기술 코드는 무결성 보존을 위해 절대로 번역하지 않음
        if in_code_block:
            translated_paragraphs.append(p)
            continue
            
        # 빈 줄은 그대로 통과
        if not p.strip():
            translated_paragraphs.append(p)
            continue
            
        # 일반 마크다운 문단 번역 실행
        try:
            # 텍스트 번역 기동
            translated_p = translator.translate(p)
            
            # [철통 방어 핵심]: 번역기 응답이 NoneType으로 반환될 경우 원본 문장 강제 복원
            if translated_p is None:
                translated_p = p
                
            translated_paragraphs.append(translated_p)
        except Exception as e:
            print(f"  [WARNING] 문맥 번역 실패: {e}")
            translated_paragraphs.append(p)  # 에러 시 원문 보조 복원
            
    return "\n".join(translated_paragraphs)


def build_blog_data():
    posts = []
    
    if not os.path.exists(POSTS_DIR):
        print(f"[ERROR] 포스팅 디렉터리를 찾을 수 없습니다: '{POSTS_DIR}'")
        return
        
    print(f"[INFO] 다국어 블로그 정적 포스팅 파싱 시작 (경로: {POSTS_DIR})")
    
    # 1차 마크다운 원본 리스트 수집
    markdown_files = [f for f in os.listdir(POSTS_DIR) if f.endswith(".md")]
    
    # 모든 마크다운 파일에 대해 다국어 번역 및 파싱 전개
    for filename in markdown_files:
        filepath = os.path.join(POSTS_DIR, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Frontmatter(설정 헤더)와 Markdown 본문 분리
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                frontmatter_text = parts[1]
                markdown_text = parts[2]
            else:
                frontmatter_text = ""
                markdown_text = content
        else:
            frontmatter_text = ""
            markdown_text = content
            
        # YAML Frontmatter 파싱
        meta = {}
        if frontmatter_text.strip():
            try:
                meta = yaml.safe_load(frontmatter_text)
            except Exception as e:
                print(f"[WARNING] '{filename}' 파일 헤더 파싱 오류: {e}")
                
        # 기본 메타데이터 보완
        orig_title = meta.get("title", os.path.splitext(filename)[0])
        date = meta.get("date", datetime.now().strftime("%Y-%m-%d"))
        orig_description = meta.get("description", "")
        tags = meta.get("tags", [])
        thumbnail = meta.get("thumbnail", "")
        slug = meta.get("slug", os.path.splitext(filename)[0])
        
        # 각각의 지원 언어(ko, en, ja)별 번역 기사 독립 객체 빌드
        for lang in LANGUAGES:
            print(f"[PROCESS] 기사 팽창 중: {filename} -> 언어 코드: [{lang}]")
            
            try:
                if lang == 'ko':
                    title = orig_title
                    description = orig_description
                    translated_markdown_body = markdown_text
                else:
                    # 메타 데이터(제목 및 기사 설명) 번역
                    translator = GoogleTranslator(source='ko', target=lang)
                    title = translator.translate(orig_title)
                    
                    # 제목이 None으로 반환될 경우 보조
                    if title is None:
                        title = orig_title
                        
                    description = translator.translate(orig_description)
                    if description is None:
                        description = orig_description
                    
                    # 본문 마크다운 번역 가동
                    translated_markdown_body = translate_markdown(markdown_text, lang)
                
                # 마크다운 본문을 HTML로 최종 렌더링
                html_content = markdown.markdown(
                    translated_markdown_body, 
                    extensions=['fenced_code', 'tables', 'nl2br']
                )
                
                post_data = {
                    "title": title,
                    "date": str(date),
                    "description": description,
                    "tags": tags,
                    "thumbnail": thumbnail,
                    "slug": slug,
                    "lang": lang,
                    "content": html_content
                }
                
                posts.append(post_data)
                print(f"  [OK] 컴파일 성공: {slug} [{lang}]")
                
            except Exception as e:
                print(f"  [ERROR] 번역 빌드 실패: {filename} [{lang}]: {e}")
                
    # 날짜를 기준으로 내림차순 정렬
    posts.sort(key=lambda x: x["date"], reverse=True)
    
    # JSON 파일로 최종 배포 쓰기 (디렉터리 생성 보장)
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)
        
    print(f"\n[COMPLETE] 총 {len(posts)}개의 다국어 기사가 '{OUTPUT_FILE}' 파일로 완전히 컴파일되었습니다!")

if __name__ == "__main__":
    build_blog_data()
