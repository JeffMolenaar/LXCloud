/**
 * Utility functions for the LXCloud application
 */

/**
 * Format a date to a localized string
 * @param {string|Date} date - The date to format
 * @returns {string} - Formatted date string
 */
export const formatDate = (date) => {
  if (!date) return 'Never';
  
  try {
    const dateObj = typeof date === 'string' ? new Date(date) : date;
    return dateObj.toLocaleString();
  } catch (error) {
    console.error('Error formatting date:', error);
    return 'Invalid date';
  }
};

/**
 * Format coordinates to a readable string
 * @param {number} latitude - Latitude coordinate
 * @param {number} longitude - Longitude coordinate
 * @returns {string} - Formatted coordinates
 */
export const formatCoordinates = (latitude, longitude) => {
  if (latitude == null || longitude == null) return 'No location';
  
  return `${parseFloat(latitude).toFixed(4)}, ${parseFloat(longitude).toFixed(4)}`;
};

/**
 * Validate email format
 * @param {string} email - Email to validate
 * @returns {boolean} - True if valid email format
 */
export const isValidEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

/**
 * Validate password strength
 * @param {string} password - Password to validate
 * @returns {object} - Validation result with isValid and message
 */
export const validatePassword = (password) => {
  if (!password) {
    return { isValid: false, message: 'Password is required' };
  }
  
  if (password.length < 8) {
    return { isValid: false, message: 'Password must be at least 8 characters long' };
  }
  
  return { isValid: true, message: 'Password is valid' };
};

/**
 * Get status badge class for screen status
 * @param {boolean} isOnline - Whether the screen is online
 * @returns {string} - CSS class name
 */
export const getStatusBadgeClass = (isOnline) => {
  return isOnline ? 'status-online' : 'status-offline';
};

/**
 * Get status text for screen status
 * @param {boolean} isOnline - Whether the screen is online
 * @returns {string} - Status text
 */
export const getStatusText = (isOnline) => {
  return isOnline ? 'Online' : 'Offline';
};

/**
 * Debounce function to limit rapid function calls
 * @param {Function} func - Function to debounce
 * @param {number} delay - Delay in milliseconds
 * @returns {Function} - Debounced function
 */
export const debounce = (func, delay) => {
  let timeoutId;
  return (...args) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func.apply(null, args), delay);
  };
};

/**
 * Check if user has admin privileges
 * @param {object} user - User object
 * @returns {boolean} - True if user is admin or administrator
 */
export const isAdmin = (user) => {
  return user && (user.is_admin || user.is_administrator);
};

/**
 * Check if user is super admin
 * @param {object} user - User object
 * @returns {boolean} - True if user is super admin
 */
export const isSuperAdmin = (user) => {
  return user && user.is_admin;
};

/**
 * Generate a random ID for temporary use
 * @returns {string} - Random ID
 */
export const generateId = () => {
  return Math.random().toString(36).substr(2, 9);
};

/**
 * Calculate distance between two coordinates (in kilometers)
 * @param {number} lat1 - First latitude
 * @param {number} lon1 - First longitude
 * @param {number} lat2 - Second latitude
 * @param {number} lon2 - Second longitude
 * @returns {number} - Distance in kilometers
 */
export const calculateDistance = (lat1, lon1, lat2, lon2) => {
  const R = 6371; // Radius of the Earth in kilometers
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLon = (lon2 - lon1) * Math.PI / 180;
  const a = 
    Math.sin(dLat/2) * Math.sin(dLat/2) +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * 
    Math.sin(dLon/2) * Math.sin(dLon/2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
  const distance = R * c;
  return distance;
};

/**
 * Handle API errors consistently
 * @param {Error} error - Error object from API call
 * @returns {string} - User-friendly error message
 */
export const handleApiError = (error) => {
  console.error('API Error:', error);
  
  if (error.response?.data?.error) {
    return error.response.data.error;
  }
  
  if (error.code === 'NETWORK_ERROR' || error.message === 'Network Error') {
    return 'Cannot connect to server. Please check your network connection.';
  }
  
  if (error.code === 'ECONNREFUSED') {
    return 'Server is not running. Please contact administrator.';
  }
  
  if (error.response?.status >= 500) {
    return 'Server error. Please try again later.';
  }
  
  return 'An error occurred. Please try again.';
};

/**
 * Download data as JSON file
 * @param {object} data - Data to download
 * @param {string} filename - Name of the file
 */
export const downloadJSON = (data, filename) => {
  const dataStr = JSON.stringify(data, null, 2);
  const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
  
  const exportFileDefaultName = filename.endsWith('.json') ? filename : `${filename}.json`;
  
  const linkElement = document.createElement('a');
  linkElement.setAttribute('href', dataUri);
  linkElement.setAttribute('download', exportFileDefaultName);
  linkElement.click();
};