import React from 'react';
import Header from '../components/Header';

const Landing = () => {

  const pillars = [
    {
      num: 'Pillar 1',
      icon: '🎫',
      title: 'User Layer',
      owner: 'Built by Anjali P Remesh',
      college: 'TKM College of Engineering',
      desc: 'The user-facing support experience. Users raise tickets, file disputes, get instant auto-replies and track resolution.',
      features: ['Smart ticket form with AI suggestions', 'Structured dispute center', 'FAQ help center', 'Resolution survey', 'Real Bustler bug data'],
      btn: 'Open User Layer →',
      link: 'https://bustler-frontend.vercel.app',
      color: '#E8232A',
      bg: '#fde8e8'
    },
    {
      num: 'Pillar 2',
      icon: '⚙️',
      title: 'Ops Layer',
      owner: 'Built by Ambadi Sajan',
      college: 'Providence College of Engineering',
      desc: 'The internal operations dashboard. Ops agents view, filter and resolve tickets. Smart routing assigns the right agent automatically.',
      features: ['Smart triage engine', 'Agent dashboard with live stats', 'Smart routing by specialty', 'Agent profile tracker', 'Auto-refresh every 30 seconds'],
      btn: 'Open Ops Dashboard →',
      link: 'https://bustler-pulse-six.vercel.app',
      color: '#00A99D',
      bg: '#e0f7f5'
    },
    {
      num: 'Pillar 3',
      icon: '🧠',
      title: 'Intelligence Layer',
      owner: 'Built by Adhilekshmi R',
      college: 'Providence College of Engineering',
      desc: 'The analytics brain. Product team sees patterns, heatmaps and system health. Every resolved ticket becomes structured knowledge.',
      features: ['System health — live status page', 'Product feedback reports', 'Issue heatmap by week', 'Micro-report auto-generator', 'Agent leaderboard'],
      btn: 'Open Intelligence →',
      link: 'https://bustler-pulse.vercel.app/login',
      color: '#6366f1',
      bg: '#ede9fe'
    }
  ];

  const stats = [
    { num: '3', label: 'Pillars' },
    { num: '33', label: 'API Endpoints' },
    { num: '6', label: 'Frontend Pages' },
    { num: '100%', label: 'Live & Connected' }
  ];

  const flow = [
    { role: 'User', desc: 'Submits ticket via form' },
    { role: 'Auto Triage', desc: 'Classifies + scores urgency' },
    { role: 'Ops Agent', desc: 'Resolves in dashboard' },
    { role: 'Auto Generate', desc: 'Report + badge created' },
    { role: 'Product Team', desc: 'Sees patterns + insights' }
  ];

  return (
    <div style={{ minHeight: '100vh', background: '#f5f5f5' }}>
      <Header />

      {/* Hero */}
      <div style={{ textAlign: 'center', padding: '60px 20px 40px' }}>
        <div style={{
          display: 'inline-block', background: '#fde8e8', color: '#E8232A',
          padding: '6px 18px', borderRadius: '20px', fontSize: '13px',
          fontWeight: 700, marginBottom: '20px'
        }}>🚀 Live System</div>
        <h1 style={{ fontSize: '42px', fontWeight: 800, marginBottom: '12px' }}>
          Bustler <span style={{ color: '#E8232A' }}>Pulse</span>
        </h1>
        <p style={{ color: '#666', fontSize: '16px', maxWidth: '560px', margin: '0 auto 16px', lineHeight: 1.6 }}>
          An intelligent support & operations framework built for Bustler — connecting users, ops agents, and the product team in one unified system.
        </p>
        <p style={{ color: '#aaa', fontSize: '13px', marginBottom: '48px' }}>
          Built by Adhilekshmi R · Ambadi Sajan · Anjali P Remesh
        </p>

        {/* Stats */}
        <div style={{ display: 'flex', justifyContent: 'center', gap: '40px', flexWrap: 'wrap', marginBottom: '56px' }}>
          {stats.map(s => (
            <div key={s.label} style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '32px', fontWeight: 800, color: '#E8232A' }}>{s.num}</div>
              <div style={{ fontSize: '12px', color: '#888', fontWeight: 500, marginTop: '2px' }}>{s.label}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Pillars */}
      <div style={{ maxWidth: '1100px', margin: '0 auto', padding: '0 20px 60px' }}>
        <div style={{ textAlign: 'center', fontSize: '13px', fontWeight: 700, color: '#888', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: '28px' }}>
          Three Pillars — One System
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '24px', marginBottom: '40px' }}>
          {pillars.map(p => (
            <div key={p.num} style={{
              background: 'white', border: '2px solid #e5e7eb', borderRadius: '20px',
              padding: '32px 24px', display: 'flex', flexDirection: 'column',
              boxShadow: '0 2px 12px rgba(0,0,0,0.06)'
            }}>
              <span style={{
                display: 'inline-block', background: p.bg, color: p.color,
                padding: '4px 12px', borderRadius: '10px', fontSize: '11px',
                fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em',
                marginBottom: '16px', alignSelf: 'flex-start'
              }}>{p.num}</span>
              <div style={{ fontSize: '48px', marginBottom: '16px' }}>{p.icon}</div>
              <div style={{ fontSize: '20px', fontWeight: 800, marginBottom: '6px' }}>{p.title}</div>
              <div style={{ fontSize: '13px', fontWeight: 600, color: p.color, marginBottom: '4px' }}>{p.owner}</div>
              <div style={{ fontSize: '11px', color: '#aaa', marginBottom: '14px' }}>{p.college}</div>
              <div style={{ fontSize: '13px', color: '#666', lineHeight: 1.6, marginBottom: '20px', flex: 1 }}>{p.desc}</div>
              <div style={{ marginBottom: '24px' }}>
                {p.features.map(f => (
                  <div key={f} style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px', color: '#555', padding: '4px 0' }}>
                    <span style={{ color: p.color, fontWeight: 700 }}>✓</span> {f}
                  </div>
                ))}
              </div>
              <a href={p.link} target="_blank" rel="noreferrer" style={{
                display: 'block', padding: '12px', borderRadius: '10px',
                fontSize: '14px', fontWeight: 700, background: p.color,
                color: 'white', textAlign: 'center', textDecoration: 'none'
              }}>{p.btn}</a>
            </div>
          ))}
        </div>

        {/* Flow */}
        <div style={{
          background: 'white', border: '1px solid #e5e7eb', borderRadius: '16px',
          padding: '32px', boxShadow: '0 2px 12px rgba(0,0,0,0.06)', marginBottom: '28px'
        }}>
          <div style={{ fontSize: '18px', fontWeight: 700, textAlign: 'center', marginBottom: '24px' }}>
            🔄 How the system works — end to end
          </div>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', flexWrap: 'wrap', gap: '8px' }}>
            {flow.map((f, i) => (
              <React.Fragment key={f.role}>
                <div style={{
                  background: '#f9fafb', border: '1px solid #e5e7eb', borderRadius: '10px',
                  padding: '12px 16px', fontSize: '13px', textAlign: 'center', minWidth: '140px'
                }}>
                  <strong style={{ display: 'block', fontSize: '12px', color: '#888', marginBottom: '4px', textTransform: 'uppercase', letterSpacing: '0.04em' }}>{f.role}</strong>
                  {f.desc}
                </div>
                {i < flow.length - 1 && <span style={{ fontSize: '20px', color: '#ccc' }}>→</span>}
              </React.Fragment>
            ))}
          </div>
        </div>

        {/* API */}
        <div style={{ background: '#1a1a2e', borderRadius: '16px', padding: '28px 32px', marginBottom: '28px' }}>
          <div style={{ color: 'white', fontSize: '16px', fontWeight: 700, marginBottom: '20px' }}>
            🔗 Shared Backend — All pillars connect here
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px' }}>
            {[
              { label: 'Live API', url: 'https://bustler-pulse.onrender.com' },
              { label: 'API Docs', url: 'https://bustler-pulse.onrender.com/docs' },
              { label: 'GitHub', url: 'github.com/Adhilekshmi-cloud/Bustler-Pulse-' },
              { label: 'Database', url: 'PostgreSQL on Render — permanent storage' }
            ].map(item => (
              <div key={item.label} style={{ background: 'rgba(255,255,255,0.08)', borderRadius: '10px', padding: '14px 16px' }}>
                <div style={{ fontSize: '11px', color: '#888', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '6px' }}>{item.label}</div>
                <div style={{ fontSize: '13px', color: '#00A99D', fontFamily: 'monospace', wordBreak: 'break-all' }}>{item.url}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Team */}
        <div style={{ textAlign: 'center', fontSize: '13px', fontWeight: 700, color: '#888', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: '20px' }}>
          The Team
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
          {[
            { name: 'Anjali P Remesh', college: 'TKM College of Engineering', role: 'Pillar 1 — User Layer', color: '#E8232A', bg: '#fde8e8' },
            { name: 'Ambadi Sajan', college: 'Providence College of Engineering', role: 'Pillar 2 — Ops Layer', color: '#00A99D', bg: '#e0f7f5' },
            { name: 'Adhilekshmi R', college: 'Providence College of Engineering', role: 'Pillar 3 — Intelligence', color: '#6366f1', bg: '#ede9fe' }
          ].map(member => (
            <div key={member.name} style={{
              background: 'white', border: '1px solid #e5e7eb', borderRadius: '14px',
              padding: '24px', textAlign: 'center', boxShadow: '0 2px 8px rgba(0,0,0,0.05)'
            }}>
              <div style={{
                width: '56px', height: '56px', borderRadius: '50%', background: member.color,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontSize: '22px', fontWeight: 800, color: 'white', margin: '0 auto 14px'
              }}>A</div>
              <div style={{ fontSize: '15px', fontWeight: 700, marginBottom: '4px' }}>{member.name}</div>
              <div style={{ fontSize: '12px', color: '#888', marginBottom: '12px' }}>{member.college}</div>
              <span style={{
                display: 'inline-block', padding: '3px 12px', borderRadius: '10px',
                fontSize: '11px', fontWeight: 600, background: member.bg, color: member.color
              }}>{member.role}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Footer */}
      <div style={{
        background: 'white', borderTop: '1px solid #e5e7eb',
        padding: '24px 40px', textAlign: 'center', color: '#888', fontSize: '13px'
      }}>
        <strong style={{ color: '#1a1a1a' }}>Bustler Pulse</strong> · Bustler Summer Internship 2026 · Providence College of Engineering · CSE Artificial Intelligence
      </div>
    </div>
  );
};

export default Landing;