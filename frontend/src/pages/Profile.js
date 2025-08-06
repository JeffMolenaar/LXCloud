import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Profile = () => {
  const { user } = useAuth();

  return (
    <div className="container">
      <h1>Profile Settings</h1>
      
      <div className="card">
        <h2>Account Information</h2>
        <div style={{ display: 'grid', gap: '15px' }}>
          <div>
            <label className="form-label">Username</label>
            <div className="form-input" style={{ background: '#f8f9fa', cursor: 'not-allowed' }}>
              {user?.username}
            </div>
          </div>
          
          <div>
            <label className="form-label">Email</label>
            <div className="form-input" style={{ background: '#f8f9fa', cursor: 'not-allowed' }}>
              {user?.email}
            </div>
          </div>
          
          <div>
            <label className="form-label">Account Type</label>
            <div className="form-input" style={{ background: '#f8f9fa', cursor: 'not-allowed' }}>
              {user?.is_admin ? 'Super Administrator' : 
               user?.is_administrator ? 'Administrator' : 'Regular User'}
            </div>
          </div>
          
          <div>
            <label className="form-label">Two-Factor Authentication</label>
            <div className="form-input" style={{ 
              background: '#f8f9fa', 
              cursor: 'not-allowed',
              color: user?.two_fa_enabled ? '#28a745' : '#dc3545',
              fontWeight: 'bold'
            }}>
              {user?.two_fa_enabled ? 'Enabled' : 'Disabled'}
            </div>
          </div>
        </div>
      </div>

      <div className="card">
        <h2>Security Settings</h2>
        <div style={{ display: 'grid', gap: '15px' }}>
          <Link to="/change-password" className="button">
            Change Password
          </Link>
          <Link to="/2fa-settings" className="button">
            Manage Two-Factor Authentication
          </Link>
        </div>
      </div>

      <div style={{ marginTop: '20px' }}>
        <Link to="/" className="button button-secondary">
          Back to Dashboard
        </Link>
      </div>
    </div>
  );
};

export default Profile;