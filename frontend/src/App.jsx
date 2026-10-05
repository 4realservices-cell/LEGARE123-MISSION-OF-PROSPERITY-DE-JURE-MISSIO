import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Login } from './Login';
import { Dashboard } from './Dashboard';

export const App = () => {
  const { token, loading } = useAuth();
  const [showLogin, setShowLogin] = useState(!token);

  if (loading) return <div>Loading...</div>;

  return showLogin ? (
    <Login onLoginSuccess={() => setShowLogin(false)} />
  ) : (
    <Dashboard />
  );
};
