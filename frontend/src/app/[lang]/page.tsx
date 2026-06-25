import Link from 'next/link';
import AdSenseUnit from '@/components/AdSenseUnit';
// Next.js 내부 데이터 저장소에 파이썬이 다국어 번역 적재해 놓은 posts.json 로드
import postsData from '@/data/posts.json';

interface BlogPost {
  title: string;
  date: string;
  description: string;
  tags: string[];
  thumbnail: string;
  slug: string;
  lang: string;
}

// Next.js 16+ 비동기 Params 컴포넌트 프롭스 규격
interface PageProps {
  params: Promise<{
    lang: string;
  }>;
}

/**
 * 1. 빌드 타임에 지원 언어 목록(/ko, /en, /ja)을 정적 라우트 주소로 선제 생성하는 로직
 */
export async function generateStaticParams() {
  return [
    { lang: 'ko' },
    { lang: 'en' },
    { lang: 'ja' }
  ];
}

/**
 * 다국어 블로그 홈 페이지 렌더러 컴포넌트입니다.
 */
export default async function Home({ params }: PageProps) {
  const resolvedParams = await params;
  const lang = resolvedParams.lang || 'ko';
  
  // 1차 필터링: postsData 데이터베이스에서 현재 라우트 언어 스펙에 부합하는 글만 추출
  const allPosts: BlogPost[] = postsData as BlogPost[];
  const posts = allPosts.filter((post) => post.lang === lang);

  // [프리미엄 포털 구조] 최신 1개는 Featured, 그 다음 9개는 Recent로 분리
  const featuredPost = posts[0];
  const recentPosts = posts.slice(1, 10);

  // 2차 다국어 번역 딕셔너리 (i18n) 설정 - 레이아웃 핵심 텍스트 자동 대응
  const translations = {
    ko: {
      badge: '✨ 프리미엄 지식 아카이브',
      welcome: '지식의 가치를 더하는 공간,',
      description: '최신 웹 개발 트렌드, 서버 아키텍처 및 실무 엔지니어링 지식을 깊이 있게 다루는 프리미엄 테크놀로지 블로그입니다.',
      latest: '최신 발행 아티클',
      total: `총 ${posts.length}개 발행됨`,
      readMore: '자세히 보기',
      featured: '🔥 오늘의 추천 아티클',
      viewAll: '모든 기사 보기 →'
    },
    en: {
      badge: '✨ Premium Knowledge Archive',
      welcome: 'A space that adds value to knowledge,',
      description: 'A premium technology blog covering the latest web development trends, server architecture, and practical engineering knowledge in depth.',
      latest: 'Latest Publications',
      total: `Total ${posts.length} articles published`,
      readMore: 'Read Article',
      featured: '🔥 Featured Article',
      viewAll: 'View All Articles →'
    },
    ja: {
      badge: '✨ プレミアム知識アーカイブ',
      welcome: '知識の価値を高める空間、',
      description: '最新のWeb開発トレンド、サーバーアーキテクチャ、および実務エンジニアリングの知識を深く掘り下げるプレミアムテクノロジーブログです。',
      latest: '最新の発行記事',
      total: `合計 ${posts.length} 個の記事`,
      readMore: '詳細を見る',
      featured: '🔥 おすすめ記事',
      viewAll: 'すべての記事を見る →'
    }
  };

  const t = translations[lang as 'ko' | 'en' | 'ja'] || translations.ko;

  return (
    <div className="mx-auto max-w-6xl px-6 py-12">
      
      {/* 럭셔리 네온 아우라 히어로 섹션 */}
      <section className="relative overflow-hidden rounded-3xl bg-[#090d16]/80 border border-slate-800/60 p-8 md:p-12 mb-16 text-center md:text-left">
        <div className="absolute top-0 right-0 w-80 h-80 bg-violet-600/10 rounded-full blur-3xl -z-10" />
        <div className="absolute bottom-0 left-0 w-60 h-60 bg-cyan-600/10 rounded-full blur-3xl -z-10" />
        
        <span className="inline-block rounded-full bg-violet-500/10 border border-violet-500/20 px-4 py-1 text-xs font-semibold text-violet-300 mb-4">
          {t.badge}
        </span>
        
        <h1 className="text-3xl md:text-5xl font-extrabold tracking-tight text-white mb-4 leading-tight">
          {t.welcome} <br className="hidden md:inline"/>
          <span className="bg-gradient-to-r from-violet-400 via-indigo-400 to-cyan-400 bg-clip-text text-transparent">
            GoldenLog
          </span>
        </h1>
        
        <p className="text-slate-400 max-w-2xl text-base md:text-lg leading-relaxed">
          {t.description}
        </p>
      </section>

      {/* [Featured Post] 대형 썸네일 추천 기사 (애드센스 구조 최적화) */}
      {featuredPost && (
        <div className="mb-20">
          <h2 className="text-xl font-bold tracking-tight text-violet-400 flex items-center gap-2 mb-6 font-['Outfit']">
            {t.featured}
          </h2>
          <Link href={`/${lang}/posts/${featuredPost.slug}`} className="group relative flex flex-col md:flex-row overflow-hidden rounded-3xl border border-slate-800/80 bg-[#070b12]/80 transition-all duration-300 hover:border-violet-500/40 hover:shadow-2xl hover:shadow-violet-600/10">
            {/* Featured 이미지 */}
            <div className="w-full md:w-1/2 h-64 md:h-auto bg-slate-900 relative overflow-hidden">
              {featuredPost.thumbnail ? (
                <img src={featuredPost.thumbnail} alt={featuredPost.title} className="absolute inset-0 w-full h-full object-cover opacity-80 group-hover:opacity-100 transition-opacity duration-500 group-hover:scale-105" />
              ) : (
                <div className="absolute inset-0 bg-gradient-to-br from-violet-900/40 to-cyan-900/20 flex items-center justify-center">
                  <span className="text-6xl filter drop-shadow-lg">✨</span>
                </div>
              )}
            </div>
            {/* Featured 내용 */}
            <div className="w-full md:w-1/2 p-8 md:p-12 flex flex-col justify-center">
              <span className="text-sm text-slate-500 font-semibold mb-3">{featuredPost.date}</span>
              <h3 className="text-3xl font-extrabold text-white group-hover:text-violet-400 transition-colors duration-200 mb-4 leading-tight">
                {featuredPost.title}
              </h3>
              <p className="text-slate-400 text-base leading-relaxed line-clamp-3 mb-6">
                {featuredPost.description}
              </p>
              <div className="flex flex-wrap gap-2 mt-auto">
                {featuredPost.tags.map((tag) => (
                  <span key={tag} className="rounded bg-violet-600/20 border border-violet-500/30 px-3 py-1 text-xs text-violet-300 font-semibold">
                    #{tag}
                  </span>
                ))}
              </div>
            </div>
          </Link>
        </div>
      )}

      {/* 타이틀 및 발행 현황 영역 */}
      <div className="flex items-center justify-between mb-8 pb-4 border-b border-slate-800">
        <h2 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2 font-['Outfit']">
          {t.latest}
          <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
        </h2>
        <span className="text-xs text-slate-500 font-medium">{t.total}</span>
      </div>

      {/* 포스팅 카드 그리드 레이아웃 (반응형 3열 구성 - 최신 9개만 노출) */}
      <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
        {recentPosts.map((post) => (
          <article 
            key={`${post.slug}-${post.lang}`}
            className="group relative flex flex-col overflow-hidden rounded-2xl border border-slate-800/60 bg-[#070b12]/60 transition-all duration-300 hover:-translate-y-1.5 hover:border-violet-500/40 hover:shadow-2xl hover:shadow-violet-600/5"
          >
            {/* 카드 상단 썸네일 장식 영역 */}
            <div className="relative h-48 w-full bg-slate-900 flex items-center justify-center border-b border-slate-800/40 overflow-hidden">
              {post.thumbnail ? (
                <img src={post.thumbnail} alt={post.title} className="absolute inset-0 w-full h-full object-cover opacity-60 group-hover:opacity-90 transition-opacity duration-300 group-hover:scale-105" loading="lazy" />
              ) : (
                <>
                  <div className="absolute top-0 right-0 w-24 h-24 bg-violet-500/5 rounded-full blur-xl transition-all group-hover:bg-violet-500/15" />
                  <span className="text-4xl text-violet-400 group-hover:scale-110 transition-transform duration-300 filter drop-shadow-[0_4px_6px_rgba(139,92,246,0.2)]">📝</span>
                </>
              )}
            </div>

            {/* 카드 하단 텍스트 상세 영역 */}
            <div className="flex flex-grow flex-col p-6">
              <span className="text-xs text-slate-500 font-semibold mb-2">{post.date}</span>
              
              <h3 className="text-xl font-bold text-slate-100 group-hover:text-violet-400 transition-colors duration-200 line-clamp-2 mb-2">
                <Link href={`/${lang}/posts/${post.slug}`} className="focus:outline-none">
                  {post.title}
                </Link>
              </h3>
              
              <p className="text-slate-400 text-sm leading-relaxed line-clamp-3 mb-4">
                {post.description}
              </p>

              {/* 개별 태그 목록 */}
              <div className="mt-auto flex flex-wrap gap-1.5">
                {post.tags.map((tag) => (
                  <span 
                    key={tag}
                    className="rounded bg-slate-800/40 border border-slate-800/80 px-2.5 py-0.5 text-xs text-slate-400"
                  >
                    #{tag}
                  </span>
                ))}
              </div>
            </div>
          </article>
        ))}
      </div>

      {/* [아카이브 링크] 모든 기사 보기 버튼 */}
      <div className="mt-12 flex justify-center">
        <Link 
          href={`/${lang}/archive`}
          className="inline-flex items-center justify-center px-8 py-3 text-sm font-bold text-white bg-slate-800 hover:bg-violet-600 rounded-full transition-colors duration-300 shadow-lg shadow-black/50"
        >
          {t.viewAll}
        </Link>
      </div>

      {/* 사이트 메인 홈 하단 디스플레이 광고 슬롯 */}
      <div className="mt-24">
        <AdSenseUnit slot="1000000001" format="auto" />
      </div>
    </div>
  );
}
