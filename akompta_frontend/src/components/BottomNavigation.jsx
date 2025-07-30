import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { 
  Wallet, 
  BarChart3, 
  User, 
  Bell, 
  Settings,
  Mic
} from 'lucide-react';

const BottomNavigation = ({ onVoiceClick }) => {
  const location = useLocation();
  const navigate = useNavigate();

  const navItems = [
    {
      icon: Wallet,
      path: '/wallet',
      label: 'Wallet'
    },
    {
      icon: BarChart3,
      path: '/dashboard',
      label: 'Dashboard'
    },
    {
      icon: Mic,
      path: '/voice',
      label: 'Voice',
      isVoice: true
    },
    {
      icon: Bell,
      path: '/notifications',
      label: 'Notifications'
    },
    {
      icon: Settings,
      path: '/profile',
      label: 'Settings'
    }
  ];

  const handleNavClick = (item) => {
    if (item.isVoice) {
      onVoiceClick();
    } else {
      navigate(item.path);
    }
  };

  return (
    <div className="bottom-nav">
      {navItems.map((item, index) => {
        const Icon = item.icon;
        const isActive = location.pathname === item.path;
        
        return (
          <div
            key={index}
            className={`nav-item ${isActive ? 'active' : ''} ${item.isVoice ? 'voice-nav-item' : ''}`}
            onClick={() => handleNavClick(item)}
          >
            {item.isVoice ? (
              <div className="voice-button-small w-12 h-12 bg-akompta-primary rounded-full flex items-center justify-center">
                <Icon size={20} color="white" />
              </div>
            ) : (
              <Icon 
                size={20} 
                color={isActive ? 'var(--akompta-primary)' : '#666'} 
              />
            )}
            {!item.isVoice && (
              <span className="text-xs mt-1">{item.label}</span>
            )}
          </div>
        );
      })}
    </div>
  );
};

export default BottomNavigation;

