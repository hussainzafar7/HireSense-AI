import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import interviewService from '../services/interviewService';
import ScoreGauge from '../components/ScoreGauge';

export default function InterviewResult() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [report, setReport] = useState(null);
  const [transcript, setTranscript] = useState([]);

  useEffect(() => {
    interviewService.getReport(id).then(setReport);
    interviewService.getTranscript(id).then(d => setTranscript(d.transcript || []));
  }, [id]);

  if (!report) return <div style={{ padding: 40, textAlign: 'center', color: '#64748b' }}>Loading report...</div>;

  const score = report.overall_score || 0;
  const scoreColor = score >= 80 ? '#22c55e' : score >= 60 ? '#eab308' : '#ef4444';
  const recColor = report.recommendation === 'highly_recommended' ? '#22c55e' : report.recommendation === 'recommended' ? '#6366f1' : report.recommendation === 'consider_review' ? '#eab308' : '#ef4444';

  return (
    <div style={{ padding: 32, maxWidth: 800, margin: '0 auto' }}>
      {/* Header */}
      <div style={{ background: '#1e293b', borderRadius: 16, padding: 32, border: '1px solid #334155', marginBottom: 24, textAlign: 'center' }}>
        <h2 style={{ marginBottom: 16 }}>Interview Results</h2>
        <div style={{ display: 'flex', justifyContent: 'center', marginBottom: 20 }}>
          <ScoreGauge score={score} size={180} label="Overall Score" color={scoreColor} />
        </div>
        <div style={{ display: 'flex', gap: 24, justifyContent: 'center', marginBottom: 20, flexWrap: 'wrap' }}>
          {[
            { label: 'Technical', score: report.technical_score, color: '#6366f1' },
            { label: 'Communication', score: report.communication_score, color: '#8b5cf6' },
            { label: 'Confidence', score: report.confidence_score, color: '#a855f7' },
          ].map((s, i) => (
            <div key={i} style={{ background: '#0f0f1a', padding: '12px 24px', borderRadius: 12, minWidth: 120 }}>
              <div style={{ fontSize: '1.3rem', fontWeight: 700, color: s.score >= 80 ? '#22c55e' : s.score >= 60 ? '#eab308' : '#ef4444' }}>{s.score.toFixed(0)}%</div>
              <div style={{ color: '#94a3b8', fontSize: '0.8rem' }}>{s.label}</div>
            </div>
          ))}
        </div>
        <div style={{
          display: 'inline-block', padding: '8px 24px', borderRadius: 20, fontWeight: 600,
          background: `${recColor}22`, color: recColor, border: `1px solid ${recColor}`,
          marginBottom: 16,
        }}>
          {report.recommendation?.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
        </div>
        {report.summary && <p style={{ color: '#94a3b8', lineHeight: 1.7 }}>{report.summary}</p>}
      </div>

      {/* Strengths & Weaknesses */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 24 }}>
        {report.strengths?.length > 0 && (
          <div style={{ background: '#1e293b', padding: 24, borderRadius: 16, border: '1px solid #334155' }}>
            <h3 style={{ color: '#22c55e', marginBottom: 12, fontSize: '1rem' }}>Strengths</h3>
            {report.strengths.map((s, i) => <div key={i} style={{ color: '#94a3b8', padding: '4px 0', fontSize: '0.9rem' }}>✅ {s}</div>)}
          </div>
        )}
        {report.weaknesses?.length > 0 && (
          <div style={{ background: '#1e293b', padding: 24, borderRadius: 16, border: '1px solid #334155' }}>
            <h3 style={{ color: '#eab308', marginBottom: 12, fontSize: '1rem' }}>Areas for Improvement</h3>
            {report.weaknesses.map((w, i) => <div key={i} style={{ color: '#94a3b8', padding: '4px 0', fontSize: '0.9rem' }}>📝 {w}</div>)}
          </div>
        )}
      </div>

      {/* Transcript */}
      {transcript.length > 0 && (
        <div style={{ background: '#1e293b', borderRadius: 16, padding: 24, border: '1px solid #334155', marginBottom: 24 }}>
          <h3 style={{ marginBottom: 16 }}>Question Breakdown</h3>
          {transcript.map((item, i) => (
            <div key={i} style={{
              padding: '16px 0', borderBottom: i < transcript.length - 1 ? '1px solid #334155' : 'none',
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                <span style={{ color: '#6366f1', fontWeight: 600, fontSize: '0.9rem' }}>Q{i+1}: {item.type}</span>
                <span style={{ fontWeight: 600, color: item.score >= 80 ? '#22c55e' : item.score >= 60 ? '#eab308' : '#ef4444' }}>{item.score.toFixed(0)}%</span>
              </div>
              <p style={{ color: '#e2e8f0', fontSize: '0.9rem', marginBottom: 8 }}>{item.question}</p>
              {item.answer && <p style={{ color: '#94a3b8', fontSize: '0.85rem', marginBottom: 4 }}><span style={{ color: '#64748b' }}>Answer:</span> {item.answer}</p>}
              {item.feedback && <p style={{ color: '#64748b', fontSize: '0.8rem', fontStyle: 'italic' }}>{item.feedback}</p>}
            </div>
          ))}
        </div>
      )}

      {/* Actions */}
      <div style={{ display: 'flex', gap: 12, justifyContent: 'center' }}>
        <button onClick={() => interviewService.exportPdf(id)} style={{ padding: '12px 24px', background: '#6366f1', color: '#fff', border: 'none', borderRadius: 8, fontWeight: 600, cursor: 'pointer' }}>
          Download PDF Report
        </button>
        <button onClick={() => navigate('/interview/start')} style={{ padding: '12px 24px', background: 'transparent', color: '#6366f1', border: '1px solid #6366f1', borderRadius: 8, fontWeight: 600, cursor: 'pointer' }}>
          New Interview
        </button>
        <button onClick={() => navigate('/dashboard/candidate')} style={{ padding: '12px 24px', background: 'transparent', color: '#94a3b8', border: '1px solid #334155', borderRadius: 8, fontWeight: 600, cursor: 'pointer' }}>
          Dashboard
        </button>
      </div>
    </div>
  );
}
