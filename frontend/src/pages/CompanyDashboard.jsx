import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import dashboardService from '../services/dashboardService';
import ScoreGauge from '../components/ScoreGauge';
import HiringFunnel from '../components/HiringFunnel';

export default function CompanyDashboard() {
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [funnel, setFunnel] = useState(null);

  useEffect(() => {
    dashboardService.company().then(setData).catch(() => {});
    dashboardService.funnel().then(setFunnel).catch(() => {});
  }, []);

  if (!data) return <div style={{ padding: 40, textAlign: 'center', color: '#64748b' }}>Loading dashboard...</div>;

  return (
    <div style={{ padding: 32, maxWidth: 1100, margin: '0 auto' }}>
      <h2 style={{ marginBottom: 24 }}>Company Dashboard</h2>

      {/* Stats Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 16, marginBottom: 32 }}>
        {[
          { label: 'Total Jobs', value: data.total_jobs, color: '#6366f1' },
          { label: 'Open Jobs', value: data.open_jobs, color: '#22c55e' },
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
          <ScoreGauge score={data.avg_ats_score || 0} size={160} label="Avg ATS" color="#6366f1" />
        </div>
        <div style={{ background: '#1e293b', padding: 24, borderRadius: 16, border: '1px solid #334155' }}>
          <ScoreGauge score={data.avg_interview_score || 0} size={160} label="Avg Interview" color="#8b5cf6" />
        </div>
      </div>

      {/* Hiring Funnel */}
      {funnel && <div style={{ marginBottom: 32 }}><HiringFunnel data={funnel} /></div>}

      {/* Top 5 Candidates */}
      {data.top_candidates?.length > 0 && (
        <div style={{ background: '#1e293b', borderRadius: 16, padding: 24, border: '1px solid #334155', marginBottom: 24 }}>
          <h3 style={{ marginBottom: 16 }}>Top Candidates by ATS</h3>
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid #334155' }}>
                  <th style={{ textAlign: 'left', padding: '10px 12px', color: '#64748b', fontWeight: 500 }}>Name</th>
                  <th style={{ textAlign: 'center', padding: '10px 12px', color: '#64748b', fontWeight: 500 }}>ATS Score</th>
                  <th style={{ textAlign: 'left', padding: '10px 12px', color: '#64748b', fontWeight: 500 }}>Matched Skills</th>
                  <th style={{ textAlign: 'left', padding: '10px 12px', color: '#64748b', fontWeight: 500 }}>Missing Skills</th>
                </tr>
              </thead>
              <tbody>
                {data.top_candidates.map((c, i) => (
                  <tr key={i} style={{ borderBottom: '1px solid #1e293b' }}>
                    <td style={{ padding: '10px 12px', color: '#e2e8f0', fontWeight: 500 }}>{c.name || 'Candidate'}</td>
                    <td style={{ padding: '10px 12px', textAlign: 'center', color: c.ats_score >= 80 ? '#22c55e' : c.ats_score >= 60 ? '#eab308' : '#ef4444', fontWeight: 700 }}>{c.ats_score.toFixed(0)}%</td>
                    <td style={{ padding: '10px 12px', color: '#22c55e', fontSize: '0.8rem' }}>{c.matched_skills?.filter(Boolean).slice(0, 3).join(', ')}</td>
                    <td style={{ padding: '10px 12px', color: '#ef4444', fontSize: '0.8rem' }}>{c.missing_skills?.filter(Boolean).slice(0, 3).join(', ') || '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Per-Job Breakdown */}
      {data.per_job_breakdown?.length > 0 && (
        <div style={{ background: '#1e293b', borderRadius: 16, padding: 24, border: '1px solid #334155', marginBottom: 24 }}>
          <h3 style={{ marginBottom: 16 }}>Per-Job Breakdown</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {data.per_job_breakdown.map((j, i) => (
              <div key={i} onClick={() => navigate(`/jobs/${j.job_id}`)} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 16px', background: '#0f0f1a', borderRadius: 8, cursor: 'pointer' }}>
                <div>
                  <div style={{ color: '#e2e8f0', fontWeight: 500, fontSize: '0.9rem' }}>{j.title}</div>
                  <span style={{ padding: '2px 8px', borderRadius: 8, background: j.status === 'open' ? '#22c55e22' : '#64748b22', color: j.status === 'open' ? '#22c55e' : '#64748b', fontSize: '0.75rem' }}>{j.status}</span>
                </div>
                <div style={{ display: 'flex', gap: 24 }}>
                  <div style={{ textAlign: 'center' }}><div style={{ color: '#6366f1', fontWeight: 600 }}>{j.applications}</div><div style={{ color: '#64748b', fontSize: '0.75rem' }}>Apps</div></div>
                  <div style={{ textAlign: 'center' }}><div style={{ color: '#8b5cf6', fontWeight: 600 }}>{j.interviews}</div><div style={{ color: '#64748b', fontSize: '0.75rem' }}>Interviews</div></div>
                  <div style={{ textAlign: 'center' }}><div style={{ color: j.avg_ats >= 80 ? '#22c55e' : j.avg_ats >= 60 ? '#eab308' : '#ef4444', fontWeight: 600 }}>{j.avg_ats.toFixed(0)}%</div><div style={{ color: '#64748b', fontSize: '0.75rem' }}>Avg ATS</div></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Actions */}
      <div style={{ display: 'flex', gap: 12 }}>
        <button onClick={() => navigate('/jobs/create')} style={{ flex: 1, padding: '14px', background: '#6366f1', color: '#fff', border: 'none', borderRadius: 8, fontWeight: 600, cursor: 'pointer' }}>
          Post New Job
        </button>
        <button onClick={() => navigate('/jobs')} style={{ flex: 1, padding: '14px', background: '#1e293b', color: '#6366f1', border: '1px solid #6366f1', borderRadius: 8, fontWeight: 600, cursor: 'pointer' }}>
          View All Jobs
        </button>
      </div>
    </div>
  );
}
