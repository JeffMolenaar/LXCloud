// API endpoints and configuration constants
export const API_CONFIG = {
  // Dynamic API base URL for local network access
  getBaseUrl: () => {
    // If running in development with a specific backend URL
    if (process.env.REACT_APP_API_URL) {
      return process.env.REACT_APP_API_URL;
    }
    
    // For production, use the same host as the frontend
    if (process.env.NODE_ENV === 'production') {
      return `${window.location.protocol}//${window.location.host}/api`;
    }
    
    // For development, try to detect the backend server
    const backendHost = process.env.REACT_APP_BACKEND_HOST || window.location.hostname;
    const backendPort = process.env.REACT_APP_BACKEND_PORT || '5000';
    return `http://${backendHost}:${backendPort}/api`;
  }
};

// API endpoints
export const API_ENDPOINTS = {
  // Authentication
  REGISTER: '/register',
  LOGIN: '/login',
  LOGOUT: '/logout',
  CURRENT_USER: '/user',

  // User management
  CHANGE_PASSWORD: '/user/change-password',
  SETUP_2FA: '/user/2fa/setup',
  VERIFY_2FA: '/user/2fa/verify',
  DISABLE_2FA: '/user/2fa/disable',

  // Screen management
  SCREENS: '/screens',
  SCREEN_BY_ID: (id) => `/screens/${id}`,
  SCREEN_DATA: (id) => `/screens/${id}/data`,
  UNBIND_SCREEN: (id) => `/screens/${id}/unbind`,

  // Admin endpoints
  ADMIN_USERS: '/admin/users',
  ADMIN_TOGGLE_USER: (id) => `/admin/users/${id}/toggle-admin`,
  ADMIN_SETTINGS: '/admin/settings',
  ADMIN_UPDATE_SETTINGS: '/admin/settings',

  // System endpoints
  HEALTH: '/health',
  VERSION: '/version'
};

// Application constants
export const APP_CONFIG = {
  APP_NAME: 'LXCloud',
  APP_DESCRIPTION: 'LED Screen Management Platform',
  
  // Map configuration
  DEFAULT_MAP_CENTER: [52.3676, 4.9041], // Amsterdam, Netherlands
  DEFAULT_MAP_ZOOM: 2,
  
  // Marker URLs
  MARKER_ICONS: {
    ONLINE: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-green.png',
    OFFLINE: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png'
  },
  
  // Socket.io configuration
  SOCKET_URL: process.env.NODE_ENV === 'production' 
    ? window.location.origin 
    : 'http://localhost:5000'
};

// User roles and permissions
export const USER_ROLES = {
  ADMIN: 'admin',
  ADMINISTRATOR: 'administrator',
  USER: 'user'
};

// Screen status
export const SCREEN_STATUS = {
  ONLINE: true,
  OFFLINE: false
};

// Form validation constants
export const VALIDATION = {
  MIN_PASSWORD_LENGTH: 8,
  MAX_USERNAME_LENGTH: 50,
  MAX_EMAIL_LENGTH: 100,
  MAX_SCREEN_NAME_LENGTH: 100
};

// Error messages
export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Cannot connect to server. Please check your network connection.',
  SERVER_ERROR: 'Server is not running. Please contact administrator.',
  INVALID_CREDENTIALS: 'Invalid username or password.',
  REGISTRATION_FAILED: 'Registration failed. Please try again.',
  UNAUTHORIZED: 'You are not authorized to perform this action.',
  GENERIC_ERROR: 'An error occurred. Please try again.'
};

// Success messages
export const SUCCESS_MESSAGES = {
  LOGIN_SUCCESS: 'Login successful',
  REGISTRATION_SUCCESS: 'Registration successful',
  LOGOUT_SUCCESS: 'Logout successful',
  SCREEN_ADDED: 'Screen added successfully',
  SCREEN_UPDATED: 'Screen updated successfully',
  SCREEN_DELETED: 'Screen deleted successfully',
  PASSWORD_CHANGED: 'Password changed successfully'
};