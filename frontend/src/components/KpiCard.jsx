// Health ring SVG component
function HealthRing({ score, color }) {
  const r   = 20;
  const circ = 2 * Math.PI * r;
  const dash = (score / 100) * circ;

  const colors = {
    cyan:   '#00d4ff',
    green:  '#00e5a0',
    amber:  '#ffb020',
    red:    '#ff4d6d',
    purple: '#a855f7',
  };

  return (
    <div className="health-ring">
      <svg width="52" height="52" viewBox="0 0 52 52">
        <circle cx="26" cy="26" r={r} fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="4" />
        <circle
          cx="26" cy="26" r={r}
          fill="none"
          stroke={colors[color] || colors.cyan}
          strokeWidth="4"
          strokeDasharray={`${dash} ${circ}`}
          strokeLinecap="round"
          style={{ transition: 'stroke-dasharray 0.6s ease', filter: `drop-shadow(0 0 4px ${colors[color]})` }}
        />
      </svg>
      <div className="health-text">{score}%</div>
    </div>
  );
}

export default function KpiCard({ icon, label, value, color, meta = [], alert, health }) {
  return (
    <div className={`kpi-card color-${color}`}>
      <div className="kpi-header">
        <div className={`kpi-icon color-${color}`}>{icon}</div>
        {alert && <span className="kpi-alert-badge">⚠ ALERT</span>}
      </div>

      <div className="kpi-value">{value}</div>
      <div className="kpi-label">{label}</div>

      <div className="kpi-meta">
        {meta.map((item, i) => (
          <span key={i} className="kpi-meta-item">{item}</span>
        ))}
      </div>

      {health !== undefined && <HealthRing score={health} color={color} />}
    </div>
  );
}
