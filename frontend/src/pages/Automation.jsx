import { useState, useEffect, useCallback } from 'react';
import {
  getRules, getPending, evaluateRules, approveAction, rejectAction
} from '../api.js';

const ACTION_ICONS = {
  DRAFT_PAYMENT_REMINDER: '💳',
  ALERT_DEPT_LEAD:        '📢',
  ESCALATE_HR_STAFFING:   '👥',
};

function RuleCard({ rule }) {
  return (
    <div className="rule-card">
      <div className="rule-header">
        <div className="rule-icon">
          {ACTION_ICONS[rule.action_type] || '⚡'}
        </div>
        <div style={{ flex: 1 }}>
          <div className="rule-name">{rule.name}</div>
          <span className="rule-trigger">{rule.trigger_event}</span>
        </div>
        <span className={`badge ${rule.is_active ? 'badge-approved' : 'badge-rejected'}`}>
          {rule.is_active ? 'Active' : 'Inactive'}
        </span>
      </div>

      <div className="rule-condition">{rule.condition_summary}</div>

      <div className="rule-footer">
        <span className="badge badge-auto">{rule.action_type}</span>
        {rule.requires_approval
          ? <span className="badge badge-pending">Requires Approval</span>
          : <span className="badge badge-approved">Auto Execute</span>}
      </div>
    </div>
  );
}

function ApprovalCard({ log, onApprove, onReject, actioning }) {
  const payload = log.action_payload;
  const isActioning = actioning === log.id;

  return (
    <div className="approval-card" style={{
      borderColor: 'rgba(255,176,32,0.2)',
      background: 'rgba(255,176,32,0.03)',
    }}>
      <div className="rule-header" style={{ marginBottom: 12 }}>
        <div className="rule-icon" style={{ background: 'var(--warning-dim)', borderColor: 'rgba(255,176,32,0.3)' }}>
          {ACTION_ICONS[log.action_type] || '⚡'}
        </div>
        <div style={{ flex: 1 }}>
          <div className="rule-name">{log.rule_name}</div>
          <span className="badge badge-pending" style={{ marginTop: 4 }}>Pending Approval</span>
        </div>
        <span className="badge badge-auto">{log.department}</span>
      </div>

      <div className="approval-trigger">{log.trigger_reason}</div>

      {payload && (
        <div className="approval-payload">
          {JSON.stringify(payload, null, 2)}
        </div>
      )}

      <div className="rule-footer" style={{ marginBottom: 14 }}>
        <span className="badge badge-auto">{log.action_type}</span>
        <span style={{ fontSize: 11, color: 'var(--text-muted)', marginLeft: 'auto' }}>
          {log.timestamp ? new Date(log.timestamp).toLocaleString() : '—'}
        </span>
      </div>

      <div className="approval-actions">
        <button
          className="btn btn-success"
          onClick={() => onApprove(log.id)}
          disabled={isActioning}
        >
          {isActioning ? '⏳' : '✓'} Approve
        </button>
        <button
          className="btn btn-danger"
          onClick={() => onReject(log.id)}
          disabled={isActioning}
        >
          {isActioning ? '⏳' : '✕'} Reject
        </button>
      </div>
    </div>
  );
}

export default function Automation({ onPendingChange }) {
  const [rules,     setRules]     = useState([]);
  const [pending,   setPending]   = useState([]);
  const [loading,   setLoading]   = useState(true);
  const [evalLoading, setEvalLoading] = useState(false);
  const [actioning, setActioning] = useState(null);
  const [evalResult, setEvalResult] = useState(null);
  const [tab,       setTab]       = useState('pending');

  const fetchData = useCallback(async () => {
    try {
      const [r, p] = await Promise.all([getRules(), getPending()]);
      setRules(r);
      setPending(p);
      onPendingChange?.(p.length);
    } finally {
      setLoading(false);
    }
  }, [onPendingChange]);

  useEffect(() => { fetchData(); }, [fetchData]);

  const handleEvaluate = async () => {
    setEvalLoading(true);
    setEvalResult(null);
    try {
      const res = await evaluateRules();
      setEvalResult(res);
      await fetchData();
    } catch (e) {
      setEvalResult({ error: e.message });
    } finally {
      setEvalLoading(false);
    }
  };

  const handleApprove = async (id) => {
    setActioning(id);
    try {
      await approveAction(id, 'Admin Manager');
      await fetchData();
    } catch (e) {
      alert('Approve failed: ' + e.message);
    } finally {
      setActioning(null);
    }
  };

  const handleReject = async (id) => {
    setActioning(id);
    try {
      await rejectAction(id, 'Admin Manager');
      await fetchData();
    } catch (e) {
      alert('Reject failed: ' + e.message);
    } finally {
      setActioning(null);
    }
  };

  if (loading) return (
    <div className="loading-state"><div className="spinner" /><span>Loading automation engine…</span></div>
  );

  return (
    <div className="page">
      {/* Eval Banner */}
      {evalResult && !evalResult.error && (
        <div className={`alert-banner ${evalResult.rules_triggered > 0 ? 'warning' : 'success'}`} style={{ marginBottom: 20 }}>
          {evalResult.rules_triggered > 0
            ? `⚡ ${evalResult.rules_triggered} rule(s) triggered — ${evalResult.logs_created} new action(s) queued`
            : '✅ All rules evaluated — no conditions triggered'}
        </div>
      )}
      {evalResult?.error && (
        <div className="alert-banner danger" style={{ marginBottom: 20 }}>
          ❌ Evaluation failed: {evalResult.error}
        </div>
      )}

      {/* Actions bar */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 24 }}>
        <div className="section-title">Automation Engine</div>
        <button
          className="btn btn-primary"
          onClick={handleEvaluate}
          disabled={evalLoading}
        >
          {evalLoading ? '⏳ Evaluating…' : '▶ Run Rule Evaluation'}
        </button>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 20 }}>
        {['pending', 'rules'].map(t => (
          <button
            key={t}
            className={`btn btn-sm ${tab === t ? 'btn-primary' : 'btn-ghost'}`}
            onClick={() => setTab(t)}
          >
            {t === 'pending'
              ? `⏳ Pending Approvals${pending.length > 0 ? ` (${pending.length})` : ''}`
              : '📋 Rule Definitions'}
          </button>
        ))}
      </div>

      {tab === 'pending' && (
        <>
          {pending.length === 0 ? (
            <div className="empty-state">
              <div className="empty-state-icon">✅</div>
              <div className="empty-state-title">No Pending Actions</div>
              <div className="empty-state-desc">
                Run the rule evaluator to check for triggered conditions.
                Approved and rejected actions are visible in the Audit Trail.
              </div>
            </div>
          ) : (
            <div className="automation-grid">
              {pending.map(log => (
                <ApprovalCard
                  key={log.id}
                  log={log}
                  onApprove={handleApprove}
                  onReject={handleReject}
                  actioning={actioning}
                />
              ))}
            </div>
          )}
        </>
      )}

      {tab === 'rules' && (
        <div className="automation-grid">
          {rules.map(rule => (
            <RuleCard key={rule.id} rule={rule} />
          ))}
        </div>
      )}
    </div>
  );
}
