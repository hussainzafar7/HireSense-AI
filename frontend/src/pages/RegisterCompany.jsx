import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function RegisterCompany() {
  const [form, setForm] = useState({ email: '', password: '', company_name: '', industry: '', website: '', location: '', company_size: '', description: '', contact_person: '', contact_phone: '' });
  const [error, setError] = useState('');
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });
  const handleSubmit = async (e) => {
    e.preventDefault(); setError('');
    try {
      await register('company', form);
      navigate('/dashboard/company');
    } catch (err) { setError(err.response?.data?.error || 'Registration failed'); }
  };

  const inputStyle = { width: '100%', padding: '10px 14px', background: '#0f0f1a', border: '1px solid #334155', borderRadius: 8, color: '#e2e8f0', fontSize: '0.85rem' };
  const grid2 = { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 };

  return (
    <div style={{ minHeight: 'calc(100vh - 60px)', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 20 }}>
      <div style={{ background: '#1e293b', padding: 40, borderRadius: 16, width: '100%', maxWidth: 600, border: '1px solid #334155' }}>
        <h2 style={{ marginBottom: 8 }}>Company Registration</h2>
        <p style={{ color: '#94a3b8', marginBottom: 24, fontSize: '0.9rem' }}>Create your company account</p>
        {error && <div style={{ background: '#ef444422', color: '#ef4444', padding: '10px 16px', borderRadius: 8, marginBottom: 16, fontSize: '0.85rem' }}>{error}</div>}
        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: 12 }}>
            <label style={{ display: 'block', marginBottom: 4, color: '#94a3b8', fontSize: '0.8rem' }}>Company Name *</label>
            <input name="company_name" value={form.company_name} onChange={handleChange} required style={inputStyle} />
          </div>
          <div style={grid2}>
            <div style={{ marginBottom: 12 }}>
              <label style={{ display: 'block', marginBottom: 4, color: '#94a3b8', fontSize: '0.8rem' }}>Email *</label>
              <input type="email" name="email" value={form.email} onChange={handleChange} required style={inputStyle} />
            </div>
            <div style={{ marginBottom: 12 }}>
              <label style={{ display: 'block', marginBottom: 4, color: '#94a3b8', fontSize: '0.8rem' }}>Password *</label>
              <input type="password" name="password" value={form.password} onChange={handleChange} required style={inputStyle} />
            </div>
          </div>
          <div style={grid2}>
            <div style={{ marginBottom: 12 }}>
              <label style={{ display: 'block', marginBottom: 4, color: '#94a3b8', fontSize: '0.8rem' }}>Industry</label>
              <input name="industry" value={form.industry} onChange={handleChange} style={inputStyle} />
            </div>
            <div style={{ marginBottom: 12 }}>
              <label style={{ display: 'block', marginBottom: 4, color: '#94a3b8', fontSize: '0.8rem' }}>Website</label>
              <input name="website" value={form.website} onChange={handleChange} style={inputStyle} />
            </div>
          </div>
          <div style={grid2}>
            <div style={{ marginBottom: 12 }}>
              <label style={{ display: 'block', marginBottom: 4, color: '#94a3b8', fontSize: '0.8rem' }}>Location</label>
              <input name="location" value={form.location} onChange={handleChange} style={inputStyle} />
            </div>
            <div style={{ marginBottom: 12 }}>
              <label style={{ display: 'block', marginBottom: 4, color: '#94a3b8', fontSize: '0.8rem' }}>Company Size</label>
              <input name="company_size" value={form.company_size} onChange={handleChange} style={inputStyle} placeholder="1-10, 11-50, 51-200..." />
            </div>
          </div>
          <div style={grid2}>
            <div style={{ marginBottom: 12 }}>
              <label style={{ display: 'block', marginBottom: 4, color: '#94a3b8', fontSize: '0.8rem' }}>Contact Person</label>
              <input name="contact_person" value={form.contact_person} onChange={handleChange} style={inputStyle} />
            </div>
            <div style={{ marginBottom: 12 }}>
              <label style={{ display: 'block', marginBottom: 4, color: '#94a3b8', fontSize: '0.8rem' }}>Contact Phone</label>
              <input name="contact_phone" value={form.contact_phone} onChange={handleChange} style={inputStyle} />
            </div>
          </div>
          <div style={{ marginBottom: 20 }}>
            <label style={{ display: 'block', marginBottom: 4, color: '#94a3b8', fontSize: '0.8rem' }}>Description</label>
            <textarea name="description" value={form.description} onChange={handleChange} rows={3} style={{ ...inputStyle, resize: 'vertical' }} />
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
