import React, { useState, useEffect, useRef, useCallback } from 'react';
import { createPortal } from 'react-dom';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';

/* ───────────────────────── Types ───────────────────────── */

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  status?: string;
  chart_image?: string | null;
  kpis?: KPI[] | null;
  kpi_sources?: string[] | null;
  kpi_source_routes?: string[] | null;
  is_kpi_response?: boolean;
  timestamp: string;
}

interface KPI {
  name: string;
  category?: string;
  description?: string;
  formula_latex?: string;
  formula_plain?: string;
  reasoning?: string;
  data_requirements?: string[];
  source?: string;
  sources?: string[];
}

interface ChatPanelProps {
  onClose: () => void;
  apiBase: string;
  apiPrefix: string;
  appMode?: 'admin' | 'user';
}

/* ───────────────────────── Helpers ───────────────────────── */

const now = () => {
  const d = new Date();
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: true });
};

const uid = () => crypto.randomUUID();

const getKpiSummary = (content: string) => {
  if (!content) return '';
  const match = content.match(/^([^*]+?)(?=\*\*\d|\n\n\*\*|\n\d+\.)/s);
  return match ? match[1].trim() : content.split('\n\n')[0];
};

/* ───────────────────────── Sub-Components ───────────────────────── */

const StatusDot: React.FC<{ text: string }> = ({ text }) => (
  <div className="flex items-center gap-2 px-1 py-2">
    <span className="w-2 h-2 rounded-full bg-[#ff4756] animate-pulse shadow-[0_0_6px_#ff4756]" />
    <span className="text-[11px] text-gray-400 font-mono">{text}</span>
  </div>
);

const KPICard: React.FC<{ kpi: KPI; index: number }> = ({ kpi, index }) => {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="rounded-xl border border-white/10 bg-white/[0.03] backdrop-blur-lg overflow-hidden">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center gap-3 px-4 py-3 text-left hover:bg-white/[0.03] transition-colors"
      >
        <span className="w-6 h-6 rounded-full bg-[#ff4756]/20 text-[#ff4756] text-[11px] font-bold flex items-center justify-center shrink-0">
          {index}
        </span>
        <div className="flex-1 min-w-0">
          <p className="text-[12px] font-semibold text-gray-100 truncate">{kpi.name}</p>
          {kpi.category && (
            <p className="text-[10px] text-gray-500 mt-0.5">{kpi.category}</p>
          )}
        </div>
        <svg
          className={`w-4 h-4 text-gray-500 transition-transform ${expanded ? 'rotate-180' : ''}`}
          fill="none" viewBox="0 0 24 24" stroke="currentColor"
        >
          <polyline points="6 9 12 15 18 9" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </button>

      {expanded && (
        <div className="px-4 pb-3 border-t border-white/5 pt-3 space-y-2">
          {kpi.description && (
            <p className="text-[11px] text-gray-300 leading-relaxed">{kpi.description}</p>
          )}
          {(kpi.formula_latex || kpi.formula_plain) && (
            <div className="bg-black/40 rounded-lg px-3 py-2 border border-white/5">
              <span className="text-[9px] uppercase text-gray-500 font-mono">Formula</span>
              <div className="text-[12px] text-gray-200 mt-1 copilot-md">
                <ReactMarkdown remarkPlugins={[remarkMath]} rehypePlugins={[rehypeKatex]}>
                  {(kpi.formula_plain || kpi.formula_latex || '').includes('$') 
                    ? (kpi.formula_plain || kpi.formula_latex || '') 
                    : `$$${kpi.formula_plain || kpi.formula_latex}$$`}
                </ReactMarkdown>
              </div>
            </div>
          )}
          {kpi.reasoning && (
            <div>
              <span className="text-[9px] uppercase text-gray-500 font-mono">Why this KPI?</span>
              <p className="text-[11px] text-gray-400 mt-0.5">{kpi.reasoning}</p>
            </div>
          )}
          {kpi.data_requirements && kpi.data_requirements.length > 0 && (
            <div>
              <span className="text-[9px] uppercase text-gray-500 font-mono">Required Data</span>
              <ul className="mt-1 space-y-0.5">
                {kpi.data_requirements.map((req, i) => (
                  <li key={i} className="text-[11px] text-gray-400 flex items-start gap-1.5">
                    <span className="text-[#ff4756] mt-0.5">•</span>{req}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

/* ───────────────────────── Main Component ───────────────────────── */

export const ChatPanel: React.FC<ChatPanelProps> = ({ onClose, apiBase, apiPrefix, appMode = 'admin' }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputVal, setInputVal] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(() => uid());
  const [zoomedImage, setZoomedImage] = useState<string | null>(null);
  
  // Clear chat when appMode changes
  useEffect(() => {
    setMessages([]);
    setSessionId(uid());
    setInputVal('');
    // Any running request will be orphaned (technically we could use an AbortController, but this is fine)
  }, [appMode]);

  // User filter state
  const [validUsers, setValidUsers] = useState<string[]>([]);
  const [userFilterEnabled, setUserFilterEnabled] = useState(false);
  const [selectedUserName, setSelectedUserName] = useState('');
  const [userFilterError, setUserFilterError] = useState('');

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Fetch users when in User Mode
  useEffect(() => {
    if (appMode === 'user') {
      fetch(`${apiBase}${apiPrefix}/users`)
        .then(res => res.json())
        .then(data => {
          if (Array.isArray(data.users)) {
            setValidUsers(data.users);
          }
        })
        .catch(() => {
          setValidUsers([]);
          setUserFilterError('User list is unavailable right now.');
        });
    } else {
      setValidUsers([]);
      setUserFilterEnabled(false);
      setSelectedUserName('');
      setUserFilterError('');
    }
  }, [appMode, apiBase]);

  const resolveCanonicalUserName = (name: string) => {
    const cleaned = (name || '').trim();
    if (!cleaned) return null;
    return validUsers.find((user) => user.toLowerCase() === cleaned.toLowerCase()) || null;
  };

  // Auto-scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Focus input on mount
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const updateMessage = useCallback((msgId: string, updater: Partial<ChatMessage> | ((prev: ChatMessage) => ChatMessage)) => {
    setMessages(prev =>
      prev.map(msg => {
        if (msg.id !== msgId) return msg;
        return typeof updater === 'function' ? updater(msg) : { ...msg, ...updater };
      })
    );
  }, []);

  /* ─── Stream handler (ported from frontend/App.js) ─── */
  const handleSubmit = useCallback(async (e?: React.FormEvent, customInput?: string) => {
    e?.preventDefault();
    const query = (customInput || inputVal).trim();
    if (!query || isLoading) return;

    const userMsgId = uid();
    const botMsgId = uid();
    const ts = now();

    setUserFilterError('');
    let scopedUserName = null;
    if (appMode === 'user' && userFilterEnabled) {
      scopedUserName = resolveCanonicalUserName(selectedUserName);
      if (!scopedUserName) {
        setUserFilterError(
          validUsers.length > 0
            ? 'Enter a valid user name from the user list.'
            : 'User list is unavailable right now. Please switch the filter off.'
        );
        return;
      }
    }

    if (!customInput) setInputVal('');

    setMessages(prev => [
      ...prev,
      { id: userMsgId, role: 'user', content: query, timestamp: ts },
      { id: botMsgId, role: 'assistant', content: '', status: 'Understanding your query...', timestamp: ts },
    ]);
    setIsLoading(true);

    try {
      const response = await fetch(`${apiBase}${apiPrefix}/chat/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          message: query, 
          session_id: sessionId,
          user_filter_enabled: appMode === 'user' ? userFilterEnabled : false,
          user_name: scopedUserName
        }),
      });

      if (!response.ok || !response.body) throw new Error('Failed to get response');

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      let gotResult = false;

      const handleEvent = (payload: Record<string, unknown>) => {
        const eventType = payload?.type as string;

        if (eventType === 'status') {
          updateMessage(botMsgId, { status: (payload.message as string) || '' });
        } else if (eventType === 'token') {
          updateMessage(botMsgId, (prev) => ({
            ...prev,
            content: `${prev.content || ''}${(payload.message as string) || ''}`,
          }));
        } else if (eventType === 'result') {
          gotResult = true;
          updateMessage(botMsgId, (prev) => ({
            ...prev,
            content: (payload.reply as string) ?? prev.content,
            chart_image: (payload.chart_image as string) || null,
            kpis: (payload.kpis as KPI[]) || null,
            kpi_sources: (payload.kpi_sources as string[]) || null,
            kpi_source_routes: (payload.kpi_source_routes as string[]) || null,
            is_kpi_response: Boolean(payload.is_kpi_response),
            status: '',
          }));
        } else if (eventType === 'error') {
          gotResult = true;
          updateMessage(botMsgId, (prev) => ({
            ...prev,
            content: (payload.message as string) || prev.content || 'Request failed.',
            status: '',
          }));
        } else if (eventType === 'done') {
          updateMessage(botMsgId, { status: '' });
        }
      };

      // Read NDJSON stream
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          const trimmed = line.trim();
          if (!trimmed) continue;
          try {
            handleEvent(JSON.parse(trimmed));
          } catch {
            // Ignore partial JSON lines
          }
        }
      }

      // Handle remaining buffer
      if (buffer.trim()) {
        try {
          handleEvent(JSON.parse(buffer.trim()));
        } catch {
          // Ignore
        }
      }

      if (!gotResult) {
        throw new Error('Stream ended before a response was received');
      }
    } catch (error) {
      updateMessage(botMsgId, {
        content: (error as Error)?.message || 'Connection error. Is the backend running?',
        status: '',
      });
    } finally {
      setIsLoading(false);
    }
  }, [inputVal, isLoading, apiBase, apiPrefix, sessionId, updateMessage]);

  /* ───────────────────────── Render ───────────────────────── */

  return (
    <aside
      className="w-[500px] flex-shrink-0 h-full flex flex-col relative z-20 border-l border-white/5 shadow-[-10px_0_30px_rgba(0,0,0,0.5)]"
      style={{
        background: 'rgba(255,255,255,0.015)',
        backdropFilter: 'blur(32px)',
        WebkitBackdropFilter: 'blur(32px)'
      }}
    >
      {/* ─── Header ─── */}
      <div className="flex items-center justify-between p-4 border-b border-white/5 bg-black/20 shrink-0">
        <h2 className="text-white font-medium flex items-center gap-2">
          <svg className="w-5 h-5 text-[#ff4756]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
          AI Assistant
        </h2>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-white transition-colors p-1 rounded hover:bg-white/10"
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      {/* ─── User Filter UI (User Mode Only) ─── */}
      {appMode === 'user' && (
        <div className="bg-black/30 border-b border-white/5 py-2.5 px-4 shrink-0">
          <div className="flex items-center gap-3">
            <label className="flex items-center gap-2 cursor-pointer outline-none">
              <input
                type="checkbox"
                checked={userFilterEnabled}
                onChange={(e) => {
                  setUserFilterEnabled(e.target.checked);
                  setUserFilterError('');
                  if (!e.target.checked) setSelectedUserName('');
                }}
                disabled={isLoading}
                className="w-3.5 h-3.5 rounded border-white/10 bg-black/40 accent-[#ff4756] focus:ring-[#ff4756]/50"
              />
              <span className="text-[11px] font-medium text-gray-300 select-none">User Filter</span>
            </label>
            
            {userFilterEnabled && (
              <select
                value={selectedUserName}
                onChange={(e) => setSelectedUserName(e.target.value)}
                disabled={isLoading || validUsers.length === 0}
                className="flex-1 bg-black/60 border border-white/10 rounded-lg px-2 py-1 text-[11px] text-white focus:outline-none focus:border-[#ff4756]/50 focus:ring-1 focus:ring-[#ff4756]/50 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <option value="">-- Select a User --</option>
                {validUsers.map(u => (
                  <option key={u} value={u}>{u}</option>
                ))}
              </select>
            )}
          </div>
          {userFilterError && (
            <div className="mt-1.5 text-[10px] text-[#ff4756] animate-pulse">{userFilterError}</div>
          )}
        </div>
      )}

      {/* ─── Messages ─── */}
      <div className="flex-1 overflow-y-auto p-5 flex flex-col gap-5">
        {messages.length === 0 && (
          <div className="flex-1 flex flex-col items-center justify-center text-center px-4 py-12 gap-3">
            <div className="w-12 h-12 rounded-full bg-gradient-to-tr from-[#ff4756] to-[#ffb7bc] p-px">
              <div className="w-full h-full rounded-full bg-black/80 flex items-center justify-center">
                <svg className="w-6 h-6 text-[#ff4756]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
            </div>
            <p className="text-sm text-gray-300 font-semibold">Ask me anything</p>
            <p className="text-[11px] text-gray-500 max-w-[220px]">
              I can query your data, generate charts, discover KPIs, and answer questions about operations.
            </p>
          </div>
        )}

        {messages.map((msg) => (
          <div key={msg.id} className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
            {/* Meta row */}
            <div className="flex items-center gap-2 mb-1.5 px-1">
              {msg.role === 'assistant' && (
                <div className="w-5 h-5 rounded bg-[#ff4756]/20 border border-[#ff4756]/30 flex items-center justify-center shrink-0">
                  <svg className="w-3 h-3 text-[#ff4756]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
              )}
              <span className="text-[10px] text-gray-500 font-mono">{msg.role === 'user' ? 'You' : 'AI Assistant'}</span>
              <span className="text-[10px] text-gray-700 font-mono">•</span>
              <span className="text-[10px] text-gray-600 font-mono">{msg.timestamp}</span>
            </div>

            {/* Bubble */}
            <div className={`
              max-w-[90%] rounded-2xl text-[13px] leading-relaxed relative overflow-hidden
              ${msg.role === 'user'
                ? 'bg-white/[0.04] border border-white/[0.08] rounded-tr-sm text-gray-200 p-4'
                : 'bg-white/[0.06] border border-white/[0.1] rounded-tl-sm text-gray-100 backdrop-blur-xl p-4'}
            `}>
              {/* Status indicator */}
              {msg.status && <StatusDot text={msg.status} />}

              {/* KPI Response */}
              {msg.is_kpi_response && msg.kpis && msg.kpis.length > 0 ? (
                <div className="space-y-3">
                  {msg.content && (
                    <div className="copilot-md text-[12px]">
                      <ReactMarkdown remarkPlugins={[remarkGfm, remarkMath]} rehypePlugins={[rehypeKatex]}>
                        {getKpiSummary(msg.content)}
                      </ReactMarkdown>
                    </div>
                  )}
                  <div className="space-y-2">
                    {msg.kpis.map((kpi, i) => (
                      <KPICard key={i} kpi={kpi} index={i + 1} />
                    ))}
                  </div>
                  {msg.kpi_sources && msg.kpi_sources.length > 0 && (
                    <div className="pt-2 border-t border-white/5">
                      <span className="text-[9px] uppercase text-gray-500 font-mono">Sources</span>
                      <div className="mt-1 space-y-1">
                        {msg.kpi_sources.map((src, i) => {
                          const isUrl = src.startsWith('http') || src.startsWith('www');
                          const href = src.startsWith('www') ? `https://${src}` : src;
                          if (isUrl) {
                            return (
                              <a key={i} href={href} target="_blank" rel="noreferrer" className="block text-[10px] text-[#ff4756] hover:underline break-all">
                                {src}
                              </a>
                            );
                          }
                          return <p key={i} className="text-[10px] text-gray-400 break-all">{src}</p>;
                        })}
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                /* Regular markdown response */
                msg.content && (
                  <div className="copilot-md text-[12px]">
                    <ReactMarkdown
                      remarkPlugins={[remarkGfm, remarkMath]}
                      rehypePlugins={[rehypeKatex]}
                      components={{
                        a: ({ children, ...props }) => (
                          <a {...props} target="_blank" rel="noreferrer" className="text-[#ff4756] underline">
                            {children}
                          </a>
                        ),
                      }}
                    >
                      {msg.content}
                    </ReactMarkdown>
                  </div>
                )
              )}

              {/* Chart image with zoom/download controls */}
              {msg.chart_image && (
                <div className="mt-3 rounded-xl overflow-hidden border border-white/10 relative group">
                  <img
                    src={`data:image/png;base64,${msg.chart_image}`}
                    alt="Generated Chart"
                    className="w-full bg-black/40 cursor-pointer"
                    onClick={() => setZoomedImage(`data:image/png;base64,${msg.chart_image}`)}
                  />
                  {/* Hover controls */}
                  <div className="absolute top-2 right-2 flex gap-1.5 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button
                      onClick={() => setZoomedImage(`data:image/png;base64,${msg.chart_image}`)}
                      className="w-8 h-8 rounded-lg bg-black/70 backdrop-blur-md border border-white/15 text-white flex items-center justify-center hover:bg-black/90 transition-all hover:scale-105"
                      title="Zoom In"
                    >
                      <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <circle cx="11" cy="11" r="8" />
                        <line x1="21" y1="21" x2="16.65" y2="16.65" />
                        <line x1="11" y1="8" x2="11" y2="14" />
                        <line x1="8" y1="11" x2="14" y2="11" />
                      </svg>
                    </button>
                    <a
                      href={`data:image/png;base64,${msg.chart_image}`}
                      download="chart.png"
                      className="w-8 h-8 rounded-lg bg-black/70 backdrop-blur-md border border-white/15 text-white flex items-center justify-center hover:bg-black/90 transition-all hover:scale-105"
                      title="Download Chart"
                    >
                      <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                        <polyline points="7 10 12 15 17 10" />
                        <line x1="12" y1="15" x2="12" y2="3" />
                      </svg>
                    </a>
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}

        <div ref={messagesEndRef} />
      </div>

      {/* ─── Input Area ─── */}
      <div className="p-4 border-t border-white/5 bg-black/20">
        <form onSubmit={handleSubmit} className="relative">
          <input
            ref={inputRef}
            type="text"
            value={inputVal}
            onChange={(e) => setInputVal(e.target.value)}
            placeholder="Ask about operations..."
            disabled={isLoading}
            className="w-full bg-black/60 border border-white/10 rounded-xl pl-4 pr-12 py-3.5 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-[#ff4756]/50 focus:ring-1 focus:ring-[#ff4756]/50 shadow-inner transition-all font-medium disabled:opacity-50 disabled:cursor-not-allowed"
          />
          <button
            type="submit"
            disabled={!inputVal.trim() || isLoading}
            className="absolute right-2 top-1/2 -translate-y-1/2 w-9 h-9 rounded-lg bg-[#ff4756]/20 text-[#ff4756] hover:bg-[#ff4756]/40 hover:text-[#ffb7bc] flex items-center justify-center transition-all hover:scale-105 active:scale-95 disabled:opacity-30 disabled:hover:scale-100"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 10l7-7m0 0l7 7m-7-7v18" />
            </svg>
          </button>
        </form>
      </div>

      {/* ─── Zoomed Chart Modal ─── */}
      {zoomedImage && createPortal(
        <div
          className="fixed inset-0 z-[100] bg-black/90 backdrop-blur-md flex items-center justify-center p-10"
          onClick={() => setZoomedImage(null)}
          style={{ animation: 'fadeIn 0.2s ease-out' }}
        >
          <button
            className="absolute top-6 right-6 w-10 h-10 rounded-full bg-white/10 text-white flex items-center justify-center hover:bg-white/20 transition-all hover:scale-110"
            onClick={() => setZoomedImage(null)}
          >
            <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
          <img
            src={zoomedImage}
            alt="Zoomed Chart"
            className="max-w-[90vw] max-h-[90vh] rounded-2xl border border-white/10 shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          />
        </div>,
        document.body
      )}
    </aside>
  );
};
