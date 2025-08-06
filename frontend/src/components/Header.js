import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useSettings } from '../context/SettingsContext';

const Header = () => {
  const { user, logout, isAuthenticated } = useAuth();
  const { settings } = useSettings();
  const navigate = useNavigate();
  const location = useLocation();
  const [showUserDropdown, setShowUserDropdown] = useState(false);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const isActiveLink = (path) => {
    return location.pathname === path ? 'active' : '';
  };

  const toggleUserDropdown = () => {
    setShowUserDropdown(!showUserDropdown);
  };

  const closeDropdown = () => {
    setShowUserDropdown(false);
  };

  if (!isAuthenticated) {
    return (
      <header className="header">
        <div className="header-content">
          <div className="logo">
            {settings.logoUrl ? (
              <img 
                src={settings.logoUrl} 
                alt={settings.logoText} 
                style={{ height: '40px', maxWidth: '200px', objectFit: 'contain' }}
              />
            ) : (
              settings.logoText
            )}
          </div>
          <nav className="nav-links">
            <Link to="/login" className={`nav-link ${isActiveLink('/login')}`}>
              Login
            </Link>
            <Link to="/register" className={`nav-link ${isActiveLink('/register')}`}>
              Register
            </Link>
          </nav>
        </div>
      </header>
    );
  }

  return (
    <header className="header">
      <div className="header-content">
        <div className="logo">
          {settings.logoUrl ? (
            <img 
              src={settings.logoUrl} 
              alt={settings.logoText} 
              style={{ height: '40px', maxWidth: '200px', objectFit: 'contain' }}
            />
          ) : (
            settings.logoText
          )}
        </div>
        <nav className="nav-links">
          <Link to="/" className={`nav-link ${isActiveLink('/')}`}>
            Dashboard
          </Link>
          <Link to="/screens" className={`nav-link ${isActiveLink('/screens')}`}>
            Manage Screens
          </Link>
          {(user?.is_admin || user?.is_administrator) && (
            <Link to="/admin" className={`nav-link ${isActiveLink('/admin')}`}>
              Admin Panel
            </Link>
          )}
          {user?.is_admin && (
            <Link to="/admin/settings" className={`nav-link ${isActiveLink('/admin/settings')}`}>
              ⚙️ Settings
            </Link>
          )}
          
          <div className="user-dropdown-container">
            <span 
              className="nav-link user-dropdown-trigger" 
              onClick={toggleUserDropdown}
              style={{ cursor: 'pointer', position: 'relative' }}
            >
              Welcome, {user?.username} {user?.is_admin && '(Admin)'} {user?.is_administrator && '(Administrator)'} ▼
            </span>
            
            {showUserDropdown && (
              <div className="user-dropdown" onClick={closeDropdown}>
                <Link to="/profile" className="dropdown-item">
                  Profile Settings
                </Link>
                <Link to="/change-password" className="dropdown-item">
                  Change Password
                </Link>
                <Link to="/2fa-settings" className="dropdown-item">
                  Two-Factor Authentication
                </Link>
                <div className="dropdown-divider"></div>
                <button onClick={handleLogout} className="dropdown-item logout-button">
                  Logout
                </button>
              </div>
            )}
          </div>
        </nav>
      </div>
      
      {/* Overlay to close dropdown when clicking outside */}
      {showUserDropdown && (
        <div 
          className="dropdown-overlay" 
          onClick={closeDropdown}
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            zIndex: 998
          }}
        />
      )}
    </header>
  );
};

export default Header;