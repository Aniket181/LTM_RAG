'use client';

import { useState } from 'react';
import {
  FileText, CheckCircle2, Clock, XCircle, BarChart2,
  ExternalLink, Database, Upload, Info, ChevronDown, ChevronUp,
} from 'lucide-react';
import { MOCK_SOURCES } from '@/lib/mock-data';
import type { SourceDocument } from '@/lib/types';

function statusMeta(status: SourceDocument['ingestion_status']) {
  const map = {
    Processed: { label: 'Ingested',  color: '#10b981', icon: <CheckCircle2 size={12} color="#10b981" /> },
    Pending:  { label: 'Pending',   color: '#f59e0b', icon: <Clock size={12} color="#f59e0b" /> },
    Failed:   { label: 'Failed',    color: '#ef4444', icon: <XCircle size={12} color="#ef4444" /> },
  };
  return map[status] || map.Pending;
}

function SourceCard({ doc }: { doc: SourceDocument }) {
  const [expanded, setExpanded] = useState(false);
  const meta = statusMeta(doc.ingestion_status);

  return (
    <div className="card glass-hover animate-fade-in-up">
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: '1rem' }}>
        {/* Icon */}
        <div style={{
          width: 42, height: 42, borderRadius: '0.625rem', flexShrink: 0,
          background: doc.ingestion_status === 'Processed' ? 'rgba(99,102,241,0.15)' : 'rgba(245,158,11,0.1)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          border: `1px solid ${doc.ingestion_status === 'Processed' ? 'rgba(99,102,241,0.25)' : 'rgba(245,158,11,0.2)'}`,
        }}>
          <FileText size={18} color={doc.ingestion_status === 'Processed' ? '#818cf8' : '#f59e0b'} />
        </div>

        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap', marginBottom: '0.3rem' }}>
            <span style={{ fontWeight: 600, fontSize: '0.9rem', color: 'var(--text-primary)' }}>
              {doc.title}
            </span>
            <span style={{
              padding: '0.15rem 0.55rem', borderRadius: 9999,
              fontSize: '0.68rem', fontWeight: 600,
              background: `${meta.color}18`, color: meta.color,
              border: `1px solid ${meta.color}30`,
              display: 'inline-flex', alignItems: 'center', gap: '0.3rem',
            }}>
              {meta.icon}{meta.label}
            </span>
          </div>

          <div style={{ display: 'flex', gap: '1.25rem', flexWrap: 'wrap', fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.625rem' }}>
            {doc.document_type && <span className="badge badge-info" style={{ fontSize: '0.68rem' }}>{doc.document_type}</span>}
            {doc.academic_year && <span>AY: {doc.academic_year}</span>}
            {doc.chunk_count !== undefined && doc.chunk_count > 0 && (
              <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                <BarChart2 size={11} /> {doc.chunk_count} chunks indexed
              </span>
            )}
            {doc.last_verified_date && <span>Verified: {new Date(doc.last_verified_date).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })}</span>}
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
            {doc.source_url && (
              <a
                href={doc.source_url}
                target="_blank"
                rel="noopener noreferrer"
                className="btn-ghost"
                style={{ fontSize: '0.75rem', padding: '0.3rem 0.625rem' }}
              >
                Official Source <ExternalLink size={11} />
              </a>
            )}
            <button
              className="btn-ghost"
              onClick={() => setExpanded(!expanded)}
              style={{ fontSize: '0.75rem', padding: '0.3rem 0.625rem' }}
            >
              {expanded ? <><ChevronUp size={11} /> Less</> : <><ChevronDown size={11} /> Details</>}
            </button>
          </div>

          {expanded && (
            <div style={{
              marginTop: '0.875rem', padding: '0.75rem', borderRadius: '0.625rem',
              background: 'rgba(255,255,255,0.03)', border: '1px solid var(--border-subtle)',
              fontSize: '0.78rem', color: 'var(--text-secondary)',
            }}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem' }}>
                {[
                  ['Document ID', doc.id],
                  ['Type', doc.document_type],
                  ['Academic Year', doc.academic_year ?? '—'],
                  ['Ingestion Status', meta.label],
                  ['Chunks Indexed', doc.chunk_count?.toString() ?? '0'],
                  ['Ingested At', new Date(doc.created_at).toLocaleDateString('en-IN')],
                ].map(([k, v]) => (
                  <div key={k}>
                    <div style={{ color: 'var(--text-muted)', fontSize: '0.7rem', marginBottom: '0.1rem' }}>{k}</div>
                    <div style={{ fontWeight: 500 }}>{v}</div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default function SourcesPage() {
  const ingested = MOCK_SOURCES.filter((d) => d.ingestion_status === 'Processed');
  const pending  = MOCK_SOURCES.filter((d) => d.ingestion_status === 'Pending');
  const failed   = MOCK_SOURCES.filter((d) => d.ingestion_status === 'Failed');
  const totalChunks = MOCK_SOURCES.reduce((sum, d) => sum + (d.chunk_count ?? 0), 0);

  return (
    <div className="animate-fade-in">
      <div className="page-header">
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <h1 className="page-title"><span className="gradient-text">Source Documents</span></h1>
            <p className="page-subtitle">Official documents ingested into the RAG knowledge base</p>
          </div>
          <button className="btn-secondary" disabled style={{ opacity: 0.5, cursor: 'not-allowed' }}>
            <Upload size={14} /> Ingest Document
            <span style={{ fontSize: '0.7rem', marginLeft: '0.25rem' }}>(Phase 4)</span>
          </button>
        </div>
      </div>

      {/* Stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem', marginBottom: '1.75rem' }}>
        {[
          { value: MOCK_SOURCES.length, label: 'Total Documents', color: '#6366f1', icon: <Database size={18} color="#6366f1" /> },
          { value: ingested.length,    label: 'Ingested',         color: '#10b981', icon: <CheckCircle2 size={18} color="#10b981" /> },
          { value: pending.length,     label: 'Pending',          color: '#f59e0b', icon: <Clock size={18} color="#f59e0b" /> },
          { value: totalChunks,        label: 'Chunks Indexed',   color: '#06b6d4', icon: <BarChart2 size={18} color="#06b6d4" /> },
        ].map(({ value, label, color, icon }) => (
          <div key={label} className="card animate-fade-in-up" style={{ textAlign: 'center', padding: '1.1rem' }}>
            <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '0.5rem' }}>{icon}</div>
            <div style={{ fontSize: '1.75rem', fontWeight: 800, color }}>{value}</div>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '0.2rem', textTransform: 'uppercase', letterSpacing: '0.04em' }}>{label}</div>
          </div>
        ))}
      </div>

      {/* Info banner */}
      <div style={{
        display: 'flex', alignItems: 'flex-start', gap: '0.75rem',
        padding: '0.875rem 1.1rem', marginBottom: '1.5rem',
        background: 'rgba(99,102,241,0.07)', border: '1px solid rgba(99,102,241,0.18)',
        borderRadius: '0.75rem', fontSize: '0.8rem', color: '#a5b4fc', lineHeight: 1.55,
      }}>
        <Info size={15} style={{ flexShrink: 0, marginTop: 1 }} />
        <span>
          All documents are sourced from official government and institutional portals.
          Each document is split into semantic chunks, embedded using <strong>BAAI/bge-small-en-v1.5</strong>,
          and stored in the vector database for hybrid retrieval. Document ingestion will be fully active in <strong>Phase 4</strong>.
        </span>
      </div>

      {/* Document list */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.875rem' }}>
        {MOCK_SOURCES.map((doc, i) => (
          <div key={doc.id} style={{ animationDelay: `${i * 0.07}s` }}>
            <SourceCard doc={doc} />
          </div>
        ))}
      </div>

      {/* Disclaimer */}
      <div style={{
        marginTop: '2rem', padding: '0.875rem 1.1rem',
        background: 'rgba(245,158,11,0.06)', border: '1px solid rgba(245,158,11,0.2)',
        borderRadius: '0.75rem', fontSize: '0.78rem', color: '#d97706',
        display: 'flex', alignItems: 'flex-start', gap: '0.75rem',
      }}>
        <Info size={14} style={{ flexShrink: 0, marginTop: 2 }} />
        Scholarship eligibility criteria, benefits, and deadlines change regularly. This system reflects information
        as of the last verified date shown for each document. Always refer to the official portal for current information.
      </div>
    </div>
  );
}
