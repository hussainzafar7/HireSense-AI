import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import jobService from '../services/jobService';

export default function JobList() {
  const [jobs, setJobs] = useState([]);
  const [filters, setFilters] = useState({ search: '', location: '', employment_type: '' });
  const navigate = useNavigate();

  useEffect(() => {
    jobService.list(filters).then(setJobs).catch(() => {});
  }, [filters]);

  return (
    <div style={{ padding: 32, maxWidth: 900, margin: '0 auto' }}>
      <h2 style={{ marginBottom: 20 }}>Open Positions</h2>
      <div style={{ display: 'flex', gap: 12, marginBottom: 24, flexWrap: 'wrap' }}>
        <input placeholder="Search jobs..." value={filters.search} onChange={e => setFilters({...filters, search: e.target.value})}
          style={{ padding: '10px 16px', background: '#1e293b', border: '1px solid #334155', borderRadius: 8, color: '#e2e8f0', flex: 1, minWidth: 200, fontSize: '0.85rem' }} />
        <input placeholder="Location" value={filters.location} onChange={e => setFilters({...filters, location: e.target.value})}
          style={{ padding: '10px 16px', background: '#1e293b', border: '1px solid #334155', borderRadius: 8, color: '#e2e8f0', width: 150, fontSize: '0.85rem' }} />
        <select value={filters.employment_type} onChange={e => setFilters({...filters, employment_type: e.target.value})}
          style={{ padding: '10px 16px', background: '#1e293b', border: '1px solid #334155', borderRadius: 8, color: '#e2e8f0', fontSize: '0.85rem' }}>
          <option value="">All Types</option>
          <option value="full-time">Full-time</option>
          <option value="part-time">Part-time</option>
          <option value="contract">Contract</option>
          <option value="internship">Internship</option>
        </select>
      </div>
      {jobs.length === 0 ? (
        <div style={{ textAlign: 'center', padding: 60, color: '#64748b' }}>No jobs found</div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          {jobs.map(job => (
            <div key={job.id} onClick={() => navigate(`/jobs/${job.id}`)} style={{ background: '#1e293b', padding: 20, borderRadius: 12, border: '1px solid #334155', cursor: 'pointer' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <h3 style={{ marginBottom: 4, color: '#e2e8f0' }}>{job.title}</h3>
                  <p style={{ color: '#94a3b8', fontSize: '0.85rem' }}>{job.company_name} · {job.location || 'Remote'} · {job.employment_type}</p>
                </div>
                <span style={{ padding: '4px 12px', borderRadius: 12, background: '#6366f122', color: '#6366f1', fontSize: '0.8rem', fontWeight: 600 }}>{job.experience_level || 'Any'}</span>
              </div>
              <div style={{ marginTop: 12, display: 'flex', gap: 8 }}>
                {job.salary_min && <span style={{ color: '#22c55e', fontSize: '0.85rem', fontWeight: 500 }}>${job.salary_min?.toLocaleString()} - ${job.salary_max?.toLocaleString()}</span>}
                {job.remote_allowed && <span style={{ color: '#06b6d4', fontSize: '0.85rem' }}>🌐 Remote OK</span>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
