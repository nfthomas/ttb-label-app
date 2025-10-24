import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const verifyLabel = async (formData) => {
  try {
    const response = await api.post('/api/verify', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    if (error.response) {
      throw new Error(error.response.data.detail || 'Verification failed');
    }
    throw new Error('Network error occurred');
  }
};

export const healthCheck = () => api.get('/api/health');

export default api;