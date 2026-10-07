'use client';

import { use, useState, useEffect } from 'react';
import Link from 'next/link';
import {
  ArrowLeft, CheckCircle2, XCircle, AlertCircle, HelpCircle,
  ExternalLink, Clock, Calendar, FileText, GraduationCap,
  IndianRupee, Info,
} from 'lucide-react';
import { getOpportunity } from '@/lib/api';
import type { Opportunity } from '@/lib/types';

function daysUntil(d: string) { return Math.ceil((new Date(d).getTime() - Date.now()) / 86400000); }

export default function OpportunityDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [opp, setOpp] = useState<Opportunity | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchO() {
      try {
        const o = await getOpportunity(id);
        setOpp(o);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }
    fetchO();
  }, [id]);

  if (loading) {
    return (
      <div className="animate-fade-in" style={{ textAlign: 'center', padding: '4rem', color: 'var(--text-muted)' }}>
        Loading opportunity details...
      </div>
    );
  }

  if (!opp) {
    return (
      <div className="animate-fade-in" style={{ textAlign: 'center', padding: '4rem' }}>
        <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🔍</div>
        <div style={{ color: 'var(--text-secondary)' }}>Opportunity not found.</div>
        <Link href="/opportunities" className="btn-primary" style={{ marginTop: '1.5rem', display: 'inline-flex' }}>
          <ArrowLeft size={14} /> Back to Opportunities
        </Link>
      </div>
    );
  }

  const days = opp.closing_date ? daysUntil(opp.closing_date) : null;
  const statusColors: Record<string, string> = { Active: '#10b981', Closed: '#ef4444', Upcoming: '#06b6d4', Unknown: '#6b7280' };
  const eligibilityColors: Record<string, string> = { ELIGIBLE: '#10b981', NOT_ELIGIBLE: '#ef4444', POTENTIALLY_ELIGIBLE: '#f59e0b', INSUFFICIENT_INFORMATION: '#6b7280' };

  return (
    <div className="animate-fade-in">
      {/* Back */}
      <Link href="/opportunities" className="btn-ghost" style={{ marginBottom: '1.5rem', display: 'inline-flex' }}>
        <ArrowLeft size={14} /> Back to Opportunities
      </Link>

      {/* Header */}
      <div className="card" style={{ marginBottom: '1.5rem', background: 'linear-gradient(135deg, rgba(99,102,241,0.1) 0%, rgba(139,92,246,0.06) 100%)' }}>
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: '1.25rem', flexWrap: 'wrap' }}>
          <div style={{ flex: 1, minWidth: 280 }}>
            <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginBottom: '0.625rem' }}>
              <span className="badge badge-info">{opp.opportunity_type}</span>
              <span style={{ padding: '0.2rem 0.55rem', borderRadius: 9999, fontSize: '0.7rem', fontWeight: 600, background: `${statusColors[opp.status]}18`, color: statusColors[opp.status], border: `1px solid ${statusColors[opp.status]}33` }}>
                {opp.status}
              </span>
            </div>
            <h1 style={{ fontSize: '1.4rem', fontWeight: 700, color: 'var(--text-primary)', lineHeight: 1.3, marginBottom: '0.5rem' }}>
              {opp.name}
            </h1>
            <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '1rem' }}>{opp.provider}</div>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.65 }}>{opp.description}</p>
          </div>

          {/* Key Info Box */}
          <div style={{ width: 220, flexShrink: 0 }}>
            <div className="glass" style={{ padding: '1rem', borderRadius: '0.75rem' }}>
              {opp.amount && (
                <div style={{ textAlign: 'center', marginBottom: '0.875rem', paddingBottom: '0.875rem', borderBottom: '1px solid var(--border-subtle)' }}>
                  <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#10b981' }}>
                    ₹{opp.amount.toLocaleString('en-IN')}
                  </div>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>per year</div>
                </div>
              )}
              {[
                opp.closing_date && { label: 'Deadline', value: new Date(opp.closing_date).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' }), icon: Calendar, warn: days !== null && days <= 30 },
                opp.duration && { label: 'Duration', value: opp.duration, icon: Clock, warn: false },
                opp.academic_year && { label: 'Academic Year', value: opp.academic_year, icon: GraduationCap, warn: false },
                opp.last_verified_date && { label: 'Last Verified', value: new Date(opp.last_verified_date).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' }), icon: Info, warn: false },
              ].filter(Boolean).map((item: any, i) => (
                <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.75rem', marginBottom: '0.5rem' }}>
                  <item.icon size={12} color={item.warn ? '#f59e0b' : 'var(--text-muted)'} />
                  <span style={{ color: 'var(--text-muted)' }}>{item.label}:</span>
                  <span style={{ color: item.warn ? '#f59e0b' : 'var(--text-secondary)', fontWeight: 500 }}>{item.value}</span>
                </div>
              ))}
              {opp.official_url && (
                <a href={opp.official_url} target="_blank" rel="noopener noreferrer" className="btn-primary" style={{ width: '100%', justifyContent: 'center', marginTop: '0.75rem', fontSize: '0.8rem', padding: '0.5rem 1rem' }}>
                  Apply Now <ExternalLink size={12} />
                </a>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Main Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: '1.5rem', alignItems: 'start' }}>
        <div>
          {/* Required Documents */}
          {opp.required_documents && opp.required_documents.length > 0 && (
            <div className="card" style={{ marginBottom: '1.25rem' }}>
              <div className="section-title">Required Documents</div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                {opp.required_documents.map((doc, i) => (
                  <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '0.625rem', padding: '0.5rem 0.75rem', background: 'rgba(255,255,255,0.03)', borderRadius: '0.5rem', fontSize: '0.83rem', color: 'var(--text-secondary)' }}>
                    <FileText size={13} color="#818cf8" style={{ flexShrink: 0 }} />
                    {doc}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Application Process */}
          {opp.application_process && (
            <div className="card">
              <div className="section-title">How to Apply</div>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.7 }}>{opp.application_process}</p>
              {opp.official_url && (
                <a href={opp.official_url} target="_blank" rel="noopener noreferrer" className="btn-secondary" style={{ marginTop: '1rem', display: 'inline-flex', fontSize: '0.8rem' }}>
                  Official Portal <ExternalLink size={12} />
                </a>
              )}
            </div>
          )}
        </div>

        {/* Right Panel */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          {/* Eligibility Criteria */}
          <div className="card">
            <div className="section-title">Eligibility Criteria</div>
            {[
              { label: 'Education Level', value: opp.education_level.join(', ') },
              opp.course && { label: 'Eligible Courses', value: opp.course.join(', ') },
              opp.minimum_cgpa && { label: 'Min. CGPA', value: `${opp.minimum_cgpa}/10` },
              opp.minimum_percentage && { label: 'Min. Percentage', value: `${opp.minimum_percentage}%` },
              opp.maximum_income && { label: 'Max. Family Income', value: `₹${opp.maximum_income.toLocaleString('en-IN')}` },
              opp.category && { label: 'Eligible Categories', value: opp.category.join(', ') },
              opp.gender && { label: 'Gender', value: opp.gender },
              opp.state && { label: 'Eligible States', value: opp.state.join(', ') },
              opp.institution_type && { label: 'Institution Type', value: opp.institution_type.join(', ') },
              opp.nationality_requirement && { label: 'Nationality', value: opp.nationality_requirement },
            ].filter(Boolean).map((item: any, i) => (
              <div key={i} style={{ display: 'flex', justifyContent: 'space-between', padding: '0.35rem 0', borderBottom: '1px solid rgba(255,255,255,0.04)', fontSize: '0.78rem' }}>
                <span style={{ color: 'var(--text-muted)' }}>{item.label}</span>
                <span style={{ color: 'var(--text-secondary)', fontWeight: 500, textAlign: 'right', maxWidth: '55%' }}>{item.value}</span>
              </div>
            ))}
          </div>

          {/* Source */}
          {opp.source_document && (
            <div className="card">
              <div className="section-title">Source</div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{opp.source_document}</div>
              {opp.academic_year && <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.3rem' }}>Academic Year: {opp.academic_year}</div>}
              {opp.last_verified_date && <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>Last verified: {new Date(opp.last_verified_date).toLocaleDateString('en-IN')}</div>}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
