import axios from 'axios';

// Dynamic API base URL for local network access
const getApiBaseUrl = () => {
  // If running in development with a specific backend URL
  if (process.env.REACT_APP_API_URL) {
    return process.env.REACT_APP_API_URL;
  }
  
  // For production, use the same host as the frontend
  if (process.env.NODE_ENV === 'production') {
    return `${window.location.protocol}//${window.location.host}/api`;
  }
  
  // For development, try to detect the backend server
  // Default to localhost, but allow override via environment
  const backendHost = process.env.REACT_APP_BACKEND_HOST || window.location.hostname;
  const backendPort = process.env.REACT_APP_BACKEND_PORT || '5000';
  return `http://${backendHost}:${backendPort}/api`;
};

const API_BASE_URL = getApiBaseUrl();

// Configure axios defaults
axios.defaults.withCredentials = true;

const api = {
  // Authentication
  register: (userData) => axios.post(`${API_BASE_URL}/register`, userData),
  login: (credentials) => axios.post(`${API_BASE_URL}/login`, credentials),
  logout: () => axios.post(`${API_BASE_URL}/logout`),
  getCurrentUser: () => axios.get(`${API_BASE_URL}/user`),

  // User management
  changePassword: (data) => axios.post(`${API_BASE_URL}/user/change-password`, data),
  setup2FA: () => axios.post(`${API_BASE_URL}/user/2fa/setup`),
  verify2FA: (data) => axios.post(`${API_BASE_URL}/user/2fa/verify`, data),
  disable2FA: (data) => axios.post(`${API_BASE_URL}/user/2fa/disable`, data),

  // Screen management
  getScreens: () => axios.get(`${API_BASE_URL}/screens`),
  addScreen: (screenData) => axios.post(`${API_BASE_URL}/screens`, screenData),
  updateScreen: (screenId, data) => axios.put(`${API_BASE_URL}/screens/${screenId}`, data),
  deleteScreen: (screenId) => axios.delete(`${API_BASE_URL}/screens/${screenId}`),
  unbindScreen: (screenId) => axios.post(`${API_BASE_URL}/screens/${screenId}/unbind`),
  getScreenData: (screenId) => axios.get(`${API_BASE_URL}/screens/${screenId}/data`),

  // Admin endpoints
  getUsers: () => axios.get(`${API_BASE_URL}/admin/users`),
  toggleUserAdmin: (userId) => axios.post(`${API_BASE_URL}/admin/users/${userId}/toggle-admin`),
  createAdmin: (data) => axios.post(`${API_BASE_URL}/admin/create-admin`, data),
  unbindUserScreens: (userId) => axios.post(`${API_BASE_URL}/admin/users/${userId}/unbind-screens`),
  resetUserPassword: (userId, data) => axios.post(`${API_BASE_URL}/admin/users/${userId}/reset-password`, data),
  deleteUser: (userId) => axios.delete(`${API_BASE_URL}/admin/users/${userId}/delete`),

  // Device updates (for testing)
  deviceUpdate: (deviceData) => axios.post(`${API_BASE_URL}/device/update`, deviceData),
  
  // Controller registration
  controllerRegister: (data) => axios.post(`${API_BASE_URL}/controller/register`, data),

  // Settings management (admin only)
  getSettings: () => axios.get(`${API_BASE_URL}/admin/settings`),
  updateSettings: (settings) => axios.post(`${API_BASE_URL}/admin/settings`, settings),
};

export default api;