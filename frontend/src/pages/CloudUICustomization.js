import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useSettings } from '../context/SettingsContext';
import api from '../services/api';

const CloudUICustomization = () => {
  const { user } = useAuth();
  const { settings, updateSettings } = useSettings();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [uiSettings, setUiSettings] = useState({
    app_name: 'LXCloud',
    primary_color: '#667eea',
    secondary_color: '#f093fb',
    logo_url: '',
    favicon_url: '',
    background_image_url: ''
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
      
      // Sync with admin settings for super admins
      if (user?.is_admin && loadedSettings.logo_url) {
        setAdminSettings(prev => ({ ...prev, logoUrl: loadedSettings.logo_url }));
      }
      if (user?.is_admin && loadedSettings.favicon_url) {
        setAdminSettings(prev => ({ ...prev, faviconUrl: loadedSettings.favicon_url }));
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
    
    // Sync with admin settings for super admins
    if (user?.is_admin) {
      if (field === 'logo_url') {
        handleAdminInputChange('logoUrl', value);
      } else if (field === 'favicon_url') {
        handleAdminInputChange('faviconUrl', value);
      }
    }
  };

  const handleAdminInputChange = (field, value) => {
    setAdminSettings(prev => ({
      ...prev,
      [field]: value
    }));
    
    // Sync with UI settings for logo and favicon
    if (field === 'logoUrl') {
      setUiSettings(prev => ({ ...prev, logo_url: value }));
    } else if (field === 'faviconUrl') {
      setUiSettings(prev => ({ ...prev, favicon_url: value }));
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

      const response = await api.uploadUIAsset(formData);
      
      // Update the appropriate settings with the new URL
      if (type === 'map_marker_online') {
        handleAdminInputChange('mapMarkerOnline', response.data.url);
      } else if (type === 'map_marker_offline') {
        handleAdminInputChange('mapMarkerOffline', response.data.url);
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
    }
  };

  const saveUISettings = async () => {
    try {
      setLoading(true);
      
      // Save UI settings
      await api.updateUISettings(uiSettings);
      
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
      setUiSettings({
        app_name: 'LXCloud',
        primary_color: '#667eea',
        secondary_color: '#f093fb',
        logo_url: '',
        favicon_url: '',
        background_image_url: ''
      });
      
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
            <label className="form-label">Secondary Color</label>
            <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
              <input
                type="color"
                value={uiSettings.secondary_color}
                onChange={(e) => handleInputChange('secondary_color', e.target.value)}
                style={{ width: '50px', height: '40px', border: 'none', borderRadius: '4px' }}
              />
              <input
                type="text"
                className="form-input"
                value={uiSettings.secondary_color}
                onChange={(e) => handleInputChange('secondary_color', e.target.value)}
                placeholder="#f093fb"
                style={{ flex: 1 }}
              />
            </div>
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

      {/* Super Admin Settings - Advanced Settings (only for super admins) */}
      {user?.is_admin && (
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

          <div className="form-group">
            <h3>Preview</h3>
            <div style={{ display: 'grid', gap: '20px' }}>
              <div>
                <h4>Header Logo Preview</h4>
                <div style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', padding: '15px', borderRadius: '8px', color: 'white' }}>
                  {uiSettings.logo_url ? (
                    <img 
                      src={uiSettings.logo_url} 
                      alt={adminSettings.logoText} 
                      style={{ height: '40px', maxWidth: '200px', objectFit: 'contain' }}
                      onError={(e) => {
                        e.target.style.display = 'none';
                        e.target.nextSibling.style.display = 'inline';
                      }}
                    />
                  ) : null}
                  <span style={{ display: uiSettings.logo_url ? 'none' : 'inline', fontSize: '1.8rem', fontWeight: 'bold' }}>
                    {adminSettings.logoText}
                  </span>
                </div>
              </div>

              <div>
                <h4>Browser Title Preview</h4>
                <div style={{ background: '#f8f9fa', padding: '10px', borderRadius: '4px', border: '1px solid #dee2e6' }}>
                  <strong>{adminSettings.siteName}</strong>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

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
          disabled={loading || uploadingLogo || uploadingFavicon || uploadingBackground || uploadingMapMarkerOnline || uploadingMapMarkerOffline}
          style={{ backgroundColor: uiSettings.primary_color, borderColor: uiSettings.primary_color }}
        >
          {loading ? 'Saving...' : 'Save Settings'}
        </button>
      </div>
    </div>
  );
};

export default CloudUICustomization;