import apiClient from './apiClient';

const authService = {
  login: async (email, password) => {
    const res = await apiClient.post('/auth/login', { email, password });
    return res.data;
  },
  register: async (role, formData) => {
    const endpoint = role === 'candidate' ? '/auth/register/candidate' : '/auth/register/company';
    const res = await apiClient.post(endpoint, formData);
    return res.data;
  },
  getMe: async () => {
    const res = await apiClient.get('/auth/me');
    return res.data;
  },
};

export default authService;
