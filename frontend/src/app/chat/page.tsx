'use client';

import { useState, useRef, useEffect } from 'react';
import {
  Send, Bot, User, Sparkles, BookOpen, ExternalLink,
  AlertCircle, RefreshCw, Info, Zap,
} from 'lucide-react';
import type { ChatMessage, RAGSource } from '@/lib/types';

// ---- Mock RAG responses keyed by keyword patterns ----
const MOCK_RESPONSES: Array<{ pattern: RegExp; answer: string; sources: RAGSource[] }> = [
  {
    pattern: /pragati|aicte.*girl|girl.*aicte/i,
    answer: `**AICTE Pragati Scholarship** is designed for girl students pursuing technical education at AICTE-approved institutions.

**Key Details:**
- **Amount:** ₹50,000 per annum (covers tuition fees and incidentals)
- **Eligibility:** Female students in B.Tech, B.E, B.Arch, or Diploma programmes
- **Income Limit:** Annual family income below ₹8,00,000
- **Application:** Via the AICTE portal (aicte-india.org)
- **Status:** Currently Active for 2025-26

**Required Documents:** Admission letter, income certificate, Aadhaar card, bank passbook, previous year marksheet.

⚠️ *Please verify the current deadline and eligibility criteria from the official AICTE portal before applying.*`,
    sources: [
      { document_title: 'AICTE Pragati & Saksham Scholarship Guidelines 2025', source_url: 'https://aicte-india.org', section: 'Eligibility and Benefits', last_verified: '2025-08-15' },
    ],
  },
  {
    pattern: /csss|central sector|ministry.*education/i,
    answer: `**Central Sector Scheme of Scholarships (CSSS)** is a major scholarship by the Ministry of Education for meritorious students from low-income families.

**Key Details:**
- **Amount:** ₹10,000/year for UG students; ₹20,000/year for PG students
- **Eligibility:** Students who scored above 80% in Class XII from recognized boards
- **Income Limit:** Annual family income below ₹8,00,000
- **Education Level:** UG and PG
- **Institution Type:** Government, Deemed, or Central Universities
- **Duration:** Up to 3 years (renewable based on performance)

**Application:** Apply through the National Scholarship Portal at scholarships.gov.in

⚠️ *Eligibility criteria and deadlines are subject to change. Always verify from the official NSP portal.*`,
    sources: [
      { document_title: 'CSSS Guidelines 2025-26', source_url: 'https://scholarships.gov.in', section: 'Scheme Overview', last_verified: '2025-09-01' },
    ],
  },
  {
    pattern: /income.*limit|family income|financial/i,
    answer: `The income eligibility limits vary significantly across scholarship schemes. Here is a summary based on available source documents:

| Scholarship | Max. Family Income |
|---|---|
| CSSS (Central Sector) | ₹8,00,000/year |
| AICTE Pragati | ₹8,00,000/year |
| AICTE Saksham | ₹8,00,000/year |
| Post-Matric SC | ₹2,50,000/year |
| NSP Pre-Matric Minority | ₹1,00,000/year |
| PM Scholarship (PMSS) | No income limit |
| UGC Single Girl Child | No income limit |

**Note:** Income is typically assessed as total annual household income from all sources. An income certificate from a competent authority is required.

⚠️ *These figures are from official guidelines last verified in 2025. Verify current limits before applying.*`,
    sources: [
      { document_title: 'CSSS Guidelines 2025-26', source_url: 'https://scholarships.gov.in', last_verified: '2025-09-01' },
      { document_title: 'AICTE Pragati & Saksham Scholarship Guidelines 2025', source_url: 'https://aicte-india.org', last_verified: '2025-08-15' },
      { document_title: 'NSP Pre-Matric Minority Scholarship Guidelines', source_url: 'https://scholarships.gov.in', last_verified: '2025-08-20' },
    ],
  },
  {
    pattern: /b\.?tech|engineering|technical/i,
    answer: `Several scholarship and fellowship schemes are available for **B.Tech / Engineering students**:

1. **CSSS (Central Sector)** — ₹10,000/yr, requires 80%+ in Class XII, income < ₹8L
2. **AICTE Pragati** — ₹50,000/yr, for girl students in technical programmes
3. **AICTE Saksham** — ₹50,000/yr, for differently-abled students
4. **PM Scholarship Scheme** — ₹2,500–3,000/month, for wards of ex-servicemen
5. **Post-Matric SC Scholarship** — for SC students, income < ₹2.5L

**How to search:** Use the Opportunities page to filter by course (B.Tech) and your category to see relevant results.

⚠️ *Verify all eligibility criteria from official portals before applying.*`,
    sources: [
      { document_title: 'CSSS Guidelines 2025-26', source_url: 'https://scholarships.gov.in', last_verified: '2025-09-01' },
      { document_title: 'AICTE Pragati & Saksham Scholarship Guidelines 2025', source_url: 'https://aicte-india.org', last_verified: '2025-08-15' },
    ],
  },
  {
    pattern: /phd|research|fellowship|inspire/i,
    answer: `For **PhD / Research students**, the main fellowship available in our knowledge base is:

**DST INSPIRE Fellowship**
- **Provider:** Department of Science & Technology, Government of India
- **Amount:** ₹31,000/month + ₹20,000/year research grant
- **Duration:** 5 years
- **Eligibility:** Students pursuing PhD in natural/basic sciences (Physics, Chemistry, Mathematics, Biology, Earth Sciences) with 60%+ in UG/PG
- **Status:** Upcoming (applications expected Jan–Mar 2026)
- **Apply via:** online-inspire.gov.in

For other disciplines, the **UGC-NET JRF** and **CSIR NET Fellowship** are also available — though these are not yet in our current knowledge base.

⚠️ *The available source information in this system is limited to documents currently ingested. Verify from the official DST/UGC portal.*`,
    sources: [
      { document_title: 'DST INSPIRE Fellowship Programme Guidelines', source_url: 'https://online-inspire.gov.in', section: 'Eligibility and Award Details', last_verified: '2025-06-30' },
    ],
  },
];

function getResponse(query: string): { answer: string; sources: RAGSource[] } {
  for (const r of MOCK_RESPONSES) {
    if (r.pattern.test(query)) return { answer: r.answer, sources: r.sources };
  }
  return {
    answer: `I searched the available scholarship knowledge base for: *"${query}"*

The available source documents do not contain specific information to fully answer this query.

**What I can help with:**
- Specific scholarship details (CSSS, AICTE Pragati, INSPIRE, etc.)
- Income eligibility limits across schemes
- Scholarships for specific courses (B.Tech, Engineering)
- PhD / research fellowships

Try asking something like:
- *"What is the income limit for CSSS?"*
- *"Scholarships for B.Tech female students"*
- *"AICTE Pragati eligibility criteria"*
- *"PhD fellowships in science"*

⚠️ *This is a mock RAG response. Real LLM integration will be connected in Phase 10.*`,
    sources: [],
  };
}

function SourceCard({ source }: { source: RAGSource }) {
  return (
    <div style={{
      display: 'flex', alignItems: 'flex-start', gap: '0.5rem',
      padding: '0.5rem 0.625rem', borderRadius: '0.5rem',
      background: 'rgba(99,102,241,0.07)', border: '1px solid rgba(99,102,241,0.15)',
      fontSize: '0.72rem',
    }}>
      <BookOpen size={11} color="#818cf8" style={{ flexShrink: 0, marginTop: 2 }} />
      <div>
        <div style={{ color: '#a5b4fc', fontWeight: 600 }}>{source.document_title}</div>
        {source.section && <div style={{ color: 'var(--text-muted)' }}>§ {source.section}</div>}
        {source.last_verified && <div style={{ color: 'var(--text-muted)' }}>Verified: {source.last_verified}</div>}
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

function ChatBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === 'user';

  const renderMarkdown = (text: string) => {
    return text
      .split('\n')
      .map((line, i) => {
        if (line.startsWith('**') && line.endsWith('**')) {
          return <p key={i} style={{ fontWeight: 700, color: 'var(--text-primary)', marginBottom: '0.25rem' }}>{line.replace(/\*\*/g, '')}</p>;
        }
        if (line.startsWith('- ') || line.startsWith('* ')) {
          return <li key={i} style={{ marginLeft: '1rem', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>{line.slice(2).replace(/\*\*(.*?)\*\*/g, '$1')}</li>;
        }
        if (line.startsWith('⚠️')) {
          return <p key={i} style={{ color: '#f59e0b', fontSize: '0.78rem', marginTop: '0.5rem', fontStyle: 'italic' }}>{line}</p>;
        }
        if (line.match(/^\d+\./)) {
          return <li key={i} style={{ marginLeft: '1rem', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>{line.replace(/^\d+\.\s/, '').replace(/\*\*(.*?)\*\*/g, '$1')}</li>;
        }
        if (line === '') return <br key={i} />;
        return <p key={i} style={{ color: 'var(--text-secondary)', marginBottom: '0.2rem', fontSize: '0.85rem' }}>{line.replace(/\*\*(.*?)\*\*/g, '$1').replace(/\*(.*?)\*/g, '$1')}</p>;
      });
  };

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
          <div>{renderMarkdown(message.content)}</div>
        </div>
        {message.sources && message.sources.length > 0 && (
          <div style={{ marginTop: '0.625rem' }}>
            <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', marginBottom: '0.35rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.06em' }}>
              Sources
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
  'What is the income limit for CSSS scholarship?',
  'Scholarships for B.Tech female students',
  'AICTE Pragati eligibility criteria',
  'PhD fellowships in science and technology',
];

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'welcome',
      role: 'assistant',
      content: `Hello! I'm ScholarAI, your intelligent scholarship assistant. 🎓

I can help you find relevant scholarships, explain eligibility criteria, and answer questions about educational opportunities — all grounded in official source documents.

**What I can help with:**
- Scholarship eligibility criteria and requirements
- Income limits and academic requirements
- Document requirements and application process
- Deadlines and benefit amounts

Ask me anything about the scholarships in our knowledge base!

⚠️ *Note: This is running in mock mode. Real LLM (Google Gemini) will be connected in Phase 10. All information is sourced from official documents.*`,
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
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

    // Simulate retrieval + generation latency
    await new Promise((resolve) => setTimeout(resolve, 1200 + Math.random() * 800));

    const { answer, sources } = getResponse(query);
    const aiMessage: ChatMessage = {
      id: (Date.now() + 1).toString(),
      role: 'assistant',
      content: answer,
      sources,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, aiMessage]);
    setLoading(false);
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
            <p className="page-subtitle">Ask anything about scholarships — answers grounded in official source documents</p>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.4rem 0.875rem', background: 'rgba(245,158,11,0.1)', border: '1px solid rgba(245,158,11,0.25)', borderRadius: 9999, fontSize: '0.72rem', color: '#f59e0b' }}>
            <Zap size={11} /> Mock Mode
          </div>
        </div>
      </div>

      {/* Chat area */}
      <div className="card" style={{ flex: 1, display: 'flex', flexDirection: 'column', minHeight: 0 }}>
        {/* Messages */}
        <div style={{ flex: 1, overflowY: 'auto', paddingRight: '0.25rem', marginBottom: '1rem' }}>
          {messages.map((msg) => <ChatBubble key={msg.id} message={msg} />)}
          {loading && <TypingIndicator />}
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
          Answers are grounded in official source documents. Always verify from the official portal before applying.
        </div>
      </div>
    </div>
  );
}
