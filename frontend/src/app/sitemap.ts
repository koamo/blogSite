import { MetadataRoute } from 'next';
// [절대참조 적용]: Next.js 번들 규격에 맞게 최적 경로 호출
import postsData from '@/data/posts.json';

interface BlogPost {
  slug: string;
  date: string;
}

export default function sitemap(): MetadataRoute.Sitemap {
  const posts: BlogPost[] = postsData as BlogPost[];
  const baseUrl = process.env.NEXT_PUBLIC_SITE_URL || 'http://localhost:3000';

  // 1. 핵심 기본 루트 페이지 설정
  const routes = [
    {
      url: baseUrl,
      lastModified: new Date(),
      changeFrequency: 'daily' as const,
      priority: 1.0,
    },
  ];

  // 2. 파싱된 정적 기사들의 개별 라우트를 사이트맵에 다이렉트 자동 누적
  const postRoutes = posts.map((post) => ({
    url: `${baseUrl}/posts/${post.slug}`,
    lastModified: new Date(post.date),
    changeFrequency: 'weekly' as const,
    priority: 0.8,
  }));

  return [...routes, ...postRoutes];
}
