'use client';

import { useState, useRef, useEffect } from 'react';
import {
  Send, Bot, User, Sparkles, BookOpen, ExternalLink,
  AlertCircle, RefreshCw, CheckCircle2, XCircle, HelpCircle,
} from 'lucide-react';
import type { ChatMessage, SourceAttribution, EligibilityResult } from '@/lib/types';
import { useStudent } from '@/lib/useStudent';
import { askQuestion, evaluateEligibility } from '@/lib/api';

// ── Eligibility Intent Detection ──────────────────────────────────────────
const ELIGIBILITY_PATTERNS = [
  /which scholarships? (am i|i am|can i|do i) (eligible|qualify|get)/i,
  /am i eligible/i,
  /do i qualify/i,
  /scholarships? for me/i,
  /what (can|scholarships?) (i|am i) (apply|eligible)/i,
  /my eligible/i,
  /scholarships? i (can|could) get/i,
  /eligible.*scholarship/i,
  /scholarship.*eligible/i,
  /why am i eligible/i,
  /qualify for/i,
];

function isEligibilityQuestion(query: string): boolean {
  return ELIGIBILITY_PATTERNS.some((p) => p.test(query));
}

// ── Source Card ───────────────────────────────────────────────────────────
function SourceCard({ source }: { source: SourceAttribution }) {
  return (
    <div style={{
      display: 'flex', alignItems: 'flex-start', gap: '0.5rem',
      padding: '0.5rem 0.625rem', borderRadius: '0.5rem',
      background: 'rgba(99,102,241,0.07)', border: '1px solid rgba(99,102,241,0.15)',
      fontSize: '0.72rem',
    }}>
      <BookOpen size={11} color="#818cf8" style={{ flexShrink: 0, marginTop: 2 }} />
      <div>
        <div style={{ color: '#a5b4fc', fontWeight: 600 }}>
          {source.source_title ?? source.opportunity_name ?? 'Official Document'}
        </div>
        {source.page_number && (
          <div style={{ color: 'var(--text-muted)' }}>Page {source.page_number}</div>
        )}
        {source.source_url && (
          <a href={source.source_url} target="_blank" rel="noopener noreferrer"
            style={{ color: '#6366f1', display: 'inline-flex', alignItems: 'center', gap: 3, marginTop: 2 }}>
            Official source <ExternalLink size={9} />
          </a>
        )}
      </div>
    </div>
  );
}

// ── Eligibility Summary Card ──────────────────────────────────────────────
function EligibilityCard({ result }: { result: EligibilityResult }) {
  const statusMeta: Record<string, { icon: React.ReactNode; color: string; label: string }> = {
    ELIGIBLE: { icon: <CheckCircle2 size={12} color="#10b981" />, color: '#10b981', label: 'Eligible' },
    NOT_ELIGIBLE: { icon: <XCircle size={12} color="#ef4444" />, color: '#ef4444', label: 'Not Eligible' },
    POTENTIALLY_ELIGIBLE: { icon: <AlertCircle size={12} color="#f59e0b" />, color: '#f59e0b', label: 'Potentially Eligible' },
    INSUFFICIENT_INFORMATION: { icon: <HelpCircle size={12} color="#6b7280" />, color: '#6b7280', label: 'More Info Needed' },
  };
  const meta = statusMeta[result.overall_status] ?? statusMeta.INSUFFICIENT_INFORMATION;

  return (
    <div style={{
      padding: '0.5rem 0.75rem', borderRadius: '0.5rem',
      background: `${meta.color}0f`, border: `1px solid ${meta.color}28`,
      fontSize: '0.72rem', display: 'flex', alignItems: 'center', gap: '0.4rem',
    }}>
      {meta.icon}
      <span style={{ color: meta.color, fontWeight: 600 }}>{meta.label}</span>
      {result.summary && (
        <span style={{ color: 'var(--text-muted)', marginLeft: '0.25rem' }}>· {result.summary}</span>
      )}
    </div>
  );
}

// ── Chat Bubble ───────────────────────────────────────────────────────────
function ChatBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === 'user';

  const renderText = (text: string) =>
    text.split('\n').map((line, i) => {
      if (line.startsWith('**') && line.endsWith('**'))
        return <p key={i} style={{ fontWeight: 700, color: 'var(--text-primary)', marginBottom: '0.25rem' }}>{line.replace(/\*\*/g, '')}</p>;
      if (line.startsWith('- ') || line.startsWith('* '))
        return <li key={i} style={{ marginLeft: '1rem', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>{line.slice(2).replace(/\*\*(.*?)\*\*/g, '$1')}</li>;
      if (line.startsWith('⚠️'))
        return <p key={i} style={{ color: '#f59e0b', fontSize: '0.78rem', marginTop: '0.5rem', fontStyle: 'italic' }}>{line}</p>;
      if (line.match(/^\d+\./))
        return <li key={i} style={{ marginLeft: '1rem', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>{line.replace(/^\d+\.\s/, '').replace(/\*\*(.*?)\*\*/g, '$1')}</li>;
      if (line === '') return <br key={i} />;
      return <p key={i} style={{ color: 'var(--text-secondary)', marginBottom: '0.2rem', fontSize: '0.85rem' }}>{line.replace(/\*\*(.*?)\*\*/g, '$1').replace(/\*(.*?)\*/g, '$1')}</p>;
    });

  if (isUser) {
    return (
      <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '1rem' }}>
        <div className="chat-bubble-user">{message.content}</div>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '1.25rem', alignItems: 'flex-start' }}>
      <div style={{
        width: 32, height: 32, borderRadius: '50%', flexShrink: 0,
        background: 'var(--grad-primary)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        boxShadow: '0 0 15px rgba(99,102,241,0.3)',
      }}>
        <Bot size={16} color="white" />
      </div>
      <div style={{ flex: 1, maxWidth: '85%' }}>
        <div className="chat-bubble-ai">
          <div>{renderText(message.content)}</div>
        </div>
        {/* Eligibility results */}
        {message.eligibilityContext && message.eligibilityContext.length > 0 && (
          <div style={{ marginTop: '0.5rem', display: 'flex', flexDirection: 'column', gap: '0.3rem' }}>
            {message.eligibilityContext.slice(0, 5).map((r, i) => (
              <EligibilityCard key={i} result={r} />
            ))}
            {message.eligibilityContext.length > 5 && (
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                + {message.eligibilityContext.length - 5} more results
              </div>
            )}
          </div>
        )}
        {/* Source attribution */}
        {message.sources && message.sources.length > 0 && (
          <div style={{ marginTop: '0.625rem' }}>
            <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', marginBottom: '0.35rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.06em' }}>
              Official Sources
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.375rem' }}>
              {message.sources.map((s, i) => <SourceCard key={i} source={s} />)}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function TypingIndicator() {
  return (
    <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '1rem', alignItems: 'center' }}>
      <div style={{ width: 32, height: 32, borderRadius: '50%', background: 'var(--grad-primary)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
        <Bot size={16} color="white" />
      </div>
      <div className="chat-bubble-ai" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem', padding: '0.75rem 1rem' }}>
        <div className="typing-dot" />
        <div className="typing-dot" />
        <div className="typing-dot" />
      </div>
    </div>
  );
}

const SUGGESTIONS = [
  'Which scholarships am I eligible for?',
  'What documents are required for AICTE Pragati?',
  'What is the income limit for central sector scholarship?',
  'What is the application process for NSP scholarships?',
];

export default function ChatPage() {
  const { student, studentId } = useStudent();
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'welcome',
      role: 'assistant',
      content: `Hello! I'm ScholarAI, your intelligent scholarship assistant. 🎓

I can help you find relevant scholarships, explain eligibility criteria, and answer questions about educational opportunities — all grounded in official source documents (NSP, UGC, AICTE, Ministry of Education).

**What I can help with:**
- Which scholarships you are eligible for (uses deterministic eligibility engine)
- Scholarship eligibility criteria and requirements
- Income limits and academic requirements
- Document requirements and application process
- Deadlines and benefit amounts

Ask me anything about the scholarships in our knowledge base!

⚠️ *All answers are grounded in official documents. Always verify from the official portal before applying.*`,
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [loadingStage, setLoadingStage] = useState('');
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const sendMessage = async (query: string) => {
    if (!query.trim() || loading) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: query,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    let eligibilityContext: EligibilityResult[] = [];
    let ragQuery = query;
    let aiSources: SourceAttribution[] = [];
    let aiAnswer = '';

    try {
      const isEligQuery = isEligibilityQuestion(query);

      // ── STEP 1: Deterministic Eligibility (if eligibility question) ──────
      if (isEligQuery && studentId) {
        setLoadingStage('Checking eligibility…');
        try {
          const eligResult = await evaluateEligibility(studentId);
          eligibilityContext = eligResult.evaluations;

          // Build a structured context prefix for the LLM
          const eligible = eligibilityContext.filter(e => e.overall_status === 'ELIGIBLE');
          const potential = eligibilityContext.filter(e => e.overall_status === 'POTENTIALLY_ELIGIBLE');
          const insufficient = eligibilityContext.filter(e => e.overall_status === 'INSUFFICIENT_INFORMATION');

          // Compose an augmented query that passes eligibility facts to RAG
          ragQuery = `Student eligibility determination (deterministic engine result):
ELIGIBLE opportunities (${eligible.length}): ${eligible.map(e => e.opportunity_id).join(', ') || 'None'}
POTENTIALLY ELIGIBLE (${potential.length}): ${potential.map(e => e.opportunity_id).join(', ') || 'None'}
INSUFFICIENT INFORMATION (${insufficient.length}): ${insufficient.length > 0 ? 'Some opportunities need more profile information' : 'None'}

Original student question: ${query}

Using only official source documents, explain the eligibility results to the student and provide supporting information from official scholarship guidelines.`;
        } catch {
          // If eligibility check fails (e.g., no student), fall back to plain RAG
          eligibilityContext = [];
          ragQuery = query;
        }
      } else if (isEligQuery && !studentId) {
        // Eligibility question but no profile
        const noProfileMessage: ChatMessage = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: `To check your scholarship eligibility, I need your student profile first.

Please go to the **[Profile page](/profile)** to set up your profile, then come back and ask again.

Once your profile is saved, I can use the deterministic eligibility engine to tell you exactly which scholarships you qualify for.`,
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, noProfileMessage]);
        setLoading(false);
        setLoadingStage('');
        return;
      }

      // ── STEP 2: RAG Retrieval + LLM Generation ───────────────────────────
      setLoadingStage('Retrieving official documents…');
      const ragResponse = await askQuestion(ragQuery, undefined, 5);
      aiAnswer = ragResponse.answer;
      aiSources = ragResponse.sources;

    } catch (err) {
      aiAnswer = `I'm sorry, I encountered an error while processing your question. Please check that the backend is running and try again.\n\nError: ${err instanceof Error ? err.message : 'Unknown error'}`;
      aiSources = [];
    }

    const aiMessage: ChatMessage = {
      id: (Date.now() + 1).toString(),
      role: 'assistant',
      content: aiAnswer,
      sources: aiSources,
      eligibilityContext: eligibilityContext.length > 0 ? eligibilityContext : undefined,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, aiMessage]);
    setLoading(false);
    setLoadingStage('');
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendMessage(input);
  };

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 4rem)', maxHeight: 900 }}>
      {/* Header */}
      <div className="page-header" style={{ marginBottom: '1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div>
            <h1 className="page-title" style={{ display: 'flex', alignItems: 'center', gap: '0.625rem' }}>
              <Sparkles size={22} color="#818cf8" />
              <span className="gradient-text">AI Assistant</span>
            </h1>
            <p className="page-subtitle">
              {student?.name ? `Answering for ${student.name} · ` : ''}
              Answers grounded in official NSP, UGC, AICTE & Ministry sources
            </p>
          </div>
          <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
            {!studentId && (
              <div style={{ padding: '0.4rem 0.875rem', background: 'rgba(245,158,11,0.1)', border: '1px solid rgba(245,158,11,0.25)', borderRadius: 9999, fontSize: '0.72rem', color: '#f59e0b' }}>
                ⚠️ No profile — eligibility queries require a profile
              </div>
            )}
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.4rem 0.875rem', background: 'rgba(16,185,129,0.1)', border: '1px solid rgba(16,185,129,0.25)', borderRadius: 9999, fontSize: '0.72rem', color: '#10b981' }}>
              <Bot size={11} /> Llama 3.2 via Ollama
            </div>
          </div>
        </div>
      </div>

      {/* Chat area */}
      <div className="card" style={{ flex: 1, display: 'flex', flexDirection: 'column', minHeight: 0 }}>
        {/* Messages */}
        <div style={{ flex: 1, overflowY: 'auto', paddingRight: '0.25rem', marginBottom: '1rem' }}>
          {messages.map((msg) => <ChatBubble key={msg.id} message={msg} />)}
          {loading && (
            <div>
              {loadingStage && (
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: '0.5rem', marginLeft: '2.75rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                  <RefreshCw size={10} className="animate-spin-slow" />
                  {loadingStage}
                </div>
              )}
              <TypingIndicator />
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        {/* Suggestions */}
        {messages.length === 1 && !loading && (
          <div style={{ marginBottom: '0.875rem' }}>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: '0.5rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.06em' }}>
              Suggested questions
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
              {SUGGESTIONS.map((s) => (
                <button
                  key={s}
                  className="btn-ghost"
                  onClick={() => sendMessage(s)}
                  style={{ fontSize: '0.75rem', padding: '0.35rem 0.75rem', border: '1px solid var(--border-subtle)', borderRadius: 9999 }}
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Input */}
        <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '0.625rem', paddingTop: '0.875rem', borderTop: '1px solid var(--border-subtle)' }}>
          <input
            className="input"
            id="chat-input"
            style={{ flex: 1 }}
            placeholder="Ask about scholarship eligibility, requirements, deadlines..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={loading}
            autoComplete="off"
          />
          <button
            type="submit"
            className="btn-primary"
            id="send-chat-btn"
            disabled={!input.trim() || loading}
            style={{ padding: '0.625rem 1rem', flexShrink: 0 }}
          >
            {loading ? <RefreshCw size={15} className="animate-spin-slow" /> : <Send size={15} />}
          </button>
        </form>

        {/* Disclaimer */}
        <div style={{ marginTop: '0.5rem', fontSize: '0.68rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.375rem' }}>
          <AlertCircle size={10} />
          Eligibility is determined by the deterministic engine — not by the LLM.
          Answers grounded in official NSP, UGC, AICTE & Ministry sources.
          Always verify from the official portal before applying.
        </div>
      </div>
    </div>
  );
}
