'use client';

import { useState, useMemo } from 'react';
import Link from 'next/link';
import { Search, Filter, X, ArrowRight, Clock, ExternalLink, CheckCircle2, AlertCircle, XCircle } from 'lucide-react';
import { MOCK_OPPORTUNITIES } from '@/lib/mock-data';
import type { Opportunity, OpportunityType, EducationLevel } from '@/lib/types';

function daysUntil(d: string) { return Math.ceil((new Date(d).getTime() - Date.now()) / 86400000); }

function OpportunityCard({ opp }: { opp: Opportunity }) {
  const days = opp.closing_date ? daysUntil(opp.closing_date) : null;
  const statusColors = { Active: '#10b981', Closed: '#ef4444', Upcoming: '#06b6d4', Unknown: '#6b7280' };
  const color = statusColors[opp.status] ?? '#6b7280';

  return (
    <Link href={`/opportunities/${opp.id}`} style={{ textDecoration: 'none' }}>
      <div className="card glass-hover" style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '0.75rem', gap: '0.5rem' }}>
          <div>
            <span className={`badge badge-${opp.opportunity_type === 'Fellowship' ? 'cyan' : opp.opportunity_type === 'Grant' ? 'eligible' : 'info'}`} style={{ marginBottom: '0.4rem', display: 'inline-flex' }}>
              {opp.opportunity_type}
            </span>
            <h3 style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--text-primary)', lineHeight: 1.35 }}>
              {opp.name}
            </h3>
          </div>
          <span style={{ padding: '0.2rem 0.55rem', borderRadius: 9999, fontSize: '0.68rem', fontWeight: 600, background: `${color}18`, color, border: `1px solid ${color}33`, whiteSpace: 'nowrap', flexShrink: 0 }}>
            {opp.status}
          </span>
        </div>

        <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', lineHeight: 1.55, flex: 1, marginBottom: '0.875rem' }}>
          {opp.provider}
        </p>

        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem', marginBottom: '0.875rem' }}>
          {opp.education_level.slice(0, 3).map((l) => (
            <span key={l} className="badge badge-unknown" style={{ fontSize: '0.68rem' }}>{l}</span>
          ))}
          {opp.category?.slice(0, 2).map((c) => (
            <span key={c} className="badge badge-info" style={{ fontSize: '0.68rem' }}>{c}</span>
          ))}
        </div>

        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', paddingTop: '0.75rem', borderTop: '1px solid var(--border-subtle)' }}>
          <div style={{ display: 'flex', gap: '1rem', fontSize: '0.75rem' }}>
            {opp.amount && <span style={{ color: '#10b981', fontWeight: 600 }}>₹{opp.amount.toLocaleString('en-IN')}</span>}
            {days !== null && days > 0 && (
              <span style={{ color: days <= 14 ? '#ef4444' : days <= 30 ? '#f59e0b' : 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: 4 }}>
                <Clock size={11} /> {days}d left
              </span>
            )}
            {days !== null && days <= 0 && <span style={{ color: '#ef4444', fontSize: '0.72rem' }}>Closed</span>}
          </div>
          <ArrowRight size={14} color="var(--text-muted)" />
        </div>
      </div>
    </Link>
  );
}

export default function OpportunitiesPage() {
  const [query, setQuery] = useState('');
  const [filterType, setFilterType] = useState<string>('');
  const [filterLevel, setFilterLevel] = useState<string>('');
  const [filterStatus, setFilterStatus] = useState<string>('');
  const [showFilters, setShowFilters] = useState(false);

  const filtered = useMemo(() => {
    return MOCK_OPPORTUNITIES.filter((o) => {
      const q = query.toLowerCase();
      const matchQ = !q || o.name.toLowerCase().includes(q) || o.provider.toLowerCase().includes(q) || o.description.toLowerCase().includes(q);
      const matchType = !filterType || o.opportunity_type === filterType;
      const matchLevel = !filterLevel || o.education_level.includes(filterLevel as EducationLevel);
      const matchStatus = !filterStatus || o.status === filterStatus;
      return matchQ && matchType && matchLevel && matchStatus;
    });
  }, [query, filterType, filterLevel, filterStatus]);

  const clearFilters = () => { setQuery(''); setFilterType(''); setFilterLevel(''); setFilterStatus(''); };
  const hasFilters = query || filterType || filterLevel || filterStatus;

  return (
    <div className="animate-fade-in">
      <div className="page-header">
        <h1 className="page-title"><span className="gradient-text">Opportunities</span></h1>
        <p className="page-subtitle">Browse {MOCK_OPPORTUNITIES.length} scholarships, fellowships, and grants</p>
      </div>

      {/* Search + Filters */}
      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
          <div style={{ flex: 1, minWidth: 240, position: 'relative' }}>
            <Search size={15} style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
            <input
              className="input"
              id="search-opportunities"
              style={{ paddingLeft: '2.25rem' }}
              placeholder="Search by name, provider, field..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
          </div>
          <button className="btn-secondary" onClick={() => setShowFilters(!showFilters)} id="toggle-filters">
            <Filter size={14} /> Filters {hasFilters && '•'}
          </button>
          {hasFilters && (
            <button className="btn-ghost" onClick={clearFilters} id="clear-filters">
              <X size={14} /> Clear
            </button>
          )}
        </div>

        {showFilters && (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.75rem', marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid var(--border-subtle)' }}>
            <div>
              <label className="label">Type</label>
              <select className="select" value={filterType} onChange={(e) => setFilterType(e.target.value)} id="filter-type">
                <option value="">All Types</option>
                {['Scholarship','Fellowship','Grant','Loan','Award'].map((t) => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>
            <div>
              <label className="label">Education Level</label>
              <select className="select" value={filterLevel} onChange={(e) => setFilterLevel(e.target.value)} id="filter-level">
                <option value="">All Levels</option>
                {['Class 10','Class 12','Diploma','UG','PG','PhD'].map((l) => <option key={l} value={l}>{l}</option>)}
              </select>
            </div>
            <div>
              <label className="label">Status</label>
              <select className="select" value={filterStatus} onChange={(e) => setFilterStatus(e.target.value)} id="filter-status">
                <option value="">All Statuses</option>
                {['Active','Upcoming','Closed'].map((s) => <option key={s} value={s}>{s}</option>)}
              </select>
            </div>
          </div>
        )}
      </div>

      {/* Results */}
      <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
        Showing <strong style={{ color: 'var(--text-primary)' }}>{filtered.length}</strong> of {MOCK_OPPORTUNITIES.length} opportunities
      </div>
      {filtered.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-secondary)' }}>
          <Search size={32} style={{ margin: '0 auto 1rem', opacity: 0.4 }} />
          <div>No opportunities match your filters.</div>
          <button className="btn-ghost" onClick={clearFilters} style={{ marginTop: '1rem' }}>Clear filters</button>
        </div>
      ) : (
        <div className="grid-3">
          {filtered.map((opp, i) => (
            <div key={opp.id} className="animate-fade-in-up" style={{ animationDelay: `${i * 0.05}s` }}>
              <OpportunityCard opp={opp} />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
