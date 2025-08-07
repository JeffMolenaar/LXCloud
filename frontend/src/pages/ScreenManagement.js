import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

const ScreenManagement = () => {
  const [screens, setScreens] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedScreens, setSelectedScreens] = useState(new Set());
  const [editingScreen, setEditingScreen] = useState(null);
  const [editName, setEditName] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    loadScreens();
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

  const handleSelectScreen = (screenId) => {
    const newSelected = new Set(selectedScreens);
    if (newSelected.has(screenId)) {
      newSelected.delete(screenId);
    } else {
      newSelected.add(screenId);
    }
    setSelectedScreens(newSelected);
  };

  const handleSelectAll = () => {
    if (selectedScreens.size === screens.length) {
      setSelectedScreens(new Set());
    } else {
      setSelectedScreens(new Set(screens.map(s => s.id)));
    }
  };

  const handleEditScreen = (screen) => {
    setEditingScreen(screen.id);
    setEditName(screen.custom_name || '');
  };

  const handleSaveEdit = async (screenId) => {
    try {
      await api.updateScreen(screenId, { custom_name: editName });
      setEditingScreen(null);
      loadScreens();
    } catch (error) {
      setError('Failed to update screen');
      console.error('Error updating screen:', error);
    }
  };

  const handleCancelEdit = () => {
    setEditingScreen(null);
    setEditName('');
  };

  const handleDeleteSelected = async () => {
    if (selectedScreens.size === 0) return;
    
    if (!window.confirm(`Are you sure you want to delete ${selectedScreens.size} screen(s)?`)) {
      return;
    }

    try {
      await Promise.all(
        Array.from(selectedScreens).map(screenId => api.deleteScreen(screenId))
      );
      setSelectedScreens(new Set());
      loadScreens();
    } catch (error) {
      setError('Failed to delete some screens');
      console.error('Error deleting screens:', error);
    }
  };

  const handleViewData = (screenId) => {
    navigate(`/screens/${screenId}/data`);
  };

  const handleUnbindScreen = async (screenId, screenName) => {
    if (!window.confirm(`Are you sure you want to unbind this screen "${screenName}"? This will make it an unassigned controller.`)) {
      return;
    }

    try {
      await api.unbindScreen(screenId);
      loadScreens();
    } catch (error) {
      setError('Failed to unbind screen');
      console.error('Error unbinding screen:', error);
    }
  };

  if (loading) {
    return <div className="loading">Loading screens...</div>;
  }

  return (
    <div className="container screen-management">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h1 style={{ color: '#333' }}>Screen Management</h1>
        {selectedScreens.size > 0 && (
          <button
            className="button button-danger"
            onClick={handleDeleteSelected}
          >
            Delete Selected ({selectedScreens.size})
          </button>
        )}
      </div>

      {error && (
        <div className="alert alert-error">
          {error}
        </div>
      )}

      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h2>All Screens</h2>
          <label>
            <input
              type="checkbox"
              className="checkbox"
              checked={screens.length > 0 && selectedScreens.size === screens.length}
              onChange={handleSelectAll}
            />
            Select All
          </label>
        </div>

        {screens.length === 0 ? (
          <p style={{ textAlign: 'center', color: '#666', padding: '40px' }}>
            No screens found. Add some screens from the dashboard to get started.
          </p>
        ) : (
          <div className="screen-list">
            {screens.map((screen) => (
              <div key={screen.id} className="screen-item">
                <div style={{ display: 'flex', alignItems: 'center' }}>
                  <input
                    type="checkbox"
                    className="checkbox"
                    checked={selectedScreens.has(screen.id)}
                    onChange={() => handleSelectScreen(screen.id)}
                  />
                  <div className="screen-info">
                    {editingScreen === screen.id ? (
                      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <input
                          type="text"
                          value={editName}
                          onChange={(e) => setEditName(e.target.value)}
                          className="form-input"
                          style={{ width: '200px' }}
                          placeholder="Custom name"
                        />
                        <button
                          className="button"
                          style={{ padding: '6px 12px', fontSize: '14px' }}
                          onClick={() => handleSaveEdit(screen.id)}
                        >
                          Save
                        </button>
                        <button
                          className="button button-secondary"
                          style={{ padding: '6px 12px', fontSize: '14px' }}
                          onClick={handleCancelEdit}
                        >
                          Cancel
                        </button>
                      </div>
                    ) : (
                      <>
                        <h3>{screen.custom_name || screen.serial_number}</h3>
                        <p>Serial: {screen.serial_number}</p>
                        <p>
                          Location: {
                            screen.latitude && screen.longitude
                              ? `${screen.latitude.toFixed(4)}, ${screen.longitude.toFixed(4)}`
                              : 'Not available'
                          }
                        </p>
                        <p>
                          Last seen: {
                            screen.last_seen
                              ? new Date(screen.last_seen).toLocaleString()
                              : 'Never'
                          }
                        </p>
                      </>
                    )}
                  </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <span className={`status-badge ${screen.online_status ? 'status-online' : 'status-offline'}`}>
                    {screen.online_status ? 'Online' : 'Offline'}
                  </span>
                  
                  <div className="actions">
                    <button
                      className="button"
                      style={{ padding: '8px 16px', fontSize: '14px' }}
                      onClick={() => handleViewData(screen.id)}
                      title="View Data"
                    >
                      📊
                    </button>
                    {editingScreen !== screen.id && (
                      <>
                        <button
                          className="button button-secondary"
                          style={{ padding: '8px 16px', fontSize: '14px' }}
                          onClick={() => handleEditScreen(screen)}
                          title="Edit Name"
                        >
                          ✏️
                        </button>
                        <button
                          className="button button-secondary"
                          style={{ padding: '8px 16px', fontSize: '14px', backgroundColor: '#dc3545', borderColor: '#dc3545', color: 'white' }}
                          onClick={() => handleUnbindScreen(screen.id, screen.custom_name || screen.serial_number)}
                          title="Unbind this screen from user"
                        >
                          🔗❌
                        </button>
                      </>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="card">
        <h2>Bulk Actions</h2>
        <p style={{ color: '#666', marginBottom: '20px' }}>
          Select screens above to perform bulk actions. You can select multiple screens using the checkboxes.
        </p>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button
            className="button button-secondary"
            onClick={handleSelectAll}
          >
            {selectedScreens.size === screens.length ? 'Deselect All' : 'Select All'}
          </button>
          <button
            className="button button-danger"
            onClick={handleDeleteSelected}
            disabled={selectedScreens.size === 0}
          >
            Delete Selected ({selectedScreens.size})
          </button>
        </div>
      </div>
    </div>
  );
};

export default ScreenManagement;