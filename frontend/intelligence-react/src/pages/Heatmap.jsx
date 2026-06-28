import React, { useState, useEffect } from 'react';
import Sidebar from '../components/Sidebar';
import { useSidebar } from '../context/SidebarContext';
import { getHeatmap, getReportsSummary } from '../api';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

const COLORS = {
  payment: '#E8232A',
  refund: '#f97316',
  delivery: '#f59e0b',
  quality: '#00A99D',
  no_response: '#6366f1',
  other: '#8b5cf6'
};

const getHeatColor = (count, max) => {
  if (count === 0) return '#f3f4f6';
  const intensity = count / max;
  if (intensity > 0.7) return '#E8232A';
  if (intensity > 0.4) return '#f97316';
  if (intensity > 0.2) return '#f59e0b';
  return '#00A99D';
};

const Heatmap = () => {
  const { isOpen } = useSidebar();
  const [heatmapData, setHeatmapData] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const load = async () => {
      try {
        const [h, s] = await Promise.all([getHeatmap(), getReportsSummary()]);
        setHeatmapData(h.data.heatmap || []);
        setSummary(s.data);
      } catch {
        setError('⚠️ Could not connect to backend.');
      }
      setLoading(false);
    };
    load();
  }, []);

  const categories = [...new Set(heatmapData.map(d => d.category))];
  const weeks = [...new Set(heatmapData.map(d => d.week))].sort((a, b) => a - b);
  const lookup = {};
  heatmapData.forEach(d => { lookup[`${d.category}_${d.week}`] = d.count; });

  const catTotals = {};
  categories.forEach(cat => {
    catTotals[cat] = heatmapData.filter(d => d.category === cat).reduce((s, d) => s + d.count, 0);
  });

  const weekTotals = {};
  weeks.forEach(w => {
    weekTotals[w] = heatmapData.filter(d => d.week === w).reduce((s, d) => s + d.count, 0);
  });

  const hottestCat = Object.entries(catTotals).sort((a, b) => b[1] - a[1])[0];
  const peakWeek = Object.entries(weekTotals).sort((a, b) => b[1] - a[1])[0];
  const maxCount = heatmapData.length > 0 ? Math.max(...heatmapData.map(d => d.count)) : 1;

  const barData = categories.map(cat => ({
    name: cat.replace('_', ' '),
    value: catTotals[cat],
    color: COLORS[cat] || '#8b5cf6'
  }));

  return (
    <div style={{ minHeight: '100vh', background: '#f5f5f5' }}>
      <Sidebar />

      <div style={{ marginLeft: isOpen ? '240px' : '0px', transition: 'margin-left 0.2s ease', display: 'flex', justifyContent: 'center' }}>
      <div style={{ width: '100%', maxWidth: '1000px', padding: '40px 20px' }}>

        <h1 style={{ fontSize: '28px', fontWeight: 800, marginBottom: '6px' }}>Issue Heatmap</h1>
        <p style={{ color: '#666', marginBottom: '36px' }}>Which issues spike at which time — helping the product team predict and prevent problems</p>

        {loading && <div style={{ textAlign: 'center', padding: '60px', color: '#999' }}>Loading heatmap data...</div>}
        {error && <div style={{ textAlign: 'center', padding: '60px', color: '#E8232A' }}>{error}</div>}

        {!loading && !error && (
          <>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px', marginBottom: '32px' }}>
              {[
                { icon: '🔥', title: 'Hottest Category', value: hottestCat ? hottestCat[0].replace('_', ' ') : 'N/A', desc: 'Most reported issue type' },
                { icon: '📅', title: 'Peak Week', value: peakWeek ? `Week ${peakWeek[0]}` : 'N/A', desc: 'Week with most issues' },
                { icon: '📊', title: 'Total Tracked', value: summary?.total_tickets ?? 0, desc: 'Issues in heatmap' }
              ].map(card => (
                <div key={card.title} style={{
                  background: 'white', border: '1px solid #e5e7eb', borderRadius: '14px',
                  padding: '22px', boxShadow: '0 2px 8px rgba(0,0,0,0.05)'
                }}>
                  <div style={{ fontSize: '28px', marginBottom: '10px' }}>{card.icon}</div>
                  <div style={{ fontSize: '13px', fontWeight: 600, color: '#888', textTransform: 'uppercase', letterSpacing: '0.04em', marginBottom: '8px' }}>{card.title}</div>
                  <div style={{ fontSize: '22px', fontWeight: 800, color: '#E8232A', marginBottom: '4px', textTransform: 'capitalize' }}>{card.value}</div>
                  <div style={{ fontSize: '12px', color: '#aaa' }}>{card.desc}</div>
                </div>
              ))}
            </div>

            {barData.length > 0 && (
              <div style={{
                background: 'white', border: '1px solid #e5e7eb', borderRadius: '14px',
                padding: '28px', marginBottom: '28px', boxShadow: '0 2px 8px rgba(0,0,0,0.05)'
              }}>
                <div style={{ fontSize: '16px', fontWeight: 700, marginBottom: '20px' }}>📊 Issues by Category</div>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={barData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
                    <XAxis dataKey="name" tick={{ fill: '#888', fontSize: 13 }} />
                    <YAxis tick={{ fill: '#888', fontSize: 13 }} />
                    <Tooltip />
                    <Bar dataKey="value" radius={[8, 8, 0, 0]}>
                      {barData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}

            {heatmapData.length === 0 ? (
              <div style={{
                textAlign: 'center', padding: '40px', color: '#999',
                background: 'white', borderRadius: '12px', border: '1px solid #e5e7eb'
              }}>
                📭 No heatmap data yet — submit and resolve tickets to see patterns.
              </div>
            ) : (
              <div style={{
                background: 'white', border: '1px solid #e5e7eb', borderRadius: '14px',
                padding: '28px', boxShadow: '0 2px 8px rgba(0,0,0,0.05)'
              }}>
                <div style={{ fontSize: '16px', fontWeight: 700, marginBottom: '6px' }}>🔥 Category × Week Heatmap</div>
                <div style={{ fontSize: '13px', color: '#888', marginBottom: '24px' }}>Darker = more issues. Hover to see count.</div>

                <div style={{ display: 'flex', gap: '6px', paddingLeft: '118px', marginBottom: '6px' }}>
                  {weeks.map(w => (
                    <div key={w} style={{ flex: 1, textAlign: 'center', fontSize: '11px', color: '#aaa', fontWeight: 600 }}>W{w}</div>
                  ))}
                </div>

                {categories.map(cat => (
                  <div key={cat} style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                    <div style={{ width: '110px', fontSize: '13px', color: '#666', textAlign: 'right', fontWeight: 500, textTransform: 'capitalize' }}>
                      {cat.replace('_', ' ')}
                    </div>
                    <div style={{ display: 'flex', gap: '6px', flex: 1 }}>
                      {weeks.map(w => {
                        const count = lookup[`${cat}_${w}`] || 0;
                        const color = getHeatColor(count, maxCount);
                        return (
                          <div key={w} title={`${cat} — Week ${w}: ${count} issue(s)`}
                            style={{
                              flex: 1, height: '38px', borderRadius: '8px',
                              background: color, display: 'flex', alignItems: 'center',
                              justifyContent: 'center', fontSize: '12px', fontWeight: 700,
                              color: count === 0 ? '#ccc' : 'white', cursor: 'pointer'
                            }}>
                            {count > 0 ? count : ''}
                          </div>
                        );
                      })}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </>
        )}
      </div>
      </div>
    </div>
  );
};

export default Heatmap;