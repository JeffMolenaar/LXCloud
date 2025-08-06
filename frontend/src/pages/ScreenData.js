import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api';

const ScreenData = () => {
  const { screenId } = useParams();
  const navigate = useNavigate();
  const [screen, setScreen] = useState(null);
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadScreenData();
  }, [screenId]);

  const loadScreenData = async () => {
    try {
      // Get screen info first
      const screensResponse = await api.getScreens();
      const currentScreen = screensResponse.data.screens.find(s => s.id === parseInt(screenId));
      
      if (!currentScreen) {
        setError('Screen not found');
        return;
      }
      
      setScreen(currentScreen);
      
      // Get screen data
      const dataResponse = await api.getScreenData(screenId);
      setData(dataResponse.data.data);
    } catch (error) {
      setError('Failed to load screen data');
      console.error('Error loading screen data:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatDataForJSON = () => {
    if (!screen || !data) return {};
    
    return {
      screen: {
        id: screen.id,
        serial_number: screen.serial_number,
        custom_name: screen.custom_name,
        latitude: screen.latitude,
        longitude: screen.longitude,
        online_status: screen.online_status,
        last_seen: screen.last_seen,
        created_at: screen.created_at
      },
      data: data,
      generated_at: new Date().toISOString(),
      total_records: data.length
    };
  };

  const downloadJSON = () => {
    const jsonData = formatDataForJSON();
    const blob = new Blob([JSON.stringify(jsonData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `screen_${screen.serial_number}_data.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  if (loading) {
    return <div className="loading">Loading screen data...</div>;
  }

  if (error) {
    return (
      <div className="container">
        <div className="alert alert-error">
          {error}
        </div>
        <button className="button" onClick={() => navigate('/screens')}>
          Back to Screen Management
        </button>
      </div>
    );
  }

  return (
    <div className="container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h1 style={{ color: '#333' }}>Screen Data</h1>
        <button className="button" onClick={() => navigate('/screens')}>
          Back to Screens
        </button>
      </div>

      {/* Screen Information */}
      <div className="card">
        <h2>Screen Information</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px' }}>
          <div>
            <strong>Name:</strong> {screen.custom_name || screen.serial_number}
          </div>
          <div>
            <strong>Serial Number:</strong> {screen.serial_number}
          </div>
          <div>
            <strong>Status:</strong>{' '}
            <span className={`status-badge ${screen.online_status ? 'status-online' : 'status-offline'}`}>
              {screen.online_status ? 'Online' : 'Offline'}
            </span>
          </div>
          <div>
            <strong>Location:</strong>{' '}
            {screen.latitude && screen.longitude
              ? `${screen.latitude.toFixed(6)}, ${screen.longitude.toFixed(6)}`
              : 'Not available'}
          </div>
          <div>
            <strong>Last Seen:</strong>{' '}
            {screen.last_seen ? new Date(screen.last_seen).toLocaleString() : 'Never'}
          </div>
          <div>
            <strong>Added:</strong> {new Date(screen.created_at).toLocaleString()}
          </div>
        </div>
      </div>

      {/* Data Actions */}
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h2>Data Records ({data.length})</h2>
          <div style={{ display: 'flex', gap: '10px' }}>
            <button className="button" onClick={downloadJSON}>
              Download JSON
            </button>
            <button className="button button-secondary" onClick={loadScreenData}>
              Refresh Data
            </button>
          </div>
        </div>
      </div>

      {/* JSON Preview */}
      <div className="card">
        <h3>JSON Data Preview</h3>
        <pre style={{
          background: '#f8f9fa',
          padding: '20px',
          borderRadius: '6px',
          overflow: 'auto',
          maxHeight: '400px',
          fontSize: '14px',
          fontFamily: 'monospace'
        }}>
          {JSON.stringify(formatDataForJSON(), null, 2)}
        </pre>
      </div>

      {/* Data Table */}
      {data.length > 0 && (
        <div className="card">
          <h3>Recent Data Records</h3>
          <div style={{ overflowX: 'auto' }}>
            <table style={{
              width: '100%',
              borderCollapse: 'collapse',
              marginTop: '20px'
            }}>
              <thead>
                <tr style={{ background: '#f8f9fa' }}>
                  <th style={{ padding: '12px', textAlign: 'left', borderBottom: '2px solid #dee2e6' }}>
                    Timestamp
                  </th>
                  <th style={{ padding: '12px', textAlign: 'left', borderBottom: '2px solid #dee2e6' }}>
                    Information
                  </th>
                </tr>
              </thead>
              <tbody>
                {data.map((record, index) => (
                  <tr key={index} style={{ borderBottom: '1px solid #dee2e6' }}>
                    <td style={{ padding: '12px' }}>
                      {new Date(record.timestamp).toLocaleString()}
                    </td>
                    <td style={{ padding: '12px' }}>
                      {record.information || 'No information'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {data.length === 0 && (
        <div className="card">
          <p style={{ textAlign: 'center', color: '#666', padding: '40px' }}>
            No data records found for this screen. Data will appear here once the screen starts sending information.
          </p>
        </div>
      )}
    </div>
  );
};

export default ScreenData;