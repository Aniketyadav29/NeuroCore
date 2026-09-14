import { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { sendChat, reindex, indexStatus } from '../api.js';

const SUGGESTIONS = [
  'Why did support tickets spike this week?',
  'Which clients have overdue invoices?',
  'Is the support team understaffed?',
  'What happened after the Q1 product launch?',
  'Connect the ProPay Suite situation across all departments',
];

function TypingIndicator() {
  return (
    <div className="chat-message">
      <div className="chat-avatar ai">🧠</div>
      <div className="chat-bubble">
        <div className="chat-bubble-content">
          <div className="typing-indicator">
            <div className="typing-dot" />
            <div className="typing-dot" />
            <div className="typing-dot" />
          </div>
        </div>
      </div>
    </div>
  );
}

function ChatMessage({ msg }) {
  if (msg.role === 'user') {
    return (
      <div className="chat-message" style={{ flexDirection: 'row-reverse' }}>
        <div className="chat-avatar user">👤</div>
        <div className="chat-bubble user">
          <div className="chat-bubble-content">{msg.content}</div>
        </div>
      </div>
    );
  }

  return (
    <div className="chat-message">
      <div className="chat-avatar ai">🧠</div>
      <div className="chat-bubble">
        <div className="chat-bubble-content">
          <ReactMarkdown>{msg.content}</ReactMarkdown>
        </div>
        <div className="chat-meta">
          <span className="provider-chip">🔌 {msg.provider}</span>
          <span style={{ color: 'var(--text-muted)' }}>· {msg.contextUsed} records</span>
          {msg.citations?.slice(0, 8).map(c => (
            <span key={c} className="citation-chip">{c}</span>
          ))}
        </div>
      </div>
    </div>
  );
}

export default function Chat() {
  const [messages, setMessages] = useState([]);
  const [input,    setInput]    = useState('');
  const [loading,  setLoading]  = useState(false);
  const [indexing, setIndexing] = useState(false);
  const [indexInfo, setIndexInfo] = useState(null);
  const bottomRef = useRef(null);

  useEffect(() => {
    indexStatus().then(setIndexInfo).catch(() => {});
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const send = async (text) => {
    const q = (text || input).trim();
    if (!q || loading) return;
    setInput('');
    setMessages(m => [...m, { role: 'user', content: q }]);
    setLoading(true);
    try {
      const res = await sendChat(q);
      setMessages(m => [...m, {
        role:       'ai',
        content:    res.answer,
        citations:  res.citations,
        provider:   res.provider,
        contextUsed: res.context_used,
      }]);
    } catch (e) {
      setMessages(m => [...m, {
        role: 'ai',
        content: `**Error:** ${e.message}\n\nMake sure the backend is running and the index is populated.`,
        citations: [], provider: 'error', contextUsed: 0,
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleReindex = async () => {
    setIndexing(true);
    try {
      const res = await reindex();
      const info = await indexStatus();
      setIndexInfo(info);
      setMessages(m => [...m, {
        role: 'ai',
        content: `✅ **Reindex complete!** Indexed **${res.total_indexed}** records across ${Object.keys(res.by_department).length} departments:\n\n${
          Object.entries(res.by_department).map(([k,v]) => `- **${k.toUpperCase()}**: ${v} records`).join('\n')
        }\n\nYou can now ask questions about the company data.`,
        citations: [], provider: 'system', contextUsed: 0,
      }]);
    } catch (e) {
      setMessages(m => [...m, {
        role: 'ai',
        content: `**Reindex failed:** ${e.message}`,
        citations: [], provider: 'error', contextUsed: 0,
      }]);
    } finally {
      setIndexing(false);
    }
  };

  const handleKey = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  };

  const isEmpty = indexInfo?.status === 'empty';

  return (
    <div className="chat-container">
      <div className="chat-messages">
        {messages.length === 0 && (
          <div style={{ textAlign: 'center', padding: '40px 20px' }}>
            <div style={{ fontSize: 56, marginBottom: 16 }}>🧠</div>
            <h2 style={{ color: 'var(--text-primary)', marginBottom: 8, fontSize: 20 }}>
              NeuroCore Intelligence Engine
            </h2>
            <p style={{ color: 'var(--text-muted)', maxWidth: 420, margin: '0 auto 24px', fontSize: 14, lineHeight: 1.7 }}>
              Ask any cross-departmental question. The RAG engine will retrieve relevant records
              from HR, Sales, Finance and Support and synthesize an answer with citations.
            </p>

            {isEmpty && (
              <div className="alert-banner warning" style={{ justifyContent: 'center', marginBottom: 20, maxWidth: 500, margin: '0 auto 20px' }}>
                ⚠️ Vector store is empty — reindex the database first
              </div>
            )}

            <button
              className="btn btn-primary"
              onClick={handleReindex}
              disabled={indexing}
              style={{ marginBottom: 28 }}
            >
              {indexing ? '⏳ Indexing…' : '🔄 Reindex Database'}
            </button>

            {indexInfo && !isEmpty && (
              <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 24 }}>
                Index: <strong style={{ color: 'var(--success)' }}>{indexInfo.total_documents} docs</strong> ready
              </div>
            )}
          </div>
        )}

        {messages.map((msg, i) => (
          <ChatMessage key={i} msg={msg} />
        ))}

        {loading && <TypingIndicator />}
        <div ref={bottomRef} />
      </div>

      <div className="chat-input-area">
        {messages.length === 0 && (
          <div className="chat-suggestions">
            {SUGGESTIONS.map(s => (
              <button key={s} className="suggestion-chip" onClick={() => send(s)}>
                {s}
              </button>
            ))}
          </div>
        )}

        <div className="chat-input-row">
          <textarea
            className="chat-input"
            rows={1}
            placeholder="Ask about HR, Sales, Finance, or Support… (Enter to send)"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKey}
            disabled={loading}
          />
          <button
            className="chat-send-btn"
            onClick={() => send()}
            disabled={!input.trim() || loading}
            title="Send"
          >
            ➤
          </button>
        </div>
      </div>
    </div>
  );
}
