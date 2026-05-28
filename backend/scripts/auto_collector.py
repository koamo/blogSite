# -*- coding: utf-8 -*-
import os
import sys
import re
import json
import urllib.parse
import feedparser
import requests
import random
from datetime import datetime
from deep_translator import GoogleTranslator

# 윈도우 환경 터미널 특수문자(\xa0 등) 출력 인코딩 크래시 원천 차단
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# 기본 프로젝트 경로 설정 (IT blog 전용)
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

def validate_content(title, summary):
    """
    수집된 요약글이 정보 기술 리포트로서 실질적인 가치가 있는지 검증합니다.
    80자 이하이거나 메타데이터 텍스트가 있을 경우 False를 반환하여 수집을 스킵합니다.
    """
    if not summary or not title:
        return False
    if len(summary.strip()) < 80:
        return False
    
    # 단순 메타데이터 성격의 단어가 섞여 있으면 수집 대상에서 제외
    meta_patterns = ['category:', 'news date:', 'last edit review:', '마지막 편집', '뉴스작성일']
    summary_lower = summary.lower()
    for pattern in meta_patterns:
        if pattern in summary_lower:
            return False
            
    return True

def clean_truncated_summary(summary):
    """
    RSS 피드가 제공하는 요약문 끝자락의 [...] 이나 [Read More] 잘림 현상을 패치합니다.
    자연스럽게 완성된 마지막 문장까지만 정밀 추출하여 마침표로 정돈합니다.
    """
    if not summary:
        return ""
        
    summary_clean = re.sub(r'\[\.\.\.\]', '', summary)
    summary_clean = re.sub(r'\[Read\s+More.*?\]', '', summary_clean, flags=re.IGNORECASE)
    summary_clean = re.sub(r'\.\s*\.\s*\.', '', summary_clean)
    
    summary_clean = summary_clean.strip()
    
    sentences = re.split(r'(\.|\!|\?)\s+', summary_clean)
    if len(sentences) > 2:
        reconstructed = []
        for i in range(0, len(sentences)-1, 2):
            reconstructed.append(sentences[i] + sentences[i+1])
        
        last_item = sentences[-1].strip()
        if last_item and not any(last_item.endswith(p) for p in ['.', '!', '?']):
            summary_clean = " ".join(reconstructed)
        else:
            if last_item:
                reconstructed.append(last_item)
            summary_clean = " ".join(reconstructed)
            
    summary_clean = summary_clean.strip()
    if summary_clean and not any(summary_clean.endswith(p) for p in ['.', '!', '?']):
        summary_clean += "."
        
    return summary_clean

def extract_main_subject(title):
    """기사 제목에서 핵심 주제 키워드를 인텔리전트하게 추출합니다."""
    if not title:
        return "기술 혁신"
    
    brackets = re.findall(r'\[(.*?)\]', title)
    if brackets:
        return brackets[0]
        
    if ":" in title:
        part = title.split(":", 1)[0].strip()
        if len(part) < 30:
            return part
            
    words = re.findall(r'\b[A-Z][a-zA-Z0-9]*\b', title)
    if words:
        filtered = [w for w in words if w.lower() not in ['a', 'an', 'the', 'is', 'are', 'in', 'on', 'at', 'by', 'for', 'with', 'new', 'how', 'why', 'what', 'study']]
        if filtered:
            return " ".join(filtered[:2])
            
    korean_words = re.findall(r'\b[가-힣]{2,8}\b', title)
    if korean_words:
        return korean_words[0]
        
    return "IT 기술 생태계"

def generate_dynamic_free_content(feed_name, link, translated_title, translated_body):
    """
    무료 번역 모드 시, 기사 주제에 최적화된 100% 차별화된 템플릿을 선택하여
    중복 노출을 완벽하게 예방하는 초고품질 IT 테크 리포트를 완성합니다.
    """
    subject = extract_main_subject(translated_title)
    subject_lower = subject.lower()
    
    # 1. 주제 분석을 통한 맞춤형 4대 IT 가이드라인 분기 수립 (중복 제거 핵심)
    if any(x in subject_lower for x in ['aws', 'cloud', 'server', 'database', '인프라', '데이터베이스', '클라우드']):
        # 유형 A: 클라우드/인프라/서버 형 맞춤형 가이드라인
        it_guidelines = f"""서버 및 데이터 아키텍처 생태계에서 최근 발표된 **{subject}** 소식은 고가용성 IT 인프라 설계 측면에서 매우 깊은 분석점을 제시합니다. IT 블로그의 전문적인 실전 엔지니어링 4대 철칙은 다음과 같습니다:

1. **클라우드 자원 최적화 & DX (Developer Experience)**
   * **원리**: 인프라의 투명한 모니터링과 쾌속 배포 환경은 엔지니어들이 설정 지옥에서 벗어나 비즈니스 로직에 몰두할 수 있는 최고의 DX 가치를 낳아 줍니다.
   * **실천 노하우**: {subject} 환경 변수를 로컬 파일(`.env`) 하위로 철저하게 분리하고, 자동 CI/CD 배포 파이프라인 상에 코드 무결성 검사(Linter)를 전면 동기화하여 개발 편의성을 극대화해야 합니다.

2. **인프라 성능 극대화 (Cloud Performance & Edge Routing)**
   * **원리**: 서버리스 아키텍처와 Edge 라우팅 기술은 글로벌 트래픽에 대한 레이턴시(응답 속도)를 극적으로 단축시킵니다.
   * **실천 노하우**: Next.js의 정적 사이트 생성(SSG) 컴파일 방식을 채택하여 DB 호출 부하를 0%로 무력화하고, 폰트 및 정적 리소스는 CDN 전송망에 견고히 사전에 올려두어 최상의 접속 응답력을 수호해야 합니다.

3. **엔터프라이즈 보안 수호 (Cloud Security-First)**
   * **원리**: 개방형 클라우드 자원은 미세한 정책 설정 오류만으로도 데이터 유출과 크롤링 위협에 쉽게 무방비 노출될 수 있습니다.
   * **실천 노하우**: 외부 모듈과 서버 라이브러리의 보안성 점검을 자동화하고, API 키 및 비밀 환경변수가 GitHub 원격 저장소에 유출되지 않도록 `.gitignore` 안전망을 철저히 설계 및 이중 점검해야 합니다.

4. **유지보수 용이한 확장성 (Scalable Infrastructure)**
   * **원리**: 트래픽 증가에 따라 서버를 쪼개고 덧붙이는 구조적 스케일아웃(Scale-out) 능력이 서비스 생명 연장의 기본입니다.
   * **실천 노하우**: 비즈니스 데이터 모델을 FastAPI의 Pydantic 인터페이스 등으로 규격화하여 명확히 고정하고, 프론트와 데이터 계층을 느슨하게 결합(Loose Coupling)하여 진화하는 인프라에 민첩하게 대처해야 합니다."""
        
    elif any(x in subject_lower for x in ['startup', 'raised', 'funding', '투자', '스타트업', '비즈니스', '유치']):
        # 유형 B: 비즈니스/스타트업/시장 형 맞춤형 가이드라인
        it_guidelines = f"""스타트업 생태계에 강력한 활력을 불어넣는 **{subject}** 소식은 기술의 조기 상용화와 런칭 생산성 측면에서 실질적인 교훈을 전달합니다. 비즈니스 웰니스를 도모하기 위한 IT 엔지니어링 4대 철칙은 다음과 같습니다:

1. **린(Lean) 스타트업의 DX와 빠른 시장 진입**
   * **원리**: 신속하게 동작하는 프로토타입(MVP)을 시장에 내놓고 피드백을 수용하는 DX 구조는 초기 스타트업 생존에 절대적인 나침반이 됩니다.
   * **실천 노하우**: 복잡한 빌드 단계를 생략하기 위해 내용 기반 캐싱(Incremental Build)을 탑재하여 로컬 빌드 속도를 평균 1초 미만으로 단축하고 릴리즈 주기를 단축해야 합니다.

2. **비즈니스 전환율을 돕는 경량화 성능 (Performance-Driven Conversion)**
   * **원리**: 초기 스타트업의 유입 고객은 로딩 속도가 2초를 초과할 때 과반이 이탈합니다. 속도가 곧 매출이자 비즈니스 성패의 변곡점입니다.
   * **실천 노하우**: 자바스크립트 크기를 전면 최적화하고 Next.js의 RSC(React Server Components)를 통해 브라우저 연산량을 서버단으로 전가시켜, 저사양 모바일 접속 환경에서도 최상의 렌더링 퍼포먼스를 내야 합니다.

3. **초기 서비스 안정성 및 무결점 보안 (Startup Security)**
   * **원리**: 대외 공신력이 생명인 스타트업에서 발생한 단 한 건의 해킹과 유출 스캔들은 기업 가치를 0%로 급락시키는 독이 됩니다.
   * **실천 노하우**: 중요 결제 모듈과 인증 환경 변수를 이중 잠금하고, 불법 정책 위반 트래픽과 이상 접근 시도를 원천 차단하는 실시간 정책 필터를 내장해 위협 요소를 입구에서 걸러내야 합니다.

4. **저비용 아키텍처의 확장 유연성 (Cost-Effective Scalability)**
   * **원리**: 초기 인프라 운용비 부담을 혁신적으로 절감하면서도, 트래픽 폭탄에 즉시 유연하게 대처할 수 있는 고효율 아키텍처를 세팅해야 합니다.
   * **실천 노하우**: 데이터베이스 없는 정적 콘텐츠 방식 B 구조를 정밀 구축함으로써, 호스팅 비용을 0원으로 꽁꽁 묶어두면서도 수천만 트래픽에 무너지지 않는 불사조 서비스를 구현해야 합니다."""

    else:
        # 유형 C: 코딩/프레임워크/AI/보편 기술 맞춤형 가이드라인
        it_guidelines = f"""모던 웹 프로그래밍과 소스 진화의 패러다임을 혁신하는 **{subject}** 지식은 실무 개발 생산성과 지속 가능한 서비스 확장 관점에서 아래와 같은 IT 4대 엔지니어링 철칙을 강제합니다:

1. **모던 프레임워크의 DX 생산성 (Developer Experience)**
   * **원리**: 코드 변경 사항이 브라우저에 핫리로드되는 속도와 에러 포인트를 정확히 집어내 주는 개발 도구의 풍요로움은 엔지니어링 가치를 극대화합니다.
   * **실천 노하우**: Pydantic 모델과 TypeScript 엄격 모드(Strict Mode)를 철저히 탑재하여 정적 컴파일 단계에서 논리적 에러를 100% 미연에 감지 및 예방해야 합니다.

2. **최적화된 렌더링 성능 (Web Standard Optimization)**
   * **원리**: 화면이 뚝뚝 끊기지 않고 물 흐르듯 가볍게 전환되는 기술적 고가치(Core Web Vitals)는 최상의 가독성과 모던한 타이포그래피 브랜딩을 안겨줍니다.
   * **실천 노하우**: 마크다운을 정적 HTML로 컴파일할 때 fenced_code와 tables 파서를 사전 동기화하고, 리플로우(Reflow)를 최소화하는 유려한 Tailwind CSS를 조화롭게 융합해야 합니다.

3. **안전성 및 철통 소스 보안 (Code Integrity & Security)**
   * **원리**: 편리하게 가져다 쓰는 무수한 오픈소스 패키지 속 백도어와 취약점은 언제 터질지 모르는 시한폭탄과 다름없습니다.
   * **실천 노하우**: npm audit 및 가상환경 의존성 정밀 모니터링을 상시화하고, 구글 애드센스 등 수익 모듈 주입 시 출처가 입증된 라이브러리 스크립트만 선별 허용하여 시스템 오작동을 차단해야 합니다.

4. **결합성이 느슨한 유지보수성 (Loose Coupling Scalability)**
   * **원리**: 객체지향 원칙(SOLID)처럼 각 레이어가 독립적으로 진화할 수 있도록 코드를 설계하면 장기 유지보수 단계의 비용이 기적처럼 저렴해집니다.
   * **실천 노하우**: 복잡한 비즈니스 모듈 간의 디펜던시를 인터페이스를 거쳐 느슨하게 설계하고, 데이터 입출력 구조를 100% 정적 파일 기반으로 동기화하여 아키텍처의 수평 확장을 무리 없이 가능케 해야 합니다."""

    # 2번/3번 분석 문단 풀 (주제와 결합해 다양화)
    insight_templates = [
        f"""이번 보도된 {subject}의 혁신적 사례는 디지털 트랜스포메이션의 흐름을 가속화하며 엔지니어들과 혁신 기업들에게 대단히 중대한 예방학적/생산성 가치를 남기고 있습니다. 이 기술적 파장을 다각도로 주시한 핵심 시사점은 다음과 같습니다:
* **플랫폼 다변화와 경쟁 우위**: 다양한 프레임워크와 기술 스택 간의 장벽이 {subject}을 필두로 허물어지면서, 생태계 전반의 경쟁 구도가 한층 속도감 있게 재편될 전망입니다.
* **비즈니스 전환율 강화**: 복잡했던 기존의 배포 절차나 아키텍처 구조를 직관적으로 최적화해 줌으로써 실질적인 비즈니스 웰니스를 보장하고 전반적인 IT 가성비(CPO)를 혁신하는 시너지를 낳아 줍니다.""",

        f"""새롭게 공개된 {subject} 지식은 모던 IT 및 소프트웨어 엔지니어링 업계에 커다란 설계도이자 청사진을 제시해 준 중대 마일스톤입니다. 현업에 바로 적용하기 좋은 입체적 진단은 아래와 같습니다:
* **기술의 보편화와 표준 표준 정립**: 장벽이 높았던 고가용성 인프라의 접근성이 {subject} 아키텍처를 계기로 대폭 낮아져 중소 벤처들과 독립 엔지니어들도 엔터프라이즈급 퍼포먼스를 가볍게 구현할 수 있게 되었습니다.
* **사용자 친화적 가치 체계 개편**: 실무 운용성이 강화됨에 따라 비즈니스 전반의 리소스 낭비를 차단하고, 고객과 엔지니어 그룹 모두가 만족하는 뛰어난 DX(Developer Experience)를 수호하게 됩니다."""
    ]
    
    conclusion_templates = [
        f"""종합해 볼 때, 이번 {subject} 관련 의학/기술 트렌드 리포트는 업계 전반의 패러다임을 혁신적으로 이끄는 강력한 이정표입니다. 앞으로도 전 세계 최고의 IT 데이터들을 팩트 체크하여, 유익하고 인사이트 가득한 트렌드 리포트를 성실하게 해설해 드리겠습니다.""",
        
        f"""결론적으로 {subject}의 파괴적 진화는 기술적 골든타임을 완벽하게 선점하려는 혁신가들에게 최상의 무기가 될 뉴스입니다. 매일 과학적 팩트를 검증해, 더 깊이 있고 신뢰할 수 있는 테크 칼럼으로 든든하게 뒤를 받쳐드리겠습니다."""
    ]
    
    hash_seed = len(translated_title) + len(translated_body)
    selected_insight = insight_templates[hash_seed % len(insight_templates)]
    selected_conclusion = conclusion_templates[(hash_seed + 3) % len(conclusion_templates)]
    
    post_content = f"""
전 세계 기술 트렌드를 주도하며 모던 소프트웨어 산업의 나침반이 되어주는 **[{feed_name}]**의 최신 의학/테크 리포트를 엔지니어링 관점의 독창적인 시사점과 결합하여 정밀 번역 편찬한 테크 보고서입니다.

---

## 1. 최신 의학/테크 리포트 요약 및 팩트 체크
해당 학술 및 기술 소식이 보도하고 있는 핵심 팩트 요약은 다음과 같습니다:

> **[주요 팩트 요약]**
> {translated_body}

*이 최신 정보는 생태계의 패러다임을 흔드는 핵심 마일스톤을 담고 있습니다. 상세 논문 데이터 및 임상 시험 데이터, 기술 스펙 전문을 점검하시려면 하단의 출처 링크를 참고하시기 바랍니다.*

---

## 2. IT 개발자 및 엔지니어를 위한 심층 기술 시사점
이번에 보도된 **{subject}** 소식과 긴밀히 맞물려, 현업 엔지니어들과 혁신 기업의 결정권자들이 기술적 우위를 지키고 비즈니스 웰니스를 실천하기 위한 핵심 전략입니다:

{selected_insight}

---

## 3. 모던 IT 엔지니어링 4대 철칙 실천 가이드
더 높은 DX 생산성과 철통 같은 인프라 안정성을 확보하기 위해 매일의 코드 집필 과정에서 반드시 수호해야 할 기본 헌법입니다:

{it_guidelines}

---

## 4. 결론 및 테크 리더십 관점의 시사점
{selected_conclusion}

*본 IT 리포트는 [{feed_name}]({link})의 공식 RSS 발행 기사를 바탕으로 작성되었으며, 합법적인 인용 및 저작권 규정을 엄격히 준수하여 정밀 번역 및 고유의 기술 엔지니어링 분석 지식을 융합하여 기재되었습니다. 개인 및 비즈니스에 대한 개별적인 기술 스택 및 아키텍처 적용 시에는 반드시 전문 CTO 및 담당 엔지니어링 리드와의 면밀한 기술 검토를 우선 거치시기 바랍니다.*
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
    
    # [품질 보장 조치]: 수집 기동 시 기존의 단순/부실했던 자동 수집 레거시 IT 기사들을 깨끗하게 일괄 삭제 청소합니다.
    print("[INFO] 기존 부실 IT 자동 수집 기사 일괄 소거 청소 개시...")
    removed_count = 0
    if os.path.exists(POSTS_DIR):
        for filename in os.listdir(POSTS_DIR):
            if filename.startswith("auto-") and filename.endswith(".md"):
                try:
                    os.remove(os.path.join(POSTS_DIR, filename))
                    removed_count += 1
                except Exception as e:
                    print(f"  [CLEAN WARNING] 파일 삭제 실패 {filename}: {e}")
    print(f"[INFO] 레거시 IT 자동 수집 기사 총 {removed_count}개 일괄 삭제 완료!")
    
    collected_count = 0
    # 피드당 2개씩 수집하여 최종 엄선된 고품질 기사 총 5~6개 수집 목표 달성
    max_collect_limit = 6
    
    for idx, feed_info in enumerate(feeds):
        if collected_count >= max_collect_limit:
            break
            
        print(f"\n[FEED] 테크 채널 분석 개시: {feed_info['name']}")
        try:
            feed = feedparser.parse(feed_info["url"])
        except Exception as e:
            print(f"  [ERROR] RSS 피드를 읽어들일 수 없습니다: {e}")
            continue
            
        # 가장 최근 기사 최신 3개씩 파싱 시도 (필터에 통과하지 못하는 부실 기사가 있으므로 3개씩 후보 확보)
        entries = feed.entries[:3]
        
        for entry in entries:
            if collected_count >= max_collect_limit:
                break
                
            title = entry.title
            link = entry.link
            summary = entry.get("summary", entry.get("description", ""))
            summary_clean = clean_html(summary)
            
            # [보안 필터 1]: 애드센스 정책 위반 키워드가 섞여 있으면 스크랩 원천 배제
            if check_blacklist(title) or check_blacklist(summary_clean):
                print(f"  [BLOCKED] 애드센스 정책 위반 소지 감지 기사 배제: {title[:20]}...")
                continue
                
            # [품질 필터 2]: 요약문 글자 수가 80자 이하이거나 메타데이터 텍스트만 있는 부실 기사는 수집 원천 제외!
            if not validate_content(title, summary_clean):
                print(f"  [SKIP QUALITY] 알맹이가 없고 단순 메타데이터만 든 부실 기사 거부: {title[:20]}...")
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
                Your task is to write a highly detailed, extremely engaging, and long-form (at least 1800 Korean characters) blog post in Korean based on this information.
                
                CRITICAL COPYRIGHT & POLICY RULES:
                1. DO NOT copy-paste standard or generic explanations. You must write a completely customized, unique, and highly specific 4 principles guide that directly relates to the input news topic.
                   For instance, if the news is about Amazon Bedrock prompt optimization:
                     - Explain Developer Experience (DX) in terms of Prompt Engineering and playground latency.
                     - Explain Web Performance in terms of LLM token latency and network payload.
                     - Explain Security in terms of data privacy and model parameters protection.
                     - Explain Scalability in terms of deploying multiple AI models for business growth.
                   Every principle must be 100% custom-written and deeply tailored to the specific news topic. Repeating generic definitions is strictly forbidden!
                2. Adhere strictly to the Google AdSense Program Policies. Never generate illegal, adult, hacking, crack, bypass, gambling, or violent contents.
                3. The tone of voice must be polite, highly professional, informative, and friendly (use '-요', '-습니다' style).
                
                Input Article Title: {title}
                Input Article Summary: {cleaned_summary}
                
                Your Output Format MUST contain only the raw body of the article in standard Markdown format.
                Do not include YAML frontmatter, do not include H1 title inside the markdown.
                Structure the post beautifully with Heading 2 (##) and Heading 3 (###).
                Include:
                ## 1. 최신 의학/테크 리포트 요약 및 팩트 체크 (Detailed explanation of the news)
                ## 2. IT 개발자 및 엔지니어를 위한 심층 기술 시사점 (Empathy, practical daily tech tips, connection to modern DX/UX)
                ## 3. 모던 IT 엔지니어링 4대 철칙 실천 가이드 (DX, Web Performance, Security-First, Scalability specific engineering guidelines deeply customized to this news)
                ## 4. 결론 및 테크 리더십 관점의 시사점 (Empathetic tech closing statement)
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