import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import { getReportsSummary, getReportsPatterns, getDetailedReports } from '../api';

const Reports = () => {
  const navigate = useNavigate();
  const [tab, setTab] = useState('patterns');
  const [summary, setSummary] = useState(null);
  const [patterns, setPatterns] = useState([]);
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const load = async () => {
      try {
        const [s, p, r] = await Promise.all([
          getReportsSummary(),
          getReportsPatterns(),
          getDetailedReports()
        ]);
        setSummary(s.data);
        setPatterns(p.data.patterns || []);
        setReports(r.data.reports || []);
      } catch {
        setError('⚠️ Could not connect to backend.');
      }
      setLoading(false);
    };
    load();
  }, []);

  const maxCount = patterns.length > 0 ? Math.max(...patterns.map(p => p.total_issues)) : 1;

  const getPriorityStyle = (priority) => {
    if (priority?.includes('High')) return { background: '#fde8e8', color: '#E8232A', border: '1px solid #E8232A' };
    if (priority?.includes('Medium')) return { background: '#fff8e8', color: '#d97706', border: '1px solid #f59e0b' };
    return { background: '#dcfce7', color: '#16a34a', border: '1px solid #22c55e' };
  };

  const navItems = [
    { label: '🧠 Home', path: '/intelligence' },
    { label: '🟢 Health', path: '/health' },
    { label: '📋 Reports', path: '/reports', active: true },
    { label: '🔥 Heatmap', path: '/heatmap' }
  ];

  return (
    <div style={{ minHeight: '100vh', background: '#f5f5f5' }}>
      <Header showLogout={true} />

      <div style={{ maxWidth: '1000px', margin: '0 auto', padding: '40px 20px' }}>

        {/* Nav */}
        <div style={{ display: 'flex', gap: '10px', marginBottom: '32px' }}>
          {navItems.map(n => (
            <button key={n.path} onClick={() => navigate(n.path)} style={{
              padding: '8px 18px', borderRadius: '8px', fontSize: '14px', fontWeight: 600,
              border: `2px solid ${n.active ? '#E8232A' : '#e5e7eb'}`,
              background: n.active ? '#E8232A' : 'white',
              color: n.active ? 'white' : '#888', cursor: 'pointer'
            }}>{n.label}</button>
          ))}
        </div>

        <h1 style={{ fontSize: '28px', fontWeight: 800, marginBottom: '6px' }}>Product Feedback Reports</h1>
        <p style={{ color: '#666', marginBottom: '36px' }}>Patterns from resolved tickets — helping the product team fix root causes</p>

        {loading && <div style={{ textAlign: 'center', padding: '60px', color: '#999' }}>Loading reports...</div>}
        {error && <div style={{ textAlign: 'center', padding: '60px', color: '#E8232A' }}>{error}</div>}

        {summary && (
          <>
            {/* Summary Cards */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px', marginBottom: '36px' }}>
              {[
                { label: 'Total Tickets', value: summary.total_tickets, color: '#00A99D' },
                { label: 'Critical Issues', value: summary.critical_tickets, color: '#E8232A' },
                { label: 'Resolved', value: summary.resolved_tickets, color: '#16a34a' },
                { label: 'Avg CSAT', value: summary.avg_csat ?? 'N/A', color: '#f59e0b' }
              ].map(s => (
                <div key={s.label} style={{
                  background: 'white', border: '1px solid #e5e7eb', borderRadius: '14px',
                  padding: '20px', textAlign: 'center', boxShadow: '0 2px 8px rgba(0,0,0,0.05)'
                }}>
                  <div style={{ fontSize: '36px', fontWeight: 800, color: s.color, marginBottom: '6px' }}>{s.value}</div>
                  <div style={{ color: '#666', fontSize: '13px', fontWeight: 500 }}>{s.label}</div>
                </div>
              ))}
            </div>

            {/* Tabs */}
            <div style={{ display: 'flex', gap: '8px', marginBottom: '24px' }}>
              {[
                { key: 'patterns', label: '📊 Issue Patterns' },
                { key: 'reports', label: '📋 All Reports' }
              ].map(t => (
                <button key={t.key} onClick={() => setTab(t.key)} style={{
                  padding: '10px 22px', borderRadius: '10px', fontSize: '14px', fontWeight: 600,
                  border: `2px solid ${tab === t.key ? '#E8232A' : '#e5e7eb'}`,
                  background: tab === t.key ? '#E8232A' : 'white',
                  color: tab === t.key ? 'white' : '#888', cursor: 'pointer'
                }}>{t.label}</button>
              ))}
            </div>

            {/* Patterns Tab */}
            {tab === 'patterns' && (
              <div>
                <h2 style={{ fontSize: '18px', fontWeight: 700, marginBottom: '16px' }}>Most Common Issues — Ranked by Frequency</h2>
                {patterns.length === 0 ? (
                  <div style={{ textAlign: 'center', padding: '40px', color: '#999' }}>
                    No patterns yet — resolve some tickets to see insights!
                  </div>
                ) : patterns.map((p, i) => (
                  <div key={p.category} style={{
                    background: 'white', border: '1px solid #e5e7eb', borderRadius: '12px',
                    padding: '20px 24px', marginBottom: '14px', display: 'flex',
                    alignItems: 'center', gap: '20px', boxShadow: '0 2px 8px rgba(0,0,0,0.05)'
                  }}>
                    <div style={{ fontSize: '26px', fontWeight: 800, color: '#ccc', width: '40px', textAlign: 'center' }}>#{i + 1}</div>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontSize: '16px', fontWeight: 700, textTransform: 'capitalize', marginBottom: '4px' }}>
                        {p.category.replace('_', ' ')}
                      </div>
                      <div style={{ color: '#888', fontSize: '13px' }}>
                        {p.total_issues} issue{p.total_issues !== 1 ? 's' : ''} reported · Avg CSAT: {p.avg_csat ?? 'N/A'}
                      </div>
                    </div>
                    <div style={{ flex: 1, background: '#f3f4f6', borderRadius: '4px', height: '8px', margin: '0 16px' }}>
                      <div style={{ height: '8px', borderRadius: '4px', background: '#00A99D', width: `${(p.total_issues / maxCount) * 100}%` }} />
                    </div>
                    <span style={{
                      padding: '6px 14px', borderRadius: '20px', fontSize: '12px', fontWeight: 700,
                      whiteSpace: 'nowrap', ...getPriorityStyle(p.priority)
                    }}>{p.priority?.split('—')[0].trim()}</span>
                  </div>
                ))}
              </div>
            )}

            {/* Reports Tab */}
            {tab === 'reports' && (
              <div>
                <h2 style={{ fontSize: '18px', fontWeight: 700, marginBottom: '16px' }}>All Micro-Reports</h2>
                {reports.length === 0 ? (
                  <div style={{ textAlign: 'center', padding: '40px', color: '#999' }}>
                    No reports yet — resolve some tickets first!
                  </div>
                ) : (
                  <div style={{ background: 'white', borderRadius: '12px', overflow: 'hidden', boxShadow: '0 2px 8px rgba(0,0,0,0.05)' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                      <thead>
                        <tr>
                          {['ID', 'Category', 'What Broke & Why', 'How Fixed', 'Resolved By', 'Date', 'CSAT'].map(h => (
                            <th key={h} style={{
                              background: '#E8232A', padding: '14px 16px', textAlign: 'left',
                              fontSize: '13px', color: 'white', fontWeight: 700,
                              textTransform: 'uppercase', letterSpacing: '0.04em'
                            }}>{h}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {reports.map(r => (
                          <tr key={r.report_id} style={{ borderBottom: '1px solid #f3f4f6' }}>
                            <td style={{ padding: '14px 16px', fontSize: '14px' }}>#{r.report_id}</td>
                            <td style={{ padding: '14px 16px' }}>
                              <span style={{ padding: '3px 10px', borderRadius: '10px', fontSize: '12px', fontWeight: 700, background: '#e0f7f5', color: '#00A99D', textTransform: 'capitalize' }}>
                                {r.category}
                              </span>
                            </td>
                            <td style={{ padding: '14px 16px', fontSize: '14px', verticalAlign: 'top' }}>
                              <div style={{ fontWeight: 600, marginBottom: '4px' }}>{r.what_broke}</div>
                              <div style={{ color: '#888', fontSize: '12px' }}>Why: {r.why_it_happened ?? '—'}</div>
                              <div style={{ color: '#aaa', fontSize: '11px', marginTop: '2px' }}>User: {r.user_id}</div>
                            </td>
                            <td style={{ padding: '14px 16px', fontSize: '14px', color: '#444' }}>{r.how_fixed ?? '—'}</td>
                            <td style={{ padding: '14px 16px', fontSize: '14px', color: '#00A99D', fontWeight: 700 }}>{r.resolved_by}</td>
                            <td style={{ padding: '14px 16px', fontSize: '12px', color: '#888' }}>
                              {new Date(r.resolved_at).toLocaleDateString()}<br />
                              {new Date(r.resolved_at).toLocaleTimeString()}
                            </td>
                            <td style={{ padding: '14px 16px', color: '#f59e0b' }}>
                              {r.csat_score ? '★'.repeat(r.csat_score) + '☆'.repeat(5 - r.csat_score) : 'N/A'}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default Reports;