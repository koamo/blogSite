import type { Metadata } from 'next';
import Link from 'next/link';
import { notFound } from 'next/navigation';
import AdSenseUnit from '@/components/AdSenseUnit';
// [절대참조 적용]: Next.js 번들 규격에 맞게 최적 경로 호출
import postsData from '@/data/posts.json';

interface BlogPost {
  title: string;
  date: string;
  description: string;
  tags: string[];
  thumbnail: string;
  slug: string;
  content: string;
}

interface PageProps {
  params: Promise<{
    slug: string;
  }>;
}

/**
 * 1. 빌드 타임에 모든 포스팅 경로를 물리 정적 파일로 생성하는 핵심 SSG 로직
 */
export async function generateStaticParams() {
  const posts: BlogPost[] = postsData as BlogPost[];
  return posts.map((post) => ({
    slug: post.slug,
  }));
}

/**
 * 2. 각 아티클의 내용에 따라 동적으로 메타태그를 생성하는 기술적 SEO 최적화 로직
 */
export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const resolvedParams = await params;
  const posts: BlogPost[] = postsData as BlogPost[];
  const post = posts.find((p) => p.slug === resolvedParams.slug);
  
  if (!post) {
    return {
      title: 'Not Found',
    };
  }
  
  return {
    title: post.title,
    description: post.description,
    keywords: post.tags,
    openGraph: {
      title: post.title,
      description: post.description,
      type: 'article',
      publishedTime: post.date,
      authors: ['GoldenLog'],
      tags: post.tags,
    },
  };
}

/**
 * 블로그 상세 기사 페이지 렌더러 컴포넌트입니다.
 */
export default async function PostDetailPage({ params }: PageProps) {
  const resolvedParams = await params;
  const posts: BlogPost[] = postsData as BlogPost[];
  const post = posts.find((p) => p.slug === resolvedParams.slug);
  
  if (!post) {
    notFound();
  }
  
  return (
    <article className="mx-auto max-w-4xl px-6 py-12">
      
      {/* 럭셔리 트랜지션 뒤로가기 링크 */}
      <Link 
        href="/"
        className="inline-flex items-center gap-1.5 text-sm text-slate-400 hover:text-violet-400 transition-colors mb-8 group focus:outline-none"
      >
        <span className="inline-block transition-transform group-hover:-translate-x-1 duration-200">←</span>
        전체 아티클 목록으로
      </Link>

      {/* 기사 헤더 및 메타데이터 영역 */}
      <header className="mb-8 pb-8 border-b border-slate-800/60">
        <div className="flex flex-wrap gap-2 mb-4">
          {post.tags.map((tag) => (
            <span 
              key={tag}
              className="rounded bg-violet-600/10 border border-violet-500/20 px-2.5 py-0.5 text-xs text-violet-300 font-semibold"
            >
              #{tag}
            </span>
          ))}
        </div>
        
        <h1 className="text-3xl md:text-5xl font-black tracking-tight text-white mb-4 leading-tight font-['Outfit']">
          {post.title}
        </h1>
        
        <div className="flex items-center gap-3 text-slate-500 text-sm">
          <span className="font-semibold text-slate-400">By GoldenLog</span>
          <span>·</span>
          <span>{post.date}</span>
        </div>
      </header>

      {/* [수익화 장치 1] 기사 본문 상단 애드센스 배너 영역 */}
      <AdSenseUnit slot="2000000001" format="auto" />

      {/* [본문 렌더링] 마크다운 컴파일 HTML 및 수려한 타이포그래피 이식 */}
      <section 
        className="prose max-w-none my-12"
        dangerouslySetInnerHTML={{ __html: post.content }}
      />

      {/* [수익화 장치 2] 기사 본문 하단 애드센스 배너 영역 */}
      <AdSenseUnit slot="2000000002" format="auto" />
      
    </article>
  );
}
