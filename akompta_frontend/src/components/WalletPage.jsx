import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Wallet, Plus, Minus, CreditCard, Smartphone, TrendingUp, TrendingDown, Eye, EyeOff } from 'lucide-react';

const WalletPage = () => {
  const { user, authenticatedFetch, API_BASE_URL } = useAuth();
  const [walletData, setWalletData] = useState({
    balance: 0,
    savings: 0,
    recentTransactions: []
  });
  const [loading, setLoading] = useState(true);
  const [showBalance, setShowBalance] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    fetchWalletData();
  }, []);

  const fetchWalletData = async () => {
    try {
      const response = await authenticatedFetch(`${API_BASE_URL}/savings/`);
      if (response.ok) {
        const data = await response.json();
        // Assuming data is an array of savings transactions
        const totalSavings = data.reduce((sum, transaction) => {
          return sum + (transaction.transaction_type === 'deposit' ? parseFloat(transaction.amount) : -parseFloat(transaction.amount));
        }, 0);

        setWalletData({
          balance: totalSavings, // For simplicity, balance is total savings for now
          savings: totalSavings,
          recentTransactions: data.sort((a, b) => new Date(b.transaction_date) - new Date(a.transaction_date))
        });
      } else {
        console.error('Failed to fetch wallet data:', response.statusText);
      }
    } catch (error) {
      console.error('Error fetching wallet data:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR', {
      day: '2-digit',
      month: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getProviderInfo = (provider) => {
    switch (provider) {
      case 'mtn_momo':
        return { name: 'MTN MoMo', color: 'yellow', icon: '📱' };
      case 'orange_money':
        return { name: 'Orange Money', color: 'orange', icon: '📱' };
      case 'moov_money':
        return { name: 'Moov Money', color: 'blue', icon: '📱' };
      default:
        return { name: 'Espèces', color: 'green', icon: '💵' };
    }
  };

  const tabs = [
    { id: 'overview', label: 'Aperçu', icon: Wallet },
    { id: 'savings', label: 'Épargne', icon: TrendingUp },
    { id: 'transactions', label: 'Historique', icon: CreditCard }
  ];

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center pb-20">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      {/* Header */}
      <div className="akompta-gradient px-6 py-8">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-white rounded-full flex items-center justify-center">
              <Wallet size={24} className="text-akompta-primary" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-800">Mon Portefeuille</h1>
              <p className="text-gray-600 text-sm">{user?.business_name || 'Mon Commerce'}</p>
            </div>
          </div>
          <button
            onClick={() => setShowBalance(!showBalance)}
            className="p-2 bg-white/20 rounded-full hover:bg-white/30 transition-colors"
          >
            {showBalance ? <EyeOff size={20} className="text-gray-700" /> : <Eye size={20} className="text-gray-700" />}
          </button>
        </div>

        {/* Balance Card */}
        <div className="bg-white rounded-2xl p-6 shadow-lg mb-6">
          <div className="text-center">
            <p className="text-gray-600 text-sm mb-2">Solde Total</p>
            <p className="text-3xl font-bold text-akompta-primary mb-4">
              {showBalance ? `${walletData.balance.toLocaleString()} FCFA` : '••••••'}
            </p>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="text-center">
                <p className="text-gray-500 text-xs">Épargne</p>
                <p className="text-lg font-semibold text-blue-600">
                  {showBalance ? `${walletData.savings.toLocaleString()}` : '••••••'}
                </p>
              </div>
              <div className="text-center">
                <p className="text-gray-500 text-xs">Disponible</p>
                <p className="text-lg font-semibold text-green-600">
                  {showBalance ? `${(walletData.balance - walletData.savings).toLocaleString()}` : '••••••'}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-2 gap-4">
          <button className="bg-white/10 backdrop-blur-sm rounded-xl p-4 flex items-center space-x-3 hover:bg-white/20 transition-colors">
            <div className="w-10 h-10 bg-green-500 rounded-full flex items-center justify-center">
              <Plus size={20} className="text-white" />
            </div>
            <div className="text-left">
              <p className="font-medium text-gray-800">Épargner</p>
              <p className="text-xs text-gray-600">Ajouter à l'épargne</p>
            </div>
          </button>
          
          <button className="bg-white/10 backdrop-blur-sm rounded-xl p-4 flex items-center space-x-3 hover:bg-white/20 transition-colors">
            <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center">
              <Minus size={20} className="text-white" />
            </div>
            <div className="text-left">
              <p className="font-medium text-gray-800">Retirer</p>
              <p className="text-xs text-gray-600">Retrait d'épargne</p>
            </div>
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="px-6 -mt-4">
        <div className="flex space-x-1 bg-white rounded-lg p-1 shadow-sm mb-6">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex-1 flex items-center justify-center space-x-2 py-3 px-4 rounded-md text-sm font-medium transition-all ${
                  activeTab === tab.id
                    ? 'bg-akompta-primary text-white shadow-sm'
                    : 'text-gray-600 hover:text-gray-800 hover:bg-gray-50'
                }`}
              >
                <Icon size={16} />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>

        {/* Tab Content */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Statistics - Placeholder for now, will need separate API endpoint */}
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-white rounded-lg p-4 shadow-sm">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                    <TrendingUp size={20} className="text-green-600" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Ce mois</p>
                    <p className="font-semibold text-gray-800">+0 FCFA</p>
                  </div>
                </div>
              </div>
              
              <div className="bg-white rounded-lg p-4 shadow-sm">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                    <Wallet size={20} className="text-blue-600" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Objectif</p>
                    <p className="font-semibold text-gray-800">0 FCFA</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Progress Bar - Placeholder for now */}
            <div className="bg-white rounded-lg p-4 shadow-sm">
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium text-gray-700">Objectif d'épargne</span>
                <span className="text-sm text-gray-500">0%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-akompta-primary h-2 rounded-full" style={{ width: '0%' }}></div>
              </div>
              <p className="text-xs text-gray-500 mt-2">0 / 0 FCFA</p>
            </div>
          </div>
        )}

        {activeTab === 'savings' && (
          <div className="space-y-4">
            <div className="bg-white rounded-lg p-6 shadow-sm text-center">
              <div className="w-16 h-16 bg-akompta-secondary rounded-full flex items-center justify-center mx-auto mb-4">
                <TrendingUp size={32} className="text-akompta-primary" />
              </div>
              <h3 className="text-xl font-bold text-gray-800 mb-2">Épargne Totale</h3>
              <p className="text-3xl font-bold text-akompta-primary mb-4">
                {walletData.savings.toLocaleString()} FCFA
              </p>
              
              <div className="grid grid-cols-2 gap-4 mt-6">
                <button className="btn-primary">
                  <Plus size={16} className="mr-2" />
                  Épargner
                </button>
                <button className="btn-secondary">
                  <Minus size={16} className="mr-2" />
                  Retirer
                </button>
              </div>
            </div>

            {/* Savings Tips */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h4 className="font-semibold text-blue-800 mb-2">💡 Conseil d'épargne</h4>
              <p className="text-sm text-blue-700">
                Essayez d'épargner 10% de vos bénéfices quotidiens pour atteindre vos objectifs plus rapidement.
              </p>
            </div>
          </div>
        )}

        {activeTab === 'transactions' && (
          <div className="space-y-4">
            {walletData.recentTransactions.map((transaction) => {
              const providerInfo = getProviderInfo(transaction.mobile_money_provider); // Changed to mobile_money_provider
              const isDeposit = transaction.transaction_type === 'deposit'; // Changed to transaction_type
              
              return (
                <div key={transaction.id} className="bg-white rounded-lg p-4 shadow-sm">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                        isDeposit ? 'bg-green-100' : 'bg-red-100'
                      }`}>
                        {isDeposit ? 
                          <Plus size={20} className="text-green-600" /> : 
                          <Minus size={20} className="text-red-600" />
                        }
                      </div>
                      <div>
                        <p className="font-medium text-gray-800">{transaction.notes || (isDeposit ? 'Dépôt' : 'Retrait')}</p>
                        <div className="flex items-center space-x-2">
                          <span className="text-sm text-gray-600">{formatDate(transaction.transaction_date)}</span>
                          <span className="text-xs">•</span>
                          <span className="text-sm text-gray-600">{providerInfo.name}</span>
                        </div>
                      </div>
                    </div>
                    
                    <div className="text-right">
                      <p className={`font-bold ${
                        isDeposit ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {isDeposit ? '+' : '-'}{parseFloat(transaction.amount).toLocaleString()} FCFA
                      </p>
                      <p className="text-xs text-gray-500 capitalize">{transaction.transaction_type}</p>
                    </div>
                  </div>
                </div>
              );
            })}

            {walletData.recentTransactions.length === 0 && (
              <div className="text-center py-12">
                <CreditCard size={48} className="mx-auto text-gray-400 mb-4" />
                <h3 className="text-lg font-medium text-gray-600 mb-2">Aucune transaction</h3>
                <p className="text-gray-500">Vos transactions d'épargne apparaîtront ici</p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Mobile Money Integration */}
      <div className="fixed bottom-20 left-1/2 transform -translate-x-1/2 bg-white rounded-full shadow-lg p-4 border">
        <div className="flex items-center space-x-3">
          <Smartphone size={20} className="text-akompta-primary" />
          <span className="text-sm text-gray-600">Mobile Money</span>
          <button className="bg-akompta-primary text-white px-4 py-2 rounded-full text-sm font-medium hover:bg-akompta-dark transition-colors">
            Connecter
          </button>
        </div>
      </div>
    </div>
  );
};

export default WalletPage;


