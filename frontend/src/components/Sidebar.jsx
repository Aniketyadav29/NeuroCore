import { NavLink } from 'react-router-dom';

const NAV = [
  { to: '/',           icon: '⬡',  label: 'Dashboard',         section: 'OVERVIEW' },
  { to: '/chat',       icon: '🧠', label: 'AI Intelligence',    section: 'INTELLIGENCE' },
  { to: '/automation', icon: '⚡', label: 'Automation',         section: 'ENGINE' },
  { to: '/audit',      icon: '📋', label: 'Audit Trail',        section: null },
];

export default function Sidebar({ pendingCount }) {
  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <div className="sidebar-logo-icon">🧠</div>
        <div className="sidebar-logo-text">
          <span className="brand">NeuroCore AI</span>
          <span className="tagline">Corporate Intelligence</span>
        </div>
      </div>

      <nav className="sidebar-nav">
        {NAV.map(({ to, icon, label, section }) => (
          <div key={to}>
            {section && <div className="nav-section-label">{section}</div>}
            <NavLink
              to={to}
              end={to === '/'}
              className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}
            >
              <span className="nav-icon">{icon}</span>
              {label}
              {to === '/automation' && pendingCount > 0 && (
                <span className="nav-badge">{pendingCount}</span>
              )}
            </NavLink>
          </div>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="status-dot">All systems operational</div>
      </div>
    </aside>
  );
}
