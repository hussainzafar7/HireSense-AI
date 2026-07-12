import React, { useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import resumeService from '../services/resumeService';

export default function UploadResume() {
  const [searchParams] = useSearchParams();
  const jobId = searchParams.get('jobId');
  const navigate = useNavigate();
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;
    setUploading(true); setError('');
    try {
      const res = await resumeService.upload(file, jobId ? parseInt(jobId) : null);
      setResult(res);
      if (jobId) navigate(`/match/${jobId}`);
      else navigate(`/resume/${res.resume_id}`);
    } catch (err) { setError(err.response?.data?.error || 'Upload failed'); }
    setUploading(false);
  };

  return (
    <div style={{ minHeight: 'calc(100vh - 60px)', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 20 }}>
      <div style={{ background: '#1e293b', padding: 40, borderRadius: 16, width: '100%', maxWidth: 500, border: '1px solid #334155' }}>
        <h2 style={{ marginBottom: 8 }}>Upload Resume</h2>
        <p style={{ color: '#94a3b8', marginBottom: 24, fontSize: '0.9rem' }}>Supported: PDF, DOCX, TXT (max 16MB)</p>
        {error && <div style={{ background: '#ef444422', color: '#ef4444', padding: '10px 16px', borderRadius: 8, marginBottom: 16 }}>{error}</div>}
        {result && (
          <div style={{ background: '#22c55e22', color: '#22c55e', padding: '12px 16px', borderRadius: 8, marginBottom: 16 }}>
            Resume uploaded! ATS Score: {result.ats_score?.toFixed(0) || 'Pending'}
          </div>
        )}
        <form onSubmit={handleSubmit}>
          <div style={{
            border: '2px dashed #334155', borderRadius: 12, padding: 40, textAlign: 'center',
            cursor: 'pointer', marginBottom: 20,
          }} onClick={() => document.getElementById('file-input').click()}>
            <div style={{ fontSize: '2rem', marginBottom: 8 }}>📄</div>
            <p style={{ color: '#94a3b8' }}>{file ? file.name : 'Click to select or drag a file'}</p>
            <input id="file-input" type="file" accept=".pdf,.docx,.txt" onChange={e => setFile(e.target.files[0])} style={{ display: 'none' }} />
          </div>
          <button type="submit" disabled={!file || uploading} style={{
            width: '100%', padding: '12px', background: file && !uploading ? '#6366f1' : '#334155', color: '#fff',
            border: 'none', borderRadius: 8, fontSize: '0.95rem', fontWeight: 600, cursor: file && !uploading ? 'pointer' : 'not-allowed',
          }}>
            {uploading ? 'Uploading...' : 'Upload & Analyze'}
          </button>
        </form>
      </div>
    </div>
  );
}
