import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { SettingsProvider } from './context/SettingsContext';
import Header from './components/Header';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import ScreenManagement from './pages/ScreenManagement';
import ScreenData from './pages/ScreenData';
import Profile from './pages/Profile';
import ChangePassword from './pages/ChangePassword';
import TwoFactorSettings from './pages/TwoFactorSettings';
import AdminPanel from './pages/AdminPanel';
import AdminSettings from './pages/AdminSettings';

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return <div className="loading">Loading...</div>;
  }
  
  return isAuthenticated ? children : <Navigate to="/login" />;
};

const AdminRoute = ({ children }) => {
  const { user, isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return <div className="loading">Loading...</div>;
  }
  
  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }
  
  if (!user?.is_admin && !user?.is_administrator) {
    return <Navigate to="/" />;
  }
  
  return children;
};

const SuperAdminRoute = ({ children }) => {
  const { user, isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return <div className="loading">Loading...</div>;
  }
  
  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }
  
  if (!user?.is_admin) {
    return <Navigate to="/" />;
  }
  
  return children;
};

const PublicRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return <div className="loading">Loading...</div>;
  }
  
  return !isAuthenticated ? children : <Navigate to="/" />;
};

function App() {
  return (
    <AuthProvider>
      <SettingsProvider>
        <Router>
          <div className="App">
            <Header />
            <Routes>
              <Route 
                path="/login" 
                element={
                  <PublicRoute>
                    <Login />
                  </PublicRoute>
                } 
              />
              <Route 
                path="/register" 
                element={
                  <PublicRoute>
                    <Register />
                  </PublicRoute>
                } 
              />
              <Route 
                path="/" 
                element={
                  <ProtectedRoute>
                    <Dashboard />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/screens" 
                element={
                  <ProtectedRoute>
                    <ScreenManagement />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/screens/:screenId/data" 
                element={
                  <ProtectedRoute>
                    <ScreenData />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/profile" 
                element={
                  <ProtectedRoute>
                    <Profile />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/change-password" 
                element={
                  <ProtectedRoute>
                    <ChangePassword />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/2fa-settings" 
                element={
                  <ProtectedRoute>
                    <TwoFactorSettings />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/admin" 
                element={
                  <AdminRoute>
                    <AdminPanel />
                  </AdminRoute>
                } 
              />
              <Route 
                path="/admin/settings" 
                element={
                  <SuperAdminRoute>
                    <AdminSettings />
                  </SuperAdminRoute>
                } 
              />
            </Routes>
          </div>
        </Router>
      </SettingsProvider>
    </AuthProvider>
  );
}

export default App;