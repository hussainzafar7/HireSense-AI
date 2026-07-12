import apiClient from './apiClient';

const interviewService = {
  start: async (jobId, resumeId) => {
    const res = await apiClient.post('/interview-room/start', { job_id: jobId, resume_id: resumeId });
    return res.data;
  },
  submitAnswer: async (interviewId, questionId, answerText) => {
    const res = await apiClient.post('/interview-room/submit-answer', {
      interview_id: interviewId, question_id: questionId, answer_text: answerText,
    });
    return res.data;
  },
  skip: async (interviewId, questionId) => {
    const res = await apiClient.post('/interview-room/skip', { interview_id: interviewId, question_id: questionId });
    return res.data;
  },
  complete: async (interviewId) => {
    const res = await apiClient.post('/interview-room/complete', { interview_id: interviewId });
    return res.data;
  },
  getState: async (id) => {
    const res = await apiClient.get(`/interview-room/state/${id}`);
    return res.data;
  },
  getTranscript: async (id) => {
    const res = await apiClient.get(`/interview-room/transcript/${id}`);
    return res.data;
  },
  getReport: async (id) => {
    const res = await apiClient.get(`/interview-room/report/${id}`);
    return res.data;
  },
  exportPdf: async (id) => {
    const res = await apiClient.post(`/interview-room/export-pdf/${id}`, {}, { responseType: 'blob' });
    const url = window.URL.createObjectURL(new Blob([res.data], { type: 'application/pdf' }));
    const a = document.createElement('a');
    a.href = url; a.download = `hiresense_report_${id}.pdf`;
    a.click(); window.URL.revokeObjectURL(url);
  },
  getHistory: async () => {
    const res = await apiClient.get('/interview/history');
    return res.data;
  },
};

export default interviewService;
