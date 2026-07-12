import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Home() {
  const { user } = useAuth();

  return (
    <div style={{ minHeight: 'calc(100vh - 60px)' }}>
      <div style={{ textAlign: 'center', padding: '80px 20px 60px', background: 'linear-gradient(180deg, #1e293b 0%, #0f0f1a 100%)' }}>
        <h1 style={{ fontSize: '3rem', fontWeight: 800, marginBottom: 16, background: 'linear-gradient(135deg, #6366f1, #a855f7)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
          HireSense AI
        </h1>
        <p style={{ fontSize: '1.2rem', color: '#94a3b8', maxWidth: 600, margin: '0 auto 32px' }}>
          AI-powered recruitment platform with smart resume parsing, ATS scoring, and voice-based interviews.
        </p>
        {!user && (
          <div style={{ display: 'flex', gap: 16, justifyContent: 'center' }}>
            <Link to="/register/candidate" style={{ padding: '14px 32px', background: '#6366f1', color: '#fff', borderRadius: 10, textDecoration: 'none', fontWeight: 600 }}>I'm a Candidate</Link>
            <Link to="/register/company" style={{ padding: '14px 32px', background: 'transparent', color: '#6366f1', border: '2px solid #6366f1', borderRadius: 10, textDecoration: 'none', fontWeight: 600 }}>I'm a Company</Link>
          </div>
        )}
        {user && (
          <Link to={user.role === 'company' ? '/dashboard/company' : '/dashboard/candidate'} style={{ padding: '14px 32px', background: '#6366f1', color: '#fff', borderRadius: 10, textDecoration: 'none', fontWeight: 600, display: 'inline-block' }}>
            Go to Dashboard
          </Link>
        )}
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: 24, padding: '40px 20px', maxWidth: 1000, margin: '0 auto' }}>
        {[
          { title: 'Smart Resume Parsing', desc: 'Upload PDF/DOCX resumes. Our local AI extracts skills, experience, education, and projects using spaCy NLP.' },
          { title: 'ATS Score Engine', desc: 'Advanced matching algorithm evaluates resumes against job descriptions with weighted scoring and skill gap analysis.' },
          { title: 'Voice AI Interviews', desc: 'Browser-based voice interviews with speech recognition, text-to-speech, and real-time answer evaluation.' },
          { title: 'Detailed Reports', desc: 'Generate comprehensive PDF reports with score breakdowns, strengths/weaknesses, and hiring recommendations.' },
        ].map((f, i) => (
          <div key={i} style={{ background: '#1e293b', padding: 24, borderRadius: 12, border: '1px solid #334155' }}>
            <h3 style={{ marginBottom: 8, color: '#e2e8f0', fontSize: '1.05rem' }}>{f.title}</h3>
            <p style={{ color: '#94a3b8', fontSize: '0.9rem', lineHeight: 1.6 }}>{f.desc}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
