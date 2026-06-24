import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import { getHealth, getHealthDetailed } from '../api';

const Health = () => {
  const navigate = useNavigate();
  const [health, setHealth] = useState(null);
  const [detailed, setDetailed] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [lastUpdated, setLastUpdated] = useState('');

  const loadHealth = async () => {
    try {
      const [h, d] = await Promise.all([getHealth(), getHealthDetailed()]);
      setHealth(h.data);
      setDetailed(d.data);
      setLastUpdated(new Date().toLocaleTimeString());
      setError('');
    } catch (err) {
      setError('⚠️ Could not connect to backend. Make sure server is running.');
    }
    setLoading(false);
  };

  useEffect(() => {
    loadHealth();
    const interval = setInterval(loadHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  const getStatusStyle = () => {
    if (!health) return {};
    if (health.status === 'operational') return { background: 'linear-gradient(135deg, #e8f8f5, #d0f0ea)', border: '2px solid #00A99D' };
    if (health.status === 'degraded') return { background: 'linear-gradient(135deg, #fff8e8, #ffefc0)', border: '2px solid #f59e0b' };
    return { background: 'linear-gradient(135deg, #fef0f0, #fdd8d8)', border: '2px solid #E8232A' };
  };

  const getStatusIcon = () => {
    if (!health) return '⏳';
    if (health.status === 'operational') return '✅';
    if (health.status === 'degraded') return '⚠️';
    return '🔴';
  };

  const getStatusTitle = () => {
    if (!health) return 'Loading...';
    if (health.status === 'operational') return 'All Systems Operational';
    if (health.status === 'degraded') return 'Degraded Performance';
    return 'Active Incident';
  };

  return (
    <div style={{ minHeight: '100vh', background: '#f5f5f5' }}>
      <Header showLogout={true} />

      <div style={{ maxWidth: '960px', margin: '0 auto', padding: '40px 20px' }}>

        {/* Nav */}
        <div style={{ display: 'flex', gap: '10px', marginBottom: '32px' }}>
          {[
            { label: '🧠 Home', path: '/intelligence' },
            { label: '🟢 Health', path: '/health', active: true },
            { label: '📋 Reports', path: '/reports' },
            { label: '🔥 Heatmap', path: '/heatmap' }
          ].map(n => (
            <button key={n.path} onClick={() => navigate(n.path)} style={{
              padding: '8px 18px', borderRadius: '8px', fontSize: '14px', fontWeight: 600,
              border: `2px solid ${n.active ? '#E8232A' : '#e5e7eb'}`,
              background: n.active ? '#E8232A' : 'white',
              color: n.active ? 'white' : '#888', cursor: 'pointer'
            }}>{n.label}</button>
          ))}
        </div>

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
          <h1 style={{ fontSize: '28px', fontWeight: 800 }}>System Health</h1>
          <span style={{ fontSize: '13px', color: '#888' }}>Last updated: {lastUpdated}</span>
        </div>
        <p style={{ color: '#666', marginBottom: '36px' }}>Live status of Bustler's support operations — updated in real time</p>

        {loading && <div style={{ textAlign: 'center', padding: '60px', color: '#999' }}>Loading system status...</div>}
        {error && <div style={{ textAlign: 'center', padding: '60px', color: '#E8232A' }}>{error}</div>}

        {health && (
          <>
            {/* Status Card */}
            <div style={{
              ...getStatusStyle(), borderRadius: '16px', padding: '28px 32px',
              marginBottom: '32px', display: 'flex', alignItems: 'center', gap: '20px'
            }}>
              <div style={{ fontSize: '44px' }}>{getStatusIcon()}</div>
              <div>
                <h2 style={{ fontSize: '22px', fontWeight: 700, marginBottom: '6px' }}>{getStatusTitle()}</h2>
                <p style={{ color: '#555', fontSize: '14px' }}>{health.message}</p>
              </div>
            </div>

            {/* Stats */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '20px', marginBottom: '32px' }}>
              {[
                { label: 'Open Tickets', value: health.open_tickets, color: '#00A99D' },
                { label: 'Critical Issues', value: health.critical_tickets, color: '#E8232A' },
                { label: 'Resolved Today', value: health.resolved_today, color: '#22c55e' }
              ].map(stat => (
                <div key={stat.label} style={{
                  background: 'white', border: '1px solid #e5e7eb', borderRadius: '14px',
                  padding: '24px', textAlign: 'center', boxShadow: '0 2px 8px rgba(0,0,0,0.05)'
                }}>
                  <div style={{ fontSize: '42px', fontWeight: 800, color: stat.color, marginBottom: '6px' }}>{stat.value}</div>
                  <div style={{ color: '#666', fontSize: '14px', fontWeight: 500 }}>{stat.label}</div>
                </div>
              ))}
            </div>

            {/* Category Breakdown */}
            {detailed && (
              <>
                <h2 style={{ fontSize: '18px', fontWeight: 700, marginBottom: '16px' }}>Category Breakdown</h2>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '16px', marginBottom: '32px' }}>
                  {Object.entries(detailed.breakdown).map(([cat, data]) => (
                    <div key={cat} style={{
                      background: 'white', border: '1px solid #e5e7eb', borderRadius: '12px',
                      padding: '20px', boxShadow: '0 2px 8px rgba(0,0,0,0.05)'
                    }}>
                      <h4 style={{ fontSize: '13px', fontWeight: 700, color: '#888', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '14px' }}>
                        {cat.replace('_', ' ')}
                      </h4>
                      {[
                        { label: 'Open', value: data.open, color: '#00A99D', bg: '#e0f7f5' },
                        { label: 'Critical', value: data.critical, color: '#E8232A', bg: '#fde8e8' },
                        { label: 'Resolved', value: data.resolved, color: '#16a34a', bg: '#dcfce7' }
                      ].map(item => (
                        <div key={item.label} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '8px 0', borderBottom: '1px solid #f3f4f6' }}>
                          <span style={{ fontSize: '14px', color: '#444' }}>{item.label}</span>
                          <span style={{ padding: '2px 10px', borderRadius: '10px', fontSize: '12px', fontWeight: 700, background: item.bg, color: item.color }}>{item.value}</span>
                        </div>
                      ))}
                    </div>
                  ))}
                </div>
              </>
            )}

            <div style={{ textAlign: 'center' }}>
              <button onClick={loadHealth} style={{
                background: '#E8232A', color: 'white', border: 'none',
                padding: '12px 28px', borderRadius: '10px', fontWeight: 700,
                fontSize: '14px', cursor: 'pointer'
              }}>↻ Refresh Status</button>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default Health;