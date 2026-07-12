import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import interviewService from '../services/interviewService';
import resumeService from '../services/resumeService';
import dashboardService from '../services/dashboardService';
import ScoreGauge from '../components/ScoreGauge';
import HiringFunnel from '../components/HiringFunnel';

export default function Reports() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [interviews, setInterviews] = useState([]);
  const [resumes, setResumes] = useState([]);
  const [dashboard, setDashboard] = useState(null);
  const [funnel, setFunnel] = useState(null);
  const [tab, setTab] = useState('interviews');

  useEffect(() => {
    interviewService.getHistory().then(setInterviews).catch(() => {});
    resumeService.getMine().then(setResumes).catch(() => {});
    if (user?.role === 'company') {
      dashboardService.company().then(setDashboard);
      dashboardService.funnel().then(setFunnel);
    } else {
      dashboardService.candidate().then(setDashboard);
    }
  }, [user]);

  const cardStyle = { background: '#1e293b', borderRadius: 16, padding: 24, border: '1px solid #334155', marginBottom: 16 };

  return (
    <div style={{ padding: 32, maxWidth: 900, margin: '0 auto' }}>
      <h2 style={{ marginBottom: 24 }}>Reports & Analytics</h2>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 24 }}>
        {['interviews', 'resumes', 'dashboard'].filter(t => t !== 'dashboard' || user).map(t => (
          <button key={t} onClick={() => setTab(t)} style={{
            padding: '8px 20px', borderRadius: 8, border: 'none', cursor: 'pointer', textTransform: 'capitalize',
            background: tab === t ? '#6366f1' : '#1e293b', color: '#fff', fontWeight: 500, fontSize: '0.85rem',
          }}>{t}</button>
        ))}
      </div>

      {tab === 'interviews' && (
        <div>
          <h3 style={{ marginBottom: 16, color: '#94a3b8', fontSize: '0.95rem' }}>Interview History</h3>
          {interviews.length === 0 ? (
            <div style={cardStyle}><p style={{ color: '#64748b', textAlign: 'center' }}>No interviews yet</p></div>
          ) : (
            interviews.map((iv, i) => (
              <div key={i} onClick={() => navigate(`/interview/result/${iv.id}`)} style={{ ...cardStyle, cursor: 'pointer' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <div style={{ color: '#e2e8f0', fontWeight: 600 }}>{iv.job_title || 'General Interview'}</div>
                    <div style={{ color: '#64748b', fontSize: '0.85rem' }}>
                      {iv.total_questions} questions · {iv.answered_questions} answered · {new Date(iv.started_at).toLocaleDateString()}
                    </div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '1.2rem', fontWeight: 700, color: iv.overall_score >= 80 ? '#22c55e' : iv.overall_score >= 60 ? '#eab308' : '#ef4444' }}>{iv.overall_score.toFixed(0)}%</div>
                    <span style={{ padding: '2px 10px', borderRadius: 12, fontSize: '0.75rem', background: iv.recommendation === 'highly_recommended' ? '#22c55e22' : iv.recommendation === 'recommended' ? '#6366f122' : '#eab30822', color: iv.recommendation === 'highly_recommended' ? '#22c55e' : iv.recommendation === 'recommended' ? '#6366f1' : '#eab308' }}>{iv.recommendation?.replace(/_/g, ' ')}</span>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {tab === 'resumes' && (
        <div>
          <h3 style={{ marginBottom: 16, color: '#94a3b8', fontSize: '0.95rem' }}>Resume History</h3>
          {resumes.length === 0 ? (
            <div style={cardStyle}><p style={{ color: '#64748b', textAlign: 'center' }}>No resumes uploaded</p></div>
          ) : (
            resumes.map((r, i) => (
              <div key={i} onClick={() => navigate(`/resume/${r.id}`)} style={{ ...cardStyle, cursor: 'pointer' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <div style={{ color: '#e2e8f0', fontWeight: 600 }}>{r.original_filename}</div>
                    <div style={{ color: '#64748b', fontSize: '0.85rem' }}>{r.job_title || 'No job'} · {new Date(r.created_at).toLocaleDateString()}</div>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <span style={{ fontWeight: 700, color: r.ats_score >= 80 ? '#22c55e' : r.ats_score >= 60 ? '#eab308' : '#ef4444' }}>{r.ats_score.toFixed(0)}%</span>
                    <span style={{ padding: '2px 10px', borderRadius: 12, fontSize: '0.75rem', background: r.status === 'matched' ? '#22c55e22' : '#6366f122', color: r.status === 'matched' ? '#22c55e' : '#6366f1' }}>{r.status}</span>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {tab === 'dashboard' && dashboard && (
        <div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: 16, marginBottom: 24 }}>
            {user?.role === 'company' ? [
              { label: 'Total Jobs', value: dashboard.total_jobs },
              { label: 'Open Jobs', value: dashboard.open_jobs },
              { label: 'Applications', value: dashboard.total_applications },
              { label: 'Interviews', value: dashboard.total_interviews },
            ] : [
              { label: 'Resumes', value: dashboard.total_resumes },
              { label: 'Applications', value: dashboard.total_applications },
              { label: 'Interviews', value: dashboard.total_interviews },
            ].map((s, i) => (
              <div key={i} style={{ background: '#1e293b', padding: 20, borderRadius: 12, border: '1px solid #334155', textAlign: 'center' }}>
                <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#6366f1' }}>{s.value}</div>
                <div style={{ color: '#94a3b8', fontSize: '0.8rem' }}>{s.label}</div>
              </div>
            ))}
          </div>

          {user?.role === 'company' && (
            <div style={{ display: 'flex', gap: 24, justifyContent: 'center', marginBottom: 24 }}>
              <ScoreGauge score={dashboard.avg_ats_score || 0} size={140} label="Avg ATS" />
              <ScoreGauge score={dashboard.avg_interview_score || 0} size={140} label="Avg Interview" color="#8b5cf6" />
            </div>
          )}

          {user?.role === 'candidate' && (
            <div style={{ display: 'flex', gap: 24, justifyContent: 'center', marginBottom: 24 }}>
              <ScoreGauge score={dashboard.best_ats_score || 0} size={140} label="Best ATS" />
              <ScoreGauge score={dashboard.best_interview_score || 0} size={140} label="Best Interview" color="#8b5cf6" />
            </div>
          )}

          {funnel && <HiringFunnel data={funnel} />}
        </div>
      )}
    </div>
  );
}
