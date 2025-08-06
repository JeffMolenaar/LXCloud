import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Header = () => {
  const { user, logout, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const isActiveLink = (path) => {
    return location.pathname === path ? 'active' : '';
  };

  if (!isAuthenticated) {
    return (
      <header className="header">
        <div className="header-content">
          <div className="logo">LXCloud</div>
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
        <div className="logo">LXCloud</div>
        <nav className="nav-links">
          <Link to="/" className={`nav-link ${isActiveLink('/')}`}>
            Dashboard
          </Link>
          <Link to="/screens" className={`nav-link ${isActiveLink('/screens')}`}>
            Manage Screens
          </Link>
          <span className="nav-link">Welcome, {user?.username}</span>
          <button onClick={handleLogout} className="nav-link" style={{background: 'none', border: 'none', color: 'white', cursor: 'pointer'}}>
            Logout
          </button>
        </nav>
      </div>
    </header>
  );
};

export default Header;