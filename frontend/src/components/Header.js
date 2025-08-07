import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useSettings } from '../context/SettingsContext';
import { useTheme } from '../context/ThemeContext';

const Header = () => {
  const { user, logout, isAuthenticated } = useAuth();
  const { settings } = useSettings();
  const { theme } = useTheme();
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

  // Apply theme settings for proper header styling
  const headerStyle = {
    height: theme.header_height || '60px',
    background: theme.header_color || '#667eea',
    color: theme.header_text_color || '#ffffff',
    boxShadow: theme.header_shadow === 'true' ? '0 2px 10px rgba(0,0,0,0.1)' : 'none',
    position: theme.header_sticky === 'true' ? 'sticky' : 'static',
    top: theme.header_sticky === 'true' ? '0' : 'auto',
    zIndex: theme.header_sticky === 'true' ? '1000' : 'auto'
  };

  const headerContentStyle = {
    height: '100%',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    maxWidth: '1200px',
    margin: '0 auto',
    padding: '0 20px'
  };

  const logoStyle = {
    display: 'flex',
    alignItems: theme.logo_vertical_alignment === 'top' ? 'flex-start' :
                theme.logo_vertical_alignment === 'bottom' ? 'flex-end' : 'center',
    fontSize: '1.8rem',
    fontWeight: 'bold',
    color: theme.header_text_color || '#ffffff'
  };

  const navLinksStyle = {
    display: 'flex',
    gap: theme.header_button_spacing || '15px',
    justifyContent: theme.header_button_alignment === 'center' ? 'center' :
                   theme.header_button_alignment === 'right' ? 'flex-end' :
                   theme.header_button_alignment === 'left' ? 'flex-start' :
                   theme.header_button_alignment === 'justify' ? 'space-between' : 'flex-end',
    alignItems: theme.header_button_vertical_alignment === 'top' ? 'flex-start' :
               theme.header_button_vertical_alignment === 'bottom' ? 'flex-end' : 'center',
    height: '100%'
  };

  if (!isAuthenticated) {
    return (
      <header className="header" style={headerStyle}>
        <div className="header-content" style={headerContentStyle}>
          <div className="logo" style={logoStyle}>
            {settings.logoUrl ? (
              <img 
                src={settings.logoUrl} 
                alt={settings.logoText} 
                style={{ height: '40px', maxWidth: '200px', objectFit: 'contain' }}
              />
            ) : (
              <span style={{ color: theme.header_text_color || '#ffffff' }}>
                {settings.logoText}
              </span>
            )}
          </div>
          <nav className="nav-links" style={navLinksStyle}>
            <Link 
              to="/login" 
              className={`nav-link ${isActiveLink('/login')}`}
              style={{ 
                color: theme.header_text_color || '#ffffff',
                alignSelf: theme.header_button_vertical_alignment === 'top' ? 'flex-start' :
                         theme.header_button_vertical_alignment === 'bottom' ? 'flex-end' : 'center'
              }}
            >
              Login
            </Link>
            <Link 
              to="/register" 
              className={`nav-link ${isActiveLink('/register')}`}
              style={{ 
                color: theme.header_text_color || '#ffffff',
                alignSelf: theme.header_button_vertical_alignment === 'top' ? 'flex-start' :
                         theme.header_button_vertical_alignment === 'bottom' ? 'flex-end' : 'center'
              }}
            >
              Register
            </Link>
          </nav>
        </div>
      </header>
    );
  }

  return (
    <header className="header" style={headerStyle}>
      <div className="header-content" style={headerContentStyle}>
        <div className="logo" style={logoStyle}>
          {(theme.logo_url || settings.logoUrl) ? (
            <img 
              src={theme.logo_url || settings.logoUrl} 
              alt={theme.app_name || settings.logoText} 
              style={{ 
                height: '40px', 
                maxWidth: '200px', 
                objectFit: 'contain'
              }}
              onError={(e) => {
                e.target.style.display = 'none';
                e.target.nextSibling.style.display = 'inline';
              }}
            />
          ) : null}
          <span style={{ 
            display: (theme.logo_url || settings.logoUrl) ? 'none' : 'inline',
            color: theme.header_text_color || '#ffffff'
          }}>
            {theme.app_name || settings.logoText}
          </span>
        </div>
        <nav className="nav-links" style={navLinksStyle}>
          <Link 
            to="/" 
            className={`nav-link ${isActiveLink('/')}`}
            style={{ 
              color: theme.header_text_color || '#ffffff',
              alignSelf: theme.header_button_vertical_alignment === 'top' ? 'flex-start' :
                       theme.header_button_vertical_alignment === 'bottom' ? 'flex-end' : 'center'
            }}
          >
            Dashboard
          </Link>
          <Link 
            to="/screens" 
            className={`nav-link ${isActiveLink('/screens')}`}
            style={{ 
              color: theme.header_text_color || '#ffffff',
              alignSelf: theme.header_button_vertical_alignment === 'top' ? 'flex-start' :
                       theme.header_button_vertical_alignment === 'bottom' ? 'flex-end' : 'center'
            }}
          >
            Manage Screens
          </Link>
          {(user?.is_admin || user?.is_administrator) && (
            <Link 
              to="/admin" 
              className={`nav-link ${isActiveLink('/admin')}`}
              style={{ 
                color: theme.header_text_color || '#ffffff',
                alignSelf: theme.header_button_vertical_alignment === 'top' ? 'flex-start' :
                         theme.header_button_vertical_alignment === 'bottom' ? 'flex-end' : 'center'
              }}
            >
              Admin Panel
            </Link>
          )}
          
          <div 
            className="user-dropdown-container"
            style={{
              alignSelf: theme.header_button_vertical_alignment === 'top' ? 'flex-start' :
                       theme.header_button_vertical_alignment === 'bottom' ? 'flex-end' : 'center'
            }}
          >
            <span 
              className="nav-link user-dropdown-trigger" 
              onClick={toggleUserDropdown}
              style={{ 
                cursor: 'pointer', 
                position: 'relative',
                color: theme.header_text_color || '#ffffff'
              }}
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