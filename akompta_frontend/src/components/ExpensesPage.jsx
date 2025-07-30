import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Plus, Search, TrendingDown, Receipt, Calendar } from 'lucide-react';

const ExpensesPage = () => {
  const { authenticatedFetch, API_BASE_URL } = useAuth();
  const [expenses, setExpenses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');

  const categories = [
    { id: 'all', label: 'Toutes', color: 'gray' },
    { id: 'transport', label: 'Transport', color: 'blue' },
    { id: 'achat_stock', label: 'Achat Stock', color: 'green' },
    { id: 'equipement', label: 'Équipement', color: 'purple' },
    { id: 'communication', label: 'Communication', color: 'orange' },
    { id: 'autres', label: 'Autres', color: 'gray' }
  ];

  useEffect(() => {
    fetchExpenses();
  }, []);

  const fetchExpenses = async () => {
    try {
      const response = await authenticatedFetch(`${API_BASE_URL}/expenses/`);
      if (response.ok) {
        const data = await response.json();
        setExpenses(data);
      } else {
        console.error('Failed to fetch expenses:', response.statusText);
      }
    } catch (error) {
      console.error('Error fetching expenses:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredExpenses = expenses.filter(expense => {
    const matchesSearch = expense.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || expense.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const totalExpenses = filteredExpenses.reduce((sum, expense) => sum + parseFloat(expense.amount), 0);

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR', {
      day: '2-digit',
      month: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getCategoryInfo = (categoryId) => {
    return categories.find(cat => cat.id === categoryId) || categories[0];
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
      <div className="bg-red-600 px-6 py-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center">
              <TrendingDown size={20} className="text-red-600" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-white">Dépenses</h1>
              <p className="text-white/80 text-sm">Suivi des dépenses</p>
            </div>
          </div>
          <button className="bg-white text-red-600 p-2 rounded-full shadow-lg hover:shadow-xl transition-shadow">
            <Plus size={24} />
          </button>
        </div>

        {/* Total Expenses */}
        <div className="bg-white/10 rounded-lg p-4 mb-4">
          <div className="flex items-center space-x-2 mb-2">
            <TrendingDown size={20} className="text-white" />
            <span className="text-white/80 text-sm">Total Dépenses</span>
          </div>
          <p className="text-2xl font-bold text-white">{totalExpenses.toLocaleString()}</p>
          <p className="text-white/60 text-xs">FCFA</p>
        </div>

        {/* Category Filter */}
        <div className="flex space-x-2 overflow-x-auto pb-2">
          {categories.map((category) => (
            <button
              key={category.id}
              onClick={() => setSelectedCategory(category.id)}
              className={`px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition-all ${
                selectedCategory === category.id
                  ? 'bg-white text-red-600 shadow-md'
                  : 'bg-white/20 text-white/80 hover:bg-white/30'
              }`}
            >
              {category.label}
            </button>
          ))}
        </div>
      </div>

      <div className="px-6 -mt-2">
        {/* Search Bar */}
        <div className="relative mb-6">
          <Search size={20} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            placeholder="Rechercher une dépense..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-3 bg-white rounded-lg shadow-sm border border-gray-200 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent"
          />
        </div>

        {/* Expenses List */}
        <div className="space-y-4">
          {filteredExpenses.map((expense) => {
            const categoryInfo = getCategoryInfo(expense.category);
            return (
              <div key={expense.id} className="bg-white rounded-lg p-4 shadow-sm border-l-4 border-red-500">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-800">{expense.description}</h3>
                    <p className="text-sm text-gray-600">{formatDate(expense.expense_date)}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-xl font-bold text-red-600">
                      -{parseFloat(expense.amount).toLocaleString()} FCFA
                    </p>
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <span className={`px-3 py-1 rounded-full text-xs font-medium bg-${categoryInfo.color}-100 text-${categoryInfo.color}-700`}>
                      {categoryInfo.label}
                    </span>
                    
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                      expense.payment_method === 'cash' 
                        ? 'bg-green-100 text-green-700'
                        : expense.payment_method === 'mobile_money'
                        ? 'bg-blue-100 text-blue-700'
                        : 'bg-purple-100 text-purple-700'
                    }`}>
                      {getPaymentMethodLabel(expense.payment_method)}
                    </span>
                  </div>

                  <button className="text-red-600 text-sm font-medium hover:underline">
                    Détails
                  </button>
                </div>

                {expense.voice_command && (
                  <div className="mt-3 p-3 bg-gray-50 rounded-lg">
                    <p className="text-xs text-gray-500 mb-1">Commande vocale:</p>
                    <p className="text-sm text-gray-700 italic">"{expense.voice_command}"</p>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {filteredExpenses.length === 0 && (
          <div className="text-center py-12">
            <Receipt size={48} className="mx-auto text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-600 mb-2">Aucune dépense trouvée</h3>
            <p className="text-gray-500">
              {searchTerm || selectedCategory !== 'all' 
                ? 'Essayez de modifier vos filtres' 
                : 'Commencez par enregistrer vos premières dépenses'}
            </p>
          </div>
        )}

        {/* Monthly Summary */}
        {filteredExpenses.length > 0 && (
          <div className="mt-8 bg-white rounded-lg p-4 shadow-sm">
            <h3 className="font-semibold text-gray-800 mb-4">Résumé par catégorie</h3>
            <div className="space-y-3">
              {categories.slice(1).map((category) => {
                const categoryExpenses = expenses.filter(exp => exp.category === category.id);
                const categoryTotal = categoryExpenses.reduce((sum, exp) => sum + parseFloat(exp.amount), 0);
                
                if (categoryTotal === 0) return null;
                
                return (
                  <div key={category.id} className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className={`w-3 h-3 rounded-full bg-${category.color}-500`}></div>
                      <span className="text-sm text-gray-700">{category.label}</span>
                    </div>
                    <span className="font-medium text-gray-800">
                      {categoryTotal.toLocaleString()} FCFA
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>

      {/* Quick Add Expense Button */}
      <div className="fixed bottom-20 right-6">
        <button className="bg-red-500 text-white p-4 rounded-full shadow-lg hover:shadow-xl hover:bg-red-600 transition-all">
          <Plus size={24} />
        </button>
      </div>
    </div>
  );
};

export default ExpensesPage;


