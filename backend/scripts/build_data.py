import os
import json
import yaml
import markdown
from datetime import datetime

# 기본 프로젝트 절대 경로 동적 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # /backend 폴더
BLOG_DIR = os.path.dirname(BASE_DIR)  # 전체 프로젝트 루트 폴더
POSTS_DIR = os.path.join(BLOG_DIR, "data", "posts")

# [보정 핵심]: Next.js 내부 폴더(frontend/src/data)로 출력 파일을 직접 다이렉트 배치
OUTPUT_FILE = os.path.join(BLOG_DIR, "frontend", "src", "data", "posts.json")

def build_blog_data():
    posts = []
    
    # 마크다운 폴더 유효성 체크
    if not os.path.exists(POSTS_DIR):
        print(f"[ERROR] 마크다운 포스팅 디렉터리를 찾을 수 없습니다: '{POSTS_DIR}'")
        return
        
    print(f"[INFO] 블로그 정적 포스팅 파싱 시작 (경로: {POSTS_DIR})")
    
    # 폴더 내 모든 파일 탐색
    for filename in os.listdir(POSTS_DIR):
        if not filename.endswith(".md"):
            continue
            
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
                print(f"[WARNING] '{filename}' 파일의 헤더를 읽는 도중 오류가 발생했습니다: {e}")
                
        # 기본 메타데이터 보완
        title = meta.get("title", os.path.splitext(filename)[0])
        date = meta.get("date", datetime.now().strftime("%Y-%m-%d"))
        description = meta.get("description", "")
        tags = meta.get("tags", [])
        thumbnail = meta.get("thumbnail", "")
        slug = meta.get("slug", os.path.splitext(filename)[0])
        
        # 마크다운 본문을 풍성한 HTML로 렌더링
        html_content = markdown.markdown(
            markdown_text, 
            extensions=['fenced_code', 'tables', 'nl2br']
        )
        
        post_data = {
            "title": title,
            "date": str(date),
            "description": description,
            "tags": tags,
            "thumbnail": thumbnail,
            "slug": slug,
            "content": html_content
        }
        
        posts.append(post_data)
        print(f"[SUCCESS] 파싱 성공: {filename} -> 슬러그: {slug}")
        
    # 날짜를 기준으로 내림차순 정렬
    posts.sort(key=lambda x: x["date"], reverse=True)
    
    # JSON 파일로 쓰기 (디렉터리 강제 생성 보장)
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)
        
    print(f"[COMPLETE] 총 {len(posts)}개의 글이 '{OUTPUT_FILE}' 파일로 통합 데이터베이스화 되었습니다!")

if __name__ == "__main__":
    build_blog_data()
