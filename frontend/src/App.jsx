import { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, useLocation } from 'react-router-dom';

import Sidebar    from './components/Sidebar.jsx';
import Dashboard  from './pages/Dashboard.jsx';
import Chat       from './pages/Chat.jsx';
import Automation from './pages/Automation.jsx';
import Audit      from './pages/Audit.jsx';

const BASE = import.meta.env.VITE_API_URL || '';


const PAGE_META = {
  '/':           { title: 'Executive Dashboard',    subtitle: 'Real-time company intelligence across all departments' },
  '/chat':       { title: 'AI Intelligence Chat',   subtitle: 'Cross-department RAG-powered question & answer engine' },
  '/automation': { title: 'Automation Center',      subtitle: 'Rule evaluation, approval workflows & action management' },
  '/audit':      { title: 'Audit Trail',            subtitle: 'Immutable history of all automation actions and reviews' },
};

function BackendStatus() {
  const [status, setStatus] = useState('checking'); // checking | ok | error
  const [info, setInfo]     = useState(null);

  useEffect(() => {
    fetch(`${BASE}/health`)
      .then(r => r.json())
      .then(d => { setStatus('ok'); setInfo(d); })
      .catch(() => setStatus('error'));
  }, []);

  if (status === 'checking') return (
    <div className="topbar-pill" title="Checking backend…">
      <span style={{ width: 7, height: 7, borderRadius: '50%', background: '#ffb020', display: 'inline-block', boxShadow: '0 0 6px #ffb020' }} />
      Connecting…
    </div>
  );

  if (status === 'error') return (
    <div className="topbar-pill" title="Backend unreachable — start the FastAPI server">
      <span style={{ width: 7, height: 7, borderRadius: '50%', background: '#ff4d6d', display: 'inline-block', boxShadow: '0 0 6px #ff4d6d' }} />
      Offline
    </div>
  );

  return (
    <div className="topbar-pill" title={`LLM: ${info?.llm_provider} · DB: ${info?.database} · Vector: ${info?.vector_store}`}>
      <span style={{ width: 7, height: 7, borderRadius: '50%', background: '#00e5a0', display: 'inline-block', boxShadow: '0 0 6px #00e5a0', animation: 'blink 2s infinite' }} />
      {info?.llm_provider ? `LLM: ${info.llm_provider}` : 'Backend OK'}
    </div>
  );
}

function AppInner() {
  const location  = useLocation();
  const [pending, setPending] = useState(0);
  const meta = PAGE_META[location.pathname] || PAGE_META['/'];

  return (
    <div className="app-shell">
      <Sidebar pendingCount={pending} />

      <div className="main-content">
        {/* Top Bar */}
        <header className="topbar">
          <div>
            <div className="topbar-title">{meta.title}</div>
            <div className="topbar-subtitle">{meta.subtitle}</div>
          </div>
          <div className="topbar-spacer" />
          <div className="topbar-pill">🧠 NeuroCore v2.0</div>
          <div className="topbar-pill">🗄 SQLite · ChromaDB</div>
          <BackendStatus />
        </header>

        {/* Pages */}
        <Routes>
          <Route path="/"           element={<Dashboard />} />
          <Route path="/chat"       element={<Chat />} />
          <Route path="/automation" element={<Automation onPendingChange={setPending} />} />
          <Route path="/audit"      element={<Audit />} />
        </Routes>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AppInner />
    </BrowserRouter>
  );
}
