import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import jobService from '../services/jobService';

export default function CreateJob() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    title: '', description: '', responsibilities: '', qualifications: '',
    required_skills: '', preferred_skills: '', location: '', employment_type: 'full-time',
    experience_level: 'mid', min_experience_years: 0, salary_min: '', salary_max: '',
    remote_allowed: false, status: 'open',
  });
  const [error, setError] = useState('');

  const handleChange = (e) => {
    const value = e.target.type === 'checkbox' ? e.target.checked : e.target.value;
    setForm({ ...form, [e.target.name]: value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault(); setError('');
    try {
      const res = await jobService.create(form);
      navigate(`/jobs/${res.id}`);
    } catch (err) { setError(err.response?.data?.error || 'Failed to create job'); }
  };

  const inputStyle = { width: '100%', padding: '10px 14px', background: '#0f0f1a', border: '1px solid #334155', borderRadius: 8, color: '#e2e8f0', fontSize: '0.85rem' };
  const grid2 = { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 };

  return (
    <div style={{ padding: 32, maxWidth: 800, margin: '0 auto' }}>
      <div style={{ background: '#1e293b', padding: 32, borderRadius: 16, border: '1px solid #334155' }}>
        <h2 style={{ marginBottom: 24 }}>Create New Job</h2>
        {error && <div style={{ background: '#ef444422', color: '#ef4444', padding: '10px 16px', borderRadius: 8, marginBottom: 16 }}>{error}</div>}
        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: 16 }}>
            <label style={{ display: 'block', marginBottom: 4, color: '#94a3b8', fontSize: '0.8rem' }}>Job Title *</label>
            <input name="title" value={form.title} onChange={handleChange} required style={inputStyle} />
          </div>
          <div style={{ marginBottom: 16 }}>
            <label style={{ display: 'block', marginBottom: 4, color: '#94a3b8', fontSize: '0.8rem' }}>Description</label>
            <textarea name="description" value={form.description} onChange={handleChange} rows={4} style={{ ...inputStyle, resize: 'vertical' }} />
          </div>
          <div style={{ marginBottom: 16 }}>
            <label style={{ display: 'block', marginBottom: 4, color: '#94a3b8', fontSize: '0.8rem' }}>Responsibilities</label>
            <textarea name="responsibilities" value={form.responsibilities} onChange={handleChange} rows={3} style={{ ...inputStyle, resize: 'vertical' }} />
          </div>
          <div style={{ marginBottom: 16 }}>
            <label style={{ display: 'block', marginBottom: 4, color: '#94a3b8', fontSize: '0.8rem' }}>Qualifications</label>
            <textarea name="qualifications" value={form.qualifications} onChange={handleChange} rows={3} style={{ ...inputStyle, resize: 'vertical' }} />
          </div>
          <div style={grid2}>
            <div style={{ marginBottom: 12 }}>
              <label style={{ display: 'block', marginBottom: 4, color: '#94a3b8', fontSize: '0.8rem' }}>Required Skills (comma separated)</label>
              <input name="required_skills" value={form.required_skills} onChange={handleChange} style={inputStyle} placeholder="Python, React, SQL..." />
            </div>
            <div style={{ marginBottom: 12 }}>
              <label style={{ display: 'block', marginBottom: 4, color: '#94a3b8', fontSize: '0.8rem' }}>Preferred Skills</label>
              <input name="preferred_skills" value={form.preferred_skills} onChange={handleChange} style={inputStyle} />
            </div>
          </div>
          <div style={grid2}>
            <div style={{ marginBottom: 12 }}>
              <label style={{ display: 'block', marginBottom: 4, color: '#94a3b8', fontSize: '0.8rem' }}>Location</label>
              <input name="location" value={form.location} onChange={handleChange} style={inputStyle} />
            </div>
            <div style={{ marginBottom: 12 }}>
              <label style={{ display: 'block', marginBottom: 4, color: '#94a3b8', fontSize: '0.8rem' }}>Employment Type</label>
              <select name="employment_type" value={form.employment_type} onChange={handleChange} style={inputStyle}>
                <option value="full-time">Full-time</option>
                <option value="part-time">Part-time</option>
                <option value="contract">Contract</option>
                <option value="internship">Internship</option>
              </select>
            </div>
          </div>
          <div style={grid2}>
            <div style={{ marginBottom: 12 }}>
              <label style={{ display: 'block', marginBottom: 4, color: '#94a3b8', fontSize: '0.8rem' }}>Experience Level</label>
              <select name="experience_level" value={form.experience_level} onChange={handleChange} style={inputStyle}>
                <option value="entry">Entry</option>
                <option value="mid">Mid</option>
                <option value="senior">Senior</option>
                <option value="lead">Lead</option>
              </select>
            </div>
            <div style={{ marginBottom: 12 }}>
              <label style={{ display: 'block', marginBottom: 4, color: '#94a3b8', fontSize: '0.8rem' }}>Min Experience (years)</label>
              <input type="number" name="min_experience_years" value={form.min_experience_years} onChange={handleChange} style={inputStyle} />
            </div>
          </div>
          <div style={grid2}>
            <div style={{ marginBottom: 12 }}>
              <label style={{ display: 'block', marginBottom: 4, color: '#94a3b8', fontSize: '0.8rem' }}>Salary Min ($)</label>
              <input type="number" name="salary_min" value={form.salary_min} onChange={handleChange} style={inputStyle} />
            </div>
            <div style={{ marginBottom: 12 }}>
              <label style={{ display: 'block', marginBottom: 4, color: '#94a3b8', fontSize: '0.8rem' }}>Salary Max ($)</label>
              <input type="number" name="salary_max" value={form.salary_max} onChange={handleChange} style={inputStyle} />
            </div>
          </div>
          <div style={{ marginBottom: 20, display: 'flex', alignItems: 'center', gap: 8 }}>
            <input type="checkbox" name="remote_allowed" checked={form.remote_allowed} onChange={handleChange} id="remote" />
            <label htmlFor="remote" style={{ color: '#94a3b8', fontSize: '0.85rem' }}>Remote Allowed</label>
          </div>
          <button type="submit" style={{ width: '100%', padding: '12px', background: '#6366f1', color: '#fff', border: 'none', borderRadius: 8, fontSize: '0.95rem', fontWeight: 600, cursor: 'pointer' }}>Create Job</button>
        </form>
      </div>
    </div>
  );
}
