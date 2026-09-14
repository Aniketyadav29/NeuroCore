import { useState, useEffect } from 'react';
import KpiCard from '../components/KpiCard.jsx';
import {
  getDashboardStats, getDashboardHR, getDashboardSales,
  getDashboardFinance, getDashboardSupport
} from '../api.js';

function formatCurrency(n) {
  if (n >= 1_000_000) return `$${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000)     return `$${(n / 1_000).toFixed(0)}K`;
  return `$${n}`;
}

function StatusBadge({ value }) {
  const cls = {
    active:       'badge-active',
    on_leave:     'badge-on-leave',
    'closed-won': 'badge-closed-won',
    overdue:      'badge-overdue',
    pending:      'badge-pending',
    paid:         'badge-approved',
    open:         'badge-open',
    critical:     'badge-critical',
    high:         'badge-high',
    medium:       'badge-medium',
  }[value] || 'badge-low';
  return <span className={`badge ${cls}`}>{value}</span>;
}

export default function Dashboard() {
  const [stats,   setStats]   = useState(null);
  const [hr,      setHR]      = useState([]);
  const [sales,   setSales]   = useState([]);
  const [finance, setFinance] = useState([]);
  const [support, setSupport] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error,   setError]   = useState(null);
  const [tab,     setTab]     = useState('hr');

  useEffect(() => {
    Promise.all([
      getDashboardStats(),
      getDashboardHR(),
      getDashboardSales(),
      getDashboardFinance(),
      getDashboardSupport(),
    ])
      .then(([s, h, sa, fi, su]) => {
        setStats(s); setHR(h); setSales(sa); setFinance(fi); setSupport(su);
      })
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return (
    <div className="loading-state">
      <div className="spinner" />
      <span>Loading dashboard…</span>
    </div>
  );

  if (error) return (
    <div className="empty-state" style={{ padding: 60 }}>
      <div className="empty-state-icon">⚠️</div>
      <div className="empty-state-title">Backend Unreachable</div>
      <div className="empty-state-desc">
        Make sure the FastAPI server is running on <code>http://localhost:8000</code>
        <br /><br />
        <strong>Error:</strong> {error}
      </div>
    </div>
  );

  const { hr: hs, sales: ss, finance: fs, support: su } = stats;

  return (
    <div className="page">
      {/* KPI Cards */}
      <div className="kpi-grid">
        <KpiCard
          icon="👥" label="Total Employees" color="cyan"
          value={hs.total_employees}
          health={hs.health_score} alert={hs.alert}
          meta={[`✅ ${hs.active} Active`, `🏖 ${hs.on_leave} On Leave`]}
        />
        <KpiCard
          icon="💼" label="Closed Revenue" color="green"
          value={formatCurrency(ss.closed_revenue)}
          health={ss.health_score} alert={ss.alert}
          meta={[`🤝 ${ss.closed_won} Won`, `🔄 ${ss.in_negotiation} Negotiating`]}
        />
        <KpiCard
          icon="📄" label="Overdue Invoices" color={fs.alert ? 'red' : 'amber'}
          value={fs.overdue}
          health={fs.health_score} alert={fs.alert}
          meta={[`💰 ${formatCurrency(fs.overdue_amount)} at risk`, `⏳ ${fs.pending} Pending`]}
        />
        <KpiCard
          icon="🎫" label="Critical Tickets" color={su.alert ? 'red' : 'purple'}
          value={su.critical}
          health={su.health_score} alert={su.alert}
          meta={[`🔴 ${su.open} Open`, `🔥 ${su.high} High`]}
        />
      </div>

      {/* Department Tabs */}
      <div className="card" style={{ marginBottom: 0 }}>
        <div className="card-header" style={{ paddingBottom: 0 }}>
          <div className="section-title">Department Records</div>
          <div style={{ display: 'flex', gap: 8 }}>
            {['hr','sales','finance','support'].map(t => (
              <button
                key={t}
                className={`btn btn-sm ${tab === t ? 'btn-primary' : 'btn-ghost'}`}
                onClick={() => setTab(t)}
              >
                {t.toUpperCase()}
              </button>
            ))}
          </div>
        </div>

        <div className="card-body" style={{ padding: '0 0 4px' }}>
          <div style={{ overflowX: 'auto' }}>
            {tab === 'hr' && (
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Name</th><th>Role</th><th>Department</th>
                    <th>Status</th><th>Salary</th><th>Leave Days</th>
                  </tr>
                </thead>
                <tbody>
                  {hr.map(e => (
                    <tr key={e.id}>
                      <td style={{ color: 'var(--text-primary)', fontWeight: 500 }}>{e.name}</td>
                      <td>{e.role}</td>
                      <td>{e.department}</td>
                      <td><StatusBadge value={e.status} /></td>
                      <td style={{ fontFamily: 'monospace' }}>${e.salary.toLocaleString()}</td>
                      <td>{e.leave_days > 0 ? `${e.leave_days}d` : '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}

            {tab === 'sales' && (
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Client</th><th>Product</th><th>Stage</th>
                    <th>Value</th><th>Rep</th><th>Close Date</th>
                  </tr>
                </thead>
                <tbody>
                  {sales.map(d => (
                    <tr key={d.id}>
                      <td style={{ color: 'var(--text-primary)', fontWeight: 500 }}>{d.client_name}</td>
                      <td>{d.product_name}</td>
                      <td><StatusBadge value={d.stage} /></td>
                      <td style={{ fontFamily: 'monospace' }}>${d.amount.toLocaleString()}</td>
                      <td>{d.rep_name}</td>
                      <td>{d.close_date || '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}

            {tab === 'finance' && (
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Invoice</th><th>Client</th><th>Amount</th>
                    <th>Due Date</th><th>Status</th><th>Days Overdue</th>
                  </tr>
                </thead>
                <tbody>
                  {finance.map(i => (
                    <tr key={i.id}>
                      <td style={{ fontFamily: 'monospace', color: 'var(--accent)', fontSize: '12px' }}>{i.invoice_number}</td>
                      <td style={{ color: 'var(--text-primary)', fontWeight: 500 }}>{i.client_name}</td>
                      <td style={{ fontFamily: 'monospace' }}>${i.amount.toLocaleString()}</td>
                      <td>{i.due_date}</td>
                      <td><StatusBadge value={i.status} /></td>
                      <td>{i.days_overdue > 0 ? <span style={{ color: 'var(--danger)' }}>{i.days_overdue}d</span> : '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}

            {tab === 'support' && (
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Ticket</th><th>Customer</th><th>Issue</th>
                    <th>Priority</th><th>Status</th><th>Agent</th>
                  </tr>
                </thead>
                <tbody>
                  {support.map(t => (
                    <tr key={t.id}>
                      <td style={{ fontFamily: 'monospace', color: 'var(--accent)', fontSize: '12px' }}>{t.ticket_code}</td>
                      <td style={{ color: 'var(--text-primary)', fontWeight: 500 }}>{t.customer_name}</td>
                      <td style={{ maxWidth: 280, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}
                          title={t.issue_summary}>{t.issue_summary}</td>
                      <td><StatusBadge value={t.priority} /></td>
                      <td><StatusBadge value={t.status} /></td>
                      <td>{t.agent_name || '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
