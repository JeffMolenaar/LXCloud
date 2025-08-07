import React, { createContext, useState, useContext, useEffect } from 'react';
import api from '../services/api';

const ThemeContext = createContext();

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

export const ThemeProvider = ({ children }) => {
  const [theme, setTheme] = useState({
    app_name: 'LXCloud',
    primary_color: '#667eea',
    secondary_color: '#f093fb',
    header_color: '#667eea',
    button_color: '#667eea',
    button_hover_color: '#5a6fd8',
    logo_url: '',
    favicon_url: '',
    background_image_url: '',
    custom_button_images: '{}'
  });
  const [loading, setLoading] = useState(true);

  const loadTheme = async () => {
    try {
      const response = await api.getUISettings();
      const themeData = response.data.settings;
      setTheme(prev => ({ ...prev, ...themeData }));
      applyTheme(themeData);
    } catch (error) {
      console.log('UI settings not found, using defaults');
      applyTheme(theme);
    } finally {
      setLoading(false);
    }
  };

  const applyTheme = (themeData) => {
    // Remove existing custom styles
    const existingStyle = document.getElementById('dynamic-theme-styles');
    if (existingStyle) {
      existingStyle.remove();
    }

    // Create new style element
    const style = document.createElement('style');
    style.id = 'dynamic-theme-styles';
    
    const customButtonImages = themeData.custom_button_images ? 
      JSON.parse(themeData.custom_button_images || '{}') : {};

    // Generate dynamic CSS
    let css = `
      /* Dynamic Header Color */
      .header {
        background: ${themeData.header_color || '#667eea'} !important;
      }

      /* Dynamic Button Colors */
      .button {
        background: ${themeData.button_color || '#667eea'} !important;
        border-color: ${themeData.button_color || '#667eea'} !important;
      }

      .button:hover {
        background: ${themeData.button_hover_color || '#5a6fd8'} !important;
        border-color: ${themeData.button_hover_color || '#5a6fd8'} !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(${hexToRgb(themeData.button_color || '#667eea')}, 0.4);
      }

      .add-screen-fab {
        background: ${themeData.button_color || '#667eea'} !important;
      }

      .add-screen-fab:hover {
        background: ${themeData.button_hover_color || '#5a6fd8'} !important;
        box-shadow: 0 4px 15px rgba(${hexToRgb(themeData.button_color || '#667eea')}, 0.4);
      }

      .tab.active {
        color: ${themeData.primary_color || '#667eea'} !important;
        border-bottom-color: ${themeData.primary_color || '#667eea'} !important;
      }

      .nav-link:hover, .nav-link.active {
        background-color: rgba(255,255,255,0.2) !important;
      }

      .screen-item {
        border-left-color: ${themeData.primary_color || '#667eea'} !important;
      }

      .form-input:focus {
        border-color: ${themeData.primary_color || '#667eea'} !important;
      }
    `;

    // Add custom button image styles
    Object.entries(customButtonImages).forEach(([buttonClass, imageUrl]) => {
      if (imageUrl) {
        // Apply to primary buttons for 'primary' class, secondary for 'secondary', etc.
        const buttonSelector = buttonClass === 'primary' ? 
          '.button:not(.button-secondary):not(.button-danger):not(.button-warning):not(.button-success)' :
          `.button.button-${buttonClass}`;
          
        css += `
          ${buttonSelector}, 
          ${buttonSelector}:hover {
            background: url('${imageUrl}') center/contain no-repeat !important;
            background-size: contain !important;
            min-height: 40px !important;
            color: transparent !important;
            border: 1px solid transparent !important;
            box-shadow: none !important;
            text-shadow: none !important;
          }
        `;
      }
    });

    style.textContent = css;
    document.head.appendChild(style);

    // Update app name in the document
    if (themeData.app_name) {
      document.title = themeData.app_name;
    }
  };

  // Helper function to convert hex to RGB
  const hexToRgb = (hex) => {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? 
      `${parseInt(result[1], 16)}, ${parseInt(result[2], 16)}, ${parseInt(result[3], 16)}` : 
      '102, 126, 234';
  };

  const updateTheme = async (newTheme) => {
    try {
      await api.updateUISettings(newTheme);
      const updatedTheme = { ...theme, ...newTheme };
      setTheme(updatedTheme);
      applyTheme(updatedTheme);
      return true;
    } catch (error) {
      console.error('Failed to update theme:', error);
      throw error;
    }
  };

  useEffect(() => {
    loadTheme();
  }, []);

  const value = {
    theme,
    updateTheme,
    loading,
    reload: loadTheme,
    applyTheme
  };

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
};