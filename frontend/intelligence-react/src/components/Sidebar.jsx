import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useSidebar } from '../context/SidebarContext';

const navItems = [
  { label: '🧠 Home', path: '/intelligence' },
  { label: '🟢 Health', path: '/health' },
  { label: '📋 Reports', path: '/reports' },
  { label: '🔥 Heatmap', path: '/heatmap' },
  { label: '👥 Agents', path: '/agents' }
];

const Sidebar = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { isOpen, toggle } = useSidebar();
  const username = localStorage.getItem('bp_username');

  const logout = () => {
    localStorage.removeItem('bp_token');
    localStorage.removeItem('bp_username');
    localStorage.removeItem('bp_role');
    window.location.href = '/login';
  };

  return (
    <>
      {/* Hamburger toggle — always visible, fixed top-left */}
      <button onClick={toggle} style={{
        position: 'fixed', top: '20px', left: isOpen ? '252px' : '16px',
        zIndex: 20, width: '36px', height: '36px', borderRadius: '8px',
        border: '1px solid #e5e7eb', background: 'white', cursor: 'pointer',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        fontSize: '16px', transition: 'left 0.2s ease', boxShadow: '0 2px 6px rgba(0,0,0,0.08)'
      }}>
        ☰
      </button>

      <div style={{
        width: '240px',
        position: 'fixed',
        top: 0,
        left: isOpen ? 0 : '-240px',
        bottom: 0,
        background: 'white',
        borderRight: '1px solid #e5e7eb',
        padding: '24px 16px',
        boxSizing: 'border-box',
        display: 'flex',
        flexDirection: 'column',
        transition: 'left 0.2s ease',
        zIndex: 10
      }}>
        <div style={{ fontSize: '20px', fontWeight: 800, color: '#E8232A', marginBottom: '32px', paddingLeft: '6px', marginTop: '4px' }}>
          Bustler <span style={{ color: '#00A99D' }}>Pulse</span>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', flex: 1 }}>
          {navItems.map(item => {
            const active = location.pathname === item.path;
            return (
              <button
                key={item.path}
                onClick={() => navigate(item.path)}
                style={{
                  padding: '12px 16px',
                  borderRadius: '10px',
                  fontSize: '14px',
                  fontWeight: 600,
                  border: 'none',
                  textAlign: 'left',
                  cursor: 'pointer',
                  background: active ? '#E8232A' : 'transparent',
                  color: active ? 'white' : '#666'
                }}
              >
                {item.label}
              </button>
            );
          })}
        </div>

        <div style={{ borderTop: '1px solid #f3f4f6', paddingTop: '16px' }}>
          <div style={{ fontSize: '13px', color: '#888', marginBottom: '10px', paddingLeft: '6px' }}>
            👋 {username || 'User'}
          </div>
          <button onClick={logout} style={{
            width: '100%',
            background: '#fde8e8',
            color: '#E8232A',
            border: '1px solid #E8232A',
            padding: '10px 16px',
            borderRadius: '8px',
            fontSize: '13px',
            fontWeight: 600,
            cursor: 'pointer'
          }}>
            Logout
          </button>
        </div>
      </div>
    </>
  );
};

export default Sidebar;