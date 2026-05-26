import type { Metadata } from 'next';
import { Outfit, Inter } from 'next/font/google';
import '../globals.css'; 
import Header from '@/components/Header';
import Footer from '@/components/Footer';
import AdSenseScript from '@/components/AdSenseScript';

// Outfit 폰트 설정
const outfit = Outfit({
  subsets: ['latin'],
  variable: '--font-outfit',
  display: 'swap',
});

// Inter 폰트 설정
const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
});

export const metadata: Metadata = {
  title: {
    default: 'GoldenLog - 가치 있는 개인 지식 블로그',
    template: '%s | GoldenLog',
  },
  description: '구글 애드센스 승인 및 최신 IT, 생산성, 자기계발 전문 지식을 전달하는 초고속 정적 블로그입니다.',
  keywords: ['애드센스', '수익형블로그', 'IT개발', '생산성팁', '노션', 'NextJS'],
  authors: [{ name: 'GoldenLog' }],
  metadataBase: new URL('http://localhost:3000'), 
  verification: {
    google: 'bGXWFZLkGtDdZACKeIEY5pQB87_7TK1-UatjnGobEkk',
  },
  other: {
    'google-adsense-account': 'ca-pub-7317136702675678',
  },
};

// Next.js 16 글로벌 레이아웃용 Props 타입 정의
interface LayoutProps {
  children: React.ReactNode;
  params: Promise<{
    lang: string;
  }>;
}

/**
 * 다국어 정적 세그먼트 최상단에서 시작하는 전역 루트 레이아웃 컴포넌트입니다.
 */
export default async function RootLayout({
  children,
  params,
}: LayoutProps) {
  const resolvedParams = await params;
  const lang = resolvedParams.lang || 'ko';

  return (
    <html lang={lang} className={`${outfit.variable} ${inter.variable}`}>
      <body className="flex min-h-screen flex-col bg-[#030712] text-slate-100 antialiased">
        {/* 구글 애드센스 전역 심사 스크립트 */}
        <AdSenseScript />
        
        {/* 상단 다국어 선택 스위처가 내장된 헤더 */}
        <Header lang={lang} />
        
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