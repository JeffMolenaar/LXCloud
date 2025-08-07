import React, { useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import { useNavigate } from 'react-router-dom';
import L from 'leaflet';
import { useSettings } from '../context/SettingsContext';
import { useTheme } from '../context/ThemeContext';
import { useScreens } from '../hooks/useScreens';
import { useWebSocket } from '../hooks/useWebSocket';
import { APP_CONFIG } from '../utils/constants';
import { formatDate } from '../utils/helpers';

// Fix for default markers in React Leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

const Dashboard = () => {
  const [showAddModal, setShowAddModal] = useState(false);
  const [newScreen, setNewScreen] = useState({
    serial_number: '',
    custom_name: '',
  });
  
  const { settings } = useSettings();
  const { applyPageCSS } = useTheme();
  const navigate = useNavigate();
  
  // Apply page-specific CSS when component mounts
  React.useEffect(() => {
    applyPageCSS('dashboard');
  }, [applyPageCSS]);
  
  // Use custom hooks for screen management
  const {
    screens,
    loading,
    error,
    addScreen,
    getScreensWithLocation,
    getScreenStats,
    updateScreenStatus,
    clearError
  } = useScreens();

  // WebSocket for real-time updates
  useWebSocket((data) => {
    updateScreenStatus(data.serial_number, data);
  });

  // Create custom icons based on settings or use defaults
  const createMarkerIcons = () => {
    const iconOptions = {
      iconSize: [25, 41],
      iconAnchor: [12, 41],
      popupAnchor: [1, -34],
      shadowSize: [41, 41],
      shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
    };

    const onlineIcon = new L.Icon({
      ...iconOptions,
      iconUrl: settings.mapMarkerOnline || APP_CONFIG.MARKER_ICONS.ONLINE,
    });

    const offlineIcon = new L.Icon({
      ...iconOptions,
      iconUrl: settings.mapMarkerOffline || APP_CONFIG.MARKER_ICONS.OFFLINE,
    });

    return { onlineIcon, offlineIcon };
  };

  const handleAddScreen = async (e) => {
    e.preventDefault();
    clearError();
    
    const result = await addScreen(newScreen);
    if (result.success) {
      setShowAddModal(false);
      setNewScreen({ serial_number: '', custom_name: '' });
    }
  };

  const handleMarkerClick = (screen) => {
    navigate(`/screens/${screen.id}/data`);
  };

  // Get screen data and statistics
  const screensWithLocation = getScreensWithLocation();
  const stats = getScreenStats();
  const { onlineIcon, offlineIcon } = createMarkerIcons();

  if (loading) {
    return <div className="loading">Loading dashboard...</div>;
  }

  return (
    <div className="container">
      <h1 style={{ marginBottom: '20px', color: '#333' }}>Dashboard</h1>
      
      {error && (
        <div className="alert alert-error">
          {error}
        </div>
      )}

      <div className="card">
        <h2 style={{ marginBottom: '20px' }}>Screen Locations</h2>
        <div className="map-container">
          <MapContainer
            center={APP_CONFIG.DEFAULT_MAP_CENTER}
            zoom={APP_CONFIG.DEFAULT_MAP_ZOOM}
            style={{ height: '100%', width: '100%' }}
          >
            <TileLayer
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            />
            
            {screensWithLocation.map((screen) => (
              <Marker
                key={screen.id}
                position={[screen.latitude, screen.longitude]}
                icon={screen.online_status ? onlineIcon : offlineIcon}
                eventHandlers={{
                  click: () => handleMarkerClick(screen),
                }}
              >
                <Popup>
                  <div>
                    <h3>{screen.custom_name || screen.serial_number}</h3>
                    <p>Serial: {screen.serial_number}</p>
                    <p>Status: {screen.online_status ? 'Online' : 'Offline'}</p>
                    <p>Last seen: {formatDate(screen.last_seen)}</p>
                    <button 
                      className="button" 
                      style={{ marginTop: '10px' }}
                      onClick={() => handleMarkerClick(screen)}
                    >
                      View Data
                    </button>
                  </div>
                </Popup>
              </Marker>
            ))}
          </MapContainer>
        </div>
        
        {screensWithLocation.length === 0 && (
          <p style={{ textAlign: 'center', color: '#666', marginTop: '20px' }}>
            No screens with location data available. Add screens and they will appear here once they send location updates.
          </p>
        )}
      </div>

      <div className="card">
        <h2>Quick Stats</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '20px' }}>
          <div style={{ textAlign: 'center', padding: '20px', background: '#f8f9fa', borderRadius: '8px' }}>
            <h3 style={{ color: '#667eea', margin: '0 0 5px 0' }}>{stats.total}</h3>
            <p style={{ margin: 0, color: '#666' }}>Total Screens</p>
          </div>
          <div style={{ textAlign: 'center', padding: '20px', background: '#f8f9fa', borderRadius: '8px' }}>
            <h3 style={{ color: '#28a745', margin: '0 0 5px 0' }}>{stats.online}</h3>
            <p style={{ margin: 0, color: '#666' }}>Online</p>
          </div>
          <div style={{ textAlign: 'center', padding: '20px', background: '#f8f9fa', borderRadius: '8px' }}>
            <h3 style={{ color: '#dc3545', margin: '0 0 5px 0' }}>{stats.offline}</h3>
            <p style={{ margin: 0, color: '#666' }}>Offline</p>
          </div>
          <div style={{ textAlign: 'center', padding: '20px', background: '#f8f9fa', borderRadius: '8px' }}>
            <h3 style={{ color: '#6c757d', margin: '0 0 5px 0' }}>{stats.withLocation}</h3>
            <p style={{ margin: 0, color: '#666' }}>With Location</p>
          </div>
        </div>
      </div>

      {/* Add Screen FAB */}
      <button
        className="add-screen-fab"
        onClick={() => setShowAddModal(true)}
        title="Add New Screen"
      >
        +
      </button>

      {/* Add Screen Modal */}
      {showAddModal && (
        <div className="modal" onClick={() => setShowAddModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <button
              className="close-button"
              onClick={() => setShowAddModal(false)}
            >
              ×
            </button>
            <h2>Add New Screen</h2>
            <form onSubmit={handleAddScreen}>
              <div className="form-group">
                <label className="form-label">Serial Number</label>
                <input
                  type="text"
                  className="form-input"
                  value={newScreen.serial_number}
                  onChange={(e) => setNewScreen({
                    ...newScreen,
                    serial_number: e.target.value
                  })}
                  required
                />
              </div>
              <div className="form-group">
                <label className="form-label">Custom Name (Optional)</label>
                <input
                  type="text"
                  className="form-input"
                  value={newScreen.custom_name}
                  onChange={(e) => setNewScreen({
                    ...newScreen,
                    custom_name: e.target.value
                  })}
                />
              </div>
              <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
                <button
                  type="button"
                  className="button button-secondary"
                  onClick={() => setShowAddModal(false)}
                >
                  Cancel
                </button>
                <button type="submit" className="button">
                  Add Screen
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;