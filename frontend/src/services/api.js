import axios from 'axios';
import { API_CONFIG, API_ENDPOINTS } from '../utils/constants';

// Get API base URL
const API_BASE_URL = API_CONFIG.getBaseUrl();

// Configure axios defaults
axios.defaults.withCredentials = true;

const api = {
  // Authentication
  register: (userData) => axios.post(`${API_BASE_URL}${API_ENDPOINTS.REGISTER}`, userData),
  login: (credentials) => axios.post(`${API_BASE_URL}${API_ENDPOINTS.LOGIN}`, credentials),
  logout: () => axios.post(`${API_BASE_URL}${API_ENDPOINTS.LOGOUT}`),
  getCurrentUser: () => axios.get(`${API_BASE_URL}${API_ENDPOINTS.CURRENT_USER}`),

  // User management
  changePassword: (data) => axios.post(`${API_BASE_URL}${API_ENDPOINTS.CHANGE_PASSWORD}`, data),
  setup2FA: () => axios.post(`${API_BASE_URL}${API_ENDPOINTS.SETUP_2FA}`),
  verify2FA: (data) => axios.post(`${API_BASE_URL}${API_ENDPOINTS.VERIFY_2FA}`, data),
  disable2FA: (data) => axios.post(`${API_BASE_URL}${API_ENDPOINTS.DISABLE_2FA}`, data),

  // Screen management
  getScreens: () => axios.get(`${API_BASE_URL}${API_ENDPOINTS.SCREENS}`),
  addScreen: (screenData) => axios.post(`${API_BASE_URL}${API_ENDPOINTS.SCREENS}`, screenData),
  updateScreen: (screenId, data) => axios.put(`${API_BASE_URL}${API_ENDPOINTS.SCREEN_BY_ID(screenId)}`, data),
  deleteScreen: (screenId) => axios.delete(`${API_BASE_URL}${API_ENDPOINTS.SCREEN_BY_ID(screenId)}`),
  unbindScreen: (screenId) => axios.post(`${API_BASE_URL}${API_ENDPOINTS.UNBIND_SCREEN(screenId)}`),
  getScreenData: (screenId) => axios.get(`${API_BASE_URL}${API_ENDPOINTS.SCREEN_DATA(screenId)}`),

  // Admin endpoints
  getUsers: () => axios.get(`${API_BASE_URL}${API_ENDPOINTS.ADMIN_USERS}`),
  toggleUserAdmin: (userId) => axios.post(`${API_BASE_URL}${API_ENDPOINTS.ADMIN_TOGGLE_USER(userId)}`),
  getAdminSettings: () => axios.get(`${API_BASE_URL}${API_ENDPOINTS.ADMIN_SETTINGS}`),
  updateAdminSettings: (settings) => axios.post(`${API_BASE_URL}${API_ENDPOINTS.ADMIN_UPDATE_SETTINGS}`, settings),
  
  // Settings methods (aliases for admin settings for SettingsContext compatibility)
  getSettings: () => axios.get(`${API_BASE_URL}${API_ENDPOINTS.ADMIN_SETTINGS}`),
  updateSettings: (settings) => axios.post(`${API_BASE_URL}${API_ENDPOINTS.ADMIN_UPDATE_SETTINGS}`, settings),
  
  // UI Settings endpoints
  getUISettings: () => axios.get(`${API_BASE_URL}${API_ENDPOINTS.ADMIN_UI_SETTINGS}`),
  updateUISettings: (settings) => axios.post(`${API_BASE_URL}${API_ENDPOINTS.ADMIN_UI_SETTINGS}`, settings),
  uploadUIAsset: (formData) => axios.post(`${API_BASE_URL}${API_ENDPOINTS.ADMIN_UPLOAD_UI_ASSET}`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  }),

  // System endpoints
  getHealth: () => axios.get(`${API_BASE_URL}${API_ENDPOINTS.HEALTH}`),
  getVersion: () => axios.get(`${API_BASE_URL}${API_ENDPOINTS.VERSION}`)
};

export default api;