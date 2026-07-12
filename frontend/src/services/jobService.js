import apiClient from './apiClient';

const jobService = {
  list: async (filters = {}) => {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([k, v]) => { if (v) params.append(k, v); });
    const res = await apiClient.get(`/jobs?${params.toString()}`);
    return res.data;
  },
  getMine: async () => {
    const res = await apiClient.get('/jobs/mine');
    return res.data;
  },
  getById: async (id) => {
    const res = await apiClient.get(`/jobs/${id}`);
    return res.data;
  },
  create: async (data) => {
    const res = await apiClient.post('/jobs', data);
    return res.data;
  },
  update: async (id, data) => {
    const res = await apiClient.put(`/jobs/${id}`, data);
    return res.data;
  },
  close: async (id) => {
    const res = await apiClient.delete(`/jobs/${id}`);
    return res.data;
  },
};

export default jobService;
