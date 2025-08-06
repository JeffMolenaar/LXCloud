import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';

const TwoFactorSettings = () => {
  const { user } = useAuth();
  const [step, setStep] = useState('main'); // main, setup, verify, disable
  const [qrCode, setQrCode] = useState('');
  const [secret, setSecret] = useState('');
  const [token, setToken] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const navigate = useNavigate();

  const setup2FA = async () => {
    setLoading(true);
    setError('');

    try {
      const response = await api.setup2FA();
      setQrCode(response.data.qr_code);
      setSecret(response.data.secret);
      setStep('verify');
    } catch (error) {
      setError(error.response?.data?.error || 'Failed to setup 2FA');
    } finally {
      setLoading(false);
    }
  };

  const verify2FA = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await api.verify2FA({ token });
      setSuccess('2FA enabled successfully');
      setStep('main');
      setToken('');
      // Refresh user data to reflect 2FA status
      window.location.reload();
    } catch (error) {
      setError(error.response?.data?.error || 'Invalid token');
    } finally {
      setLoading(false);
    }
  };

  const disable2FA = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await api.disable2FA({ token });
      setSuccess('2FA disabled successfully');
      setStep('main');
      setToken('');
      // Refresh user data to reflect 2FA status
      window.location.reload();
    } catch (error) {
      setError(error.response?.data?.error || 'Invalid token or failed to disable 2FA');
    } finally {
      setLoading(false);
    }
  };

  const renderMain = () => (
    <div>
      <h1>Two-Factor Authentication</h1>
      
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

      <div className="card">
        <h2>Current Status</h2>
        <p>
          Two-Factor Authentication is currently{' '}
          <strong style={{ color: user?.two_fa_enabled ? '#28a745' : '#dc3545' }}>
            {user?.two_fa_enabled ? 'ENABLED' : 'DISABLED'}
          </strong>
        </p>
        
        {!user?.two_fa_enabled ? (
          <div>
            <p>
              Enhance your account security by enabling two-factor authentication.
              You'll need a mobile authenticator app like Google Authenticator or Authy.
            </p>
            <button
              className="button"
              onClick={setup2FA}
              disabled={loading}
            >
              {loading ? 'Setting up...' : 'Enable 2FA'}
            </button>
          </div>
        ) : (
          <div>
            <p>
              Your account is protected with two-factor authentication.
              To disable it, you'll need to provide a current authentication code.
            </p>
            <button
              className="button button-danger"
              onClick={() => setStep('disable')}
            >
              Disable 2FA
            </button>
          </div>
        )}
      </div>

      <div style={{ marginTop: '20px' }}>
        <button
          className="button button-secondary"
          onClick={() => navigate('/')}
        >
          Back to Dashboard
        </button>
      </div>
    </div>
  );

  const renderVerify = () => (
    <div>
      <h1>Enable Two-Factor Authentication</h1>
      
      {error && (
        <div className="alert alert-error">
          {error}
        </div>
      )}

      <div className="card">
        <h2>Step 1: Scan QR Code</h2>
        <p>Use your authenticator app to scan this QR code:</p>
        <div style={{ textAlign: 'center', margin: '20px 0' }}>
          <img src={qrCode} alt="2FA QR Code" style={{ maxWidth: '300px' }} />
        </div>
        
        <h3>Or enter this code manually:</h3>
        <div style={{ 
          background: '#f8f9fa', 
          padding: '10px', 
          borderRadius: '4px', 
          fontFamily: 'monospace',
          wordBreak: 'break-all'
        }}>
          {secret}
        </div>
      </div>

      <div className="card">
        <h2>Step 2: Verify Setup</h2>
        <p>Enter the 6-digit code from your authenticator app:</p>
        
        <form onSubmit={verify2FA}>
          <div className="form-group">
            <label className="form-label">Authentication Code</label>
            <input
              type="text"
              className="form-input"
              value={token}
              onChange={(e) => setToken(e.target.value)}
              placeholder="000000"
              maxLength={6}
              pattern="[0-9]{6}"
              required
            />
          </div>

          <div style={{ display: 'flex', gap: '10px', justifyContent: 'space-between' }}>
            <button
              type="button"
              className="button button-secondary"
              onClick={() => setStep('main')}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="button"
              disabled={loading || token.length !== 6}
            >
              {loading ? 'Verifying...' : 'Enable 2FA'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );

  const renderDisable = () => (
    <div>
      <h1>Disable Two-Factor Authentication</h1>
      
      {error && (
        <div className="alert alert-error">
          {error}
        </div>
      )}

      <div className="card">
        <h2>Confirm Disable 2FA</h2>
        <p>
          <strong>Warning:</strong> Disabling two-factor authentication will make your account less secure.
        </p>
        <p>Enter a current authentication code from your app to confirm:</p>
        
        <form onSubmit={disable2FA}>
          <div className="form-group">
            <label className="form-label">Authentication Code</label>
            <input
              type="text"
              className="form-input"
              value={token}
              onChange={(e) => setToken(e.target.value)}
              placeholder="000000"
              maxLength={6}
              pattern="[0-9]{6}"
              required
            />
          </div>

          <div style={{ display: 'flex', gap: '10px', justifyContent: 'space-between' }}>
            <button
              type="button"
              className="button button-secondary"
              onClick={() => setStep('main')}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="button button-danger"
              disabled={loading || token.length !== 6}
            >
              {loading ? 'Disabling...' : 'Disable 2FA'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );

  return (
    <div className="container">
      {step === 'main' && renderMain()}
      {step === 'verify' && renderVerify()}
      {step === 'disable' && renderDisable()}
    </div>
  );
};

export default TwoFactorSettings;