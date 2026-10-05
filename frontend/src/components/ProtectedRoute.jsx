import React from 'react';
import { useAuth } from '../contexts/AuthContext';

export const ProtectedRoute = ({ children, requiredRoles = [] }) => {
  const { user, token } = useAuth();

  if (!token || !user) {
    return <div>Access denied. Please log in.</div>;
  }

  if (requiredRoles.length > 0 && !requiredRoles.includes(user.role)) {
    return <div>Insufficient permissions.</div>;
  }

  return children;
};
