import apiClient from './apiClient';

const resumeService = {
  upload: async (file, jobId) => {
    const fd = new FormData();
    fd.append('file', file);
    if (jobId) fd.append('job_id', jobId);
    const res = await apiClient.post('/resume/upload', fd);
    return res.data;
  },
  match: async (jobId) => {
    const res = await apiClient.post(`/resume/match/${jobId}`);
    return res.data;
  },
  getMine: async () => {
    const res = await apiClient.get('/resume/mine');
    return res.data;
  },
  getById: async (id) => {
    const res = await apiClient.get(`/resume/${id}`);
    return res.data;
  },
  delete: async (id) => {
    const res = await apiClient.delete(`/resume/${id}`);
    return res.data;
  },
  getByJob: async (jobId) => {
    const res = await apiClient.get(`/resume/job/${jobId}`);
    return res.data;
  },
  getQualification: async (jobId) => {
    const res = await apiClient.get(`/resume/qualification/${jobId}`);
    return res.data;
  },
};

export default resumeService;
