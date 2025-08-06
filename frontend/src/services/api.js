import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

// Configure axios defaults
axios.defaults.withCredentials = true;

const api = {
  // Authentication
  register: (userData) => axios.post(`${API_BASE_URL}/register`, userData),
  login: (credentials) => axios.post(`${API_BASE_URL}/login`, credentials),
  logout: () => axios.post(`${API_BASE_URL}/logout`),
  getCurrentUser: () => axios.get(`${API_BASE_URL}/user`),

  // Screen management
  getScreens: () => axios.get(`${API_BASE_URL}/screens`),
  addScreen: (screenData) => axios.post(`${API_BASE_URL}/screens`, screenData),
  updateScreen: (screenId, data) => axios.put(`${API_BASE_URL}/screens/${screenId}`, data),
  deleteScreen: (screenId) => axios.delete(`${API_BASE_URL}/screens/${screenId}`),
  getScreenData: (screenId) => axios.get(`${API_BASE_URL}/screens/${screenId}/data`),

  // Device updates (for testing)
  deviceUpdate: (deviceData) => axios.post(`${API_BASE_URL}/device/update`, deviceData),
};

export default api;