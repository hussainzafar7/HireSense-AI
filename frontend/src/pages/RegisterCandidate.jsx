import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function RegisterCandidate() {
  const [form, setForm] = useState({ email: '', password: '', full_name: '', phone: '', location: '', headline: '', years_of_experience: 0, current_role: '', current_company: '', skills: '' });
  const [error, setError] = useState('');
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });
  const handleSubmit = async (e) => {
    e.preventDefault(); setError('');
    try {
      await register('candidate', form);
      navigate('/dashboard/candidate');
    } catch (err) { setError(err.response?.data?.error || 'Registration failed'); }
  };

  const inputStyle = { width: '100%', padding: '10px 14px', background: '#0f0f1a', border: '1px solid #334155', borderRadius: 8, color: '#e2e8f0', fontSize: '0.85rem' };
  const grid2 = { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 };

  return (
    <div style={{ minHeight: 'calc(100vh - 60px)', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 20 }}>
      <div style={{ background: '#1e293b', padding: 40, borderRadius: 16, width: '100%', maxWidth: 600, border: '1px solid #334155' }}>
        <h2 style={{ marginBottom: 8 }}>Candidate Registration</h2>
        <p style={{ color: '#94a3b8', marginBottom: 24, fontSize: '0.9rem' }}>Create your candidate account</p>
        {error && <div style={{ background: '#ef444422', color: '#ef4444', padding: '10px 16px', borderRadius: 8, marginBottom: 16, fontSize: '0.85rem' }}>{error}</div>}
        <form onSubmit={handleSubmit}>
          <div style={grid2}>
            <div style={{ marginBottom: 12 }}>
              <label style={{ display: 'block', marginBottom: 4, color: '#94a3b8', fontSize: '0.8rem' }}>Full Name *</label>
              <input name="full_name" value={form.full_name} onChange={handleChange} required style={inputStyle} />
            </div>
            <div style={{ marginBottom: 12 }}>
              <label style={{ display: 'block', marginBottom: 4, color: '#94a3b8', fontSize: '0.8rem' }}>Email *</label>
              <input type="email" name="email" value={form.email} onChange={handleChange} required style={inputStyle} />
            </div>
          </div>
          <div style={grid2}>
            <div style={{ marginBottom: 12 }}>
              <label style={{ display: 'block', marginBottom: 4, color: '#94a3b8', fontSize: '0.8rem' }}>Password *</label>
              <input type="password" name="password" value={form.password} onChange={handleChange} required style={inputStyle} />
            </div>
            <div style={{ marginBottom: 12 }}>
              <label style={{ display: 'block', marginBottom: 4, color: '#94a3b8', fontSize: '0.8rem' }}>Phone</label>
              <input name="phone" value={form.phone} onChange={handleChange} style={inputStyle} />
            </div>
          </div>
          <div style={grid2}>
            <div style={{ marginBottom: 12 }}>
              <label style={{ display: 'block', marginBottom: 4, color: '#94a3b8', fontSize: '0.8rem' }}>Location</label>
              <input name="location" value={form.location} onChange={handleChange} style={inputStyle} />
            </div>
            <div style={{ marginBottom: 12 }}>
              <label style={{ display: 'block', marginBottom: 4, color: '#94a3b8', fontSize: '0.8rem' }}>Headline</label>
              <input name="headline" value={form.headline} onChange={handleChange} style={inputStyle} />
            </div>
          </div>
          <div style={grid2}>
            <div style={{ marginBottom: 12 }}>
              <label style={{ display: 'block', marginBottom: 4, color: '#94a3b8', fontSize: '0.8rem' }}>Years of Experience</label>
              <input type="number" name="years_of_experience" value={form.years_of_experience} onChange={handleChange} style={inputStyle} />
            </div>
            <div style={{ marginBottom: 12 }}>
              <label style={{ display: 'block', marginBottom: 4, color: '#94a3b8', fontSize: '0.8rem' }}>Current Role</label>
              <input name="current_role" value={form.current_role} onChange={handleChange} style={inputStyle} />
            </div>
          </div>
          <div style={{ marginBottom: 12 }}>
            <label style={{ display: 'block', marginBottom: 4, color: '#94a3b8', fontSize: '0.8rem' }}>Current Company</label>
            <input name="current_company" value={form.current_company} onChange={handleChange} style={inputStyle} />
          </div>
          <div style={{ marginBottom: 20 }}>
            <label style={{ display: 'block', marginBottom: 4, color: '#94a3b8', fontSize: '0.8rem' }}>Skills (comma separated)</label>
            <input name="skills" value={form.skills} onChange={handleChange} style={inputStyle} placeholder="Python, React, Docker..." />
          </div>
          <button type="submit" style={{ width: '100%', padding: '12px', background: '#6366f1', color: '#fff', border: 'none', borderRadius: 8, fontSize: '0.95rem', fontWeight: 600, cursor: 'pointer' }}>Create Account</button>
        </form>
        <div style={{ marginTop: 16, textAlign: 'center', fontSize: '0.85rem', color: '#64748b' }}>
          Already have an account? <Link to="/login" style={{ color: '#6366f1', textDecoration: 'none' }}>Sign In</Link>
        </div>
      </div>
    </div>
  );
}
