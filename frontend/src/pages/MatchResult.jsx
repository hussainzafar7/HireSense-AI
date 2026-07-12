import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import resumeService from '../services/resumeService';
import ScoreGauge from '../components/ScoreGauge';
import SkillBadge from '../components/SkillBadge';

export default function MatchResult() {
  const { jobId } = useParams();
  const navigate = useNavigate();
  const [data, setData] = useState(null);

  useEffect(() => {
    resumeService.match(jobId).then(setData).catch(() => {});
  }, [jobId]);

  if (!data) return <div style={{ padding: 40, textAlign: 'center', color: '#64748b' }}>Analyzing your resume against the job...</div>;

  return (
    <div style={{ padding: 32, maxWidth: 800, margin: '0 auto' }}>
      <div style={{ background: '#1e293b', borderRadius: 16, padding: 32, border: '1px solid #334155', marginBottom: 24 }}>
        <h2 style={{ marginBottom: 20 }}>ATS Match Results</h2>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 24, justifyContent: 'center', marginBottom: 24 }}>
          <ScoreGauge score={data.ats_score || 0} size={160} label="Overall ATS" />
          <ScoreGauge score={data.skill_match_score || 0} size={120} label="Skills" color="#8b5cf6" />
          <ScoreGauge score={data.experience_match_score || 0} size={120} label="Experience" color="#a855f7" />
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: 12, marginBottom: 20 }}>
          {[
            { label: 'Skills Match', score: data.skill_match_score },
            { label: 'Experience', score: data.experience_match_score },
            { label: 'Projects', score: data.project_match_score },
            { label: 'Certifications', score: data.certification_match_score },
            { label: 'Keywords', score: data.keyword_match_score },
          ].map((item, i) => (
            <div key={i} style={{ background: '#0f0f1a', padding: 12, borderRadius: 8, textAlign: 'center' }}>
              <div style={{ fontSize: '1.1rem', fontWeight: 700, color: item.score >= 80 ? '#22c55e' : item.score >= 60 ? '#eab308' : '#ef4444' }}>
                {item.score.toFixed(0)}%
              </div>
              <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: 4 }}>{item.label}</div>
            </div>
          ))}
        </div>

        {data.recommendations && (
          <div style={{ padding: '12px 16px', borderRadius: 8, background: '#0f0f1a', marginBottom: 20, border: '1px solid #334155' }}>
            <span style={{ color: '#6366f1', fontWeight: 600 }}>Verdict: </span>
            <span style={{ color: '#e2e8f0' }}>{data.recommendations}</span>
          </div>
        )}

        {data.matched_skills?.length > 0 && (
          <div style={{ marginBottom: 16 }}>
            <h3 style={{ color: '#22c55e', marginBottom: 8, fontSize: '0.95rem' }}>Matched Skills ({data.matched_skills.length})</h3>
            <div>{data.matched_skills.filter(Boolean).map((s, i) => <SkillBadge key={i} skill={s} matched={true} />)}</div>
          </div>
        )}

        {data.missing_skills?.length > 0 && (
          <div style={{ marginBottom: 20 }}>
            <h3 style={{ color: '#ef4444', marginBottom: 8, fontSize: '0.95rem' }}>Missing Skills ({data.missing_skills.length})</h3>
            <div>{data.missing_skills.filter(Boolean).map((s, i) => <SkillBadge key={i} skill={s} matched={false} />)}</div>
          </div>
        )}

        <div style={{ display: 'flex', gap: 12 }}>
          <button onClick={() => navigate(`/interview/start?jobId=${jobId}`)} style={{ flex: 1, padding: '12px', background: '#6366f1', color: '#fff', border: 'none', borderRadius: 8, fontWeight: 600, cursor: 'pointer' }}>
            Start Interview
          </button>
          <button onClick={() => navigate(`/resume/upload?jobId=${jobId}`)} style={{ flex: 1, padding: '12px', background: 'transparent', color: '#6366f1', border: '1px solid #6366f1', borderRadius: 8, fontWeight: 600, cursor: 'pointer' }}>
            Re-upload Resume
          </button>
        </div>
      </div>
    </div>
  );
}
