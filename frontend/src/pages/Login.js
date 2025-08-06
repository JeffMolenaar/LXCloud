import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Login = () => {
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    two_fa_token: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [requires2FA, setRequires2FA] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const result = await login(formData);
    
    if (result.success) {
      // Check if user is admin and redirect accordingly
      if (result.user && (result.user.is_admin || result.user.is_administrator)) {
        navigate('/admin');
      } else {
        navigate('/');
      }
    } else if (result.requires_2fa) {
      setRequires2FA(true);
      setError('');
    } else {
      setError(result.error);
    }
    
    setLoading(false);
  };

  const handleBack = () => {
    setRequires2FA(false);
    setFormData({
      username: '',
      password: '',
      two_fa_token: '',
    });
  };

  return (
    <div className="container">
      <div className="card" style={{ maxWidth: '400px', margin: '50px auto' }}>
        <h2 style={{ textAlign: 'center', marginBottom: '30px', color: '#333' }}>
          {requires2FA ? 'Two-Factor Authentication' : 'Login to LXCloud'}
        </h2>
        
        {error && (
          <div className="alert alert-error">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          {!requires2FA ? (
            <>
              <div className="form-group">
                <label className="form-label">Username or Email</label>
                <input
                  type="text"
                  name="username"
                  className="form-input"
                  value={formData.username}
                  onChange={handleChange}
                  required
                  disabled={loading}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Password</label>
                <input
                  type="password"
                  name="password"
                  className="form-input"
                  value={formData.password}
                  onChange={handleChange}
                  required
                  disabled={loading}
                />
              </div>
            </>
          ) : (
            <div className="form-group">
              <label className="form-label">2FA Token</label>
              <input
                type="text"
                name="two_fa_token"
                className="form-input"
                value={formData.two_fa_token}
                onChange={handleChange}
                placeholder="Enter 6-digit code from your authenticator app"
                maxLength="6"
                required
                disabled={loading}
                autoFocus
              />
              <small style={{ color: '#666' }}>
                Enter the 6-digit code from your authenticator app
              </small>
            </div>
          )}

          <button
            type="submit"
            className="button"
            style={{ width: '100%' }}
            disabled={loading}
          >
            {loading ? 'Verifying...' : requires2FA ? 'Verify' : 'Login'}
          </button>

          {requires2FA && (
            <button
              type="button"
              className="button button-secondary"
              style={{ width: '100%', marginTop: '10px' }}
              onClick={handleBack}
              disabled={loading}
            >
              Back
            </button>
          )}
        </form>

        {!requires2FA && (
          <p style={{ textAlign: 'center', marginTop: '20px', color: '#666' }}>
            Don't have an account?{' '}
            <Link to="/register" style={{ color: '#667eea', textDecoration: 'none' }}>
              Register here
            </Link>
          </p>
        )}
      </div>
    </div>
  );
};

export default Login;