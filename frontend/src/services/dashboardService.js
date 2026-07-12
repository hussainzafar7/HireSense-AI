import apiClient from './apiClient';

const dashboardService = {
  company: async () => {
    const res = await apiClient.get('/dashboard/company');
    return res.data;
  },
  candidate: async () => {
    const res = await apiClient.get('/dashboard/candidate');
    return res.data;
  },
  funnel: async () => {
    const res = await apiClient.get('/dashboard/report/funnel');
    return res.data;
  },
};

export default dashboardService;
