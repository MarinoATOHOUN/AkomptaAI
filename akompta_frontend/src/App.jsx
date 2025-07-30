import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import './App.css';

// Import des composants
import LoginPage from './components/LoginPage';
import RegisterPage from './components/RegisterPage';
import Dashboard from './components/Dashboard';
import ProductsPage from './components/ProductsPage';
import SalesPage from './components/SalesPage';
import ExpensesPage from './components/ExpensesPage';
import WalletPage from './components/WalletPage';
import VoiceRecording from './components/VoiceRecording';
import ProfilePage from './components/ProfilePage';
import BottomNavigation from './components/BottomNavigation';

// Context pour l'authentification
import { AuthProvider, useAuth } from './contexts/AuthContext';

// Composant pour les routes protégées
const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="mobile-container flex items-center justify-center">
        <div className="loading-spinner"></div>
      </div>
    );
  }
  
  return user ? children : <Navigate to="/login" />;
};

// Composant principal de l'app
const AppContent = () => {
  const { user } = useAuth();
  const [showVoiceModal, setShowVoiceModal] = useState(false);

  return (
    <div className="mobile-container">
      <Routes>
        {/* Routes publiques */}
        <Route path="/login" element={user ? <Navigate to="/dashboard" /> : <LoginPage />} />
        <Route path="/register" element={user ? <Navigate to="/dashboard" /> : <RegisterPage />} />
        
        {/* Routes protégées */}
        <Route path="/dashboard" element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        } />
        
        <Route path="/products" element={
          <ProtectedRoute>
            <ProductsPage />
          </ProtectedRoute>
        } />
        
        <Route path="/sales" element={
          <ProtectedRoute>
            <SalesPage />
          </ProtectedRoute>
        } />
        
        <Route path="/expenses" element={
          <ProtectedRoute>
            <ExpensesPage />
          </ProtectedRoute>
        } />
        
        <Route path="/wallet" element={
          <ProtectedRoute>
            <WalletPage />
          </ProtectedRoute>
        } />
        
        <Route path="/profile" element={
          <ProtectedRoute>
            <ProfilePage />
          </ProtectedRoute>
        } />
        
        {/* Redirection par défaut */}
        <Route path="/" element={<Navigate to={user ? "/dashboard" : "/login"} />} />
      </Routes>
      
      {/* Navigation bottom pour les pages protégées */}
      {user && <BottomNavigation onVoiceClick={() => setShowVoiceModal(true)} />}
      
      {/* Modal d'enregistrement vocal */}
      {showVoiceModal && (
        <VoiceRecording 
          isOpen={showVoiceModal} 
          onClose={() => setShowVoiceModal(false)} 
        />
      )}
    </div>
  );
};

// Composant App principal avec Router et Provider
function App() {
  return (
    <AuthProvider>
      <Router>
        <AppContent />
      </Router>
    </AuthProvider>
  );
}

export default App;


