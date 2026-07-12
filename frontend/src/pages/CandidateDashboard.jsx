import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import dashboardService from '../services/dashboardService';
import ScoreGauge from '../components/ScoreGauge';

export default function CandidateDashboard() {
  const navigate = useNavigate();
  const [data, setData] = useState(null);

  useEffect(() => { dashboardService.candidate().then(setData).catch(() => {}); }, []);

  if (!data) return <div style={{ padding: 40, textAlign: 'center', color: '#64748b' }}>Loading dashboard...</div>;

  return (
    <div style={{ padding: 32, maxWidth: 1000, margin: '0 auto' }}>
      <h2 style={{ marginBottom: 24 }}>Candidate Dashboard</h2>

      {/* Stats Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 16, marginBottom: 32 }}>
        {[
          { label: 'Total Resumes', value: data.total_resumes, color: '#6366f1' },
          { label: 'Applications', value: data.total_applications, color: '#8b5cf6' },
          { label: 'Interviews', value: data.total_interviews, color: '#a855f7' },
        ].map((s, i) => (
          <div key={i} style={{ background: '#1e293b', padding: 20, borderRadius: 12, border: '1px solid #334155', textAlign: 'center' }}>
            <div style={{ fontSize: '2rem', fontWeight: 800, color: s.color }}>{s.value}</div>
            <div style={{ color: '#94a3b8', fontSize: '0.85rem', marginTop: 4 }}>{s.label}</div>
          </div>
        ))}
      </div>

      {/* Score Gauges */}
      <div style={{ display: 'flex', gap: 32, justifyContent: 'center', marginBottom: 32, flexWrap: 'wrap' }}>
        <div style={{ background: '#1e293b', padding: 24, borderRadius: 16, border: '1px solid #334155' }}>
          <ScoreGauge score={data.best_ats_score || 0} size={160} label="Best ATS" color="#6366f1" />
          <div style={{ textAlign: 'center', marginTop: 8, color: '#64748b', fontSize: '0.8rem' }}>Avg: {data.avg_ats_score?.toFixed(0) || 0}%</div>
        </div>
        <div style={{ background: '#1e293b', padding: 24, borderRadius: 16, border: '1px solid #334155' }}>
          <ScoreGauge score={data.best_interview_score || 0} size={160} label="Best Interview" color="#8b5cf6" />
          <div style={{ textAlign: 'center', marginTop: 8, color: '#64748b', fontSize: '0.8rem' }}>Avg: {data.avg_interview_score?.toFixed(0) || 0}%</div>
        </div>
      </div>

      {/* Recent Applications */}
      {data.recent_applications?.length > 0 && (
        <div style={{ background: '#1e293b', borderRadius: 16, padding: 24, border: '1px solid #334155', marginBottom: 24 }}>
          <h3 style={{ marginBottom: 16 }}>Recent Applications</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {data.recent_applications.map((app, i) => (
              <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 16px', background: '#0f0f1a', borderRadius: 8 }}>
                <div>
                  <div style={{ color: '#e2e8f0', fontWeight: 500, fontSize: '0.9rem' }}>{app.job_title || 'General'}</div>
                  <div style={{ color: '#64748b', fontSize: '0.8rem' }}>{new Date(app.created_at).toLocaleDateString()}</div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <span style={{ fontWeight: 600, color: app.ats_score >= 80 ? '#22c55e' : app.ats_score >= 60 ? '#eab308' : '#ef4444' }}>
                    ATS: {app.ats_score.toFixed(0)}%
                  </span>
                  <span style={{ padding: '2px 10px', borderRadius: 12, background: app.status === 'matched' ? '#22c55e22' : '#6366f122', color: app.status === 'matched' ? '#22c55e' : '#6366f1', fontSize: '0.75rem' }}>{app.status}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recent Interviews */}
      {data.recent_interviews?.length > 0 && (
        <div style={{ background: '#1e293b', borderRadius: 16, padding: 24, border: '1px solid #334155', marginBottom: 24 }}>
          <h3 style={{ marginBottom: 16 }}>Recent Interviews</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {data.recent_interviews.map((iv, i) => (
              <div key={i} onClick={() => navigate(`/interview/result/${iv.interview_id}`)} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 16px', background: '#0f0f1a', borderRadius: 8, cursor: 'pointer' }}>
                <div>
                  <div style={{ color: '#e2e8f0', fontWeight: 500, fontSize: '0.9rem' }}>{iv.job_title || 'General'}</div>
                  <div style={{ color: '#64748b', fontSize: '0.8rem' }}>{new Date(iv.started_at).toLocaleDateString()}</div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <span style={{ fontWeight: 600, color: iv.overall_score >= 80 ? '#22c55e' : iv.overall_score >= 60 ? '#eab308' : '#ef4444' }}>
                    {iv.overall_score.toFixed(0)}%
                  </span>
                  <span style={{ padding: '2px 10px', borderRadius: 12, background: iv.status === 'completed' ? '#22c55e22' : '#eab30822', color: iv.status === 'completed' ? '#22c55e' : '#eab308', fontSize: '0.75rem' }}>{iv.status}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <div style={{ display: 'flex', gap: 12 }}>
        <button onClick={() => navigate('/resume/upload')} style={{ flex: 1, padding: '14px', background: '#6366f1', color: '#fff', border: 'none', borderRadius: 8, fontWeight: 600, cursor: 'pointer' }}>
          Upload Resume
        </button>
        <button onClick={() => navigate('/interview/start')} style={{ flex: 1, padding: '14px', background: '#1e293b', color: '#6366f1', border: '1px solid #6366f1', borderRadius: 8, fontWeight: 600, cursor: 'pointer' }}>
          Start Interview
        </button>
        <button onClick={() => navigate('/jobs')} style={{ flex: 1, padding: '14px', background: '#1e293b', color: '#94a3b8', border: '1px solid #334155', borderRadius: 8, fontWeight: 600, cursor: 'pointer' }}>
          Browse Jobs
        </button>
      </div>
    </div>
  );
}
