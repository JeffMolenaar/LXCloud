import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useSettings } from '../context/SettingsContext';
import { useTheme } from '../context/ThemeContext';
import { Tabs, TabPanel } from '../components/Tabs';
import api from '../services/api';

const CloudUICustomization = () => {
  const { user } = useAuth();
  const { settings, updateSettings } = useSettings();
  const { theme, updateTheme } = useTheme();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [uiSettings, setUiSettings] = useState({
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
    header_text_color: '#ffffff',
    
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
    
    // Header button customization
    header_button_alignment: 'default',
    header_button_vertical_alignment: 'center',
    header_button_spacing: '15px',
    header_button_individual_positions: '{}',
    header_button_individual_colors: '{}',
    header_custom_css: '',
    
    // Card and component styling
    card_shadow: 'true',
    card_border: 'true',
    card_hover_effect: 'true',
    
    // Screen management button icons
    screen_view_data_icon: '',
    screen_edit_icon: '',
    screen_unbind_icon: ''
  });
  // Super admin settings (from AdminSettings.js)
  const [adminSettings, setAdminSettings] = useState({
    logoUrl: '',
    logoText: 'LXCloud',
    siteName: 'LXCloud - LED Screen Management Platform',
    faviconUrl: '',
    mapMarkerOnline: '',
    mapMarkerOffline: ''
  });
  const [uploadingLogo, setUploadingLogo] = useState(false);
  const [uploadingFavicon, setUploadingFavicon] = useState(false);
  const [uploadingBackground, setUploadingBackground] = useState(false);
  const [uploadingMapMarkerOnline, setUploadingMapMarkerOnline] = useState(false);
  const [uploadingMapMarkerOffline, setUploadingMapMarkerOffline] = useState(false);
  const [uploadingButtonImage, setUploadingButtonImage] = useState('');
  const [customButtonImages, setCustomButtonImages] = useState({});
  const [selectedButtonType, setSelectedButtonType] = useState('');
  const [footerLinks, setFooterLinks] = useState({});
  const [customTextLabels, setCustomTextLabels] = useState({});
  const [pageTitles, setPageTitles] = useState({});
  const [headerButtonPositions, setHeaderButtonPositions] = useState({});
  const [headerButtonColors, setHeaderButtonColors] = useState({});

  useEffect(() => {
    if (!user?.is_admin && !user?.is_administrator) {
      setError('Access denied. Admin privileges required.');
      setLoading(false);
      return;
    }
    
    loadUISettings();
    // Load admin settings only for super admins
    if (user?.is_admin) {
      loadAdminSettings();
    }
  }, [user]);

  const loadUISettings = async () => {
    try {
      const response = await api.getUISettings();
      const loadedSettings = response.data.settings || uiSettings;
      setUiSettings(loadedSettings);
      
      // Parse custom button images
      try {
        const buttonImages = JSON.parse(loadedSettings.custom_button_images || '{}');
        setCustomButtonImages(buttonImages);
      } catch (e) {
        console.error('Error parsing custom button images:', e);
        setCustomButtonImages({});
      }
      
      // Parse footer links
      try {
        const footerLinksObj = JSON.parse(loadedSettings.footer_links || '{}');
        setFooterLinks(footerLinksObj);
      } catch (e) {
        console.error('Error parsing footer links:', e);
        setFooterLinks({});
      }
      
      // Parse custom text labels
      try {
        const textLabels = JSON.parse(loadedSettings.custom_text_labels || '{}');
        setCustomTextLabels(textLabels);
      } catch (e) {
        console.error('Error parsing custom text labels:', e);
        setCustomTextLabels({});
      }
      
      // Parse page titles
      try {
        const pageTitlesObj = JSON.parse(loadedSettings.page_titles || '{}');
        setPageTitles(pageTitlesObj);
      } catch (e) {
        console.error('Error parsing page titles:', e);
        setPageTitles({});
      }
      
      // Parse header button positions
      try {
        const headerPositions = JSON.parse(loadedSettings.header_button_individual_positions || '{}');
        setHeaderButtonPositions(headerPositions);
      } catch (e) {
        console.error('Error parsing header button positions:', e);
        setHeaderButtonPositions({});
      }
      
      // Parse header button colors
      try {
        const headerColors = JSON.parse(loadedSettings.header_button_individual_colors || '{}');
        setHeaderButtonColors(headerColors);
      } catch (e) {
        console.error('Error parsing header button colors:', e);
        setHeaderButtonColors({});
      }
      
      // Sync with admin settings for super admins
      if (user?.is_admin && loadedSettings.logo_url) {
        setAdminSettings(prev => ({ ...prev, logoUrl: loadedSettings.logo_url }));
      }
      if (user?.is_admin && loadedSettings.favicon_url) {
        setAdminSettings(prev => ({ ...prev, faviconUrl: loadedSettings.favicon_url }));
      }
      if (user?.is_admin && loadedSettings.app_name) {
        setAdminSettings(prev => ({ ...prev, logoText: loadedSettings.app_name }));
      }
    } catch (error) {
      if (error.response?.status === 404) {
        // Settings don't exist yet, use defaults
        console.log('UI settings not found, using defaults');
      } else {
        setError('Failed to load UI settings');
        console.error('Error loading UI settings:', error);
      }
    } finally {
      setLoading(false);
    }
  };

  const loadAdminSettings = async () => {
    try {
      const response = await api.getSettings();
      const loadedAdminSettings = {
        ...adminSettings,
        ...response.data.settings
      };
      setAdminSettings(loadedAdminSettings);
      
      // Sync with UI settings
      if (loadedAdminSettings.logoUrl) {
        setUiSettings(prev => ({ ...prev, logo_url: loadedAdminSettings.logoUrl }));
      }
      if (loadedAdminSettings.faviconUrl) {
        setUiSettings(prev => ({ ...prev, favicon_url: loadedAdminSettings.faviconUrl }));
      }
      if (loadedAdminSettings.logoText) {
        setUiSettings(prev => ({ ...prev, app_name: loadedAdminSettings.logoText }));
      }
    } catch (error) {
      if (error.response?.status === 404) {
        console.log('Admin settings not found, using defaults');
      } else {
        console.error('Error loading admin settings:', error);
      }
    }
  };

  const handleInputChange = (field, value) => {
    setUiSettings(prev => ({
      ...prev,
      [field]: value
    }));
    
    // Sync with admin settings for super admins - ensure bidirectional sync
    if (user?.is_admin) {
      if (field === 'logo_url') {
        setAdminSettings(prev => ({ ...prev, logoUrl: value }));
      } else if (field === 'favicon_url') {
        setAdminSettings(prev => ({ ...prev, faviconUrl: value }));
      } else if (field === 'app_name') {
        setAdminSettings(prev => ({ ...prev, logoText: value }));
      }
    }
  };

  const handleAdminInputChange = (field, value) => {
    setAdminSettings(prev => ({
      ...prev,
      [field]: value
    }));
    
    // Sync with UI settings for logo and favicon - ensure bidirectional sync
    if (field === 'logoUrl') {
      setUiSettings(prev => ({ ...prev, logo_url: value }));
    } else if (field === 'faviconUrl') {
      setUiSettings(prev => ({ ...prev, favicon_url: value }));
    } else if (field === 'logoText') {
      setUiSettings(prev => ({ ...prev, app_name: value }));
    }
  };

  const handleFileUpload = async (file, type) => {
    if (!file) return;

    // Validate file type
    const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/svg+xml'];
    if (!allowedTypes.includes(file.type)) {
      setError('Please upload a valid image file (JPEG, PNG, GIF, or SVG)');
      setTimeout(() => setError(''), 3000);
      return;
    }

    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      setError('File size must be less than 5MB');
      setTimeout(() => setError(''), 3000);
      return;
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('type', type);

    try {
      if (type === 'logo') setUploadingLogo(true);
      else if (type === 'favicon') setUploadingFavicon(true);
      else if (type === 'background') setUploadingBackground(true);
      else if (type === 'map_marker_online') setUploadingMapMarkerOnline(true);
      else if (type === 'map_marker_offline') setUploadingMapMarkerOffline(true);
      else if (type.startsWith('button_')) setUploadingButtonImage(type);
      else if (type.startsWith('screen_')) setUploadingButtonImage(type);

      const response = await api.uploadUIAsset(formData);
      
      // Update the appropriate settings with the new URL
      if (type === 'map_marker_online') {
        handleAdminInputChange('mapMarkerOnline', response.data.url);
      } else if (type === 'map_marker_offline') {
        handleAdminInputChange('mapMarkerOffline', response.data.url);
      } else if (type.startsWith('button_')) {
        // Handle button image uploads
        const buttonType = type.replace('button_', '');
        const updatedButtonImages = { ...customButtonImages, [buttonType]: response.data.url };
        setCustomButtonImages(updatedButtonImages);
        handleInputChange('custom_button_images', JSON.stringify(updatedButtonImages));
      } else if (type.startsWith('screen_')) {
        // Handle screen management icon uploads
        handleInputChange(type, response.data.url);
      } else {
        handleInputChange(`${type}_url`, response.data.url);
        
        // For logo and favicon, also update admin settings if user is super admin
        if (user?.is_admin && (type === 'logo' || type === 'favicon')) {
          if (type === 'logo') {
            handleAdminInputChange('logoUrl', response.data.url);
          } else if (type === 'favicon') {
            handleAdminInputChange('faviconUrl', response.data.url);
          }
        }
      }
      
      setSuccess(`${type.replace('_', ' ').charAt(0).toUpperCase() + type.slice(1).replace('_', ' ')} uploaded successfully`);
      setTimeout(() => setSuccess(''), 3000);
      
    } catch (error) {
      setError(error.response?.data?.error || `Failed to upload ${type.replace('_', ' ')}`);
      setTimeout(() => setError(''), 3000);
    } finally {
      if (type === 'logo') setUploadingLogo(false);
      else if (type === 'favicon') setUploadingFavicon(false);
      else if (type === 'background') setUploadingBackground(false);
      else if (type === 'map_marker_online') setUploadingMapMarkerOnline(false);
      else if (type === 'map_marker_offline') setUploadingMapMarkerOffline(false);
      else if (type.startsWith('button_') || type.startsWith('screen_')) setUploadingButtonImage('');
    }
  };

  const saveUISettings = async () => {
    try {
      setLoading(true);
      
      // Save UI settings
      await api.updateUISettings(uiSettings);
      
      // Update theme with the new settings
      await updateTheme(uiSettings);
      
      // For super admins, also save admin settings and update the settings context
      if (user?.is_admin) {
        await updateSettings(adminSettings);
      }
      
      setSuccess('Settings saved successfully');
      setTimeout(() => setSuccess(''), 3000);
    } catch (error) {
      setError(error.response?.data?.error || 'Failed to save settings');
      setTimeout(() => setError(''), 3000);
    } finally {
      setLoading(false);
    }
  };

  const resetToDefaults = () => {
    if (confirm('Are you sure you want to reset all settings to defaults? This will not delete uploaded files.')) {
      const defaultSettings = {
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
        header_text_color: '#ffffff',
        
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
        
        // Header button customization
        header_button_alignment: 'default',
        header_button_vertical_alignment: 'center',
        header_button_spacing: '15px',
        header_button_individual_positions: '{}',
        header_button_individual_colors: '{}',
        header_custom_css: '',
        
        // Card and component styling
        card_shadow: 'true',
        card_border: 'true',
        card_hover_effect: 'true',
        
        // Screen management button icons
        screen_view_data_icon: '',
        screen_edit_icon: '',
        screen_unbind_icon: ''
      };
      
      setUiSettings(defaultSettings);
      setCustomButtonImages({});
      setFooterLinks({});
      setCustomTextLabels({});
      setPageTitles({});
      setHeaderButtonPositions({});
      setHeaderButtonColors({});
      
      if (user?.is_admin) {
        setAdminSettings({
          logoUrl: '',
          logoText: 'LXCloud',
          siteName: 'LXCloud - LED Screen Management Platform',
          faviconUrl: '',
          mapMarkerOnline: '',
          mapMarkerOffline: ''
        });
      }
    }
  };

  if (loading) {
    return <div className="loading">Loading UI customization...</div>;
  }

  if (!user?.is_admin && !user?.is_administrator) {
    return (
      <div className="container">
        <div className="alert alert-error">
          Access denied. You need administrator privileges to access this page.
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <h1>Cloud UI Customization & Settings</h1>
      <p>Customize the appearance, branding, and system settings of your LXCloud installation.</p>
      {user?.is_admin && (
        <p style={{ color: '#667eea', fontWeight: 'bold' }}>
          ⚙️ As a super administrator, you have access to additional system settings including map markers and advanced configuration.
        </p>
      )}
      
      {error && (
        <div className="alert alert-error">
          {error}
        </div>
      )}
      
      {success && (
        <div className="alert alert-success">
          {success}
        </div>
      )}

      <Tabs defaultTab={0}>
        {/* Header & Branding Tab */}
        <TabPanel label="🏠 Header & Branding">
          <div className="card">
            <h2>General Settings</h2>
            
            <div className="form-group">
              <label className="form-label">Application Name</label>
              <input
                type="text"
                className="form-input"
                value={uiSettings.app_name}
                onChange={(e) => handleInputChange('app_name', e.target.value)}
                placeholder="LXCloud"
              />
              <small style={{ color: '#666' }}>
                This name will appear in the header and page title
              </small>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px' }}>
              <div className="form-group">
                <label className="form-label">Primary Color</label>
                <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
                  <input
                    type="color"
                    value={uiSettings.primary_color}
                    onChange={(e) => handleInputChange('primary_color', e.target.value)}
                    style={{ width: '50px', height: '40px', border: 'none', borderRadius: '4px' }}
                  />
                  <input
                    type="text"
                    className="form-input"
                    value={uiSettings.primary_color}
                    onChange={(e) => handleInputChange('primary_color', e.target.value)}
                    placeholder="#667eea"
                    style={{ flex: 1 }}
                  />
                </div>
              </div>

              <div className="form-group">
                <label className="form-label">Header Color</label>
                <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
                  <input
                    type="color"
                    value={uiSettings.header_color}
                    onChange={(e) => handleInputChange('header_color', e.target.value)}
                    style={{ width: '50px', height: '40px', border: 'none', borderRadius: '4px' }}
                  />
                  <input
                    type="text"
                    className="form-input"
                    value={uiSettings.header_color}
                    onChange={(e) => handleInputChange('header_color', e.target.value)}
                    placeholder="#667eea"
                    style={{ flex: 1 }}
                  />
                </div>
                <small style={{ color: '#666' }}>
                  This color will be applied to the header background
                </small>
              </div>

              <div className="form-group">
                <label className="form-label">Header Text Color</label>
                <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
                  <input
                    type="color"
                    value={uiSettings.header_text_color}
                    onChange={(e) => handleInputChange('header_text_color', e.target.value)}
                    style={{ width: '50px', height: '40px', border: 'none', borderRadius: '4px' }}
                  />
                  <input
                    type="text"
                    className="form-input"
                    value={uiSettings.header_text_color}
                    onChange={(e) => handleInputChange('header_text_color', e.target.value)}
                    placeholder="#ffffff"
                    style={{ flex: 1 }}
                  />
                </div>
                <small style={{ color: '#666' }}>
                  This color will be applied to the header menu text and logo
                </small>
              </div>
            </div>
          </div>

          <div className="card">
            <h2>Logo & Branding</h2>
            
            <div className="form-group">
              <label className="form-label">Application Logo</label>
              <div style={{ display: 'flex', gap: '20px', alignItems: 'flex-start' }}>
                <div style={{ flex: 1 }}>
                  <input
                    type="file"
                    accept="image/*"
                    onChange={(e) => handleFileUpload(e.target.files[0], 'logo')}
                    disabled={uploadingLogo}
                    style={{ marginBottom: '10px' }}
                  />
                  <input
                    type="text"
                    className="form-input"
                    value={uiSettings.logo_url}
                    onChange={(e) => handleInputChange('logo_url', e.target.value)}
                    placeholder="Logo URL"
                    disabled={uploadingLogo}
                  />
                  <small style={{ color: '#666' }}>
                    Upload a logo or enter a URL. Recommended size: 200x60px
                  </small>
                </div>
                {uiSettings.logo_url && (
                  <div style={{ width: '100px', height: '30px', display: 'flex', alignItems: 'center', justifyContent: 'center', border: '1px solid #ddd', borderRadius: '4px', overflow: 'hidden' }}>
                    <img 
                      src={uiSettings.logo_url} 
                      alt="Logo preview" 
                      style={{ maxWidth: '100%', maxHeight: '100%', objectFit: 'contain' }}
                      onError={(e) => {
                        e.target.style.display = 'none';
                        e.target.nextSibling.style.display = 'block';
                      }}
                    />
                    <span style={{ display: 'none', fontSize: '12px', color: '#666' }}>Invalid</span>
                  </div>
                )}
              </div>
              {uploadingLogo && <div style={{ color: '#666', fontSize: '14px' }}>Uploading logo...</div>}
            </div>

            <div className="form-group">
              <label className="form-label">Favicon</label>
              <div style={{ display: 'flex', gap: '20px', alignItems: 'flex-start' }}>
                <div style={{ flex: 1 }}>
                  <input
                    type="file"
                    accept="image/*"
                    onChange={(e) => handleFileUpload(e.target.files[0], 'favicon')}
                    disabled={uploadingFavicon}
                    style={{ marginBottom: '10px' }}
                  />
                  <input
                    type="text"
                    className="form-input"
                    value={uiSettings.favicon_url}
                    onChange={(e) => handleInputChange('favicon_url', e.target.value)}
                    placeholder="Favicon URL"
                    disabled={uploadingFavicon}
                  />
                  <small style={{ color: '#666' }}>
                    Upload a favicon or enter a URL. Recommended size: 32x32px or 16x16px
                  </small>
                </div>
                {uiSettings.favicon_url && (
                  <div style={{ width: '32px', height: '32px', display: 'flex', alignItems: 'center', justifyContent: 'center', border: '1px solid #ddd', borderRadius: '4px', overflow: 'hidden' }}>
                    <img 
                      src={uiSettings.favicon_url} 
                      alt="Favicon preview" 
                      style={{ width: '16px', height: '16px', objectFit: 'contain' }}
                      onError={(e) => {
                        e.target.style.display = 'none';
                        e.target.nextSibling.style.display = 'block';
                      }}
                    />
                    <span style={{ display: 'none', fontSize: '10px', color: '#666' }}>✗</span>
                  </div>
                )}
              </div>
              {uploadingFavicon && <div style={{ color: '#666', fontSize: '14px' }}>Uploading favicon...</div>}
            </div>
          </div>

          {/* Header Preview */}
          <div className="card">
            <h2>Header Preview</h2>
            <div style={{ 
              background: uiSettings.header_color || '#667eea', 
              color: uiSettings.header_text_color || '#ffffff', 
              padding: '15px', 
              borderRadius: '8px',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              height: (uiSettings.header_height || '60px').replace('px', '') + 'px',
              boxShadow: uiSettings.header_shadow === 'true' ? '0 2px 10px rgba(0,0,0,0.1)' : 'none'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
                {(uiSettings.logo_url || adminSettings.logoUrl) ? (
                  <img 
                    src={uiSettings.logo_url || adminSettings.logoUrl} 
                    alt="Logo" 
                    style={{ height: '40px', maxWidth: '200px', objectFit: 'contain' }}
                    onError={(e) => {
                      e.target.style.display = 'none';
                      e.target.nextSibling.style.display = 'inline';
                    }}
                  />
                ) : null}
                <span style={{ 
                  fontSize: '1.5rem', 
                  fontWeight: 'bold',
                  color: uiSettings.header_text_color || '#ffffff',
                  display: (uiSettings.logo_url || adminSettings.logoUrl) ? 'none' : 'inline'
                }}>
                  {uiSettings.app_name || adminSettings.logoText || 'LXCloud'}
                </span>
              </div>
              <div style={{ 
                display: 'flex', 
                gap: uiSettings.header_button_spacing || '15px',
                justifyContent: uiSettings.header_button_alignment === 'center' ? 'center' :
                             uiSettings.header_button_alignment === 'right' ? 'flex-end' :
                             uiSettings.header_button_alignment === 'left' ? 'flex-start' : 'flex-end',
                alignItems: uiSettings.header_button_vertical_alignment === 'top' ? 'flex-start' :
                          uiSettings.header_button_vertical_alignment === 'bottom' ? 'flex-end' : 'center'
              }}>
                <span style={{ 
                  color: uiSettings.header_text_color || '#ffffff',
                  padding: '8px 16px',
                  borderRadius: uiSettings.nav_style === 'pills' ? '20px' : '4px',
                  background: uiSettings.nav_style === 'pills' ? 'rgba(255,255,255,0.1)' : 'transparent',
                  borderBottom: uiSettings.nav_style === 'underline' ? '2px solid transparent' : 'none'
                }}>Dashboard</span>
                <span style={{ 
                  color: uiSettings.header_text_color || '#ffffff',
                  padding: '8px 16px',
                  borderRadius: uiSettings.nav_style === 'pills' ? '20px' : '4px',
                  background: uiSettings.nav_style === 'pills' ? 'rgba(255,255,255,0.1)' : 'transparent',
                  borderBottom: uiSettings.nav_style === 'underline' ? '2px solid transparent' : 'none'
                }}>Manage Screens</span>
                <span style={{ 
                  color: uiSettings.header_text_color || '#ffffff',
                  padding: '8px 16px',
                  borderRadius: uiSettings.nav_style === 'pills' ? '20px' : '4px',
                  background: uiSettings.nav_style === 'pills' ? 'rgba(255,255,255,0.1)' : 'transparent',
                  borderBottom: uiSettings.nav_style === 'underline' ? '2px solid transparent' : 'none'
                }}>Admin Panel</span>
                <span style={{ 
                  color: uiSettings.header_text_color || '#ffffff',
                  padding: '8px 16px',
                  borderRadius: uiSettings.nav_style === 'pills' ? '20px' : '4px',
                  background: uiSettings.nav_style === 'pills' ? 'rgba(255,255,255,0.1)' : 'transparent',
                  borderBottom: uiSettings.nav_style === 'underline' ? '2px solid transparent' : 'none'
                }}>Welcome, User ▼</span>
              </div>
            </div>
            <small style={{ color: '#666', marginTop: '10px', display: 'block' }}>
              ⬆️ This preview shows how your header will look with the current settings. 
              The actual header should match this preview exactly.
            </small>
          </div>

          {/* Super Admin Advanced Settings (only for super admins) */}
          {user?.is_admin && (
            <>
              <div className="card">
                <h2>Header Button Customization (Super Admin)</h2>
                <p style={{ color: '#666', marginBottom: '20px' }}>
                  Advanced controls for positioning and styling header navigation buttons. Only super administrators can modify these settings.
                </p>
                
                {/* Global Header Button Settings */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px' }}>
                  <div className="form-group">
                    <label className="form-label">Button Alignment</label>
                    <select
                      className="form-input"
                      value={uiSettings.header_button_alignment}
                      onChange={(e) => handleInputChange('header_button_alignment', e.target.value)}
                    >
                      <option value="default">Default</option>
                      <option value="left">Left</option>
                      <option value="center">Center</option>
                      <option value="right">Right</option>
                      <option value="justify">Justify (Space Between)</option>
                    </select>
                    <small style={{ color: '#666' }}>
                      Horizontal alignment of header navigation buttons
                    </small>
                  </div>

                  <div className="form-group">
                    <label className="form-label">Vertical Alignment</label>
                    <select
                      className="form-input"
                      value={uiSettings.header_button_vertical_alignment}
                      onChange={(e) => handleInputChange('header_button_vertical_alignment', e.target.value)}
                    >
                      <option value="center">Center</option>
                      <option value="top">Top</option>
                      <option value="bottom">Bottom</option>
                    </select>
                    <small style={{ color: '#666' }}>
                      Vertical alignment of header navigation buttons
                    </small>
                  </div>

                  <div className="form-group">
                    <label className="form-label">Button Spacing</label>
                    <input
                      type="text"
                      className="form-input"
                      value={uiSettings.header_button_spacing}
                      onChange={(e) => handleInputChange('header_button_spacing', e.target.value)}
                      placeholder="15px"
                    />
                    <small style={{ color: '#666' }}>
                      Gap between header navigation buttons (e.g., 15px, 1rem)
                    </small>
                  </div>
                </div>

                {/* Header Custom CSS */}
                <div className="form-group" style={{ marginTop: '30px' }}>
                  <label className="form-label">Header Custom CSS</label>
                  <textarea
                    className="form-input"
                    value={uiSettings.header_custom_css}
                    onChange={(e) => handleInputChange('header_custom_css', e.target.value)}
                    placeholder="/* Add custom CSS specifically for header styling */
.header .nav-link {
  /* Your custom header button styles */
}

.header .logo {
  /* Your custom logo styles */
}"
                    rows="6"
                    style={{ fontFamily: 'monospace', fontSize: '14px' }}
                  />
                  <small style={{ color: '#666' }}>
                    Add custom CSS specifically for header customization. This CSS will be applied after all other header styles.
                  </small>
                </div>
              </div>

              <div className="card">
                <h2>Advanced Settings (Super Admin)</h2>
                <p style={{ color: '#666', marginBottom: '20px' }}>
                  Advanced system settings that affect the entire application. Only super administrators can modify these.
                </p>
                
                <div className="form-group">
                  <label className="form-label">Header Logo Text</label>
                  <input
                    type="text"
                    className="form-input"
                    value={adminSettings.logoText}
                    onChange={(e) => handleAdminInputChange('logoText', e.target.value)}
                    placeholder="LXCloud"
                  />
                  <small style={{ color: '#666' }}>
                    Text displayed when no logo URL is provided in the header.
                  </small>
                </div>

                <div className="form-group">
                  <label className="form-label">Site Name (Browser Title)</label>
                  <input
                    type="text"
                    className="form-input"
                    value={adminSettings.siteName}
                    onChange={(e) => handleAdminInputChange('siteName', e.target.value)}
                    placeholder="LXCloud - LED Screen Management Platform"
                  />
                  <small style={{ color: '#666' }}>
                    This appears in the browser title bar and bookmarks.
                  </small>
                </div>
              </div>
            </>
          )}
        </TabPanel>

        {/* Footer Tab */}
        <TabPanel label="🦶 Footer">
          <div className="card">
            <h2>Footer Customization</h2>
            <p style={{ color: '#666', marginBottom: '20px' }}>
              Customize the footer appearance and content that appears at the bottom of all pages.
            </p>
            
            <div className="form-group">
              <label className="form-label">
                <input
                  type="checkbox"
                  checked={uiSettings.footer_enabled === 'true'}
                  onChange={(e) => handleInputChange('footer_enabled', e.target.checked ? 'true' : 'false')}
                  style={{ marginRight: '10px' }}
                />
                Enable Footer
              </label>
              <small style={{ color: '#666' }}>
                Show or hide the footer on all pages
              </small>
            </div>

            {uiSettings.footer_enabled === 'true' && (
              <>
                <div className="form-group">
                  <label className="form-label">Footer Text</label>
                  <input
                    type="text"
                    className="form-input"
                    value={uiSettings.footer_text}
                    onChange={(e) => handleInputChange('footer_text', e.target.value)}
                    placeholder="Powered by LXCloud"
                  />
                  <small style={{ color: '#666' }}>
                    Text displayed in the center of the footer
                  </small>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px' }}>
                  <div className="form-group">
                    <label className="form-label">Footer Background Color</label>
                    <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
                      <input
                        type="color"
                        value={uiSettings.footer_color}
                        onChange={(e) => handleInputChange('footer_color', e.target.value)}
                        style={{ width: '50px', height: '40px', border: 'none', borderRadius: '4px' }}
                      />
                      <input
                        type="text"
                        className="form-input"
                        value={uiSettings.footer_color}
                        onChange={(e) => handleInputChange('footer_color', e.target.value)}
                        placeholder="#f8f9fa"
                        style={{ flex: 1 }}
                      />
                    </div>
                  </div>

                  <div className="form-group">
                    <label className="form-label">Footer Text Color</label>
                    <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
                      <input
                        type="color"
                        value={uiSettings.footer_text_color}
                        onChange={(e) => handleInputChange('footer_text_color', e.target.value)}
                        style={{ width: '50px', height: '40px', border: 'none', borderRadius: '4px' }}
                      />
                      <input
                        type="text"
                        className="form-input"
                        value={uiSettings.footer_text_color}
                        onChange={(e) => handleInputChange('footer_text_color', e.target.value)}
                        placeholder="#6c757d"
                        style={{ flex: 1 }}
                      />
                    </div>
                  </div>
                </div>

                <div className="form-group">
                  <h4>Footer Preview</h4>
                  <div style={{ 
                    background: uiSettings.footer_color, 
                    color: uiSettings.footer_text_color, 
                    padding: '15px', 
                    borderRadius: '8px',
                    textAlign: 'center',
                    border: '1px solid #ddd'
                  }}>
                    {uiSettings.footer_text}
                  </div>
                </div>
              </>
            )}
          </div>
        </TabPanel>

        {/* Pages & Content Tab */}
        <TabPanel label="📄 Pages & Content">
          <div className="card">
            <h2>Button Customization</h2>
            
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px' }}>
              <div className="form-group">
                <label className="form-label">Button Color</label>
                <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
                  <input
                    type="color"
                    value={uiSettings.button_color}
                    onChange={(e) => handleInputChange('button_color', e.target.value)}
                    style={{ width: '50px', height: '40px', border: 'none', borderRadius: '4px' }}
                  />
                  <input
                    type="text"
                    className="form-input"
                    value={uiSettings.button_color}
                    onChange={(e) => handleInputChange('button_color', e.target.value)}
                    placeholder="#667eea"
                    style={{ flex: 1 }}
                  />
                </div>
                <small style={{ color: '#666' }}>
                  Default color for all buttons
                </small>
              </div>

              <div className="form-group">
                <label className="form-label">Button Hover Color</label>
                <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
                  <input
                    type="color"
                    value={uiSettings.button_hover_color}
                    onChange={(e) => handleInputChange('button_hover_color', e.target.value)}
                    style={{ width: '50px', height: '40px', border: 'none', borderRadius: '4px' }}
                  />
                  <input
                    type="text"
                    className="form-input"
                    value={uiSettings.button_hover_color}
                    onChange={(e) => handleInputChange('button_hover_color', e.target.value)}
                    placeholder="#5a6fd8"
                    style={{ flex: 1 }}
                  />
                </div>
                <small style={{ color: '#666' }}>
                  Color when hovering over buttons
                </small>
              </div>
            </div>

            <div className="form-group" style={{ marginTop: '30px' }}>
              <label className="form-label">Custom Button Images</label>
              <p style={{ color: '#666', marginBottom: '20px' }}>
                Upload custom images to replace specific button types. The image will replace the button background.
              </p>
              
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px' }}>
                {['primary', 'secondary', 'danger', 'success', 'warning'].map((buttonType) => (
                  <div key={buttonType} className="form-group">
                    <label className="form-label" style={{ textTransform: 'capitalize' }}>
                      {buttonType} Button Image
                    </label>
                    <div style={{ display: 'flex', gap: '10px', alignItems: 'flex-start' }}>
                      <div style={{ flex: 1 }}>
                        <input
                          type="file"
                          accept="image/*"
                          onChange={(e) => handleFileUpload(e.target.files[0], `button_${buttonType}`)}
                          disabled={uploadingButtonImage === `button_${buttonType}`}
                          style={{ marginBottom: '10px' }}
                        />
                        <input
                          type="text"
                          className="form-input"
                          value={customButtonImages[buttonType] || ''}
                          onChange={(e) => {
                            const updatedImages = { ...customButtonImages, [buttonType]: e.target.value };
                            setCustomButtonImages(updatedImages);
                            handleInputChange('custom_button_images', JSON.stringify(updatedImages));
                          }}
                          placeholder={`${buttonType} button image URL`}
                          disabled={uploadingButtonImage === `button_${buttonType}`}
                        />
                        <small style={{ color: '#666' }}>
                          Upload an image or enter URL for {buttonType} buttons
                        </small>
                      </div>
                      {customButtonImages[buttonType] && (
                        <div style={{ 
                          width: '80px', 
                          height: '40px', 
                          display: 'flex', 
                          alignItems: 'center', 
                          justifyContent: 'center', 
                          border: '1px solid #ddd', 
                          borderRadius: '4px', 
                          overflow: 'hidden',
                          backgroundImage: `url(${customButtonImages[buttonType]})`,
                          backgroundSize: 'contain',
                          backgroundRepeat: 'no-repeat',
                          backgroundPosition: 'center'
                        }}>
                          <span style={{ 
                            fontSize: '12px', 
                            color: 'transparent',
                            textShadow: '0 0 3px rgba(0,0,0,0.5)'
                          }}>
                            Preview
                          </span>
                        </div>
                      )}
                    </div>
                    {uploadingButtonImage === `button_${buttonType}` && (
                      <div style={{ color: '#666', fontSize: '14px' }}>
                        Uploading {buttonType} button image...
                      </div>
                    )}
                    {customButtonImages[buttonType] && (
                      <div style={{ marginTop: '10px' }}>
                        <button
                          type="button"
                          className={`button button-${buttonType === 'primary' ? '' : 'secondary'}`}
                          style={{ 
                            background: customButtonImages[buttonType] ? 
                              `url(${customButtonImages[buttonType]}) center/contain no-repeat` : 
                              undefined,
                            color: customButtonImages[buttonType] ? 'transparent' : undefined,
                            minHeight: '40px'
                          }}
                        >
                          {buttonType.charAt(0).toUpperCase() + buttonType.slice(1)} Button Preview
                        </button>
                        <button
                          type="button"
                          className="button button-danger button-small"
                          onClick={() => {
                            const updatedImages = { ...customButtonImages };
                            delete updatedImages[buttonType];
                            setCustomButtonImages(updatedImages);
                            handleInputChange('custom_button_images', JSON.stringify(updatedImages));
                          }}
                          style={{ marginLeft: '10px' }}
                        >
                          Remove
                        </button>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            <div className="form-group">
              <h4>Button Preview</h4>
              <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
                <button 
                  type="button"
                  className="button"
                  style={{ 
                    background: uiSettings.button_color || '#667eea',
                    borderColor: uiSettings.button_color || '#667eea'
                  }}
                >
                  Primary Button
                </button>
                <button 
                  type="button"
                  className="button button-secondary"
                >
                  Secondary Button
                </button>
                <button 
                  type="button"
                  className="button button-danger"
                >
                  Danger Button
                </button>
              </div>
            </div>
          </div>

          {/* Screen Management Button Icons */}
          <div className="card">
            <h2>Screen Management Button Icons</h2>
            <p style={{ color: '#666', marginBottom: '20px' }}>
              Upload custom icons to replace the default button icons in the Manage Screens page. 
              These icons will appear on each screen's action buttons.
            </p>
            
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))', gap: '20px' }}>
              {[
                { key: 'screen_view_data_icon', label: 'View Data Icon', description: 'Icon for the view data button (📊)', defaultIcon: '📊' },
                { key: 'screen_edit_icon', label: 'Edit Name Icon', description: 'Icon for the edit name button (✏️)', defaultIcon: '✏️' },
                { key: 'screen_unbind_icon', label: 'Unbind Screen Icon', description: 'Icon for the unbind screen button (🔗❌)', defaultIcon: '🔗❌' }
              ].map((iconConfig) => (
                <div key={iconConfig.key} className="form-group">
                  <label className="form-label">{iconConfig.label}</label>
                  <div style={{ display: 'flex', gap: '10px', alignItems: 'flex-start' }}>
                    <div style={{ flex: 1 }}>
                      <input
                        type="file"
                        accept="image/*"
                        onChange={(e) => handleFileUpload(e.target.files[0], iconConfig.key)}
                        disabled={uploadingButtonImage === iconConfig.key}
                        style={{ marginBottom: '10px' }}
                      />
                      <input
                        type="text"
                        className="form-input"
                        value={uiSettings[iconConfig.key] || ''}
                        onChange={(e) => handleInputChange(iconConfig.key, e.target.value)}
                        placeholder={`${iconConfig.label} URL`}
                        disabled={uploadingButtonImage === iconConfig.key}
                      />
                      <small style={{ color: '#666' }}>
                        {iconConfig.description}. Upload an image or enter URL.
                      </small>
                    </div>
                    {uiSettings[iconConfig.key] ? (
                      <div style={{ 
                        width: '40px', 
                        height: '40px', 
                        display: 'flex', 
                        alignItems: 'center', 
                        justifyContent: 'center', 
                        border: '1px solid #ddd', 
                        borderRadius: '4px', 
                        overflow: 'hidden',
                        backgroundImage: `url(${uiSettings[iconConfig.key]})`,
                        backgroundSize: 'contain',
                        backgroundRepeat: 'no-repeat',
                        backgroundPosition: 'center'
                      }}>
                      </div>
                    ) : (
                      <div style={{ 
                        width: '40px', 
                        height: '40px', 
                        display: 'flex', 
                        alignItems: 'center', 
                        justifyContent: 'center', 
                        border: '1px solid #ddd', 
                        borderRadius: '4px',
                        fontSize: '16px'
                      }}>
                        {iconConfig.defaultIcon}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Typography Settings */}
          <div className="card">
            <h2>Typography Settings</h2>
            <p style={{ color: '#666', marginBottom: '20px' }}>
              Customize fonts, sizes, and text styling across the application.
            </p>
            
            <div className="form-group">
              <label className="form-label">Font Family</label>
              <select
                className="form-input"
                value={uiSettings.font_family}
                onChange={(e) => handleInputChange('font_family', e.target.value)}
              >
                <option value="system-ui, -apple-system, sans-serif">System Default</option>
                <option value="Arial, sans-serif">Arial</option>
                <option value="Helvetica, sans-serif">Helvetica</option>
                <option value="'Times New Roman', serif">Times New Roman</option>
                <option value="Georgia, serif">Georgia</option>
                <option value="'Courier New', monospace">Courier New</option>
                <option value="'Roboto', sans-serif">Roboto</option>
                <option value="'Open Sans', sans-serif">Open Sans</option>
                <option value="'Lato', sans-serif">Lato</option>
              </select>
              <small style={{ color: '#666' }}>
                Choose the primary font family for the application
              </small>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px' }}>
              <div className="form-group">
                <label className="form-label">Base Font Size</label>
                <input
                  type="text"
                  className="form-input"
                  value={uiSettings.font_size_base}
                  onChange={(e) => handleInputChange('font_size_base', e.target.value)}
                  placeholder="16px"
                />
                <small style={{ color: '#666' }}>
                  Base text size (e.g., 16px, 1rem)
                </small>
              </div>

              <div className="form-group">
                <label className="form-label">Heading Font Size</label>
                <input
                  type="text"
                  className="form-input"
                  value={uiSettings.font_size_heading}
                  onChange={(e) => handleInputChange('font_size_heading', e.target.value)}
                  placeholder="24px"
                />
                <small style={{ color: '#666' }}>
                  Main heading size (e.g., 24px, 1.5rem)
                </small>
              </div>

              <div className="form-group">
                <label className="form-label">Line Height</label>
                <input
                  type="text"
                  className="form-input"
                  value={uiSettings.line_height}
                  onChange={(e) => handleInputChange('line_height', e.target.value)}
                  placeholder="1.5"
                />
                <small style={{ color: '#666' }}>
                  Text line spacing (e.g., 1.5, 1.6)
                </small>
              </div>
            </div>
          </div>

          {/* Background & Theme */}
          <div className="card">
            <h2>Background & Theme</h2>
            
            <div className="form-group">
              <label className="form-label">Background Image</label>
              <div style={{ display: 'flex', gap: '20px', alignItems: 'flex-start' }}>
                <div style={{ flex: 1 }}>
                  <input
                    type="file"
                    accept="image/*"
                    onChange={(e) => handleFileUpload(e.target.files[0], 'background')}
                    disabled={uploadingBackground}
                    style={{ marginBottom: '10px' }}
                  />
                  <input
                    type="text"
                    className="form-input"
                    value={uiSettings.background_image_url}
                    onChange={(e) => handleInputChange('background_image_url', e.target.value)}
                    placeholder="Background image URL"
                    disabled={uploadingBackground}
                  />
                  <small style={{ color: '#666' }}>
                    Upload a background image or enter a URL. Will be used as a subtle background pattern.
                  </small>
                </div>
                {uiSettings.background_image_url && (
                  <div style={{ width: '60px', height: '40px', display: 'flex', alignItems: 'center', justifyContent: 'center', border: '1px solid #ddd', borderRadius: '4px', overflow: 'hidden' }}>
                    <img 
                      src={uiSettings.background_image_url} 
                      alt="Background preview" 
                      style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                      onError={(e) => {
                        e.target.style.display = 'none';
                        e.target.nextSibling.style.display = 'block';
                      }}
                    />
                    <span style={{ display: 'none', fontSize: '10px', color: '#666' }}>✗</span>
                  </div>
                )}
              </div>
              {uploadingBackground && <div style={{ color: '#666', fontSize: '14px' }}>Uploading background...</div>}
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px' }}>
              <div className="form-group">
                <label className="form-label">Theme Mode</label>
                <select
                  className="form-input"
                  value={uiSettings.theme_mode}
                  onChange={(e) => handleInputChange('theme_mode', e.target.value)}
                >
                  <option value="light">Light</option>
                  <option value="dark">Dark</option>
                  <option value="auto">Auto (System)</option>
                </select>
                <small style={{ color: '#666' }}>
                  Choose between light, dark, or automatic theme
                </small>
              </div>

              <div className="form-group">
                <label className="form-label">Border Radius</label>
                <input
                  type="text"
                  className="form-input"
                  value={uiSettings.border_radius}
                  onChange={(e) => handleInputChange('border_radius', e.target.value)}
                  placeholder="8px"
                />
                <small style={{ color: '#666' }}>
                  Global border radius for cards and components
                </small>
              </div>

              <div className="form-group">
                <label className="form-label">Dashboard Layout</label>
                <select
                  className="form-input"
                  value={uiSettings.dashboard_layout}
                  onChange={(e) => handleInputChange('dashboard_layout', e.target.value)}
                >
                  <option value="grid">Grid View</option>
                  <option value="list">List View</option>
                  <option value="cards">Card View</option>
                </select>
                <small style={{ color: '#666' }}>
                  Default layout for the dashboard page
                </small>
              </div>
            </div>
          </div>
        </TabPanel>

        {/* Advanced Tab */}
        <TabPanel label="⚙️ Advanced">
          {/* Advanced Button Customization */}
          <div className="card">
            <h2>Advanced Button Styling</h2>
            <p style={{ color: '#666', marginBottom: '20px' }}>
              Configure advanced button appearance and behavior.
            </p>
            
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px' }}>
              <div className="form-group">
                <label className="form-label">Button Style</label>
                <select
                  className="form-input"
                  value={uiSettings.button_style}
                  onChange={(e) => handleInputChange('button_style', e.target.value)}
                >
                  <option value="default">Default</option>
                  <option value="rounded">Rounded</option>
                  <option value="square">Square</option>
                  <option value="outline">Outline</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Button Size</label>
                <select
                  className="form-input"
                  value={uiSettings.button_size}
                  onChange={(e) => handleInputChange('button_size', e.target.value)}
                >
                  <option value="small">Small</option>
                  <option value="medium">Medium</option>
                  <option value="large">Large</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">
                  <input
                    type="checkbox"
                    checked={uiSettings.button_shadow === 'true'}
                    onChange={(e) => handleInputChange('button_shadow', e.target.checked ? 'true' : 'false')}
                    style={{ marginRight: '10px' }}
                  />
                  Button Shadow
                </label>
              </div>

              <div className="form-group">
                <label className="form-label">
                  <input
                    type="checkbox"
                    checked={uiSettings.button_animation === 'true'}
                    onChange={(e) => handleInputChange('button_animation', e.target.checked ? 'true' : 'false')}
                    style={{ marginRight: '10px' }}
                  />
                  Button Animations
                </label>
              </div>
            </div>
          </div>

          {/* Accessibility Settings */}
          <div className="card">
            <h2>Accessibility Settings</h2>
            <p style={{ color: '#666', marginBottom: '20px' }}>
              Configure accessibility features to improve usability for all users.
            </p>
            
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px' }}>
              <div className="form-group">
                <label className="form-label">
                  <input
                    type="checkbox"
                    checked={uiSettings.high_contrast === 'true'}
                    onChange={(e) => handleInputChange('high_contrast', e.target.checked ? 'true' : 'false')}
                    style={{ marginRight: '10px' }}
                  />
                  High Contrast Mode
                </label>
                <small style={{ color: '#666' }}>
                  Increase contrast for better visibility
                </small>
              </div>

              <div className="form-group">
                <label className="form-label">
                  <input
                    type="checkbox"
                    checked={uiSettings.large_text === 'true'}
                    onChange={(e) => handleInputChange('large_text', e.target.checked ? 'true' : 'false')}
                    style={{ marginRight: '10px' }}
                  />
                  Large Text
                </label>
                <small style={{ color: '#666' }}>
                  Increase font sizes for better readability
                </small>
              </div>

              <div className="form-group">
                <label className="form-label">
                  <input
                    type="checkbox"
                    checked={uiSettings.reduced_motion === 'true'}
                    onChange={(e) => handleInputChange('reduced_motion', e.target.checked ? 'true' : 'false')}
                    style={{ marginRight: '10px' }}
                  />
                  Reduced Motion
                </label>
                <small style={{ color: '#666' }}>
                  Minimize animations and transitions
                </small>
              </div>
            </div>
          </div>

          {/* Custom CSS Injection */}
          <div className="card">
            <h2>Custom CSS (Advanced)</h2>
            <p style={{ color: '#666', marginBottom: '20px' }}>
              Inject custom CSS for advanced styling. Use with caution as incorrect CSS can break the interface.
            </p>
            
            <div className="form-group">
              <label className="form-label">Custom CSS Code</label>
              <textarea
                className="form-input"
                value={uiSettings.custom_css}
                onChange={(e) => handleInputChange('custom_css', e.target.value)}
                placeholder="/* Add your custom CSS here */
.custom-class {
  /* Your styles */
}"
                rows="10"
                style={{ fontFamily: 'monospace', fontSize: '14px' }}
              />
              <small style={{ color: '#666' }}>
                Advanced users can add custom CSS to further customize the appearance.
                Changes take effect after saving settings.
              </small>
            </div>
          </div>

          {/* Super Admin Settings - Map Markers (only for super admins) */}
          {user?.is_admin && (
            <div className="card">
              <h2>Map Markers (Super Admin)</h2>
              <p style={{ color: '#666', marginBottom: '20px' }}>
                Configure custom map markers for online and offline screens. These settings are only available to super administrators.
              </p>
              
              <div className="form-group">
                <label className="form-label">Online Screen Marker</label>
                <div style={{ display: 'flex', gap: '20px', alignItems: 'flex-start' }}>
                  <div style={{ flex: 1 }}>
                    <input
                      type="file"
                      accept="image/*"
                      onChange={(e) => handleFileUpload(e.target.files[0], 'map_marker_online')}
                      disabled={uploadingMapMarkerOnline}
                      style={{ marginBottom: '10px' }}
                    />
                    <input
                      type="text"
                      className="form-input"
                      value={adminSettings.mapMarkerOnline}
                      onChange={(e) => handleAdminInputChange('mapMarkerOnline', e.target.value)}
                      placeholder="Online marker URL"
                      disabled={uploadingMapMarkerOnline}
                    />
                    <small style={{ color: '#666' }}>
                      Upload a custom marker or enter a URL. Leave empty for default green marker.
                    </small>
                  </div>
                  {adminSettings.mapMarkerOnline && (
                    <div style={{ width: '40px', height: '40px', display: 'flex', alignItems: 'center', justifyContent: 'center', border: '1px solid #ddd', borderRadius: '4px', overflow: 'hidden' }}>
                      <img 
                        src={adminSettings.mapMarkerOnline} 
                        alt="Online marker preview" 
                        style={{ width: '30px', height: '30px', objectFit: 'contain' }}
                        onError={(e) => {
                          e.target.style.display = 'none';
                          e.target.nextSibling.style.display = 'block';
                        }}
                      />
                      <span style={{ display: 'none', fontSize: '10px', color: '#666' }}>✗</span>
                    </div>
                  )}
                </div>
                {uploadingMapMarkerOnline && <div style={{ color: '#666', fontSize: '14px' }}>Uploading online marker...</div>}
              </div>

              <div className="form-group">
                <label className="form-label">Offline Screen Marker</label>
                <div style={{ display: 'flex', gap: '20px', alignItems: 'flex-start' }}>
                  <div style={{ flex: 1 }}>
                    <input
                      type="file"
                      accept="image/*"
                      onChange={(e) => handleFileUpload(e.target.files[0], 'map_marker_offline')}
                      disabled={uploadingMapMarkerOffline}
                      style={{ marginBottom: '10px' }}
                    />
                    <input
                      type="text"
                      className="form-input"
                      value={adminSettings.mapMarkerOffline}
                      onChange={(e) => handleAdminInputChange('mapMarkerOffline', e.target.value)}
                      placeholder="Offline marker URL"
                      disabled={uploadingMapMarkerOffline}
                    />
                    <small style={{ color: '#666' }}>
                      Upload a custom marker or enter a URL. Leave empty for default red marker.
                    </small>
                  </div>
                  {adminSettings.mapMarkerOffline && (
                    <div style={{ width: '40px', height: '40px', display: 'flex', alignItems: 'center', justifyContent: 'center', border: '1px solid #ddd', borderRadius: '4px', overflow: 'hidden' }}>
                      <img 
                        src={adminSettings.mapMarkerOffline} 
                        alt="Offline marker preview" 
                        style={{ width: '30px', height: '30px', objectFit: 'contain' }}
                        onError={(e) => {
                          e.target.style.display = 'none';
                          e.target.nextSibling.style.display = 'block';
                        }}
                      />
                      <span style={{ display: 'none', fontSize: '10px', color: '#666' }}>✗</span>
                    </div>
                  )}
                </div>
                {uploadingMapMarkerOffline && <div style={{ color: '#666', fontSize: '14px' }}>Uploading offline marker...</div>}
              </div>
            </div>
          )}
        </TabPanel>
      </Tabs>

      <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end', marginTop: '20px' }}>
        <button
          type="button"
          className="button button-secondary"
          onClick={resetToDefaults}
          disabled={loading}
        >
          Reset to Defaults
        </button>
        <button
          type="button"
          className="button"
          onClick={saveUISettings}
          disabled={loading || uploadingLogo || uploadingFavicon || uploadingBackground || uploadingMapMarkerOnline || uploadingMapMarkerOffline || uploadingButtonImage}
          style={{ backgroundColor: uiSettings.button_color, borderColor: uiSettings.button_color }}
        >
          {loading ? 'Saving...' : 'Save Settings'}
        </button>
      </div>
    </div>
  );
};

export default CloudUICustomization;