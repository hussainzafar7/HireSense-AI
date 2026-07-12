import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const styles = {
  nav: { display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px 32px', background: '#1e293b', borderBottom: '1px solid #334155' },
  logo: { fontSize: '1.3rem', fontWeight: 700, color: '#6366f1', textDecoration: 'none' },
  span: { color: '#e2e8f0', fontWeight: 300 },
  links: { display: 'flex', gap: '24px', alignItems: 'center' },
  link: { color: '#cbd5e1', textDecoration: 'none', fontSize: '0.9rem', fontWeight: 500 },
  btn: { background: '#6366f1', color: '#fff', border: 'none', padding: '8px 16px', borderRadius: '8px', cursor: 'pointer', fontSize: '0.85rem', fontWeight: 600 },
  btnOut: { background: 'transparent', color: '#ef4444', border: '1px solid #ef4444', padding: '8px 16px', borderRadius: '8px', cursor: 'pointer', fontSize: '0.85rem', fontWeight: 600 },
};

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => { logout(); navigate('/login'); };

  return (
    <nav style={styles.nav}>
      <Link to="/" style={styles.logo}>HireSense <span style={styles.span}>AI</span></Link>
      <div style={styles.links}>
        <Link to="/jobs" style={styles.link}>Jobs</Link>
        {user?.role === 'company' && <Link to="/jobs/create" style={styles.link}>Post Job</Link>}
        {user?.role === 'candidate' && <Link to="/resume/upload" style={styles.link}>Upload Resume</Link>}
        {user?.role === 'candidate' && <Link to="/interview/start" style={styles.link}>Interview</Link>}
        {user?.role === 'company' && <Link to="/dashboard/company" style={styles.link}>Dashboard</Link>}
        {user?.role === 'candidate' && <Link to="/dashboard/candidate" style={styles.link}>Dashboard</Link>}
        {!user && <Link to="/login" style={styles.link}>Login</Link>}
        {!user && <Link to="/register/candidate" style={{ ...styles.btn, textDecoration: 'none' }}>Sign Up</Link>}
        {user && <button onClick={handleLogout} style={styles.btnOut}>Logout</button>}
      </div>
    </nav>
  );
}
