import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('authToken');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Products API
export const productsAPI = {
  getProducts: (params) => api.get('/products', { params }),
  getProduct: (id) => api.get(`/products/${id}`),
  updateProduct: (id, data) => api.put(`/products/${id}`, data),
  deleteProduct: (id) => api.delete(`/products/${id}`),
  syncShopify: () => api.post('/products/sync-shopify'),
};

// Users API
export const usersAPI = {
  getUsers: (params) => api.get('/users', { params }),
  getUser: (id) => api.get(`/users/${id}`),
  createUser: (data) => api.post('/users', data),
  updateUser: (id, data) => api.put(`/users/${id}`, data),
  deleteUser: (id) => api.delete(`/users/${id}`),
  activateUser: (id) => api.post(`/users/${id}/activate`),
  deactivateUser: (id) => api.post(`/users/${id}/deactivate`),
};

// Logs API
export const logsAPI = {
  getLogs: (params) => api.get('/logs', { params }),
  getRealtimeLogs: (params) => api.get('/logs/realtime', { params }),
  getLogStats: (params) => api.get('/logs/stats', { params }),
  getErrorLogs: (params) => api.get('/logs/errors', { params }),
  clearLogs: (params) => api.delete('/logs', { params }),
  exportLogs: (params) => api.get('/logs/export', { params }),
};

// AliExpress API
export const aliexpressAPI = {
  searchProducts: (params) => api.get('/aliexpress/search', { params }),
  getTrendingProducts: (params) => api.get('/aliexpress/trending', { params }),
  getProductDetail: (id) => api.get(`/aliexpress/product/${id}`),
  importProduct: (productId) => api.post('/aliexpress/import', { product_id: productId }),
  importBatch: (productIds) => api.post('/aliexpress/import-batch', { product_ids: productIds }),
  getImportStatus: () => api.get('/aliexpress/import-status'),
};

// SNS API
export const snsAPI = {
  getSNSContent: (productId, params) => api.get(`/sns/content/${productId}`, { params }),
  generateSNSContent: (productId, data) => api.post(`/sns/generate/${productId}`, data),
  updateSNSContent: (contentId, data) => api.put(`/sns/content/${contentId}`, data),
  regenerateSNSContent: (contentId) => api.post(`/sns/content/${contentId}/regenerate`),
  getPlatforms: () => api.get('/sns/platforms'),
  getAnalytics: (params) => api.get('/sns/analytics', { params }),
};

// Dashboard API
export const dashboardAPI = {
  getStats: () => api.get('/dashboard/stats'),
  getRecentActivity: () => api.get('/dashboard/recent-activity'),
};

// Health check
export const healthAPI = {
  check: () => api.get('/health'),
};

// Main API object
const mainAPI = {
  products: productsAPI,
  users: usersAPI,
  logs: logsAPI,
  aliexpress: aliexpressAPI,
  sns: snsAPI,
  dashboard: dashboardAPI,
  health: healthAPI,
  
  // Convenience methods
  getDashboardStats: dashboardAPI.getStats,
  getProducts: productsAPI.getProducts,
  getUsers: usersAPI.getUsers,
  getLogs: logsAPI.getLogs,
};

export default mainAPI;
