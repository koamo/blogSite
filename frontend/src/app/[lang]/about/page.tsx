import React from 'react';

interface PageProps {
  params: Promise<{
    lang: string;
  }>;
}

export default async function AboutPage({ params }: PageProps) {
  const resolvedParams = await params;
  const lang = resolvedParams.lang || 'ko';

  return (
    <div className="mx-auto max-w-4xl px-6 py-16 prose prose-invert">
      <h1 className="text-3xl md:text-5xl font-black mb-8">About Us</h1>
      <p>
        Welcome to GoldenLog, a premium IT and software engineering knowledge archive.
      </p>
      <p>
        Our mission is to deliver the most valuable, up-to-date technology insights, architectural deep dives, and practical engineering tips to developers and tech enthusiasts globally.
      </p>
      <p>
        We believe in the power of shared knowledge. Everything published here is curated to help you build better software and stay ahead in the rapidly evolving tech landscape.
      </p>
      <h2>Contact Information</h2>
      <ul>
        <li>Email: admin@goldenlog.tech</li>
        <li>Location: Seoul, South Korea</li>
      </ul>
      <p className="text-sm text-slate-500 mt-12">
        Last updated: June 2026
      </p>
    </div>
  );
}
