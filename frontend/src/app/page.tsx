import Link from 'next/link';
import AdSenseUnit from '@/components/AdSenseUnit';
// [절대참조 적용]: Next.js 번들 가이드라인에 맞춰 src/data/posts.json을 다이렉트 호출
import postsData from '@/data/posts.json';

interface BlogPost {
  title: string;
  date: string;
  description: string;
  tags: string[];
  thumbnail: string;
  slug: string;
}

export default function Home() {
  const posts: BlogPost[] = postsData as BlogPost[];

  return (
    <div className="mx-auto max-w-6xl px-6 py-12">
      
      {/* 럭셔리 네온 아우라 히어로 섹션 */}
      <section className="relative overflow-hidden rounded-3xl bg-[#090d16]/80 border border-slate-800/60 p-8 md:p-12 mb-16 text-center md:text-left">
        <div className="absolute top-0 right-0 w-80 h-80 bg-violet-600/10 rounded-full blur-3xl -z-10" />
        <div className="absolute bottom-0 left-0 w-60 h-60 bg-cyan-600/10 rounded-full blur-3xl -z-10" />
        
        <span className="inline-block rounded-full bg-violet-500/10 border border-violet-500/20 px-4 py-1 text-xs font-semibold text-violet-300 mb-4">
          ✨ Premium Knowledge Archive
        </span>
        
        <h1 className="text-3xl md:text-5xl font-extrabold tracking-tight text-white mb-4 leading-tight">
          지식의 가치를 더하는 공간, <br className="hidden md:inline"/>
          <span className="bg-gradient-to-r from-violet-400 via-indigo-400 to-cyan-400 bg-clip-text text-transparent">
            GoldenLog
          </span>에 오신 것을 환영합니다.
        </h1>
        
        <p className="text-slate-400 max-w-2xl text-base md:text-lg leading-relaxed">
          수익형 구글 애드센스 심사를 한 번에 통과하기 위한 최적의 기술 세팅 위에, 
          엄선된 IT 실무 기술 지식과 스마트한 시간 관리 팁, 그리고 자기계발 노하우를 깊이 있게 기록합니다.
        </p>
      </section>

      {/* 타이틀 및 발행 현황 영역 */}
      <div className="flex items-center justify-between mb-8">
        <h2 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2 font-['Outfit']">
          최신 발행 아티클
          <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
        </h2>
        <span className="text-xs text-slate-500 font-medium">총 {posts.length}개 발행됨</span>
      </div>

      {/* 포스팅 카드 그리드 레이아웃 (반응형 3열 구성) */}
      <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
        {posts.map((post) => (
          <article 
            key={post.slug}
            className="group relative flex flex-col overflow-hidden rounded-2xl border border-slate-800/60 bg-[#070b12]/60 transition-all duration-300 hover:-translate-y-1.5 hover:border-violet-500/40 hover:shadow-2xl hover:shadow-violet-600/5"
          >
            {/* 카드 상단 썸네일 장식 영역 (수려한 그라데이션 플레이스홀더) */}
            <div className="relative h-48 w-full bg-gradient-to-br from-[#0c1220] via-[#080d16] to-[#04080e] flex items-center justify-center p-6 border-b border-slate-800/40">
              <div className="absolute top-0 right-0 w-24 h-24 bg-violet-500/5 rounded-full blur-xl transition-all group-hover:bg-violet-500/15" />
              <span className="text-4xl text-violet-400 group-hover:scale-110 transition-transform duration-300 filter drop-shadow-[0_4px_6px_rgba(139,92,246,0.2)]">
                📝
              </span>
            </div>

            {/* 카드 하단 텍스트 상세 영역 */}
            <div className="flex flex-grow flex-col p-6">
              <span className="text-xs text-slate-500 font-semibold mb-2">{post.date}</span>
              
              <h3 className="text-xl font-bold text-slate-100 group-hover:text-violet-400 transition-colors duration-200 line-clamp-2 mb-2">
                <Link href={`/posts/${post.slug}`} className="focus:outline-none">
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

      {/* 사이트 메인 홈 하단 디스플레이 광고 슬롯 (구글 심사용 플레이스홀더 배치) */}
      <div className="mt-24">
        <AdSenseUnit slot="1000000001" format="auto" />
      </div>
    </div>
  );
}
