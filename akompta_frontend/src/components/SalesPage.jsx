import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Plus, Search, Calendar, TrendingUp, Package } from 'lucide-react';

const SalesPage = () => {
  const { authenticatedFetch, API_BASE_URL } = useAuth();
  const [sales, setSales] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedPeriod, setSelectedPeriod] = useState('all'); // Changed default to 'all' for now

  useEffect(() => {
    fetchSales();
  }, [selectedPeriod]); // Keep selectedPeriod for potential future filtering

  const fetchSales = async () => {
    try {
      // Adjust API endpoint based on selectedPeriod if backend supports it
      const response = await authenticatedFetch(`${API_BASE_URL}/sales/`);
      if (response.ok) {
        const data = await response.json();
        setSales(data);
      } else {
        console.error('Failed to fetch sales:', response.statusText);
      }
    } catch (error) {
      console.error('Error fetching sales:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredSales = sales.filter(sale =>
    sale.product_name && sale.product_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    sale.voice_command && sale.voice_command.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const totalSales = filteredSales.reduce((sum, sale) => sum + parseFloat(sale.total_amount), 0);
  const totalQuantity = filteredSales.reduce((sum, sale) => sum + sale.quantity, 0);

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR', {
      day: '2-digit',
      month: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getPaymentMethodLabel = (method) => {
    switch (method) {
      case 'cash': return 'Espèces';
      case 'mobile_money': return 'Mobile Money';
      case 'card': return 'Carte';
      default: return method;
    }
  };

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
      <div className="akompta-primary px-6 py-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center">
              <TrendingUp size={20} className="text-akompta-primary" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-white">Ventes</h1>
              <p className="text-white/80 text-sm">Historique des ventes</p>
            </div>
          </div>
          <button className="bg-white text-akompta-primary p-2 rounded-full shadow-lg hover:shadow-xl transition-shadow">
            <Plus size={24} />
          </button>
        </div>

        {/* Period Selector */}
        <div className="flex space-x-2 mb-4">
          {[
            { id: 'today', label: 'Aujourd\'hui' },
            { id: 'week', label: 'Cette semaine' },
            { id: 'month', label: 'Ce mois' },
            { id: 'all', label: 'Tout' }
          ].map((period) => (
            <button
              key={period.id}
              onClick={() => setSelectedPeriod(period.id)}
              className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${
                selectedPeriod === period.id
                  ? 'bg-white text-akompta-primary shadow-md'
                  : 'bg-white/20 text-white/80 hover:bg-white/30'
              }`}
            >
              {period.label}
            </button>
          ))}
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-white/10 rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-2">
              <TrendingUp size={20} className="text-white" />
              <span className="text-white/80 text-sm">Total Ventes</span>
            </div>
            <p className="text-2xl font-bold text-white">{totalSales.toLocaleString()}</p>
            <p className="text-white/60 text-xs">FCFA</p>
          </div>
          
          <div className="bg-white/10 rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-2">
              <Package size={20} className="text-white" />
              <span className="text-white/80 text-sm">Articles Vendus</span>
            </div>
            <p className="text-2xl font-bold text-white">{totalQuantity}</p>
            <p className="text-white/60 text-xs">unités</p>
          </div>
        </div>
      </div>

      <div className="px-6 -mt-2">
        {/* Search Bar */}
        <div className="relative mb-6">
          <Search size={20} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            placeholder="Rechercher une vente..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-3 bg-white rounded-lg shadow-sm border border-gray-200 focus:outline-none focus:ring-2 focus:ring-akompta-accent focus:border-transparent"
          />
        </div>

        {/* Sales List */}
        <div className="space-y-4">
          {filteredSales.map((sale) => (
            <div key={sale.id} className="bg-white rounded-lg p-4 shadow-sm border-l-4 border-green-500">
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-800 text-lg">{sale.product_name || 'Produit Inconnu'}</h3>
                  <p className="text-sm text-gray-600">{formatDate(sale.sale_date)}</p>
                </div>
                <div className="text-right">
                  <p className="text-xl font-bold text-green-600">
                    +{parseFloat(sale.total_amount).toLocaleString()} FCFA
                  </p>
                  <p className="text-sm text-gray-500">
                    {sale.quantity} × {parseFloat(sale.unit_price).toLocaleString()}
                  </p>
                </div>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                    sale.payment_method === 'cash' 
                      ? 'bg-green-100 text-green-700'
                      : sale.payment_method === 'mobile_money'
                      ? 'bg-blue-100 text-blue-700'
                      : 'bg-purple-100 text-purple-700'
                  }`}>
                    {getPaymentMethodLabel(sale.payment_method)}
                  </span>
                  
                  <div className="flex items-center space-x-1">
                    <Package size={14} className="text-gray-400" />
                    <span className="text-sm text-gray-600">{sale.quantity} unités</span>
                  </div>
                </div>

                <button className="text-akompta-primary text-sm font-medium hover:underline">
                  Détails
                </button>
              </div>

              {sale.voice_command && (
                <div className="mt-3 p-3 bg-gray-50 rounded-lg">
                  <p className="text-xs text-gray-500 mb-1">Commande vocale:</p>
                  <p className="text-sm text-gray-700 italic">"{sale.voice_command}"</p>
                </div>
              )}
            </div>
          ))}
        </div>

        {filteredSales.length === 0 && (
          <div className="text-center py-12">
            <TrendingUp size={48} className="mx-auto text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-600 mb-2">Aucune vente trouvée</h3>
            <p className="text-gray-500">
              {searchTerm ? 'Essayez un autre terme de recherche' : 'Commencez par enregistrer vos premières ventes'}
            </p>
          </div>
        )}
      </div>

      {/* Quick Add Sale Button */}
      <div className="fixed bottom-20 right-6">
        <button className="bg-green-500 text-white p-4 rounded-full shadow-lg hover:shadow-xl hover:bg-green-600 transition-all">
          <Plus size={24} />
        </button>
      </div>
    </div>
  );
};

export default SalesPage;


