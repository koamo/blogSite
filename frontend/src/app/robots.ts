import { MetadataRoute } from 'next';

/**
 * 구글 봇 등 전 세계 검색 엔진 크롤러에게 사이트 크롤링 정책을 동적으로 가이드하는 robots.txt 파일 생성기입니다.
 */
export default function robots(): MetadataRoute.Robots {
  const baseUrl = process.env.NEXT_PUBLIC_SITE_URL || 'http://localhost:3000';
  
  return {
    rules: {
      userAgent: '*',     // 모든 검색 로봇 지칭
      allow: '/',         // 사이트 전체 영역 크롤링 전면 허용 (애드센스 승인 보장)
      disallow: '/private/', // 비공개 테스트 영역 등 예외 격리
    },
    sitemap: `${baseUrl}/sitemap.xml`, // 사이트맵 절대 경로 자동 맵핑
  };
}
