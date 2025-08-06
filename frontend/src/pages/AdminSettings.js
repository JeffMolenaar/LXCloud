import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useSettings } from '../context/SettingsContext';

const AdminSettings = () => {
  const { user } = useAuth();
  const { settings, updateSettings } = useSettings();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [formData, setFormData] = useState({
    logoUrl: settings.logoUrl || '',
    logoText: settings.logoText || 'LXCloud',
    siteName: settings.siteName || 'LXCloud - LED Screen Management Platform',
    faviconUrl: settings.faviconUrl || '',
    mapMarkerOnline: settings.mapMarkerOnline || '',
    mapMarkerOffline: settings.mapMarkerOffline || ''
  });

  React.useEffect(() => {
    setFormData({
      logoUrl: settings.logoUrl || '',
      logoText: settings.logoText || 'LXCloud',
      siteName: settings.siteName || 'LXCloud - LED Screen Management Platform',
      faviconUrl: settings.faviconUrl || '',
      mapMarkerOnline: settings.mapMarkerOnline || '',
      mapMarkerOffline: settings.mapMarkerOffline || ''
    });
  }, [settings]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      await updateSettings(formData);
      setSuccess('Settings updated successfully!');
      setTimeout(() => setSuccess(''), 3000);
    } catch (error) {
      setError(error.response?.data?.error || 'Failed to update settings');
      setTimeout(() => setError(''), 5000);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  if (!user?.is_admin) {
    return (
      <div className="container">
        <div className="alert alert-error">
          Access denied. Only super administrators can access settings.
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <h1>Superadmin Settings</h1>
      
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

      <form onSubmit={handleSubmit}>
        <div className="card">
          <h2>Branding & Appearance</h2>
          
          <div className="form-group">
            <label className="form-label">Header Logo URL</label>
            <input
              type="url"
              className="form-input"
              value={formData.logoUrl}
              onChange={(e) => handleInputChange('logoUrl', e.target.value)}
              placeholder="https://example.com/logo.png"
            />
            <small style={{ color: '#666' }}>
              Leave empty to use text logo. Image will be resized to fit header (40px height).
            </small>
          </div>

          <div className="form-group">
            <label className="form-label">Logo Text</label>
            <input
              type="text"
              className="form-input"
              value={formData.logoText}
              onChange={(e) => handleInputChange('logoText', e.target.value)}
              placeholder="LXCloud"
            />
            <small style={{ color: '#666' }}>
              Text displayed when no logo URL is provided.
            </small>
          </div>

          <div className="form-group">
            <label className="form-label">Site Name (Browser Title)</label>
            <input
              type="text"
              className="form-input"
              value={formData.siteName}
              onChange={(e) => handleInputChange('siteName', e.target.value)}
              placeholder="LXCloud - LED Screen Management Platform"
            />
            <small style={{ color: '#666' }}>
              This appears in the browser title bar and bookmarks.
            </small>
          </div>

          <div className="form-group">
            <label className="form-label">Favicon URL</label>
            <input
              type="url"
              className="form-input"
              value={formData.faviconUrl}
              onChange={(e) => handleInputChange('faviconUrl', e.target.value)}
              placeholder="https://example.com/favicon.ico"
            />
            <small style={{ color: '#666' }}>
              Small icon that appears in browser tabs and bookmarks.
            </small>
          </div>
        </div>

        <div className="card">
          <h2>Map Markers</h2>
          
          <div className="form-group">
            <label className="form-label">Online Marker Icon URL</label>
            <input
              type="url"
              className="form-input"
              value={formData.mapMarkerOnline}
              onChange={(e) => handleInputChange('mapMarkerOnline', e.target.value)}
              placeholder="https://example.com/online-marker.png"
            />
            <small style={{ color: '#666' }}>
              Custom icon for online screens on the map. Leave empty for default green marker.
            </small>
          </div>

          <div className="form-group">
            <label className="form-label">Offline Marker Icon URL</label>
            <input
              type="url"
              className="form-input"
              value={formData.mapMarkerOffline}
              onChange={(e) => handleInputChange('mapMarkerOffline', e.target.value)}
              placeholder="https://example.com/offline-marker.png"
            />
            <small style={{ color: '#666' }}>
              Custom icon for offline screens on the map. Leave empty for default red marker.
            </small>
          </div>
        </div>

        <div className="card">
          <h2>Preview</h2>
          
          <div style={{ display: 'grid', gap: '20px' }}>
            <div>
              <h3>Header Logo Preview</h3>
              <div style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', padding: '15px', borderRadius: '8px', color: 'white' }}>
                {formData.logoUrl ? (
                  <img 
                    src={formData.logoUrl} 
                    alt={formData.logoText} 
                    style={{ height: '40px', maxWidth: '200px', objectFit: 'contain' }}
                    onError={(e) => {
                      e.target.style.display = 'none';
                      e.target.nextSibling.style.display = 'inline';
                    }}
                  />
                ) : null}
                <span style={{ display: formData.logoUrl ? 'none' : 'inline', fontSize: '1.8rem', fontWeight: 'bold' }}>
                  {formData.logoText}
                </span>
              </div>
            </div>

            <div>
              <h3>Browser Title Preview</h3>
              <div style={{ background: '#f8f9fa', padding: '10px', borderRadius: '4px', border: '1px solid #dee2e6' }}>
                <strong>{formData.siteName}</strong>
              </div>
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end', marginTop: '20px' }}>
          <button 
            type="submit" 
            className="button"
            disabled={loading}
          >
            {loading ? 'Updating...' : 'Save Settings'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default AdminSettings;