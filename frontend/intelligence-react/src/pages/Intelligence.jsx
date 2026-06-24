import React from 'react';
import { useNavigate } from 'react-router-dom';
import Header from '../components/Header';

const Intelligence = () => {
  const navigate = useNavigate();

  const pages = [
    { icon: '🟢', title: 'System Health', desc: 'Live status of support operations', path: '/health' },
    { icon: '📋', title: 'Reports', desc: 'Product feedback & patterns', path: '/reports' },
    { icon: '🔥', title: 'Heatmap', desc: 'Issue spikes by week', path: '/heatmap' }
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <Header showLogout={true} />
      <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '60px 20px' }}>
        <div style={{ textAlign: 'center', maxWidth: '700px' }}>

          <div style={{
            display: 'inline-block', background: '#fde8e8', color: '#E8232A',
            padding: '6px 16px', borderRadius: '20px', fontSize: '13px',
            fontWeight: 700, marginBottom: '20px'
          }}>🧠 Intelligence Layer</div>

          <h1 style={{ fontSize: '36px', fontWeight: 800, marginBottom: '10px' }}>
            Bustler <span style={{ color: '#E8232A' }}>Pulse</span>
          </h1>

          <p style={{ color: '#666', fontSize: '16px', marginBottom: '48px' }}>
            Built by Adhilekshmi R · Providence College of Engineering
          </p>

          <div style={{ display: 'flex', gap: '20px', justifyContent: 'center', flexWrap: 'wrap' }}>
            {pages.map(p => (
              <div key={p.path} onClick={() => navigate(p.path)}
                style={{
                  background: 'white', border: '2px solid #e5e7eb', borderRadius: '16px',
                  padding: '32px 24px', width: '190px', cursor: 'pointer',
                  transition: 'all 0.2s', boxShadow: '0 2px 8px rgba(0,0,0,0.05)'
                }}
                onMouseEnter={e => {
                  e.currentTarget.style.borderColor = '#E8232A';
                  e.currentTarget.style.transform = 'translateY(-4px)';
                }}
                onMouseLeave={e => {
                  e.currentTarget.style.borderColor = '#e5e7eb';
                  e.currentTarget.style.transform = 'translateY(0)';
                }}>
                <div style={{ fontSize: '36px', marginBottom: '14px' }}>{p.icon}</div>
                <div style={{ fontSize: '15px', fontWeight: 700, marginBottom: '6px' }}>{p.title}</div>
                <div style={{ fontSize: '12px', color: '#888' }}>{p.desc}</div>
              </div>
            ))}
          </div>

          <div style={{
            display: 'inline-block', background: '#e0f7f5', color: '#00A99D',
            padding: '6px 16px', borderRadius: '20px', fontSize: '12px',
            fontWeight: 600, marginTop: '32px'
          }}>● API: https://bustler-pulse.onrender.com</div>

        </div>
      </div>
      <div style={{ textAlign: 'center', padding: '20px', color: '#aaa', fontSize: '13px' }}>
        Bustler Pulse · Bustler Summer Internship 2026
      </div>
    </div>
  );
};

export default Intelligence;