import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts';
import { TrendingUp, TrendingDown, DollarSign, Package, ShoppingCart, AlertTriangle } from 'lucide-react';

const Dashboard = () => {
  const { user, authenticatedFetch, API_BASE_URL } = useAuth();
  const [dashboardData, setDashboardData] = useState({
    total_sales: 0,
    total_expenses: 0,
    net_profit: 0,
    total_savings: 0,
    // recentSales: [], // These will be fetched from specific endpoints later
    // salesChart: [],
    // lowStockProducts: []
  });
  const [loading, setLoading] = useState(true);
  const [selectedPeriod, setSelectedPeriod] = useState('week'); // This might be removed if not supported by Django API directly

  useEffect(() => {
    fetchDashboardSummary();
    // You might need separate fetches for recent sales, sales chart, and low stock products
    // if the Django API doesn't return them all in one summary endpoint.
  }, []); // Removed selectedPeriod from dependency array for now

  const fetchDashboardSummary = async () => {
    try {
      const response = await authenticatedFetch(`${API_BASE_URL}/dashboard/summary/`);
      if (response.ok) {
        const data = await response.json();
        setDashboardData(data);
      } else {
        console.error('Failed to fetch dashboard summary:', response.statusText);
      }
    } catch (error) {
      console.error('Error fetching dashboard summary:', error);
    } finally {
      setLoading(false);
    }
  };

  // Removed mockData as we are now fetching from API

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
              <img 
                src="/api/placeholder/48/48" 
                alt="Profile" 
                className="w-10 h-10 rounded-full"
              />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-800">
                Bonjour, {user?.username || 'Utilisateur'}
              </h1>
              <p className="text-gray-600 text-sm">{user?.business_name || 'Mon Commerce'}</p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-sm text-gray-600">Solde Total</p>
            <p className="text-2xl font-bold text-akompta-primary">
              {dashboardData.total_savings.toLocaleString()} FCFA
            </p>
          </div>
        </div>

        {/* Period Selector - Keep for now, but might need to adjust logic */}
        <div className="flex space-x-2 mb-4">
          {['day', 'week', 'month', 'year'].map((period) => (
            <button
              key={period}
              onClick={() => setSelectedPeriod(period)}
              className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${
                selectedPeriod === period
                  ? 'bg-white text-akompta-primary shadow-md'
                  : 'bg-white/20 text-gray-700 hover:bg-white/30'
              }`}
            >
              {period === 'day' ? 'Jour' : 
               period === 'week' ? 'Semaine' :
               period === 'month' ? 'Mois' : 'Année'}
            </button>
          ))}
        </div>
      </div>

      <div className="px-6 -mt-4">
        {/* Metrics Cards */}
        <div className="grid grid-cols-2 gap-4 mb-6">
          <div className="metric-card">
            <div className="flex items-center justify-between mb-2">
              <ShoppingCart size={24} className="text-akompta-primary" />
              <TrendingUp size={16} className="text-green-500" />
            </div>
            <div className="metric-value">{dashboardData.total_sales.toLocaleString()}</div>
            <div className="metric-label">Ventes</div>
          </div>

          <div className="metric-card">
            <div className="flex items-center justify-between mb-2">
              <DollarSign size={24} className="text-akompta-primary" />
              <TrendingDown size={16} className="text-red-500" />
            </div>
            <div className="metric-value">{dashboardData.total_expenses.toLocaleString()}</div>
            <div className="metric-label">Dépenses</div>
          </div>
        </div>

        {/* Sales Chart - Placeholder for now, will need separate API endpoint */}
        <div className="chart-container mb-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-800">Dashboard</h3>
            <div className="flex items-center space-x-4 text-sm">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-akompta-primary rounded-full"></div>
                <span>Ce mois-ci</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-gray-400 rounded-full"></div>
                <span>Mois dernier</span>
              </div>
            </div>
          </div>
          
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={[]}> {/* Data will come from API */}
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="period" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="current" fill="var(--akompta-primary)" />
              <Bar dataKey="previous" fill="#e0e0e0" />
            </BarChart>
          </ResponsiveContainer>

          <div className="mt-4 text-center">
            <span className="text-2xl font-bold text-akompta-primary">{dashboardData.net_profit.toLocaleString()}</span>
            <span className="text-gray-600 ml-2">FCFA (Bénéfice Net)</span>
          </div>
        </div>

        {/* Recent Sales - Placeholder for now, will need separate API endpoint */}
        <div className="bg-white rounded-lg p-4 mb-6 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Ventes Récentes</h3>
          <div className="space-y-3">
            {/* {dashboardData.recentSales.map((sale) => ( */}
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-akompta-secondary rounded-lg flex items-center justify-center">
                    <Package size={20} className="text-akompta-primary" />
                  </div>
                  <div>
                    <p className="font-medium text-gray-800">Aucune vente récente</p>
                    <p className="text-sm text-gray-600"></p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="font-semibold text-green-600"></p>
                  <p className="text-xs text-gray-500"></p>
                </div>
              </div>
            {/* ))}*/}
          </div>
        </div>

        {/* Low Stock Alert - Placeholder for now, will need separate API endpoint */}
        {/* {dashboardData.lowStockProducts.length > 0 && ( */}
          <div className="bg-orange-50 border border-orange-200 rounded-lg p-4 mb-6">
            <div className="flex items-center space-x-2 mb-3">
              <AlertTriangle size={20} className="text-orange-600" />
              <h3 className="font-semibold text-orange-800">Stock Faible</h3>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                  <span className="text-orange-700">Aucun produit en stock faible</span>
                  <span className="text-sm text-orange-600">
                  </span>
                </div>
            </div>
          </div>
        {/* )}*/}

        {/* Quick Actions */}
        <div className="grid grid-cols-2 gap-4 mb-6">
          <button className="bg-white p-4 rounded-lg shadow-sm border-l-4 border-blue-500 text-left hover:shadow-md transition-shadow">
            <div className="text-blue-600 font-semibold">Ajouter Produit</div>
            <div className="text-sm text-gray-600">Nouveau produit au stock</div>
          </button>
          
          <button className="bg-white p-4 rounded-lg shadow-sm border-l-4 border-green-500 text-left hover:shadow-md transition-shadow">
            <div className="text-green-600 font-semibold">Nouvelle Vente</div>
            <div className="text-sm text-gray-600">Enregistrer une vente</div>
          </button>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;


