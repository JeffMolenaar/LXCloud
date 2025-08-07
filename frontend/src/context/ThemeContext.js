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
    // Original settings
    app_name: 'LXCloud',
    primary_color: '#667eea',
    secondary_color: '#f093fb',
    header_color: '#667eea',
    button_color: '#667eea',
    button_hover_color: '#5a6fd8',
    logo_url: '',
    favicon_url: '',
    background_image_url: '',
    custom_button_images: '{}',
    
    // Footer customization
    footer_enabled: 'true',
    footer_text: 'Powered by LXCloud',
    footer_color: '#f8f9fa',
    footer_text_color: '#6c757d',
    footer_links: '{}',
    
    // Typography settings
    font_family: 'system-ui, -apple-system, sans-serif',
    font_size_base: '16px',
    font_size_heading: '24px',
    line_height: '1.5',
    
    // Navigation customization
    nav_style: 'default',
    nav_position: 'top',
    nav_color: '#667eea',
    nav_hover_color: '#5a6fd8',
    
    // Advanced button customization
    button_style: 'default',
    button_size: 'medium',
    button_shadow: 'true',
    button_animation: 'true',
    
    // Page-specific settings
    dashboard_layout: 'grid',
    dashboard_theme: 'default',
    login_background_url: '',
    login_style: 'default',
    
    // Custom text overrides
    custom_text_labels: '{}',
    page_titles: '{}',
    
    // Advanced customization
    custom_css: '',
    theme_mode: 'light',
    border_radius: '8px',
    spacing_unit: '16px',
    
    // Accessibility settings
    high_contrast: 'false',
    large_text: 'false',
    reduced_motion: 'false',
    
    // Advanced header settings
    header_height: '60px',
    header_shadow: 'true',
    header_sticky: 'true',
    
    // Card and component styling
    card_shadow: 'true',
    card_border: 'true',
    card_hover_effect: 'true'
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

    // Generate dynamic CSS with all new settings
    let css = `
      /* Root Variables for Consistent Theming */
      :root {
        --primary-color: ${themeData.primary_color || '#667eea'};
        --secondary-color: ${themeData.secondary_color || '#f093fb'};
        --header-color: ${themeData.header_color || '#667eea'};
        --button-color: ${themeData.button_color || '#667eea'};
        --button-hover-color: ${themeData.button_hover_color || '#5a6fd8'};
        --font-family: ${themeData.font_family || 'system-ui, -apple-system, sans-serif'};
        --font-size-base: ${themeData.font_size_base || '16px'};
        --font-size-heading: ${themeData.font_size_heading || '24px'};
        --line-height: ${themeData.line_height || '1.5'};
        --border-radius: ${themeData.border_radius || '8px'};
        --spacing-unit: ${themeData.spacing_unit || '16px'};
        --header-height: ${themeData.header_height || '60px'};
      }

      /* Global Typography */
      body, .App {
        font-family: var(--font-family) !important;
        font-size: var(--font-size-base) !important;
        line-height: var(--line-height) !important;
      }

      h1, h2, h3, h4, h5, h6 {
        font-family: var(--font-family) !important;
      }

      h1, .header .logo {
        font-size: var(--font-size-heading) !important;
      }

      /* Header Styling */
      .header {
        background: var(--header-color) !important;
        height: var(--header-height) !important;
        ${themeData.header_shadow === 'true' ? 'box-shadow: 0 2px 10px rgba(0,0,0,0.1) !important;' : ''}
        ${themeData.header_sticky === 'true' ? 'position: sticky !important; top: 0 !important; z-index: 1000 !important;' : ''}
      }

      /* Navigation Styling */
      .nav-links {
        ${themeData.nav_position === 'side' ? 'flex-direction: column !important;' : ''}
      }

      .nav-link {
        color: ${themeData.nav_color || '#667eea'} !important;
        ${themeData.nav_style === 'pills' ? 'border-radius: 20px !important; background: rgba(255,255,255,0.1) !important;' : ''}
        ${themeData.nav_style === 'underline' ? 'border-bottom: 2px solid transparent !important;' : ''}
      }

      .nav-link:hover, .nav-link.active {
        color: ${themeData.nav_hover_color || '#5a6fd8'} !important;
        ${themeData.nav_style === 'pills' ? 'background: rgba(255,255,255,0.2) !important;' : ''}
        ${themeData.nav_style === 'underline' ? 'border-bottom-color: currentColor !important;' : 'background-color: rgba(255,255,255,0.2) !important;'}
      }

      /* Button Styling */
      .button {
        background: var(--button-color) !important;
        border-color: var(--button-color) !important;
        border-radius: ${themeData.button_style === 'rounded' ? '25px' : 
                        themeData.button_style === 'square' ? '0' : 'var(--border-radius)'} !important;
        padding: ${themeData.button_size === 'small' ? '8px 16px' :
                 themeData.button_size === 'large' ? '16px 32px' : '12px 24px'} !important;
        font-size: ${themeData.button_size === 'small' ? '14px' :
                    themeData.button_size === 'large' ? '18px' : '16px'} !important;
        ${themeData.button_shadow === 'true' ? 'box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;' : 'box-shadow: none !important;'}
        ${themeData.button_animation === 'true' ? 'transition: all 0.2s ease !important;' : 'transition: none !important;'}
        ${themeData.button_style === 'outline' ? 'background: transparent !important; border: 2px solid var(--button-color) !important; color: var(--button-color) !important;' : ''}
      }

      .button:hover {
        background: var(--button-hover-color) !important;
        border-color: var(--button-hover-color) !important;
        ${themeData.button_animation === 'true' ? 'transform: translateY(-2px) !important;' : ''}
        ${themeData.button_shadow === 'true' ? 'box-shadow: 0 4px 15px rgba(' + hexToRgb(themeData.button_color || '#667eea') + ', 0.4) !important;' : ''}
        ${themeData.button_style === 'outline' ? 'background: var(--button-color) !important; color: white !important;' : ''}
      }

      /* Card and Component Styling */
      .card {
        border-radius: var(--border-radius) !important;
        ${themeData.card_shadow === 'true' ? 'box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;' : 'box-shadow: none !important;'}
        ${themeData.card_border === 'true' ? 'border: 1px solid #e5e7eb !important;' : 'border: none !important;'}
        ${themeData.card_hover_effect === 'true' ? 'transition: transform 0.2s ease, box-shadow 0.2s ease !important;' : ''}
      }

      ${themeData.card_hover_effect === 'true' ? `
      .card:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(0,0,0,0.15) !important;
      }` : ''}

      /* Footer Styling */
      ${themeData.footer_enabled === 'true' ? `
      .footer {
        background: ${themeData.footer_color || '#f8f9fa'} !important;
        color: ${themeData.footer_text_color || '#6c757d'} !important;
        padding: var(--spacing-unit) !important;
        text-align: center !important;
        border-top: 1px solid #e5e7eb !important;
        margin-top: auto !important;
      }` : `
      .footer {
        display: none !important;
      }`}

      /* Theme Mode Specific Styles */
      ${themeData.theme_mode === 'dark' ? `
      body, .App {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
      }
      
      .card {
        background-color: #2d2d2d !important;
        color: #ffffff !important;
      }
      
      .form-input {
        background-color: #3d3d3d !important;
        color: #ffffff !important;
        border-color: #5d5d5d !important;
      }` : ''}

      /* Accessibility Enhancements */
      ${themeData.high_contrast === 'true' ? `
      body, .App {
        filter: contrast(150%) !important;
      }` : ''}

      ${themeData.large_text === 'true' ? `
      body, .App {
        font-size: calc(var(--font-size-base) * 1.25) !important;
      }` : ''}

      ${themeData.reduced_motion === 'true' ? `
      *, *::before, *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
        scroll-behavior: auto !important;
      }` : ''}

      /* Global Spacing */
      .container {
        padding: var(--spacing-unit) !important;
      }

      .form-group {
        margin-bottom: var(--spacing-unit) !important;
      }

      /* Background Image */
      ${themeData.background_image_url ? `
      body {
        background-image: url('${themeData.background_image_url}') !important;
        background-size: cover !important;
        background-attachment: fixed !important;
        background-repeat: no-repeat !important;
      }` : ''}

      /* Form Elements */
      .form-input:focus {
        border-color: var(--primary-color) !important;
        box-shadow: 0 0 0 3px rgba(${hexToRgb(themeData.primary_color || '#667eea')}, 0.1) !important;
      }

      /* Primary Color Elements */
      .tab.active {
        color: var(--primary-color) !important;
        border-bottom-color: var(--primary-color) !important;
      }

      .screen-item {
        border-left-color: var(--primary-color) !important;
      }

      .add-screen-fab {
        background: var(--button-color) !important;
      }

      .add-screen-fab:hover {
        background: var(--button-hover-color) !important;
        box-shadow: 0 4px 15px rgba(${hexToRgb(themeData.button_color || '#667eea')}, 0.4) !important;
      }
    `;

    // Add custom button image styles
    Object.entries(customButtonImages).forEach(([buttonClass, imageUrl]) => {
      if (imageUrl) {
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

    // Add custom CSS injection
    if (themeData.custom_css) {
      css += `\n/* Custom CSS */\n${themeData.custom_css}`;
    }

    style.textContent = css;
    document.head.appendChild(style);

    // Update app name in the document
    if (themeData.app_name) {
      document.title = themeData.app_name;
    }

    // Update favicon if provided
    if (themeData.favicon_url) {
      updateFavicon(themeData.favicon_url);
    }
  };

  // Helper function to update favicon
  const updateFavicon = (faviconUrl) => {
    const link = document.querySelector("link[rel*='icon']") || document.createElement('link');
    link.type = 'image/x-icon';
    link.rel = 'shortcut icon';
    link.href = faviconUrl;
    document.getElementsByTagName('head')[0].appendChild(link);
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