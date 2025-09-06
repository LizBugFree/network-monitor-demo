import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8080/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error.response?.data || { error: 'Network error' });
  }
);

// Network API calls
export const networkAPI = {
  getTopology: (projectId) => 
    api.get('/network/topology', { params: { project_id: projectId } }),
  
  getResources: (projectId, resourceType) => 
    api.get('/network/resources', { 
      params: { 
        project_id: projectId, 
        type: resourceType 
      } 
    }),
};

// Metrics API calls
export const metricsAPI = {
  getTimeSeries: (resourceType, hours = 24) =>
    api.get('/metrics/timeseries', { 
      params: { 
        type: resourceType, 
        hours 
      } 
    }),
    
  getSummary: () =>
    api.get('/metrics/summary'),
    
  getCosts: (days = 30) =>
    api.get('/metrics/costs', { params: { days } }),
};

export default api;