import React, { createContext, useContext, useState, useEffect } from 'react';
import { api } from '../lib/api';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth deve ser usado dentro de um AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [tenant, setTenant] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    initializeAuth();
  }, []);

  const initializeAuth = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const storedUser = localStorage.getItem('user');
      const storedTenant = localStorage.getItem('tenant');

      if (token && storedUser && storedTenant) {
        setUser(JSON.parse(storedUser));
        setTenant(JSON.parse(storedTenant));
        setIsAuthenticated(true);
        
        // Verificar se o token ainda é válido
        try {
          const response = await api.getCurrentUser();
          setUser(response.user);
          setTenant(response.tenant);
        } catch (error) {
          // Token inválido, fazer logout
          logout();
        }
      }
    } catch (error) {
      console.error('Erro ao inicializar autenticação:', error);
      logout();
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    try {
      setLoading(true);
      const response = await api.login(email, password);
      
      setUser(response.user);
      setTenant(response.tenant);
      setIsAuthenticated(true);
      
      return { success: true, data: response };
    } catch (error) {
      return { success: false, error: error.message };
    } finally {
      setLoading(false);
    }
  };

  const register = async (userData) => {
    try {
      setLoading(true);
      const response = await api.register(userData);
      
      setUser(response.user);
      setTenant(response.tenant);
      setIsAuthenticated(true);
      
      return { success: true, data: response };
    } catch (error) {
      return { success: false, error: error.message };
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
    setTenant(null);
    setIsAuthenticated(false);
    api.logout();
  };

  const updateUser = (userData) => {
    setUser(userData);
    localStorage.setItem('user', JSON.stringify(userData));
  };

  const updateTenant = (tenantData) => {
    setTenant(tenantData);
    localStorage.setItem('tenant', JSON.stringify(tenantData));
  };

  const hasPermission = (permission) => {
    if (!user) return false;
    if (user.role === 'admin') return true;
    
    try {
      const permissions = user.permissions ? JSON.parse(user.permissions) : [];
      return permissions.includes(permission);
    } catch {
      return false;
    }
  };

  const isAdmin = () => {
    return user?.role === 'admin';
  };

  const isManager = () => {
    return user?.role === 'admin' || user?.role === 'manager';
  };

  const value = {
    user,
    tenant,
    loading,
    isAuthenticated,
    login,
    register,
    logout,
    updateUser,
    updateTenant,
    hasPermission,
    isAdmin,
    isManager,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

