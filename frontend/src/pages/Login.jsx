import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault(); setError('');
    try {
      const user = await login(email, password);
      navigate(user.role === 'company' ? '/dashboard/company' : '/dashboard/candidate');
    } catch (err) {
      setError(err.response?.data?.error || 'Login failed');
    }
  };

  return (
    <div style={{ minHeight: 'calc(100vh - 60px)', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 20 }}>
      <div style={{ background: '#1e293b', padding: 40, borderRadius: 16, width: '100%', maxWidth: 420, border: '1px solid #334155' }}>
        <h2 style={{ marginBottom: 8, fontSize: '1.5rem' }}>Welcome Back</h2>
        <p style={{ color: '#94a3b8', marginBottom: 24, fontSize: '0.9rem' }}>Sign in to your HireSense account</p>
        {error && <div style={{ background: '#ef444422', color: '#ef4444', padding: '10px 16px', borderRadius: 8, marginBottom: 16, fontSize: '0.85rem' }}>{error}</div>}
        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: 16 }}>
            <label style={{ display: 'block', marginBottom: 6, color: '#94a3b8', fontSize: '0.85rem' }}>Email</label>
            <input type="email" value={email} onChange={e => setEmail(e.target.value)} required style={{ width: '100%', padding: '12px 16px', background: '#0f0f1a', border: '1px solid #334155', borderRadius: 8, color: '#e2e8f0', fontSize: '0.9rem' }} />
          </div>
          <div style={{ marginBottom: 24 }}>
            <label style={{ display: 'block', marginBottom: 6, color: '#94a3b8', fontSize: '0.85rem' }}>Password</label>
            <input type="password" value={password} onChange={e => setPassword(e.target.value)} required style={{ width: '100%', padding: '12px 16px', background: '#0f0f1a', border: '1px solid #334155', borderRadius: 8, color: '#e2e8f0', fontSize: '0.9rem' }} />
          </div>
          <button type="submit" style={{ width: '100%', padding: '12px', background: '#6366f1', color: '#fff', border: 'none', borderRadius: 8, fontSize: '0.95rem', fontWeight: 600, cursor: 'pointer' }}>Sign In</button>
        </form>
        <div style={{ marginTop: 20, textAlign: 'center', fontSize: '0.85rem', color: '#64748b' }}>
          Don't have an account? <Link to="/register/candidate" style={{ color: '#6366f1', textDecoration: 'none' }}>Register as Candidate</Link> or <Link to="/register/company" style={{ color: '#6366f1', textDecoration: 'none' }}>Company</Link>
        </div>
      </div>
    </div>
  );
}
