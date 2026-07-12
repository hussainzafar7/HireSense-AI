import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import jobService from '../services/jobService';
import resumeService from '../services/resumeService';

export default function JobDetails() {
  const { id } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [job, setJob] = useState(null);
  const [qual, setQual] = useState(null);

  useEffect(() => {
    jobService.getById(id).then(setJob);
    if (user?.role === 'candidate') {
      resumeService.getQualification(id).then(setQual).catch(() => {});
    }
  }, [id, user]);

  if (!job) return <div style={{ padding: 40, textAlign: 'center', color: '#64748b' }}>Loading...</div>;

  const handleApply = () => {
    if (job.ats_pass_threshold && qual && qual.ats_score >= job.ats_pass_threshold) {
      navigate(`/interview/start?jobId=${id}`);
    } else {
      navigate(`/resume/upload?jobId=${id}`);
    }
  };

  return (
    <div style={{ padding: 32, maxWidth: 800, margin: '0 auto' }}>
      <div style={{ background: '#1e293b', borderRadius: 16, padding: 32, border: '1px solid #334155' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 24 }}>
          <div>
            <h2 style={{ marginBottom: 4 }}>{job.title}</h2>
            <p style={{ color: '#94a3b8' }}>{job.company_name} · {job.location || 'Remote'} · {job.employment_type}</p>
          </div>
          {user?.role === 'candidate' && (
            <button onClick={handleApply} style={{ padding: '10px 24px', background: '#6366f1', color: '#fff', border: 'none', borderRadius: 8, fontWeight: 600, cursor: 'pointer', fontSize: '0.9rem' }}>
              {qual?.qualified ? 'Start Interview' : (qual?.ats_score ? `Apply (ATS: ${qual.ats_score.toFixed(0)})` : 'Upload Resume')}
            </button>
          )}
        </div>

        {qual && qual.ats_score > 0 && (
          <div style={{ marginBottom: 20, padding: '12px 16px', borderRadius: 8, background: qual.qualified ? '#22c55e22' : '#eab30822', border: `1px solid ${qual.qualified ? '#22c55e' : '#eab308'}` }}>
            <span style={{ color: qual.qualified ? '#22c55e' : '#eab308', fontWeight: 600 }}>ATS Score: {qual.ats_score.toFixed(0)}%</span>
            <span style={{ color: '#94a3b8', marginLeft: 8 }}> (Pass threshold: {qual.threshold}%)</span>
            {qual.qualified && <span style={{ color: '#22c55e', marginLeft: 8 }}> ✓ Qualified</span>}
          </div>
        )}

        {job.description && (
          <div style={{ marginBottom: 20 }}>
            <h3 style={{ color: '#e2e8f0', marginBottom: 8, fontSize: '1rem' }}>Description</h3>
            <p style={{ color: '#94a3b8', lineHeight: 1.7, fontSize: '0.9rem', whiteSpace: 'pre-wrap' }}>{job.description}</p>
          </div>
        )}

        {job.responsibilities && (
          <div style={{ marginBottom: 20 }}>
            <h3 style={{ color: '#e2e8f0', marginBottom: 8, fontSize: '1rem' }}>Responsibilities</h3>
            <p style={{ color: '#94a3b8', lineHeight: 1.7, fontSize: '0.9rem', whiteSpace: 'pre-wrap' }}>{job.responsibilities}</p>
          </div>
        )}

        {job.qualifications && (
          <div style={{ marginBottom: 20 }}>
            <h3 style={{ color: '#e2e8f0', marginBottom: 8, fontSize: '1rem' }}>Qualifications</h3>
            <p style={{ color: '#94a3b8', lineHeight: 1.7, fontSize: '0.9rem', whiteSpace: 'pre-wrap' }}>{job.qualifications}</p>
          </div>
        )}

        {job.required_skills && (
          <div style={{ marginBottom: 20 }}>
            <h3 style={{ color: '#e2e8f0', marginBottom: 8, fontSize: '1rem' }}>Required Skills</h3>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
              {job.required_skills.split(',').map((s, i) => (
                <span key={i} style={{ padding: '4px 12px', borderRadius: 20, background: '#6366f122', color: '#6366f1', fontSize: '0.8rem', border: '1px solid #6366f1' }}>{s.trim()}</span>
              ))}
            </div>
          </div>
        )}

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginTop: 20, padding: 20, background: '#0f0f1a', borderRadius: 12 }}>
          <div><span style={{ color: '#64748b', fontSize: '0.8rem' }}>Experience</span><div style={{ color: '#e2e8f0', fontWeight: 600 }}>{job.min_experience_years || 0}+ years</div></div>
          <div><span style={{ color: '#64748b', fontSize: '0.8rem' }}>Experience Level</span><div style={{ color: '#e2e8f0', fontWeight: 600 }}>{job.experience_level || 'Any'}</div></div>
          <div><span style={{ color: '#64748b', fontSize: '0.8rem' }}>Salary Range</span><div style={{ color: '#22c55e', fontWeight: 600 }}>{job.salary_min ? `$${job.salary_min?.toLocaleString()} - $${job.salary_max?.toLocaleString()}` : 'Not specified'}</div></div>
          <div><span style={{ color: '#64748b', fontSize: '0.8rem' }}>Remote</span><div style={{ color: '#06b6d4', fontWeight: 600 }}>{job.remote_allowed ? 'Allowed' : 'On-site'}</div></div>
        </div>
      </div>
    </div>
  );
}
