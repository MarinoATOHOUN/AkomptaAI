import React, { createContext, useContext, useState, useEffect } from 'react';
import { jwtDecode } from 'jwt-decode';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(localStorage.getItem('akompta_access_token'));

  const API_BASE_URL = 'https://f28b1d576f3dfb.lhr.life/api'; // Nouvelle URL pour Django

  // Vérifier le token au chargement
  useEffect(() => {
    const checkAuth = async () => {
      if (token) {
        try {
          const decodedToken = jwtDecode(token);
          // Vérifier l'expiration du token
          if (decodedToken.exp * 1000 < Date.now()) {
            logout();
          } else {
            // Optionnel: récupérer les détails de l'utilisateur si nécessaire
            // Pour l'instant, nous utilisons les infos du token ou un objet user simple
            setUser({ id: decodedToken.user_id, username: decodedToken.username }); // Assurez-vous que le token contient ces infos
          }
        } catch (error) {
          console.error('Error decoding token:', error);
          logout();
        }
      }
      setLoading(false);
    };

    checkAuth();
  }, [token]);

  const login = async (username, password) => {
    try {
      const response = await fetch(`${API_BASE_URL}/token/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      });

      const data = await response.json();

      if (response.ok) {
        localStorage.setItem('akompta_access_token', data.access);
        localStorage.setItem('akompta_refresh_token', data.refresh);
        setToken(data.access);
        const decodedToken = jwtDecode(data.access);
        setUser({ id: decodedToken.user_id, username: decodedToken.username });
        return { success: true, user: { id: decodedToken.user_id, username: decodedToken.username } };
      } else {
        return { success: false, error: data.detail || 'Erreur de connexion' };
      }
    } catch (error) {
      console.error('Login error:', error);
      return { success: false, error: 'Erreur de connexion' };
    }
  };

  const register = async (userData) => {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/register/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
      });

      const data = await response.json();

      if (response.ok) {
        localStorage.setItem('akompta_access_token', data.access);
        localStorage.setItem('akompta_refresh_token', data.refresh);
        setToken(data.access);
        const decodedToken = jwtDecode(data.access);
        setUser({ id: decodedToken.user_id, username: decodedToken.username });
        return { success: true, user: { id: decodedToken.user_id, username: decodedToken.username } };
      } else {
        return { success: false, error: data.detail || data.username || data.email || 'Erreur d\'inscription' };
      }
    } catch (error) {
      console.error('Register error:', error);
      return { success: false, error: 'Erreur d\'inscription' };
    }
  };

  const logout = () => {
    localStorage.removeItem('akompta_access_token');
    localStorage.removeItem('akompta_refresh_token');
    setToken(null);
    setUser(null);
  };

  const updateUser = (updatedUser) => {
    setUser(updatedUser);
  };

  // Fonction utilitaire pour faire des requêtes authentifiées
  const authenticatedFetch = async (url, options = {}) => {
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }

    return fetch(url, {
      ...options,
      headers,
    });
  };

  const value = {
    user,
    token,
    loading,
    login,
    register,
    logout,
    updateUser,
    authenticatedFetch,
    API_BASE_URL,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};


