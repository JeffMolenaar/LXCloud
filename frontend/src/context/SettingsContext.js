import React, { createContext, useState, useContext, useEffect } from 'react';
import api from '../services/api';

const SettingsContext = createContext();

export const useSettings = () => {
  const context = useContext(SettingsContext);
  if (!context) {
    throw new Error('useSettings must be used within a SettingsProvider');
  }
  return context;
};

export const SettingsProvider = ({ children }) => {
  const [settings, setSettings] = useState({
    logoUrl: null,
    logoText: 'LXCloud',
    siteName: 'LXCloud - LED Screen Management Platform',
    faviconUrl: null,
    mapMarkerOnline: null,
    mapMarkerOffline: null
  });
  const [loading, setLoading] = useState(true);

  const loadSettings = async () => {
    try {
      const response = await api.getSettings();
      setSettings(prev => ({ ...prev, ...response.data.settings }));
    } catch (error) {
      // If settings don't exist yet, use defaults
      console.log('Settings not found, using defaults');
    } finally {
      setLoading(false);
    }
  };

  const updateSettings = async (newSettings) => {
    try {
      await api.updateSettings(newSettings);
      setSettings(prev => ({ ...prev, ...newSettings }));
      
      // Update document title and favicon
      if (newSettings.siteName) {
        document.title = newSettings.siteName;
      }
      if (newSettings.faviconUrl) {
        updateFavicon(newSettings.faviconUrl);
      }
      
      return true;
    } catch (error) {
      console.error('Failed to update settings:', error);
      throw error;
    }
  };

  const updateFavicon = (url) => {
    const link = document.querySelector("link[rel~='icon']") || document.createElement('link');
    link.type = 'image/x-icon';
    link.rel = 'icon';
    link.href = url;
    document.getElementsByTagName('head')[0].appendChild(link);
  };

  useEffect(() => {
    loadSettings();
  }, []);

  useEffect(() => {
    // Update document title when settings change
    if (settings.siteName) {
      document.title = settings.siteName;
    }
    if (settings.faviconUrl) {
      updateFavicon(settings.faviconUrl);
    }
  }, [settings.siteName, settings.faviconUrl]);

  const value = {
    settings,
    updateSettings,
    loading,
    reload: loadSettings
  };

  return (
    <SettingsContext.Provider value={value}>
      {children}
    </SettingsContext.Provider>
  );
};