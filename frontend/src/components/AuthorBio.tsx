import React from 'react';

export default function AuthorBio({ lang = 'ko' }: { lang?: string }) {
  const translations = {
    ko: {
      name: 'GoldenLog Tech Team',
      role: '프리미엄 테크놀로지 큐레이터 & 엔지니어링 스페셜리스트',
      bio: '실리콘밸리 트렌드부터 딥테크 아키텍처까지, 복잡한 기술의 본질을 꿰뚫는 프리미엄 테크 저널을 지향합니다. 가장 가치 있는 인사이트로 당신의 기술적 성장을 돕습니다.',
      articles: '모든 작성 글 보기'
    },
    en: {
      name: 'GoldenLog Tech Team',
      role: 'Premium Technology Curator & Engineering Specialist',
      bio: 'From Silicon Valley trends to deep-tech architectures, we aim to be a premium tech journal that penetrates the essence of complex technologies. We help your technical growth with the most valuable insights.',
      articles: 'View all articles'
    },
    ja: {
      name: 'GoldenLog Tech Team',
      role: 'プレミアムテクノロジーキュレーター & エンジニアリングスペシャリスト',
      bio: 'シリコンバレーのトレンドからディープテックのアーキテクチャまで、複雑な技術の本質を見抜くプレミアムテックジャーナルを目指しています。最も価値のある洞察であなたの技術的成長をサポートします。',
      articles: 'すべての記事を見る'
    }
  };

  const t = translations[lang as 'ko' | 'en' | 'ja'] || translations.ko;

  return (
    <div className="mt-16 pt-8 border-t border-slate-800/60 flex flex-col sm:flex-row gap-6 items-start">
      <div className="w-16 h-16 rounded-full bg-gradient-to-br from-cyan-500 to-indigo-600 flex-shrink-0 flex items-center justify-center text-xl text-white font-black shadow-lg">
        GL
      </div>
      <div>
        <h4 className="text-lg font-bold text-white mb-1">{t.name}</h4>
        <p className="text-cyan-400 text-sm font-semibold mb-3">{t.role}</p>
        <p className="text-slate-400 text-sm leading-relaxed mb-4">
          {t.bio}
        </p>
      </div>
    </div>
  );
}
