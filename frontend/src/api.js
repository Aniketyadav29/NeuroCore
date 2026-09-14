// Central API client for NeuroCore backend
// In dev, Vite proxies /api/* → http://localhost:8000 (see vite.config.js)
// In production, set VITE_API_URL to your deployed backend URL
const BASE = import.meta.env.VITE_API_URL || '';


async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `API error ${res.status}`);
  }
  return res.json();
}

// Dashboard
export const getDashboardStats = () => request('/api/dashboard/stats');
export const getDashboardHR      = () => request('/api/dashboard/hr');
export const getDashboardSales   = () => request('/api/dashboard/sales');
export const getDashboardFinance = () => request('/api/dashboard/finance');
export const getDashboardSupport = () => request('/api/dashboard/support');

// Chat / RAG
export const sendChat    = (query, n_results = 10) =>
  request('/api/chat', { method: 'POST', body: JSON.stringify({ query, n_results }) });
export const reindex     = () => request('/api/reindex', { method: 'POST' });
export const indexStatus = () => request('/api/index/status');

// Automation
export const evaluateRules  = () => request('/api/automation/evaluate', { method: 'POST' });
export const getRules        = () => request('/api/automation/rules');
export const getPending      = () => request('/api/automation/pending');
export const approveAction   = (id, reviewed_by) =>
  request(`/api/automation/approve/${id}`, { method: 'POST', body: JSON.stringify({ reviewed_by }) });
export const rejectAction    = (id, reviewed_by) =>
  request(`/api/automation/reject/${id}`, { method: 'POST', body: JSON.stringify({ reviewed_by }) });
export const getAuditTrail   = (params = {}) => {
  const qs = new URLSearchParams(
    Object.fromEntries(Object.entries(params).filter(([, v]) => v))
  ).toString();
  return request(`/api/automation/audit${qs ? '?' + qs : ''}`);
};
