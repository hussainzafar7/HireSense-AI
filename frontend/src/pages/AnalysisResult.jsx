import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import resumeService from '../services/resumeService';
import ScoreGauge from '../components/ScoreGauge';
import SkillBadge from '../components/SkillBadge';

export default function AnalysisResult() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [data, setData] = useState(null);

  useEffect(() => { resumeService.getById(id).then(setData).catch(() => navigate('/')); }, [id, navigate]);

  if (!data) return <div style={{ padding: 40, textAlign: 'center', color: '#64748b' }}>Loading...</div>;

  const parsed = data.parsed_data;

  return (
    <div style={{ padding: 32, maxWidth: 900, margin: '0 auto' }}>
      <div style={{ background: '#1e293b', borderRadius: 16, padding: 32, border: '1px solid #334155', marginBottom: 24 }}>
        <h2 style={{ marginBottom: 16 }}>Resume Analysis</h2>
        {parsed && (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 20 }}>
            <div><span style={{ color: '#64748b', fontSize: '0.8rem' }}>Name</span><div style={{ color: '#e2e8f0', fontWeight: 600 }}>{parsed.name || '—'}</div></div>
            <div><span style={{ color: '#64748b', fontSize: '0.8rem' }}>Email</span><div style={{ color: '#e2e8f0' }}>{parsed.email || '—'}</div></div>
            <div><span style={{ color: '#64748b', fontSize: '0.8rem' }}>Phone</span><div style={{ color: '#e2e8f0' }}>{parsed.phone || '—'}</div></div>
            <div><span style={{ color: '#64748b', fontSize: '0.8rem' }}>Location</span><div style={{ color: '#e2e8f0' }}>{parsed.location || '—'}</div></div>
            <div><span style={{ color: '#64748b', fontSize: '0.8rem' }}>LinkedIn</span><div style={{ color: '#e2e8f0' }}>{parsed.linkedin || '—'}</div></div>
            <div><span style={{ color: '#64748b', fontSize: '0.8rem' }}>GitHub</span><div style={{ color: '#e2e8f0' }}>{parsed.github || '—'}</div></div>
          </div>
        )}
        <div style={{ display: 'flex', gap: 40, alignItems: 'center', marginBottom: 20 }}>
          <ScoreGauge score={data.ats_score || 0} size={140} label="ATS Score" />
          {parsed && <ScoreGauge score={parsed.resume_strength_score || 0} size={140} label="Resume Strength" color="#a855f7" />}
        </div>
        {data.recommendations && (
          <div style={{ padding: '12px 16px', borderRadius: 8, background: '#0f0f1a', marginBottom: 20, border: '1px solid #334155' }}>
            <span style={{ color: '#6366f1', fontWeight: 600 }}>Recommendation: </span>
            <span style={{ color: '#e2e8f0' }}>{data.recommendations}</span>
          </div>
        )}
        {data.matched_skills?.length > 0 && (
          <div style={{ marginBottom: 16 }}>
            <h3 style={{ color: '#22c55e', marginBottom: 8, fontSize: '0.95rem' }}>Matched Skills</h3>
            <div>{data.matched_skills.filter(Boolean).map((s, i) => <SkillBadge key={i} skill={s} matched={true} />)}</div>
          </div>
        )}
        {data.missing_skills?.length > 0 && (
          <div style={{ marginBottom: 16 }}>
            <h3 style={{ color: '#ef4444', marginBottom: 8, fontSize: '0.95rem' }}>Missing Skills</h3>
            <div>{data.missing_skills.filter(Boolean).map((s, i) => <SkillBadge key={i} skill={s} matched={false} />)}</div>
          </div>
        )}
      </div>

      {parsed?.skills?.length > 0 && (
        <div style={{ background: '#1e293b', borderRadius: 16, padding: 24, border: '1px solid #334155', marginBottom: 24 }}>
          <h3 style={{ marginBottom: 12 }}>Extracted Skills</h3>
          <div>{parsed.skills.map((s, i) => <SkillBadge key={i} skill={s} />)}</div>
        </div>
      )}

      {parsed?.experience?.length > 0 && (
        <div style={{ background: '#1e293b', borderRadius: 16, padding: 24, border: '1px solid #334155', marginBottom: 24 }}>
          <h3 style={{ marginBottom: 12 }}>Experience</h3>
          {parsed.experience.map((exp, i) => (
            <div key={i} style={{ padding: '12px 0', borderBottom: i < parsed.experience.length - 1 ? '1px solid #334155' : 'none' }}>
              <div style={{ color: '#6366f1', fontSize: '0.85rem' }}>{exp.start_date} - {exp.end_date}</div>
              <p style={{ color: '#94a3b8', fontSize: '0.85rem', marginTop: 4 }}>{exp.context}</p>
            </div>
          ))}
        </div>
      )}

      {parsed?.projects?.length > 0 && (
        <div style={{ background: '#1e293b', borderRadius: 16, padding: 24, border: '1px solid #334155', marginBottom: 24 }}>
          <h3 style={{ marginBottom: 12 }}>Projects</h3>
          {parsed.projects.map((proj, i) => (
            <div key={i} style={{ padding: '8px 0', color: '#94a3b8', fontSize: '0.9rem' }}>• {proj.title || proj.description}</div>
          ))}
        </div>
      )}

      {parsed?.certifications?.length > 0 && (
        <div style={{ background: '#1e293b', borderRadius: 16, padding: 24, border: '1px solid #334155', marginBottom: 24 }}>
          <h3 style={{ marginBottom: 12 }}>Certifications</h3>
          {parsed.certifications.map((cert, i) => (
            <div key={i} style={{ color: '#94a3b8', fontSize: '0.9rem', padding: '4px 0' }}>• {cert}</div>
          ))}
        </div>
      )}
    </div>
  );
}
