import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import { login, register } from '../api';

const Login = () => {
  const navigate = useNavigate();
  const [tab, setTab] = useState('login');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  // Login form state
  const [loginData, setLoginData] = useState({ username: '', password: '' });

  // Register form state
  const [regData, setRegData] = useState({
    username: '', email: '', password: '', role: 'product_team'
  });

  // Check if already logged in
  if (localStorage.getItem('bp_token')) {
    navigate('/intelligence');
  }

  const handleLogin = async () => {
    if (!loginData.username || !loginData.password) {
      setError('Please enter username and password');
      return;
    }
    setLoading(true);
    setError('');
    try {
      const res = await login(loginData.username, loginData.password);
      localStorage.setItem('bp_token', res.data.access_token);
      localStorage.setItem('bp_username', res.data.username);
      localStorage.setItem('bp_role', res.data.role);
      setSuccess('Login successful! Redirecting...');
      setTimeout(() => navigate('/intelligence'), 1000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Invalid username or password');
    }
    setLoading(false);
  };

  const handleRegister = async () => {
    if (!regData.username || !regData.email || !regData.password) {
      setError('Please fill in all fields');
      return;
    }
    setLoading(true);
    setError('');
    try {
      await register(regData.username, regData.email, regData.password, regData.role);
      setSuccess('Account created! You can now sign in.');
      setTab('login');
      setLoginData({ ...loginData, username: regData.username });
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed');
    }
    setLoading(false);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      tab === 'login' ? handleLogin() : handleRegister();
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <Header />
      <div style={{
        flex: 1, display: 'flex',
        alignItems: 'center', justifyContent: 'center', padding: '40px 20px'
      }}>
        <div style={{
          background: 'white', borderRadius: '20px', padding: '48px 40px',
          width: '100%', maxWidth: '420px',
          boxShadow: '0 8px 32px rgba(0,0,0,0.10)', border: '1px solid #e5e7eb'
        }}>
          <div style={{ fontSize: '48px', textAlign: 'center', marginBottom: '16px' }}>🧠</div>
          <div style={{ fontSize: '24px', fontWeight: 800, textAlign: 'center', marginBottom: '6px' }}>
            Intelligence Layer
          </div>
          <div style={{ fontSize: '14px', color: '#888', textAlign: 'center', marginBottom: '28px' }}>
            Sign in to access system health, reports and heatmap
          </div>

          {/* Tabs */}
          <div style={{ display: 'flex', gap: '8px', marginBottom: '24px' }}>
            {['login', 'register'].map(t => (
              <button key={t} onClick={() => { setTab(t); setError(''); setSuccess(''); }}
                style={{
                  flex: 1, padding: '10px', borderRadius: '8px',
                  border: `2px solid ${tab === t ? '#E8232A' : '#e5e7eb'}`,
                  background: tab === t ? '#E8232A' : 'white',
                  color: tab === t ? 'white' : '#888',
                  fontSize: '14px', fontWeight: 600
                }}>
                {t === 'login' ? 'Sign In' : 'Register'}
              </button>
            ))}
          </div>

          {/* Messages */}
          {error && (
            <div style={{
              background: '#fde8e8', color: '#E8232A', padding: '10px 14px',
              borderRadius: '8px', fontSize: '13px', marginBottom: '16px',
              border: '1px solid #fca5a5'
            }}>{error}</div>
          )}
          {success && (
            <div style={{
              background: '#dcfce7', color: '#16a34a', padding: '10px 14px',
              borderRadius: '8px', fontSize: '13px', marginBottom: '16px',
              border: '1px solid #86efac'
            }}>{success}</div>
          )}

          {/* Login Form */}
          {tab === 'login' && (
            <div onKeyPress={handleKeyPress}>
              {[
                { label: 'Username', key: 'username', type: 'text', placeholder: 'Enter your username' },
                { label: 'Password', key: 'password', type: 'password', placeholder: 'Enter your password' }
              ].map(field => (
                <div key={field.key} style={{ marginBottom: '20px' }}>
                  <label style={{ fontSize: '13px', fontWeight: 600, color: '#444', display: 'block', marginBottom: '8px' }}>
                    {field.label}
                  </label>
                  <input
                    type={field.type}
                    placeholder={field.placeholder}
                    value={loginData[field.key]}
                    onChange={e => setLoginData({ ...loginData, [field.key]: e.target.value })}
                    style={{
                      width: '100%', padding: '12px 16px', border: '2px solid #e5e7eb',
                      borderRadius: '10px', fontSize: '14px', outline: 'none'
                    }}
                  />
                </div>
              ))}
              <button onClick={handleLogin} disabled={loading} style={{
                width: '100%', padding: '14px', background: '#E8232A',
                color: 'white', border: 'none', borderRadius: '10px',
                fontSize: '15px', fontWeight: 700,
                opacity: loading ? 0.7 : 1
              }}>
                {loading ? 'Signing in...' : 'Sign In →'}
              </button>
            </div>
          )}

          {/* Register Form */}
          {tab === 'register' && (
            <div onKeyPress={handleKeyPress}>
              {[
                { label: 'Username', key: 'username', type: 'text', placeholder: 'Choose a username' },
                { label: 'Email', key: 'email', type: 'email', placeholder: 'Enter your email' },
                { label: 'Password', key: 'password', type: 'password', placeholder: 'Choose a password' }
              ].map(field => (
                <div key={field.key} style={{ marginBottom: '20px' }}>
                  <label style={{ fontSize: '13px', fontWeight: 600, color: '#444', display: 'block', marginBottom: '8px' }}>
                    {field.label}
                  </label>
                  <input
                    type={field.type}
                    placeholder={field.placeholder}
                    value={regData[field.key]}
                    onChange={e => setRegData({ ...regData, [field.key]: e.target.value })}
                    style={{
                      width: '100%', padding: '12px 16px', border: '2px solid #e5e7eb',
                      borderRadius: '10px', fontSize: '14px', outline: 'none'
                    }}
                  />
                </div>
              ))}
              <div style={{ marginBottom: '20px' }}>
                <label style={{ fontSize: '13px', fontWeight: 600, color: '#444', display: 'block', marginBottom: '8px' }}>
                  Role
                </label>
                <select
                  value={regData.role}
                  onChange={e => setRegData({ ...regData, role: e.target.value })}
                  style={{
                    width: '100%', padding: '12px 16px', border: '2px solid #e5e7eb',
                    borderRadius: '10px', fontSize: '14px', outline: 'none'
                  }}>
                  <option value="product_team">Product Team</option>
                  <option value="admin">Admin</option>
                </select>
              </div>
              <button onClick={handleRegister} disabled={loading} style={{
                width: '100%', padding: '14px', background: '#E8232A',
                color: 'white', border: 'none', borderRadius: '10px',
                fontSize: '15px', fontWeight: 700,
                opacity: loading ? 0.7 : 1
              }}>
                {loading ? 'Creating account...' : 'Create Account →'}
              </button>
            </div>
          )}
        </div>
      </div>
      <div style={{ textAlign: 'center', padding: '20px', color: '#aaa', fontSize: '12px' }}>
        Bustler Pulse Intelligence Layer · Internal access only
      </div>
    </div>
  );
};

export default Login;