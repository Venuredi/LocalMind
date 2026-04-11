import { useState, useEffect, createContext, useContext } from 'react';
import { apiClient } from '../services/apiClient';

interface User {
  id: string;
  name: string;
  email: string;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

/**
 * Authentication hook
 * Manages: JWT tokens, user state, auth API calls
 * APIs: POST /auth/login, POST /auth/register, POST /auth/refresh
 */
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    // Check for existing token on mount
    const token = localStorage.getItem('accessToken');
    if (token) {
      validateToken(token);
    }
  }, []);

  const validateToken = async (token: string) => {
    try {
      apiClient.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      const response = await apiClient.get('/auth/me');
      setUser(response.data);
    } catch (error) {
      // Token invalid, try refresh
      await refreshToken();
    }
  };

  const refreshToken = async () => {
    try {
      const refreshToken = localStorage.getItem('refreshToken');
      if (!refreshToken) throw new Error('No refresh token');

      const response = await apiClient.post('/auth/refresh', { refreshToken });
      const { accessToken, refreshToken: newRefreshToken } = response.data;

      localStorage.setItem('accessToken', accessToken);
      localStorage.setItem('refreshToken', newRefreshToken);
      apiClient.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`;

      // Validate new token
      await validateToken(accessToken);
    } catch (error) {
      // Refresh failed, logout
      logout();
    }
  };

  /**
   * Login user
   * API: POST /auth/login
   * Stores: accessToken, refreshToken in localStorage
   */
  const login = async (email: string, password: string) => {
    setIsLoading(true);
    try {
      const response = await apiClient.post('/auth/login', { email, password });
      const { accessToken, refreshToken, user } = response.data;

      localStorage.setItem('accessToken', accessToken);
      localStorage.setItem('refreshToken', refreshToken);
      apiClient.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`;

      setUser(user);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Register new user
   * API: POST /auth/register
   * Auto-login after successful registration
   */
  const register = async (name: string, email: string, password: string) => {
    setIsLoading(true);
    try {
      const response = await apiClient.post('/auth/register', { name, email, password });
      const { accessToken, refreshToken, user } = response.data;

      localStorage.setItem('accessToken', accessToken);
      localStorage.setItem('refreshToken', refreshToken);
      apiClient.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`;

      setUser(user);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Logout user
   * Clears tokens and user state
   */
  const logout = () => {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    delete apiClient.defaults.headers.common['Authorization'];
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, isLoading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
};
