'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import {
  GraduationCap, TrendingUp, Clock, CheckCircle2,
  XCircle, AlertCircle, ArrowRight, Search,
  BookOpen, Zap, Shield, Database, ExternalLink, User,
  RefreshCw, HelpCircle,
} from 'lucide-react';
import { getHealth, getRecommendations } from '@/lib/api';
import { useStudent } from '@/lib/useStudent';
import type { HealthStatus, RankedOpportunity } from '@/lib/types';

function daysUntil(dateStr: string): number {
  const d = new Date(dateStr);
  const now = new Date();
  return Math.ceil((d.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
}

function statusColor(status: string) {
  if (status === 'ELIGIBLE') return '#10b981';
  if (status === 'POTENTIALLY_ELIGIBLE') return '#f59e0b';
  if (status === 'NOT_ELIGIBLE') return '#ef4444';
  return '#6b7280';
}

function statusLabel(status: string) {
  if (status === 'ELIGIBLE') return 'Eligible';
  if (status === 'POTENTIALLY_ELIGIBLE') return 'Potentially';
  if (status === 'NOT_ELIGIBLE') return 'Not Eligible';
  if (status === 'INSUFFICIENT_INFORMATION') return 'More Info Needed';
  return 'Unknown';
}

function statusIcon(status: string) {
  if (status === 'ELIGIBLE') return <CheckCircle2 size={13} color="#10b981" />;
  if (status === 'NOT_ELIGIBLE') return <XCircle size={13} color="#ef4444" />;
  if (status === 'POTENTIALLY_ELIGIBLE') return <AlertCircle size={13} color="#f59e0b" />;
  return <HelpCircle size={13} color="#6b7280" />;
}

function StatCard({ value, label, color, icon: Icon, loading }: {
  value: string; label: string; color: string; icon: React.ElementType; loading?: boolean;
}) {
  return (
    <div className="card animate-fade-in-up" style={{ textAlign: 'center', padding: '1.25rem' }}>
      <div style={{
        width: 44, height: 44, borderRadius: '0.75rem',
        background: `${color}22`,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        margin: '0 auto 0.75rem',
        border: `1px solid ${color}33`,
      }}>
        <Icon size={20} color={color} />
      </div>
      {loading ? (
        <div className="skeleton" style={{ height: 28, marginBottom: 8 }} />
      ) : (
        <div className="stat-value gradient-text">{value}</div>
      )}
      <div className="stat-label">{label}</div>
    </div>
  );
}

function StatusChip({ status }: { status: string }) {
  const ok = status === 'ok';
  const notCfg = status === 'not_configured';
  const color = ok ? '#10b981' : notCfg ? '#f59e0b' : '#ef4444';
  const label = ok ? 'Online' : notCfg ? 'Not Configured' : 'Error';
  return (
    <span style={{
      padding: '0.2rem 0.6rem', borderRadius: 9999,
      fontSize: '0.7rem', fontWeight: 600,
      background: `${color}18`, color, border: `1px solid ${color}33`,
    }}>
      {label}
    </span>
  );
}

export default function DashboardPage() {
  const { student, studentId, loading: studentLoading } = useStudent();
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [healthLoading, setHealthLoading] = useState(true);
  const [recommendations, setRecommendations] = useState<RankedOpportunity[]>([]);
  const [recsLoading, setRecsLoading] = useState(false);
  const [recsError, setRecsError] = useState<string | null>(null);

  useEffect(() => {
    getHealth()
      .then(setHealth)
      .catch(() => setHealth(null))
      .finally(() => setHealthLoading(false));
  }, []);

  useEffect(() => {
    if (!studentId) return;
    setRecsLoading(true);
    setRecsError(null);
    getRecommendations(studentId, 5)
      .then(setRecommendations)
      .catch((err) => setRecsError(err instanceof Error ? err.message : 'Failed to load recommendations.'))
      .finally(() => setRecsLoading(false));
  }, [studentId]);

  const eligibleCount  = recommendations.filter((r) => r.eligibility.overall_status === 'ELIGIBLE').length;
  const potentialCount = recommendations.filter((r) => r.eligibility.overall_status === 'POTENTIALLY_ELIGIBLE').length;
  const closingCount   = recommendations.filter((r) =>
    r.opportunity.closing_date && daysUntil(r.opportunity.closing_date) <= 60 && daysUntil(r.opportunity.closing_date) > 0
  ).length;

  const isLoading = studentLoading || recsLoading;

  return (
    <div className="animate-fade-in">
      {/* ---- Page Header ---- */}
      <div className="page-header">
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            {studentLoading ? (
              <div className="skeleton" style={{ height: 32, width: 260, marginBottom: 8 }} />
            ) : student ? (
              <h1 className="page-title">
                Welcome back, <span className="gradient-text">{student.name ?? 'Student'}</span> 👋
              </h1>
            ) : (
              <h1 className="page-title">Welcome to <span className="gradient-text">ScholarAI</span> 👋</h1>
            )}
            {student ? (
              <p className="page-subtitle">
                {student.course} · {student.branch} · Year {student.year_of_study} · CGPA {student.cgpa ?? '—'}
              </p>
            ) : (
              <p className="page-subtitle">Set up your profile to get personalized scholarship recommendations.</p>
            )}
          </div>
          <div style={{ display: 'flex', gap: '0.75rem' }}>
            <Link href="/opportunities" className="btn-secondary">
              <Search size={14} /> Browse All
            </Link>
            {studentId ? (
              <Link href="/recommendations" className="btn-primary">
                <Zap size={14} /> My Matches
              </Link>
            ) : (
              <Link href="/profile" className="btn-primary">
                <User size={14} /> Create Profile
              </Link>
            )}
          </div>
        </div>
      </div>

      {/* ---- No profile state ---- */}
      {!studentLoading && !studentId && (
        <div className="card animate-fade-in-up" style={{
          marginBottom: '1.75rem', padding: '1.5rem',
          background: 'rgba(99,102,241,0.07)', border: '1px solid rgba(99,102,241,0.2)',
          textAlign: 'center',
        }}>
          <User size={36} color="#818cf8" style={{ margin: '0 auto 0.75rem' }} />
          <div style={{ fontWeight: 600, color: 'var(--text-primary)', marginBottom: '0.4rem' }}>
            No profile yet
          </div>
          <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '1.25rem' }}>
            Create your student profile to see personalized eligibility results and recommendations.
          </div>
          <Link href="/profile" className="btn-primary">Set Up My Profile</Link>
        </div>
      )}

      {/* ---- Stats Row ---- */}
      <div className="grid-4" style={{ marginBottom: '1.75rem' }}>
        <StatCard
          value={isLoading ? '…' : `${recommendations.length}`}
          label="Opportunities Found"
          color="#6366f1" icon={GraduationCap} loading={isLoading}
        />
        <StatCard
          value={isLoading ? '…' : `${eligibleCount}`}
          label="You're Eligible"
          color="#10b981" icon={CheckCircle2} loading={isLoading}
        />
        <StatCard
          value={isLoading ? '…' : `${potentialCount}`}
          label="Potentially Eligible"
          color="#f59e0b" icon={AlertCircle} loading={isLoading}
        />
        <StatCard
          value={student ? `${student.cgpa ?? '—'}` : '—'}
          label="Your CGPA"
          color="#06b6d4" icon={TrendingUp} loading={studentLoading}
        />
      </div>

      {/* ---- Main Grid ---- */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: '1.5rem', alignItems: 'start' }}>

        {/* Left: Top Recommendations */}
        <div>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
            <h2 className="section-title" style={{ marginBottom: 0 }}>Top Recommendations</h2>
            <Link href="/recommendations" className="btn-ghost">
              View all <ArrowRight size={13} />
            </Link>
          </div>

          {recsError && (
            <div style={{ padding: '0.875rem', marginBottom: '1rem', background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.25)', borderRadius: '0.75rem', fontSize: '0.8rem', color: '#f87171', display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
              <AlertCircle size={14} /> {recsError}
            </div>
          )}

          {recsLoading && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.875rem' }}>
              {[1, 2, 3].map(i => <div key={i} className="skeleton" style={{ height: 90 }} />)}
            </div>
          )}

          {!recsLoading && !studentId && (
            <div className="card" style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
              Create your profile to see recommendations here.
            </div>
          )}

          {!recsLoading && studentId && recommendations.length === 0 && !recsError && (
            <div className="card" style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
              No recommendations found. Ensure there are active opportunities in the database.
            </div>
          )}

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.875rem' }}>
            {!recsLoading && recommendations.map((rec, i) => {
              const days = rec.opportunity.closing_date ? daysUntil(rec.opportunity.closing_date) : null;
              const color = statusColor(rec.eligibility.overall_status);
              const totalScore = rec.score?.total_score ?? 0;
              return (
                <Link
                  key={rec.opportunity.id}
                  href={`/opportunities/${rec.opportunity.id}`}
                  style={{ textDecoration: 'none' }}
                >
                  <div className="card glass-hover animate-fade-in-up" style={{ animationDelay: `${i * 0.08}s` }}>
                    <div style={{ display: 'flex', alignItems: 'flex-start', gap: '1rem' }}>
                      {/* Rank badge */}
                      <div style={{
                        width: 36, height: 36, borderRadius: '0.5rem', flexShrink: 0,
                        background: 'var(--grad-primary)', display: 'flex',
                        alignItems: 'center', justifyContent: 'center',
                        fontSize: '0.8rem', fontWeight: 800, color: 'white',
                      }}>
                        #{rec.rank}
                      </div>

                      <div style={{ flex: 1, minWidth: 0 }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap', marginBottom: '0.25rem' }}>
                          <span style={{ fontWeight: 600, fontSize: '0.9rem', color: 'var(--text-primary)' }}>
                            {rec.opportunity.name}
                          </span>
                          <span className={`badge badge-${rec.opportunity.opportunity_type === 'Fellowship' ? 'cyan' : 'info'}`}>
                            {rec.opportunity.opportunity_type}
                          </span>
                        </div>
                        <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginBottom: '0.625rem' }}>
                          {rec.opportunity.provider}
                        </div>

                        <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem', flexWrap: 'wrap' }}>
                          {/* Eligibility */}
                          <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                            {statusIcon(rec.eligibility.overall_status)}
                            <span style={{ fontSize: '0.78rem', color, fontWeight: 600 }}>
                              {statusLabel(rec.eligibility.overall_status)}
                            </span>
                          </div>
                          {/* Match Score */}
                          <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
                            Score: <strong style={{ color: '#818cf8' }}>{totalScore}</strong>
                          </div>
                          {/* Deadline */}
                          {days !== null && (
                            <div style={{ fontSize: '0.78rem', color: days <= 30 ? '#f59e0b' : 'var(--text-secondary)' }}>
                              {days > 0 ? `${days} days left` : 'Closed'}
                            </div>
                          )}
                          {/* Amount */}
                          {rec.opportunity.amount && (
                            <div style={{ fontSize: '0.78rem', color: '#10b981', fontWeight: 600 }}>
                              ₹{rec.opportunity.amount.toLocaleString('en-IN')}
                            </div>
                          )}
                        </div>
                      </div>

                      <ArrowRight size={16} color="var(--text-muted)" style={{ flexShrink: 0, marginTop: 4 }} />
                    </div>
                  </div>
                </Link>
              );
            })}
          </div>
        </div>

        {/* Right Column */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>

          {/* Profile Summary */}
          <div className="card animate-fade-in-up delay-100">
            <div className="card-header">
              <span className="section-title" style={{ marginBottom: 0 }}>Student Profile</span>
              <Link href="/profile" className="btn-ghost" style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem' }}>
                {student ? 'Edit' : 'Create'}
              </Link>
            </div>
            {studentLoading ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {[1,2,3,4].map(i => <div key={i} className="skeleton" style={{ height: 24 }} />)}
              </div>
            ) : student ? (
              [
                ['Education', `${student.education_level} — ${student.course}`],
                ['Branch', student.branch ?? '—'],
                ['CGPA', student.cgpa?.toString() ?? '—'],
                ['Income', student.annual_family_income ? `₹${student.annual_family_income.toLocaleString('en-IN')}/year` : '—'],
                ['Category', student.category],
                ['State', student.state ?? '—'],
                ['Institution', student.institution_type ?? '—'],
              ].map(([k, v]) => (
                <div key={k} style={{ display: 'flex', justifyContent: 'space-between', padding: '0.35rem 0', borderBottom: '1px solid rgba(255,255,255,0.04)', fontSize: '0.8rem' }}>
                  <span style={{ color: 'var(--text-muted)' }}>{k}</span>
                  <span style={{ color: 'var(--text-primary)', fontWeight: 500, textAlign: 'right', maxWidth: '55%' }}>{v}</span>
                </div>
              ))
            ) : (
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', padding: '0.5rem 0' }}>
                No profile yet. <Link href="/profile" style={{ color: '#818cf8' }}>Create one →</Link>
              </div>
            )}
          </div>

          {/* System Status */}
          <div className="card animate-fade-in-up delay-200">
            <div className="section-title">System Status</div>
            {healthLoading ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {[1,2,3].map(i => <div key={i} className="skeleton" style={{ height: 28 }} />)}
              </div>
            ) : health ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {Object.entries(health.components).map(([key, val]: [string, any]) => (
                  <div key={key} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.8rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-secondary)', textTransform: 'capitalize' }}>
                      {key === 'api' && <Zap size={12} />}
                      {key === 'database' && <Database size={12} />}
                      {key === 'vector_store' && <BookOpen size={12} />}
                      {key}
                    </div>
                    <StatusChip status={val.status} />
                  </div>
                ))}
                <div className="divider" style={{ margin: '0.5rem 0' }} />
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  LLM: {health.llm_provider} · {health.embedding_model}
                </div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  Uptime: {Math.round(health.uptime_seconds)}s · v{health.version}
                </div>
              </div>
            ) : (
              <div style={{ fontSize: '0.8rem', color: '#ef4444' }}>Backend not reachable</div>
            )}
          </div>

          {/* Quick Access */}
          <div className="card animate-fade-in-up delay-300">
            <div className="section-title">Quick Access</div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              {[
                { href: '/chat',           icon: Shield,   label: 'Ask AI about scholarships', color: '#6366f1' },
                { href: '/opportunities',  icon: Search,   label: 'Search opportunities',       color: '#06b6d4' },
                { href: '/sources',        icon: Database, label: 'View source documents',      color: '#8b5cf6' },
              ].map(({ href, icon: Icon, label, color }) => (
                <Link key={href} href={href} style={{ textDecoration: 'none' }}>
                  <div className="glass-hover" style={{
                    display: 'flex', alignItems: 'center', gap: '0.75rem',
                    padding: '0.625rem 0.75rem', borderRadius: '0.625rem',
                    border: '1px solid var(--border-subtle)', cursor: 'pointer',
                  }}>
                    <Icon size={14} color={color} />
                    <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{label}</span>
                    <ArrowRight size={12} color="var(--text-muted)" style={{ marginLeft: 'auto' }} />
                  </div>
                </Link>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* ---- Disclaimer ---- */}
      <div style={{
        marginTop: '2rem', padding: '1rem 1.25rem',
        background: 'rgba(245,158,11,0.06)', border: '1px solid rgba(245,158,11,0.2)',
        borderRadius: '0.75rem', fontSize: '0.78rem', color: '#d97706', lineHeight: 1.6,
        display: 'flex', alignItems: 'flex-start', gap: '0.75rem',
      }}>
        <ExternalLink size={14} style={{ flexShrink: 0, marginTop: 2 }} />
        <span>
          <strong>Important:</strong> All scholarship information is sourced from official portals (NSP, UGC, AICTE, Ministry of Education).
          Eligibility criteria and deadlines change regularly.{' '}
          <strong>Always verify from the official source before applying.</strong>{' '}
          This system provides decision support, not official eligibility determination.
        </span>
      </div>
    </div>
  );
}
