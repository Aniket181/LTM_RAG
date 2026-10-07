'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import {
  Star, ArrowRight, CheckCircle2, XCircle, AlertCircle,
  HelpCircle, ChevronDown, ChevronUp, Trophy, TrendingUp,
  Info, Clock, RefreshCw, User,
} from 'lucide-react';
import { useStudent } from '@/lib/useStudent';
import { getRecommendations } from '@/lib/api';
import type { RankedOpportunity, RuleResult } from '@/lib/types';

function daysUntil(d: string) {
  return Math.ceil((new Date(d).getTime() - Date.now()) / 86400000);
}

function statusMeta(status: string) {
  const map: Record<string, { label: string; color: string; icon: React.ReactNode }> = {
    ELIGIBLE:               { label: 'Eligible',              color: '#10b981', icon: <CheckCircle2 size={13} color="#10b981" /> },
    NOT_ELIGIBLE:           { label: 'Not Eligible',          color: '#ef4444', icon: <XCircle size={13} color="#ef4444" /> },
    POTENTIALLY_ELIGIBLE:   { label: 'Potentially Eligible',  color: '#f59e0b', icon: <AlertCircle size={13} color="#f59e0b" /> },
    INSUFFICIENT_INFORMATION:{ label: 'Insufficient Info',    color: '#6b7280', icon: <HelpCircle size={13} color="#6b7280" /> },
  };
  return map[status] ?? map.INSUFFICIENT_INFORMATION;
}

function ScoreBar({ value, color }: { value: number; color: string }) {
  const pct = Math.min(1, Math.max(0, value));
  return (
    <div style={{ flex: 1, height: 4, background: 'rgba(255,255,255,0.06)', borderRadius: 9999, overflow: 'hidden' }}>
      <div style={{ height: '100%', width: `${pct * 100}%`, background: color, borderRadius: 9999, transition: 'width 0.8s ease' }} />
    </div>
  );
}

function RuleChip({ rule }: { rule: RuleResult }) {
  const colorMap = { PASS: '#10b981', FAIL: '#ef4444', WARN: '#f59e0b', UNKNOWN: '#6b7280' };
  const color = colorMap[rule.result];
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', padding: '0.35rem 0.625rem', borderRadius: 9999, background: `${color}12`, border: `1px solid ${color}28`, fontSize: '0.72rem' }}>
      {rule.result === 'PASS' && <CheckCircle2 size={10} color={color} />}
      {rule.result === 'FAIL' && <XCircle size={10} color={color} />}
      {rule.result === 'WARN' && <AlertCircle size={10} color={color} />}
      {rule.result === 'UNKNOWN' && <HelpCircle size={10} color={color} />}
      <span style={{ color: 'var(--text-secondary)' }}>{rule.rule_name.replace('Rule', '')}</span>
    </div>
  );
}

function RecommendationCard({ rec }: { rec: RankedOpportunity }) {
  const [expanded, setExpanded] = useState(false);
  const meta = statusMeta(rec.eligibility.overall_status);
  const days = rec.opportunity.closing_date ? daysUntil(rec.opportunity.closing_date) : null;
  // Use total_score out of 100 if match_score is not present
  const totalScore = rec.score?.total_score ?? 0;
  const maxScore = 100;
  const scorePercent = Math.min(100, Math.round((totalScore / maxScore) * 100));

  // Normalize score breakdown for display bars (0–1)
  const breakdown = {
    deadline:    (rec.score?.deadline_score ?? 0) / 30,
    financial:   (rec.score?.financial_need_score ?? 0) / 30,
    academic:    (rec.score?.academic_merit_score ?? 0) / 20,
    demographic: (rec.score?.demographic_match_score ?? 0) / 20,
  };

  return (
    <div className="card animate-fade-in-up" style={{ marginBottom: '1rem' }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: '1.25rem' }}>
        {/* Rank */}
        <div style={{ flexShrink: 0, textAlign: 'center' }}>
          <div style={{
            width: 44, height: 44, borderRadius: '0.75rem',
            background: rec.rank <= 2 ? 'var(--grad-primary)' : 'rgba(99,102,241,0.15)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: '0.85rem', fontWeight: 800,
            color: rec.rank <= 2 ? 'white' : '#818cf8',
            border: rec.rank > 2 ? '1px solid rgba(99,102,241,0.25)' : 'none',
          }}>
            {rec.rank === 1 ? <Trophy size={20} color="white" /> : `#${rec.rank}`}
          </div>
        </div>

        {/* Main content */}
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '0.75rem', flexWrap: 'wrap' }}>
            <div>
              <div style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap', marginBottom: '0.35rem' }}>
                <span className="badge badge-info">{rec.opportunity.opportunity_type}</span>
                <span style={{ padding: '0.2rem 0.6rem', borderRadius: 9999, fontSize: '0.7rem', fontWeight: 600, background: `${meta.color}18`, color: meta.color, border: `1px solid ${meta.color}33`, display: 'inline-flex', alignItems: 'center', gap: '0.3rem' }}>
                  {meta.icon}{meta.label}
                </span>
              </div>
              <Link href={`/opportunities/${rec.opportunity.id}`} style={{ textDecoration: 'none' }}>
                <h3 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-primary)', lineHeight: 1.3, marginBottom: '0.25rem', cursor: 'pointer' }}
                  className="glass-hover">
                  {rec.opportunity.name}
                </h3>
              </Link>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>{rec.opportunity.provider}</div>
            </div>

            {/* Score */}
            <div style={{ textAlign: 'center', flexShrink: 0 }}>
              <div style={{ fontSize: '1.5rem', fontWeight: 900, lineHeight: 1 }} className="gradient-text">
                {scorePercent}%
              </div>
              <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', marginTop: '0.15rem' }}>match</div>
            </div>
          </div>

          {/* Score bars */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '0.4rem', margin: '0.875rem 0', alignItems: 'center' }}>
            {[
              { label: 'Deadline', value: breakdown.deadline, color: '#f59e0b' },
              { label: 'Financial', value: breakdown.financial, color: '#10b981' },
              { label: 'Academic', value: breakdown.academic, color: '#8b5cf6' },
              { label: 'Demographic', value: breakdown.demographic, color: '#06b6d4' },
            ].map(({ label, value, color }) => (
              <div key={label} style={{ textAlign: 'center' }}>
                <ScoreBar value={value} color={color} />
                <div style={{ fontSize: '0.62rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>{label}</div>
              </div>
            ))}
          </div>

          {/* Reasons */}
          {rec.score?.reasons && rec.score.reasons.length > 0 && (
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem', marginBottom: '0.5rem' }}>
              {rec.score.reasons.slice(0, 3).map((r, i) => (
                <span key={i} style={{ fontSize: '0.68rem', color: 'var(--text-muted)', background: 'rgba(255,255,255,0.04)', padding: '0.2rem 0.5rem', borderRadius: 9999, border: '1px solid var(--border-subtle)' }}>
                  {r}
                </span>
              ))}
            </div>
          )}

          {/* Rule chips row */}
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem', marginBottom: '0.75rem' }}>
            {rec.eligibility.rule_results.map((r, i) => <RuleChip key={i} rule={r} />)}
          </div>

          {/* Footer row */}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.5rem' }}>
            <div style={{ display: 'flex', gap: '1rem', fontSize: '0.75rem', alignItems: 'center' }}>
              {rec.opportunity.amount && (
                <span style={{ color: '#10b981', fontWeight: 700 }}>
                  ₹{rec.opportunity.amount.toLocaleString('en-IN')}/yr
                </span>
              )}
              {rec.opportunity.benefit_description && !rec.opportunity.amount && (
                <span style={{ color: '#10b981', fontWeight: 600, fontSize: '0.72rem' }}>
                  {rec.opportunity.benefit_description}
                </span>
              )}
              {days !== null && days > 0 && (
                <span style={{ color: days <= 30 ? '#f59e0b' : 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: 4 }}>
                  <Clock size={11} /> {days} days left
                </span>
              )}
              {days !== null && days <= 0 && <span style={{ color: '#ef4444', fontSize: '0.72rem' }}>Deadline passed</span>}
            </div>
            <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
              <button
                className="btn-ghost"
                onClick={() => setExpanded(!expanded)}
                style={{ fontSize: '0.75rem', padding: '0.3rem 0.625rem' }}
              >
                {expanded ? <><ChevronUp size={12} /> Hide Details</> : <><ChevronDown size={12} /> Full Analysis</>}
              </button>
              <Link href={`/opportunities/${rec.opportunity.id}`} className="btn-primary" style={{ fontSize: '0.78rem', padding: '0.35rem 0.875rem' }}>
                View <ArrowRight size={12} />
              </Link>
            </div>
          </div>

          {/* Expanded: full rule details */}
          {expanded && (
            <div style={{ marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid var(--border-subtle)' }}>
              <div style={{ fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.625rem' }}>
                Detailed Eligibility Breakdown — <span style={{ color: 'var(--text-muted)', fontWeight: 400 }}>{rec.eligibility.summary}</span>
              </div>
              {rec.eligibility.rule_results.map((rule, i) => {
                const colorMap = { PASS: '#10b981', FAIL: '#ef4444', WARN: '#f59e0b', UNKNOWN: '#6b7280' };
                const clsMap = { PASS: 'rule-pass', FAIL: 'rule-fail', WARN: 'rule-warn', UNKNOWN: 'rule-unknown' };
                const color = colorMap[rule.result];
                return (
                  <div key={i} className={`rule-row ${clsMap[rule.result]}`}>
                    <div style={{ flex: 1 }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.2rem' }}>
                        <span style={{ fontWeight: 600, color: 'var(--text-primary)', fontSize: '0.8rem' }}>{rule.rule_name.replace('Rule', ' Check')}</span>
                        <span style={{ fontSize: '0.7rem', color, fontWeight: 700 }}>{rule.result}</span>
                      </div>
                      <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                        Required: <span style={{ color: 'var(--text-secondary)' }}>{rule.required_value}</span>
                        {rule.student_value !== null && <> · Yours: <span style={{ color: 'var(--text-secondary)' }}>{rule.student_value}</span></>}
                      </div>
                      <div style={{ fontSize: '0.72rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>{rule.detail}</div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default function RecommendationsPage() {
  const { student, studentId, loading: studentLoading } = useStudent();
  const [recommendations, setRecommendations] = useState<RankedOpportunity[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!studentId) return;
    setLoading(true);
    setError(null);
    getRecommendations(studentId)
      .then(setRecommendations)
      .catch((err) => setError(err instanceof Error ? err.message : 'Failed to load recommendations.'))
      .finally(() => setLoading(false));
  }, [studentId]);

  const eligible   = recommendations.filter((r) => r.eligibility.overall_status === 'ELIGIBLE');
  const potential  = recommendations.filter((r) => r.eligibility.overall_status === 'POTENTIALLY_ELIGIBLE');
  const ineligible = recommendations.filter((r) => r.eligibility.overall_status === 'NOT_ELIGIBLE');

  if (studentLoading) {
    return (
      <div className="animate-fade-in">
        <div className="page-header">
          <h1 className="page-title"><span className="gradient-text">Recommendations</span></h1>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {[1, 2, 3].map(i => <div key={i} className="skeleton" style={{ height: 140 }} />)}
        </div>
      </div>
    );
  }

  if (!studentId) {
    return (
      <div className="animate-fade-in">
        <div className="page-header">
          <h1 className="page-title"><span className="gradient-text">Recommendations</span></h1>
        </div>
        <div className="card" style={{ textAlign: 'center', padding: '3rem 2rem' }}>
          <User size={40} color="#818cf8" style={{ margin: '0 auto 1rem' }} />
          <div style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '0.5rem' }}>Profile Required</div>
          <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>
            Create your student profile to get personalized scholarship recommendations.
          </div>
          <Link href="/profile" className="btn-primary">Set Up My Profile</Link>
        </div>
      </div>
    );
  }

  return (
    <div className="animate-fade-in">
      <div className="page-header">
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <h1 className="page-title">
              <span className="gradient-text">Recommendations</span>
            </h1>
            <p className="page-subtitle">
              {student?.name ? `Personalized for ${student.name}` : 'Personalized'} · ranked by eligibility + score + deadline
            </p>
          </div>
          {!loading && (
            <button className="btn-ghost" onClick={() => {
              setLoading(true);
              getRecommendations(studentId!)
                .then(setRecommendations)
                .catch((e) => setError(e.message))
                .finally(() => setLoading(false));
            }}>
              <RefreshCw size={13} /> Refresh
            </button>
          )}
        </div>
      </div>

      {/* Summary stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem', marginBottom: '1.75rem' }}>
        {[
          { value: recommendations.length, label: 'Total Found',  color: '#6366f1' },
          { value: eligible.length,        label: 'Eligible',     color: '#10b981' },
          { value: potential.length,       label: 'Potentially',  color: '#f59e0b' },
          { value: ineligible.length,      label: 'Not Eligible', color: '#ef4444' },
        ].map(({ value, label, color }) => (
          <div key={label} className="card animate-fade-in-up" style={{ textAlign: 'center', padding: '1.1rem' }}>
            {loading ? <div className="skeleton" style={{ height: 32, marginBottom: 8 }} /> : (
              <div style={{ fontSize: '1.75rem', fontWeight: 800, color }}>{value}</div>
            )}
            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '0.2rem', textTransform: 'uppercase', letterSpacing: '0.04em' }}>{label}</div>
          </div>
        ))}
      </div>

      {/* Info Banner */}
      <div style={{
        display: 'flex', alignItems: 'center', gap: '0.75rem',
        padding: '0.75rem 1rem', marginBottom: '1.5rem',
        background: 'rgba(99,102,241,0.07)', border: '1px solid rgba(99,102,241,0.18)',
        borderRadius: '0.75rem', fontSize: '0.78rem', color: '#a5b4fc',
      }}>
        <TrendingUp size={14} style={{ flexShrink: 0 }} />
        Eligibility is determined by a <strong style={{ marginLeft: 4 }}>deterministic rule engine</strong>, not by AI.
        Scores include deadline proximity, financial need, academic merit, and demographic match.
      </div>

      {/* Error */}
      {error && (
        <div style={{ padding: '0.875rem', marginBottom: '1rem', background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.25)', borderRadius: '0.75rem', fontSize: '0.8rem', color: '#f87171', display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          <AlertCircle size={14} /> {error}
        </div>
      )}

      {/* Loading skeletons */}
      {loading && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {[1, 2, 3].map(i => <div key={i} className="skeleton" style={{ height: 160 }} />)}
        </div>
      )}

      {/* Empty state */}
      {!loading && !error && recommendations.length === 0 && (
        <div className="card" style={{ textAlign: 'center', padding: '3rem 2rem' }}>
          <Star size={40} color="#818cf8" style={{ margin: '0 auto 1rem' }} />
          <div style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '0.5rem' }}>No Recommendations Yet</div>
          <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
            This may mean no active opportunities were found, or your profile needs more information.
          </div>
        </div>
      )}

      {/* Recommendations */}
      {!loading && recommendations.map((rec) => (
        <RecommendationCard key={rec.opportunity.id} rec={rec} />
      ))}

      {/* Disclaimer */}
      {!loading && recommendations.length > 0 && (
        <div style={{
          marginTop: '1.5rem', padding: '0.875rem 1.1rem',
          background: 'rgba(245,158,11,0.06)', border: '1px solid rgba(245,158,11,0.2)',
          borderRadius: '0.75rem', fontSize: '0.78rem', color: '#d97706',
          display: 'flex', alignItems: 'flex-start', gap: '0.75rem',
        }}>
          <Info size={14} style={{ flexShrink: 0, marginTop: 2 }} />
          Always verify eligibility and deadlines from the official portal before applying.
          This system provides decision support — not official determination.
        </div>
      )}
    </div>
  );
}
