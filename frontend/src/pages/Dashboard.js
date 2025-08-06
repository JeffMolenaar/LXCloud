import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import { useNavigate } from 'react-router-dom';
import L from 'leaflet';
import api from '../services/api';
import io from 'socket.io-client';

// Fix for default markers in React Leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

// Custom icons for online/offline status
const onlineIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-green.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

const offlineIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

const Dashboard = () => {
  const [screens, setScreens] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showAddModal, setShowAddModal] = useState(false);
  const [newScreen, setNewScreen] = useState({
    serial_number: '',
    custom_name: '',
  });
  const navigate = useNavigate();

  useEffect(() => {
    loadScreens();
    
    // Connect to WebSocket for real-time updates
    const socket = io('http://localhost:5000');
    
    socket.on('screen_update', (data) => {
      setScreens(prevScreens => 
        prevScreens.map(screen => 
          screen.serial_number === data.serial_number
            ? {
                ...screen,
                latitude: data.latitude,
                longitude: data.longitude,
                online_status: data.online_status,
                last_seen: data.timestamp,
              }
            : screen
        )
      );
    });

    return () => socket.disconnect();
  }, []);

  const loadScreens = async () => {
    try {
      const response = await api.getScreens();
      setScreens(response.data.screens);
    } catch (error) {
      setError('Failed to load screens');
      console.error('Error loading screens:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddScreen = async (e) => {
    e.preventDefault();
    try {
      await api.addScreen(newScreen);
      setShowAddModal(false);
      setNewScreen({ serial_number: '', custom_name: '' });
      loadScreens();
    } catch (error) {
      setError(error.response?.data?.error || 'Failed to add screen');
    }
  };

  const handleMarkerClick = (screen) => {
    navigate(`/screens/${screen.id}/data`);
  };

  // Default center (Amsterdam, Netherlands)
  const mapCenter = [52.3676, 4.9041];
  const screensWithLocation = screens.filter(screen => screen.latitude && screen.longitude);

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
            center={mapCenter}
            zoom={2}
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
                    <p>Last seen: {screen.last_seen ? new Date(screen.last_seen).toLocaleString() : 'Never'}</p>
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
            <h3 style={{ color: '#667eea', margin: '0 0 5px 0' }}>{screens.length}</h3>
            <p style={{ margin: 0, color: '#666' }}>Total Screens</p>
          </div>
          <div style={{ textAlign: 'center', padding: '20px', background: '#f8f9fa', borderRadius: '8px' }}>
            <h3 style={{ color: '#28a745', margin: '0 0 5px 0' }}>
              {screens.filter(s => s.online_status).length}
            </h3>
            <p style={{ margin: 0, color: '#666' }}>Online</p>
          </div>
          <div style={{ textAlign: 'center', padding: '20px', background: '#f8f9fa', borderRadius: '8px' }}>
            <h3 style={{ color: '#dc3545', margin: '0 0 5px 0' }}>
              {screens.filter(s => !s.online_status).length}
            </h3>
            <p style={{ margin: 0, color: '#666' }}>Offline</p>
          </div>
          <div style={{ textAlign: 'center', padding: '20px', background: '#f8f9fa', borderRadius: '8px' }}>
            <h3 style={{ color: '#6c757d', margin: '0 0 5px 0' }}>{screensWithLocation.length}</h3>
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