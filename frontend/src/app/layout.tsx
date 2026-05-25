import type { Metadata } from 'next';
import { Outfit, Inter } from 'next/font/google';
import './globals.css';
import Header from '@/components/Header';
import Footer from '@/components/Footer';
import AdSenseScript from '@/components/AdSenseScript';

// Outfit 폰트 설정 (제목 및 브랜드 강조용)
const outfit = Outfit({
  subsets: ['latin'],
  variable: '--font-outfit',
  display: 'swap',
});

// Inter 폰트 설정 (가독성 높은 본문 리딩용)
const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
});

/**
 * 블로그 전체의 검색 엔진 최적화(SEO)를 보장하는 기본 메타데이터 객체입니다.
 */
export const metadata: Metadata = {
  title: {
    default: 'GoldenLog - 가치를 담는 개인 지식 블로그',
    template: '%s | GoldenLog', // 하위 상세 페이지 제목 접미사 자동화
  },
  description: '구글 애드센스 통과 및 실전 IT, 생산성, 자기계발 전문 지식을 전하는 초고속 정적 블로그입니다.',
  keywords: ['애드센스', '수익형블로그', 'IT개발', '생산성팁', '노션', 'NextJS'],
  authors: [{ name: 'GoldenLog' }],
  metadataBase: new URL('http://localhost:3000'), // 빌드 검증용 기본 베이스 도메인 설정
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ko" className={`${outfit.variable} ${inter.variable}`}>
      <body className="flex min-h-screen flex-col bg-[#030712] text-slate-100 antialiased">
        {/* 구글 애드센스 전역 심사 스크립트 */}
        <AdSenseScript />
        
        {/* 상단 글래스모피즘 네비게이션 헤더 */}
        <Header />
        
        {/* 본문 콘텐츠 렌더링 영역 */}
        <main className="flex-grow">
          {children}
        </main>
        
        {/* 하단 푸터 */}
        <Footer />
      </body>
    </html>
  );
}
