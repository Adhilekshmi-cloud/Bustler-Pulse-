import React, { useState, useEffect } from 'react';
import Sidebar from '../components/Sidebar';
import { useSidebar } from '../context/SidebarContext';
import { getAgents, getLeaderboard } from '../api';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

const AVATAR_COLORS = ['#E8232A', '#00A99D', '#6366f1', '#f59e0b', '#16a34a', '#ec4899'];

const SPECIALTY_STYLES = {
  payment: { background: '#fde8e8', color: '#E8232A' },
  quality: { background: '#e0f7f5', color: '#00A99D' },
  no_response: { background: '#ede9fe', color: '#6366f1' },
  delivery: { background: '#fff8e8', color: '#d97706' }
};

const getRankEmoji = (rank) => {
  if (rank === 1) return '🥇';
  if (rank === 2) return '🥈';
  if (rank === 3) return '🥉';
  return `#${rank}`;
};

const Agents = () => {
  const { isOpen } = useSidebar();
  const [agents, setAgents] = useState([]);
  const [totalAgents, setTotalAgents] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const load = async () => {
      try {
        const leaderboardRes = await getLeaderboard();
        setAgents(leaderboardRes.data.leaderboard || []);
        setTotalAgents(leaderboardRes.data.total_agents || 0);
      } catch {
        setError('⚠️ Could not connect to backend.');
      }
      setLoading(false);
    };
    load();
  }, []);

  const totalSolved = agents.reduce((s, a) => s + a.tickets_solved, 0);
  const topAgentName = agents.length > 0 ? agents[0].name.split(' ')[0] : 'N/A';

  const barData = agents.map((a, i) => ({
    name: a.name,
    value: a.tickets_solved,
    color: AVATAR_COLORS[i % AVATAR_COLORS.length]
  }));

  return (
    <div style={{ minHeight: '100vh', background: '#f5f5f5' }}>
      <Sidebar />

      <div style={{ marginLeft: isOpen ? '240px' : '0px', transition: 'margin-left 0.2s ease', display: 'flex', justifyContent: 'center' }}>
      <div style={{ width: '100%', maxWidth: '960px', padding: '40px 20px' }}>

        <h1 style={{ fontSize: '28px', fontWeight: 800, marginBottom: '6px' }}>Agent Performance</h1>
        <p style={{ color: '#666', marginBottom: '36px' }}>Live performance tracking for every ops agent — ranked by satisfaction score</p>

        {loading && <div style={{ textAlign: 'center', padding: '60px', color: '#999' }}>Loading agent data...</div>}
        {error && <div style={{ textAlign: 'center', padding: '60px', color: '#E8232A' }}>{error}</div>}

        {!loading && !error && (
          <>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px', marginBottom: '36px' }}>
              {[
                { label: 'Total Agents', value: totalAgents, color: '#E8232A' },
                { label: 'Total Tickets Solved', value: totalSolved, color: '#00A99D' },
                { label: 'Top Agent', value: topAgentName, color: '#f59e0b' }
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

            {agents.length === 0 ? (
              <div style={{
                textAlign: 'center', padding: '40px', color: '#999',
                background: 'white', borderRadius: '12px', border: '1px solid #e5e7eb'
              }}>
                No agents yet — add agents via the API docs!
              </div>
            ) : (
              <>
                <div style={{
                  background: 'white', border: '1px solid #e5e7eb', borderRadius: '14px',
                  padding: '28px', marginBottom: '28px', boxShadow: '0 2px 8px rgba(0,0,0,0.05)'
                }}>
                  <div style={{ fontSize: '16px', fontWeight: 700, marginBottom: '20px' }}>📊 Tickets Solved by Agent</div>
                  <ResponsiveContainer width="100%" height={280}>
                    <BarChart data={barData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
                      <XAxis dataKey="name" tick={{ fill: '#888', fontSize: 13 }} />
                      <YAxis tick={{ fill: '#888', fontSize: 13 }} allowDecimals={false} />
                      <Tooltip />
                      <Bar dataKey="value" radius={[8, 8, 0, 0]}>
                        {barData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>

                <h2 style={{ fontSize: '18px', fontWeight: 700, marginBottom: '16px' }}>🏆 Agent Leaderboard — Ranked by CSAT Score</h2>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                  {agents.map((agent, i) => {
                    const rank = i + 1;
                    const csatPct = (agent.avg_csat / 5) * 100;
                    const color = AVATAR_COLORS[i % AVATAR_COLORS.length];
                    const initials = agent.name.split(' ').map(n => n[0]).join('').toUpperCase();
                    const specialtyStyle = SPECIALTY_STYLES[agent.specialty] || { background: '#f3f4f6', color: '#888' };

                    return (
                      <div key={agent.id || agent.name} style={{
                        background: 'white', border: '2px solid #e5e7eb', borderRadius: '14px',
                        padding: '20px 24px', display: 'flex', alignItems: 'center', gap: '20px',
                        boxShadow: '0 2px 8px rgba(0,0,0,0.05)'
                      }}>
                        <div style={{ fontSize: '24px', fontWeight: 800, width: '40px', textAlign: 'center' }}>
                          {getRankEmoji(rank)}
                        </div>
                        <div style={{
                          width: '48px', height: '48px', borderRadius: '50%', background: color,
                          display: 'flex', alignItems: 'center', justifyContent: 'center',
                          fontSize: '18px', fontWeight: 800, color: 'white', flexShrink: 0
                        }}>
                          {initials}
                        </div>
                        <div style={{ flex: 1 }}>
                          <div style={{ fontSize: '16px', fontWeight: 700, marginBottom: '4px' }}>
                            {agent.name}
                            {rank === 1 && (
                              <span style={{
                                display: 'inline-block', padding: '3px 10px', borderRadius: '10px',
                                fontSize: '11px', fontWeight: 700, background: '#fff8e8', color: '#d97706', marginLeft: '8px'
                              }}>⭐ Top Agent</span>
                            )}
                          </div>
                          <div style={{ marginBottom: '8px' }}>
                            <span style={{
                              padding: '3px 10px', borderRadius: '10px', fontSize: '11px', fontWeight: 700,
                              textTransform: 'capitalize', ...specialtyStyle
                            }}>{agent.specialty || 'general'}</span>
                          </div>
                          <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap', fontSize: '12px', color: '#555' }}>
                            <div>🎫 <strong style={{ color: '#1a1a1a' }}>{agent.tickets_solved}</strong> tickets solved</div>
                            <div>⚡ <strong style={{ color: '#1a1a1a' }}>{agent.avg_speed_hrs}h</strong> avg speed</div>
                          </div>
                        </div>
                        <div style={{ width: '120px' }}>
                          <div style={{ fontSize: '11px', color: '#888', marginBottom: '4px', textAlign: 'right' }}>CSAT Score</div>
                          <div style={{ height: '8px', background: '#f3f4f6', borderRadius: '4px', overflow: 'hidden' }}>
                            <div style={{ height: '8px', borderRadius: '4px', background: '#00A99D', width: `${csatPct}%` }} />
                          </div>
                          <div style={{ fontSize: '18px', fontWeight: 800, color: '#00A99D', textAlign: 'center', marginTop: '4px' }}>
                            {agent.avg_csat}/5
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </>
            )}
          </>
        )}
      </div>
      </div>
    </div>
  );
};

export default Agents;