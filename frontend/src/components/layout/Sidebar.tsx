'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard, User, Search, Star, BookOpen,
  MessageSquare, FileText, GraduationCap, Activity,
} from 'lucide-react';

const navItems = [
  { href: '/',               icon: LayoutDashboard, label: 'Dashboard' },
  { href: '/profile',        icon: User,            label: 'My Profile' },
  { href: '/opportunities',  icon: Search,          label: 'Opportunities' },
  { href: '/recommendations',icon: Star,            label: 'Recommendations' },
  { href: '/chat',           icon: MessageSquare,   label: 'AI Assistant' },
  { href: '/sources',        icon: FileText,        label: 'Sources' },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="sidebar">
      {/* Logo */}
      <div style={{ marginBottom: '2rem', paddingLeft: '0.25rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.625rem', marginBottom: '0.25rem' }}>
          <div style={{
            width: 36, height: 36,
            background: 'var(--grad-primary)',
            borderRadius: '0.625rem',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            boxShadow: '0 4px 15px rgba(99,102,241,0.4)',
            flexShrink: 0,
          }}>
            <GraduationCap size={20} color="white" />
          </div>
          <div>
            <div style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-primary)', lineHeight: 1.2 }}>
              ScholarAI
            </div>
            <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', letterSpacing: '0.04em' }}>
              RAG INTELLIGENCE
            </div>
            <div style={{ marginTop: '0.25rem', display: 'inline-block', fontSize: '0.55rem', fontWeight: 600, color: '#f59e0b', background: 'rgba(245,158,11,0.1)', padding: '0.1rem 0.35rem', borderRadius: '4px', border: '1px solid rgba(245,158,11,0.2)' }}>
              LOCAL DEMO MODE
            </div>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav style={{ flex: 1 }}>
        <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', fontWeight: 600, letterSpacing: '0.08em', textTransform: 'uppercase', padding: '0 0.875rem', marginBottom: '0.5rem' }}>
          Navigation
        </div>
        {navItems.map(({ href, icon: Icon, label }) => {
          const active = pathname === href || (href !== '/' && pathname.startsWith(href));
          return (
            <Link key={href} href={href} className={`sidebar-item ${active ? 'active' : ''}`}>
              <Icon size={16} />
              <span>{label}</span>
            </Link>
          );
        })}
      </nav>

      {/* System Status */}
      <div style={{ marginTop: 'auto', paddingTop: '1.5rem' }}>
        <div className="glass" style={{ borderRadius: '0.75rem', padding: '0.75rem', fontSize: '0.75rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
            <Activity size={12} color="#10b981" />
            <span style={{ color: '#10b981', fontWeight: 600 }}>System Online</span>
          </div>
          <div style={{ color: 'var(--text-muted)', lineHeight: 1.5 }}>
            <div>LLM: Llama 3.2 / Ollama</div>
            <div>Embeddings: BGE v1.5</div>
          </div>
        </div>
      </div>
    </aside>
  );
}
