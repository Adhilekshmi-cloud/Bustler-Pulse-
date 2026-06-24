import axios from 'axios';

const API_BASE = 'https://bustler-pulse.onrender.com';

const api = axios.create({
  baseURL: API_BASE,
});

// ── Auth ─────────────────────────────────────────────
export const login = (username, password) =>
  api.post('/auth/login', { username, password });

export const register = (username, email, password, role) =>
  api.post('/auth/register', { username, email, password, role });

// ── Health ───────────────────────────────────────────
export const getHealth = () => api.get('/health/');
export const getHealthDetailed = () => api.get('/health/detailed');

// ── Reports ──────────────────────────────────────────
export const getReportsSummary = () => api.get('/reports/summary');
export const getReportsPatterns = () => api.get('/reports/');
export const getDetailedReports = () => api.get('/reports/detailed');
export const getHeatmap = () => api.get('/reports/heatmap');

// ── Agents ───────────────────────────────────────────
export const getAgents = () => api.get('/agents/');
export const getLeaderboard = () => api.get('/agents/leaderboard/top');

export default api;