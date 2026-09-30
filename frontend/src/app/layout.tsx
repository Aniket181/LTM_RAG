import type { Metadata } from 'next';
import './globals.css';
import Sidebar from '@/components/layout/Sidebar';

export const metadata: Metadata = {
  title: {
    template: '%s | ScholarAI — RAG Scholarship Intelligence',
    default: 'ScholarAI — RAG Scholarship Intelligence System',
  },
  description:
    'Intelligent scholarship discovery and eligibility determination powered by RAG, Hybrid Retrieval, and a Deterministic Eligibility Engine.',
  keywords: ['scholarship', 'eligibility', 'RAG', 'AI', 'education', 'fellowship', 'India'],
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>
        <Sidebar />
        <main className="main-content">
          {children}
        </main>
      </body>
    </html>
  );
}
