import React, { createContext, useState, useCallback, useEffect } from 'react';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('access_token'));
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const login = useCallback(async (username, password) => {
    setLoading(true);
    setError(null);
    try {
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);
      
      const response = await fetch('/api/v1/auth/token', {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) throw new Error('Login failed');
      const data = await response.json();
      
      localStorage.setItem('access_token', data.access_token);
      setToken(data.access_token);
      
      // Fetch user info
      const meResponse = await fetch('/api/v1/auth/me', {
        headers: { Authorization: `Bearer ${data.access_token}` },
      });
      
      if (meResponse.ok) {
        const userData = await meResponse.json();
        setUser(userData);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem('access_token');
    setToken(null);
    setUser(null);
  }, []);

  // Verify token on mount
  useEffect(() => {
    if (token) {
      fetch('/api/v1/auth/me', {
        headers: { Authorization: `Bearer ${token}` },
      })
        .then(res => res.ok ? res.json() : null)
        .then(data => setUser(data))
        .catch(() => logout());
    }
  }, [token, logout]);

  return (
    <AuthContext.Provider value={{ user, token, loading, error, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = React.useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
};
