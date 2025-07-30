import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Eye, EyeOff } from 'lucide-react';

const LoginPage = () => {
  const [formData, setFormData] = useState({
    username: '', // Changed from email to username
    password: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const { login } = useAuth();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    setError(''); // Clear error when user types
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    // Pass username and password to login function
    const result = await login(formData.username, formData.password);
    
    if (!result.success) {
      setError(result.error);
    }
    
    setLoading(false);
  };

  return (
    <div className="min-h-screen akompta-gradient flex flex-col">
      {/* Header avec logo */}
      <div className="flex-1 flex flex-col justify-center px-6">
        <div className="text-center mb-8">
          <div className="w-20 h-20 mx-auto mb-4 bg-white rounded-full flex items-center justify-center shadow-lg">
            <div className="w-12 h-12 bg-gradient-to-r from-green-500 to-green-600 rounded-lg flex items-center justify-center">
              <div className="flex space-x-1">
                <div className="w-1 h-6 bg-white rounded-full"></div>
                <div className="w-1 h-4 bg-white rounded-full"></div>
                <div className="w-1 h-8 bg-white rounded-full"></div>
                <div className="w-1 h-3 bg-white rounded-full"></div>
                <div className="w-1 h-7 bg-white rounded-full"></div>
              </div>
            </div>
          </div>
          <h1 className="text-2xl font-bold text-gray-700 mb-2">Akompta AI</h1>
          <p className="text-gray-600">CosmoLAB Hub</p>
        </div>

        {/* Formulaire de connexion */}
        <div className="bg-white rounded-t-3xl px-6 py-8 shadow-xl">
          <h2 className="text-2xl font-bold text-center text-gray-800 mb-6">Login</h2>
          <p className="text-center text-gray-600 mb-8">Sign in to continue</p>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <input
                type="text" // Changed type to text
                name="username" // Changed name to username
                placeholder="Nom d'utilisateur" // Changed placeholder
                value={formData.username}
                onChange={handleChange}
                className="form-input"
                required
              />
            </div>

            <div className="relative">
              <input
                type={showPassword ? 'text' : 'password'}
                name="password"
                placeholder="Mot de passe"
                value={formData.password}
                onChange={handleChange}
                className="form-input pr-12"
                required
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500"
              >
                {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
              </button>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn-primary flex items-center justify-center"
            >
              {loading ? (
                <div className="loading-spinner"></div>
              ) : (
                'Log In'
              )}
            </button>
          </form>

          <div className="text-center mt-6">
            <Link 
              to="/forgot-password" 
              className="text-sm text-gray-600 hover:text-akompta-primary"
            >
              Mot de passe oublié ?
            </Link>
          </div>

          <div className="text-center mt-4">
            <span className="text-gray-600">Vous n'avez pas de compte ? </span>
            <Link 
              to="/register" 
              className="text-akompta-primary font-semibold hover:underline"
            >
              Inscrivez-vous
            </Link>
          </div>

          <div className="text-center mt-8 text-xs text-gray-500">
            <p>www.akompta.com</p>
            <p className="mt-2">CosmoLAB Hub</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;


