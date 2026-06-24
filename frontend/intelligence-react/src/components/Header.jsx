import React from 'react';

const Header = ({ showLogout = false }) => {
  const username = localStorage.getItem('bp_username');

  const logout = () => {
    localStorage.removeItem('bp_token');
    localStorage.removeItem('bp_username');
    localStorage.removeItem('bp_role');
    window.location.href = '/login';
  };

  return (
    <header style={{
      background: 'white',
      padding: '16px 40px',
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      borderBottom: '3px solid #E8232A',
      boxShadow: '0 2px 8px rgba(0,0,0,0.08)'
    }}>
      <div style={{ fontSize: '22px', fontWeight: 800, color: '#E8232A' }}>
        Bustler <span style={{ color: '#00A99D' }}>Pulse</span>
      </div>
      {showLogout && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <span style={{ fontSize: '13px', color: '#888' }}>
            👋 {username || 'User'}
          </span>
          <button onClick={logout} style={{
            background: '#fde8e8',
            color: '#E8232A',
            border: '1px solid #E8232A',
            padding: '6px 16px',
            borderRadius: '8px',
            fontSize: '13px',
            fontWeight: 600,
            cursor: 'pointer'
          }}>
            Logout
          </button>
        </div>
      )}
    </header>
  );
};

export default Header;