import { useState, useEffect, useCallback } from 'react';
import { getAuditTrail } from '../api.js';

const STATUS_META = {
  pending:       { cls: 'pending',  icon: '⏳', label: 'Pending'       },
  approved:      { cls: 'approved', icon: '✅', label: 'Approved'      },
  rejected:      { cls: 'rejected', icon: '❌', label: 'Rejected'      },
  auto_executed: { cls: 'auto',     icon: '⚡', label: 'Auto Executed' },
};

const ACTION_ICONS = {
  DRAFT_PAYMENT_REMINDER: '💳',
  ALERT_DEPT_LEAD:        '📢',
  ESCALATE_HR_STAFFING:   '👥',
};

function AuditEntry({ log, isLast }) {
  const sm = STATUS_META[log.status] || { cls: 'pending', icon: '?', label: log.status };

  return (
    <div className="audit-entry">
      <div className="audit-timeline-line">
        <div className={`audit-dot ${sm.cls}`} />
        {!isLast && <div className="audit-line" />}
      </div>

      <div className="audit-content">
        <div className="audit-header">
          <span style={{ fontSize: 18 }}>{ACTION_ICONS[log.action_type] || '⚡'}</span>
          <span className="audit-rule-name">{log.rule_name || 'Manual Action'}</span>
          <span className={`badge badge-${sm.cls}`}>{sm.icon} {sm.label}</span>
          {log.department && <span className="audit-dept">{log.department}</span>}
        </div>

        <div className="audit-reason">{log.trigger_reason}</div>

        <div className="audit-footer">
          <span>🕐 {log.timestamp ? new Date(log.timestamp).toLocaleString() : '—'}</span>
          {log.reviewed_by && (
            <>
              <span>·</span>
              <span>👤 {log.reviewed_by}</span>
            </>
          )}
          {log.reviewed_at && (
            <>
              <span>·</span>
              <span>Reviewed: {new Date(log.reviewed_at).toLocaleString()}</span>
            </>
          )}
          <span style={{ marginLeft: 'auto', fontFamily: 'monospace', fontSize: 10, color: 'var(--accent)' }}>
            {log.action_type}
          </span>
        </div>
      </div>
    </div>
  );
}

export default function Audit() {
  const [logs,    setLogs]    = useState([]);
  const [loading, setLoading] = useState(true);
  const [deptFilter,   setDeptFilter]   = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [error,   setError]   = useState(null);

  const fetchLogs = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getAuditTrail({ department: deptFilter, status: statusFilter });
      setLogs(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [deptFilter, statusFilter]);

  useEffect(() => { fetchLogs(); }, [fetchLogs]);

  const stats = {
    pending:  logs.filter(l => l.status === 'pending').length,
    approved: logs.filter(l => l.status === 'approved').length,
    rejected: logs.filter(l => l.status === 'rejected').length,
    auto:     logs.filter(l => l.status === 'auto_executed').length,
  };

  return (
    <div className="page">
      {/* Stats row */}
      <div style={{ display: 'flex', gap: 12, marginBottom: 24, flexWrap: 'wrap' }}>
        {[
          { label: 'Pending',       count: stats.pending,  cls: 'badge-pending'  },
          { label: 'Approved',      count: stats.approved, cls: 'badge-approved' },
          { label: 'Rejected',      count: stats.rejected, cls: 'badge-rejected' },
          { label: 'Auto Executed', count: stats.auto,     cls: 'badge-auto'     },
        ].map(({ label, count, cls }) => (
          <div key={label} style={{
            background: 'var(--bg-card)',
            border: '1px solid var(--border)',
            borderRadius: 'var(--radius-md)',
            padding: '12px 20px',
            display: 'flex', flexDirection: 'column', gap: 4,
            minWidth: 120,
          }}>
            <span style={{ fontSize: 22, fontWeight: 800, color: 'var(--text-primary)' }}>{count}</span>
            <span className={`badge ${cls}`}>{label}</span>
          </div>
        ))}
      </div>

      {/* Card */}
      <div className="card">
        <div className="card-header">
          <div className="section-title">Audit Timeline</div>
          <div className="filters-row">
            <select
              className="filter-select"
              value={deptFilter}
              onChange={e => setDeptFilter(e.target.value)}
            >
              <option value="">All Departments</option>
              <option value="HR">HR</option>
              <option value="Sales">Sales</option>
              <option value="Finance">Finance</option>
              <option value="Support">Support</option>
            </select>
            <select
              className="filter-select"
              value={statusFilter}
              onChange={e => setStatusFilter(e.target.value)}
            >
              <option value="">All Statuses</option>
              <option value="pending">Pending</option>
              <option value="approved">Approved</option>
              <option value="rejected">Rejected</option>
              <option value="auto_executed">Auto Executed</option>
            </select>
            <button className="btn btn-ghost btn-sm" onClick={fetchLogs}>
              🔄 Refresh
            </button>
          </div>
        </div>

        <div className="card-body">
          {loading ? (
            <div className="loading-state"><div className="spinner" /><span>Loading audit trail…</span></div>
          ) : error ? (
            <div className="empty-state">
              <div className="empty-state-icon">⚠️</div>
              <div className="empty-state-title">Failed to load</div>
              <div className="empty-state-desc">{error}</div>
            </div>
          ) : logs.length === 0 ? (
            <div className="empty-state">
              <div className="empty-state-icon">📋</div>
              <div className="empty-state-title">No Audit Entries</div>
              <div className="empty-state-desc">
                Run the automation rule evaluator to generate audit entries.
                All automation actions are permanently recorded here.
              </div>
            </div>
          ) : (
            <div className="audit-timeline">
              {logs.map((log, i) => (
                <AuditEntry key={log.id} log={log} isLast={i === logs.length - 1} />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
