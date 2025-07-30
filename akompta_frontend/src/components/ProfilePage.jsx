import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import {
  User,
  Settings,
  Bell,
  Shield,
  HelpCircle,
  LogOut,
  Edit,
  ChevronRight,
  Globe,
  Moon,
  Sun
} from 'lucide-react';

const ProfilePage = () => {
  const { user, logout } = useAuth();
  const [darkMode, setDarkMode] = useState(false);
  const [notifications, setNotifications] = useState(true);

  const handleLogout = () => {
    if (window.confirm('Êtes-vous sûr de vouloir vous déconnecter ?')) {
      logout();
    }
  };

  const menuItems = [
    {
      icon: User,
      title: 'Informations personnelles',
      subtitle: 'Modifier vos informations',
      action: () => console.log('Edit profile'),
      color: 'blue'
    },
    {
      icon: Bell,
      title: 'Notifications',
      subtitle: notifications ? 'Activées' : 'Désactivées',
      action: () => setNotifications(!notifications),
      color: 'green',
      toggle: true,
      value: notifications
    },
    {
      icon: Globe,
      title: 'Langue',
      subtitle: user?.preferred_language === 'fr' ? 'Français' : user?.preferred_language,
      action: () => console.log('Change language'),
      color: 'purple'
    },
    {
      icon: darkMode ? Sun : Moon,
      title: 'Mode sombre',
      subtitle: darkMode ? 'Activé' : 'Désactivé',
      action: () => setDarkMode(!darkMode),
      color: 'gray',
      toggle: true,
      value: darkMode
    },
    {
      icon: Shield,
      title: 'Sécurité',
      subtitle: 'Mot de passe et sécurité',
      action: () => console.log('Security settings'),
      color: 'red'
    },
    {
      icon: HelpCircle,
      title: 'Aide et support',
      subtitle: 'FAQ et contact',
      action: () => console.log('Help'),
      color: 'orange'
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      {/* Header */}
      <div className="akompta-gradient px-6 py-8">
        <div className="flex items-center space-x-4 mb-6">
          <div className="w-20 h-20 bg-white rounded-full flex items-center justify-center shadow-lg">
            <img 
              src="/api/placeholder/80/80" 
              alt="Profile" 
              className="w-16 h-16 rounded-full"
            />
          </div>
          <div className="flex-1">
            <h1 className="text-2xl font-bold text-gray-800">{user?.username || 'Utilisateur'}</h1>
            <p className="text-gray-600">{user?.email}</p>
            <p className="text-sm text-gray-500">{user?.business_name || 'Mon Commerce'}</p>
          </div>
          <button className="p-2 bg-white/20 rounded-full hover:bg-white/30 transition-colors">
            <Edit size={20} className="text-gray-700" />
          </button>
        </div>

        {/* Stats - These are placeholders for now, as the Django API doesn't provide them directly in the user object */}
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-white/10 backdrop-blur-sm rounded-lg p-3 text-center">
            <p className="text-2xl font-bold text-gray-800">--</p>
            <p className="text-xs text-gray-600">Produits</p>
          </div>
          <div className="bg-white/10 backdrop-blur-sm rounded-lg p-3 text-center">
            <p className="text-2xl font-bold text-gray-800">--</p>
            <p className="text-xs text-gray-600">Ventes</p>
          </div>
          <div className="bg-white/10 backdrop-blur-sm rounded-lg p-3 text-center">
            <p className="text-2xl font-bold text-gray-800">--</p>
            <p className="text-xs text-gray-600">Jours</p>
          </div>
        </div>
      </div>

      <div className="px-6 -mt-4">
        {/* Menu Items */}
        <div className="space-y-3">
          {menuItems.map((item, index) => {
            const Icon = item.icon;
            return (
              <div
                key={index}
                onClick={item.action}
                className="bg-white rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow cursor-pointer"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center bg-${item.color}-100`}>
                      <Icon size={20} className={`text-${item.color}-600`} />
                    </div>
                    <div>
                      <h3 className="font-medium text-gray-800">{item.title}</h3>
                      <p className="text-sm text-gray-600">{item.subtitle}</p>
                    </div>
                  </div>
                  
                  {item.toggle ? (
                    <div className={`w-12 h-6 rounded-full transition-colors ${
                      item.value ? 'bg-akompta-primary' : 'bg-gray-300'
                    }`}>
                      <div className={`w-5 h-5 bg-white rounded-full shadow-sm transition-transform mt-0.5 ${
                        item.value ? 'translate-x-6' : 'translate-x-0.5'
                      }`}></div>
                    </div>
                  ) : (
                    <ChevronRight size={20} className="text-gray-400" />
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* Account Section */}
        <div className="mt-8 space-y-3">
          <h2 className="text-lg font-semibold text-gray-800 px-2">Compte</h2>
          
          <div className="bg-white rounded-lg p-4 shadow-sm">
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-gray-700">Compte vérifié</span>
                <span className="px-3 py-1 bg-green-100 text-green-700 text-sm rounded-full">
                  ✓ Vérifié
                </span>
              </div>
              
              <div className="flex justify-between items-center">
                <span className="text-gray-700">Version de l'app</span>
                <span className="text-gray-500">1.0.0</span>
              </div>
              
              <div className="flex justify-between items-center">
                <span className="text-gray-700">Dernière synchronisation</span>
                <span className="text-gray-500">Il y a 2 min</span>
              </div>
            </div>
          </div>
        </div>

        {/* Logout Button */}
        <div className="mt-8">
          <button
            onClick={handleLogout}
            className="w-full bg-red-50 hover:bg-red-100 text-red-600 font-medium py-4 px-6 rounded-lg transition-colors flex items-center justify-center space-x-2"
          >
            <LogOut size={20} />
            <span>Se déconnecter</span>
          </button>
        </div>

        {/* Footer */}
        <div className="mt-8 text-center text-sm text-gray-500 space-y-2">
          <p>Akompta AI v1.0.0</p>
          <p>CosmoLAB Hub © 2025</p>
          <div className="flex justify-center space-x-4 mt-4">
            <a href="#" className="text-akompta-primary hover:underline">Conditions d'utilisation</a>
            <a href="#" className="text-akompta-primary hover:underline">Confidentialité</a>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;


