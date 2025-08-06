import { useState, useEffect } from 'react';
import api from '../services/api';
import { handleApiError } from '../utils/helpers';

/**
 * Custom hook for managing screen data and operations
 */
export const useScreens = () => {
  const [screens, setScreens] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Load screens from API
  const loadScreens = async () => {
    try {
      setLoading(true);
      setError('');
      const response = await api.getScreens();
      setScreens(response.data.screens);
    } catch (error) {
      const errorMessage = handleApiError(error);
      setError(errorMessage);
      console.error('Error loading screens:', error);
    } finally {
      setLoading(false);
    }
  };

  // Add new screen
  const addScreen = async (screenData) => {
    try {
      setError('');
      const response = await api.addScreen(screenData);
      await loadScreens(); // Reload to get updated data
      return { success: true, data: response.data };
    } catch (error) {
      const errorMessage = handleApiError(error);
      setError(errorMessage);
      return { success: false, error: errorMessage };
    }
  };

  // Update screen
  const updateScreen = async (screenId, data) => {
    try {
      setError('');
      const response = await api.updateScreen(screenId, data);
      await loadScreens(); // Reload to get updated data
      return { success: true, data: response.data };
    } catch (error) {
      const errorMessage = handleApiError(error);
      setError(errorMessage);
      return { success: false, error: errorMessage };
    }
  };

  // Delete screen
  const deleteScreen = async (screenId) => {
    try {
      setError('');
      await api.deleteScreen(screenId);
      await loadScreens(); // Reload to get updated data
      return { success: true };
    } catch (error) {
      const errorMessage = handleApiError(error);
      setError(errorMessage);
      return { success: false, error: errorMessage };
    }
  };

  // Unbind screen
  const unbindScreen = async (screenId) => {
    try {
      setError('');
      await api.unbindScreen(screenId);
      await loadScreens(); // Reload to get updated data
      return { success: true };
    } catch (error) {
      const errorMessage = handleApiError(error);
      setError(errorMessage);
      return { success: false, error: errorMessage };
    }
  };

  // Get screen data
  const getScreenData = async (screenId) => {
    try {
      setError('');
      const response = await api.getScreenData(screenId);
      return { success: true, data: response.data };
    } catch (error) {
      const errorMessage = handleApiError(error);
      setError(errorMessage);
      return { success: false, error: errorMessage };
    }
  };

  // Filter screens by status
  const getOnlineScreens = () => screens.filter(screen => screen.online_status);
  const getOfflineScreens = () => screens.filter(screen => !screen.online_status);
  const getScreensWithLocation = () => screens.filter(screen => screen.latitude && screen.longitude);

  // Get screen statistics
  const getScreenStats = () => ({
    total: screens.length,
    online: getOnlineScreens().length,
    offline: getOfflineScreens().length,
    withLocation: getScreensWithLocation().length
  });

  // Update screen status (for real-time updates)
  const updateScreenStatus = (serialNumber, statusData) => {
    setScreens(prevScreens => 
      prevScreens.map(screen => 
        screen.serial_number === serialNumber
          ? {
              ...screen,
              ...statusData,
              last_seen: statusData.timestamp || new Date().toISOString()
            }
          : screen
      )
    );
  };

  // Load screens on mount
  useEffect(() => {
    loadScreens();
  }, []);

  return {
    screens,
    loading,
    error,
    loadScreens,
    addScreen,
    updateScreen,
    deleteScreen,
    unbindScreen,
    getScreenData,
    getOnlineScreens,
    getOfflineScreens,
    getScreensWithLocation,
    getScreenStats,
    updateScreenStatus,
    clearError: () => setError('')
  };
};