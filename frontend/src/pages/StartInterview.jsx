import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import interviewService from '../services/interviewService';
import resumeService from '../services/resumeService';
import jobService from '../services/jobService';

export default function StartInterview() {
  const [searchParams] = useSearchParams();
  const jobId = searchParams.get('jobId');
  const navigate = useNavigate();
  const [resumes, setResumes] = useState([]);
  const [job, setJob] = useState(null);
  const [selectedResume, setSelectedResume] = useState('');
  const [starting, setStarting] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    resumeService.getMine().then(setResumes);
    if (jobId) jobService.getById(jobId).then(setJob);
  }, [jobId]);

  const handleStart = async () => {
    setStarting(true); setError('');
    try {
      const res = await interviewService.start(jobId ? parseInt(jobId) : null, selectedResume ? parseInt(selectedResume) : null);
      navigate(`/interview/room/${res.interview_id}`);
    } catch (err) { setError(err.response?.data?.error || 'Failed to start interview'); }
    setStarting(false);
  };

  return (
    <div style={{ minHeight: 'calc(100vh - 60px)', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 20 }}>
      <div style={{ background: '#1e293b', padding: 40, borderRadius: 16, width: '100%', maxWidth: 500, border: '1px solid #334155' }}>
        <h2 style={{ marginBottom: 8 }}>AI Interview</h2>
        <p style={{ color: '#94a3b8', marginBottom: 24, fontSize: '0.9rem' }}>
          {job ? `Position: ${job.title}` : 'General technical interview'}
        </p>
        {error && <div style={{ background: '#ef444422', color: '#ef4444', padding: '10px 16px', borderRadius: 8, marginBottom: 16 }}>{error}</div>}
        <div style={{ marginBottom: 24 }}>
          <label style={{ display: 'block', marginBottom: 8, color: '#94a3b8', fontSize: '0.85rem' }}>Select Resume (optional)</label>
          <select value={selectedResume} onChange={e => setSelectedResume(e.target.value)} style={{ width: '100%', padding: '12px 16px', background: '#0f0f1a', border: '1px solid #334155', borderRadius: 8, color: '#e2e8f0' }}>
            <option value="">No resume (general questions)</option>
            {resumes.map(r => (
              <option key={r.id} value={r.id}>{r.original_filename} {r.ats_score ? `(ATS: ${r.ats_score.toFixed(0)})` : ''}</option>
            ))}
          </select>
        </div>
        <div style={{ background: '#0f0f1a', padding: 16, borderRadius: 8, marginBottom: 24 }}>
          <p style={{ color: '#94a3b8', fontSize: '0.85rem', lineHeight: 1.6 }}>
            The interview consists of <strong style={{ color: '#e2e8f0' }}>10 questions</strong> based on your resume.
            You can use voice or text answers. Maximum 1 skip allowed.
            Estimated time: 15-20 minutes.
          </p>
        </div>
        <button onClick={handleStart} disabled={starting} style={{
          width: '100%', padding: '14px', background: starting ? '#334155' : '#6366f1', color: '#fff',
          border: 'none', borderRadius: 8, fontSize: '1rem', fontWeight: 600, cursor: starting ? 'not-allowed' : 'pointer',
        }}>
          {starting ? 'Starting...' : 'Start Interview'}
        </button>
      </div>
    </div>
  );
}
