import React from 'react';
import { useNavigate } from 'react-router-dom';

export default function ResumeCard({ resume }) {
  const navigate = useNavigate();
  const scoreColor = resume.ats_score >= 80 ? '#22c55e' : resume.ats_score >= 60 ? '#eab308' : '#ef4444';

  return (
    <div style={{
      background: '#1e293b', borderRadius: '12px', padding: '20px',
      border: '1px solid #334155', cursor: 'pointer',
    }} onClick={() => navigate(`/resume/${resume.id}`)}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
        <div>
          <div style={{ fontWeight: 600, color: '#e2e8f0' }}>{resume.original_filename}</div>
          <div style={{ fontSize: '0.8rem', color: '#64748b', marginTop: 4 }}>
            {resume.job_title || 'No job associated'} · {new Date(resume.created_at).toLocaleDateString()}
          </div>
        </div>
        <div style={{
          width: 48, height: 48, borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center',
          border: `3px solid ${scoreColor}`, color: scoreColor, fontWeight: 700, fontSize: '0.9rem',
        }}>
          {resume.ats_score?.toFixed(0) || '—'}
        </div>
      </div>
      <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
        <span style={{
          padding: '2px 10px', borderRadius: '12px', fontSize: '0.75rem',
          background: resume.status === 'matched' ? '#22c55e22' : '#6366f122',
          color: resume.status === 'matched' ? '#22c55e' : '#6366f1',
        }}>{resume.status}</span>
        <span style={{ fontSize: '0.75rem', color: '#64748b' }}>ATS Score</span>
      </div>
    </div>
  );
}
