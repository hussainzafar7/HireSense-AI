import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Navbar from './components/Navbar';
import Login from './pages/Login';
import RegisterCandidate from './pages/RegisterCandidate';
import RegisterCompany from './pages/RegisterCompany';
import Home from './pages/Home';
import JobList from './pages/JobList';
import JobDetails from './pages/JobDetails';
import CreateJob from './pages/CreateJob';
import UploadResume from './pages/UploadResume';
import AnalysisResult from './pages/AnalysisResult';
import MatchResult from './pages/MatchResult';
import StartInterview from './pages/StartInterview';
import InterviewRoom from './pages/InterviewRoom';
import InterviewResult from './pages/InterviewResult';
import CandidateDashboard from './pages/CandidateDashboard';
import CompanyDashboard from './pages/CompanyDashboard';
import Reports from './pages/Reports';

const ProtectedRoute = ({ children, allowedRoles }) => {
  const { user, loading } = useAuth();
  if (loading) return <div style={{ padding: 40, textAlign: 'center', color: '#94a3b8' }}>Loading...</div>;
  if (!user) return <Navigate to="/login" replace />;
  if (allowedRoles && !allowedRoles.includes(user.role)) return <Navigate to="/" replace />;
  return children;
};

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Navbar />
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register/candidate" element={<RegisterCandidate />} />
          <Route path="/register/company" element={<RegisterCompany />} />
          <Route path="/" element={<Home />} />
          <Route path="/jobs" element={<JobList />} />
          <Route path="/jobs/:id" element={<JobDetails />} />
          <Route path="/jobs/create" element={<ProtectedRoute allowedRoles={['company']}><CreateJob /></ProtectedRoute>} />
          <Route path="/dashboard/company" element={<ProtectedRoute allowedRoles={['company']}><CompanyDashboard /></ProtectedRoute>} />
          <Route path="/dashboard/candidate" element={<ProtectedRoute allowedRoles={['candidate']}><CandidateDashboard /></ProtectedRoute>} />
          <Route path="/resume/upload" element={<ProtectedRoute allowedRoles={['candidate']}><UploadResume /></ProtectedRoute>} />
          <Route path="/resume/:id" element={<AnalysisResult />} />
          <Route path="/match/:jobId" element={<ProtectedRoute allowedRoles={['candidate']}><MatchResult /></ProtectedRoute>} />
          <Route path="/interview/start" element={<ProtectedRoute allowedRoles={['candidate']}><StartInterview /></ProtectedRoute>} />
          <Route path="/interview/room/:id" element={<ProtectedRoute allowedRoles={['candidate']}><InterviewRoom /></ProtectedRoute>} />
          <Route path="/interview/result/:id" element={<InterviewResult />} />
          <Route path="/reports" element={<ProtectedRoute><Reports /></ProtectedRoute>} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
