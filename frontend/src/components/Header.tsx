import Link from 'next/link';

/**
 * 블로그의 글로벌 상단 네비게이션 헤더 컴포넌트입니다.
 * 초고급 글래스모피즘 배경 반투명 필터링과 그라데이션 포인트 로고가 특징입니다.
 */
export default function Header() {
  return (
    <header className="sticky top-0 z-50 w-full border-b border-slate-200/10 bg-slate-950/80 backdrop-blur-md">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-6">
        
        {/* 블로그 메인 로고 영역 (화려한 네온 그라데이션 텍스트) */}
        <Link href="/" className="flex items-center gap-2">
          <span className="bg-gradient-to-r from-violet-400 via-indigo-400 to-cyan-400 bg-clip-text text-xl font-black tracking-tight text-transparent transition-transform hover:scale-105 duration-200">
            GoldenLog.
          </span>
        </Link>
        
        {/* 네비게이션 메뉴 영역 */}
        <nav className="flex items-center gap-6">
          <Link href="/" className="text-sm font-medium text-slate-300 hover:text-violet-300 transition-colors">
            전체 기사
          </Link>
          
          {/* 애드센스 정책 안내 링크 (블로그의 애드센스 목표 표시용 연동) */}
          <a 
            href="https://adsense.google.com" 
            target="_blank" 
            rel="noopener noreferrer"
            className="rounded-full bg-violet-600/15 border border-violet-500/30 px-4 py-1.5 text-xs font-semibold text-violet-300 hover:bg-violet-600/25 transition-all hover:border-violet-500/50"
          >
            AdSense Info
          </a>
        </nav>
      </div>
    </header>
  );
}
