import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';

const AdminPanel = () => {
  const { user } = useAuth();
  const [users, setUsers] = useState([]);
  const [screens, setScreens] = useState([]);
  const [unassignedControllers, setUnassignedControllers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [showPasswordModal, setShowPasswordModal] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const [newPassword, setNewPassword] = useState('');

  useEffect(() => {
    if (!user?.is_admin && !user?.is_administrator) {
      setError('Access denied. Admin privileges required.');
      setLoading(false);
      return;
    }
    
    loadAdminData();
  }, [user]);

  const loadAdminData = async () => {
    try {
      const [usersResponse, screensResponse] = await Promise.all([
        api.getUsers(),
        api.getScreens()
      ]);
      
      setUsers(usersResponse.data.users);
      setScreens(screensResponse.data.screens || []);
      setUnassignedControllers(screensResponse.data.unassigned_controllers || []);
    } catch (error) {
      setError('Failed to load admin data');
      console.error('Error loading admin data:', error);
    } finally {
      setLoading(false);
    }
  };

  const toggleUserAdmin = async (userId) => {
    try {
      await api.toggleUserAdmin(userId);
      setSuccess('User administrator status updated');
      setTimeout(() => setSuccess(''), 3000);
      loadAdminData(); // Reload data
    } catch (error) {
      setError(error.response?.data?.error || 'Failed to update user');
      setTimeout(() => setError(''), 3000);
    }
  };

  const unbindUserScreens = async (userId, username) => {
    if (!confirm(`Are you sure you want to unbind all screens from user "${username}"? Their screens will become unassigned controllers.`)) {
      return;
    }

    try {
      const response = await api.unbindUserScreens(userId);
      setSuccess(response.data.message);
      setTimeout(() => setSuccess(''), 3000);
      loadAdminData(); // Reload data
    } catch (error) {
      setError(error.response?.data?.error || 'Failed to unbind screens');
      setTimeout(() => setError(''), 3000);
    }
  };

  const openPasswordModal = (user) => {
    setSelectedUser(user);
    setNewPassword('');
    setShowPasswordModal(true);
  };

  const closePasswordModal = () => {
    setShowPasswordModal(false);
    setSelectedUser(null);
    setNewPassword('');
  };

  const resetUserPassword = async () => {
    if (!newPassword || newPassword.length < 6) {
      setError('Password must be at least 6 characters long');
      setTimeout(() => setError(''), 3000);
      return;
    }

    try {
      const response = await api.resetUserPassword(selectedUser.id, { new_password: newPassword });
      setSuccess(response.data.message);
      setTimeout(() => setSuccess(''), 3000);
      closePasswordModal();
    } catch (error) {
      setError(error.response?.data?.error || 'Failed to reset password');
      setTimeout(() => setError(''), 3000);
    }
  };

  const deleteUser = async (userId, username) => {
    if (!confirm(`Are you sure you want to DELETE user "${username}"? This action cannot be undone. All their screens will become unassigned controllers.`)) {
      return;
    }

    try {
      const response = await api.deleteUser(userId);
      setSuccess(response.data.message);
      setTimeout(() => setSuccess(''), 3000);
      loadAdminData(); // Reload data
    } catch (error) {
      setError(error.response?.data?.error || 'Failed to delete user');
      setTimeout(() => setError(''), 3000);
    }
  };

  if (loading) {
    return <div className="loading">Loading admin panel...</div>;
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
      <h1>Admin Panel</h1>
      
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

      {/* User Management */}
      <div className="card">
        <h2>User Management</h2>
        <div className="table-responsive">
          <table className="admin-table">
            <thead>
              <tr>
                <th>Username</th>
                <th>Email</th>
                <th>Type</th>
                <th>2FA</th>
                <th>Screens</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.map(u => {
                const userScreens = screens.filter(s => s.assigned_user === u.username);
                return (
                  <tr key={u.id}>
                    <td>{u.username}</td>
                    <td>{u.email}</td>
                    <td>
                      {u.is_admin ? (
                        <span className="badge badge-danger">Super Admin</span>
                      ) : u.is_administrator ? (
                        <span className="badge badge-warning">Administrator</span>
                      ) : (
                        <span className="badge badge-secondary">User</span>
                      )}
                    </td>
                    <td>
                      <span className={`badge ${u.two_fa_enabled ? 'badge-success' : 'badge-secondary'}`}>
                        {u.two_fa_enabled ? 'Enabled' : 'Disabled'}
                      </span>
                    </td>
                    <td>{userScreens.length}</td>
                    <td>{new Date(u.created_at).toLocaleDateString()}</td>
                    <td>
                      <div style={{ display: 'flex', gap: '5px', flexWrap: 'wrap' }}>
                        {!u.is_admin && (
                          <>
                            <button
                              className="button button-small"
                              onClick={() => toggleUserAdmin(u.id)}
                              title={u.is_administrator ? 'Remove Admin' : 'Make Admin'}
                            >
                              {u.is_administrator ? 'Remove Admin' : 'Make Admin'}
                            </button>
                            
                            {userScreens.length > 0 && (
                              <button
                                className="button button-small button-secondary"
                                onClick={() => unbindUserScreens(u.id, u.username)}
                                title="Unbind all screens from this user"
                              >
                                Unbind Screens
                              </button>
                            )}
                            
                            <button
                              className="button button-small"
                              style={{ backgroundColor: '#ffc107', borderColor: '#ffc107' }}
                              onClick={() => openPasswordModal(u)}
                              title="Reset user password"
                            >
                              Reset Password
                            </button>
                            
                            <button
                              className="button button-small"
                              style={{ backgroundColor: '#dc3545', borderColor: '#dc3545' }}
                              onClick={() => deleteUser(u.id, u.username)}
                              title="Delete user permanently"
                            >
                              Delete
                            </button>
                          </>
                        )}
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Screen Overview */}
      <div className="card">
        <h2>Screen Overview</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px', marginBottom: '20px' }}>
          <div className="stat-card">
            <h3 style={{ color: '#667eea' }}>{screens.length}</h3>
            <p>Assigned Screens</p>
          </div>
          <div className="stat-card">
            <h3 style={{ color: '#f093fb' }}>{unassignedControllers.length}</h3>
            <p>Unassigned Controllers</p>
          </div>
          <div className="stat-card">
            <h3 style={{ color: '#28a745' }}>
              {[...screens, ...unassignedControllers].filter(s => s.online_status).length}
            </h3>
            <p>Online</p>
          </div>
          <div className="stat-card">
            <h3 style={{ color: '#dc3545' }}>
              {[...screens, ...unassignedControllers].filter(s => !s.online_status).length}
            </h3>
            <p>Offline</p>
          </div>
        </div>

        {unassignedControllers.length > 0 && (
          <div>
            <h3>Unassigned Controllers</h3>
            <div className="table-responsive">
              <table className="admin-table">
                <thead>
                  <tr>
                    <th>Serial Number</th>
                    <th>Status</th>
                    <th>Location</th>
                    <th>Last Seen</th>
                  </tr>
                </thead>
                <tbody>
                  {unassignedControllers.map(controller => (
                    <tr key={controller.id}>
                      <td>{controller.serial_number}</td>
                      <td>
                        <span className={`badge ${controller.online_status ? 'badge-success' : 'badge-secondary'}`}>
                          {controller.online_status ? 'Online' : 'Offline'}
                        </span>
                      </td>
                      <td>
                        {controller.latitude && controller.longitude ? (
                          `${controller.latitude.toFixed(4)}, ${controller.longitude.toFixed(4)}`
                        ) : (
                          'No location'
                        )}
                      </td>
                      <td>
                        {controller.last_seen ? 
                          new Date(controller.last_seen).toLocaleString() : 
                          'Never'
                        }
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        <h3>Assigned Screens</h3>
        <div className="table-responsive">
          <table className="admin-table">
            <thead>
              <tr>
                <th>Serial Number</th>
                <th>Custom Name</th>
                <th>Assigned User</th>
                <th>Status</th>
                <th>Location</th>
                <th>Last Seen</th>
              </tr>
            </thead>
            <tbody>
              {screens.map(screen => (
                <tr key={screen.id}>
                  <td>{screen.serial_number}</td>
                  <td>{screen.custom_name || '-'}</td>
                  <td>{screen.assigned_user || 'Unassigned'}</td>
                  <td>
                    <span className={`badge ${screen.online_status ? 'badge-success' : 'badge-secondary'}`}>
                      {screen.online_status ? 'Online' : 'Offline'}
                    </span>
                  </td>
                  <td>
                    {screen.latitude && screen.longitude ? (
                      `${screen.latitude.toFixed(4)}, ${screen.longitude.toFixed(4)}`
                    ) : (
                      'No location'
                    )}
                  </td>
                  <td>
                    {screen.last_seen ? 
                      new Date(screen.last_seen).toLocaleString() : 
                      'Never'
                    }
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Password Reset Modal */}
      {showPasswordModal && (
        <div className="modal" onClick={closePasswordModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <button
              className="close-button"
              onClick={closePasswordModal}
            >
              ×
            </button>
            <h2>Reset Password for {selectedUser?.username}</h2>
            <form onSubmit={(e) => { e.preventDefault(); resetUserPassword(); }}>
              <div className="form-group">
                <label className="form-label">New Password</label>
                <input
                  type="password"
                  className="form-input"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  minLength="6"
                  required
                  autoFocus
                />
                <small style={{ color: '#666' }}>
                  Password must be at least 6 characters long
                </small>
              </div>
              <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
                <button
                  type="button"
                  className="button button-secondary"
                  onClick={closePasswordModal}
                >
                  Cancel
                </button>
                <button 
                  type="submit" 
                  className="button"
                  style={{ backgroundColor: '#ffc107', borderColor: '#ffc107' }}
                >
                  Reset Password
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminPanel;