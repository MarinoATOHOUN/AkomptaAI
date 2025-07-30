import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Plus, Search, Edit, Trash2, Package, AlertCircle } from 'lucide-react';

const ProductsPage = () => {
  const { authenticatedFetch, API_BASE_URL } = useAuth();
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [showAddModal, setShowAddModal] = useState(false);
  const [newProduct, setNewProduct] = useState({
    name: '',
    description: '',
    price: '',
    stock_quantity: '',
    min_stock_threshold: '',
    image_url: '',
    category: ''
  });
  const [editingProduct, setEditingProduct] = useState(null);
  const [selectedTab, setSelectedTab] = useState('products');

  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    try {
      const response = await authenticatedFetch(`${API_BASE_URL}/products/`);
      if (response.ok) {
        const data = await response.json();
        setProducts(data.map(p => ({ ...p, is_low_stock: p.stock_quantity <= p.min_stock_threshold })));
      } else {
        console.error('Failed to fetch products:', response.statusText);
      }
    } catch (error) {
      console.error('Error fetching products:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddProduct = async (e) => {
    e.preventDefault();
    try {
      const response = await authenticatedFetch(`${API_BASE_URL}/products/`, {
        method: 'POST',
        body: JSON.stringify(newProduct),
      });
      if (response.ok) {
        setShowAddModal(false);
        setNewProduct({
          name: '',
          description: '',
          price: '',
          stock_quantity: '',
          min_stock_threshold: '',
          image_url: '',
          category: ''
        });
        fetchProducts(); // Refresh product list
      } else {
        console.error('Failed to add product:', response.statusText);
      }
    } catch (error) {
      console.error('Error adding product:', error);
    }
  };

  const handleUpdateProduct = async (e) => {
    e.preventDefault();
    try {
      const response = await authenticatedFetch(`${API_BASE_URL}/products/${editingProduct.id}/`, {
        method: 'PUT',
        body: JSON.stringify(editingProduct),
      });
      if (response.ok) {
        setEditingProduct(null);
        fetchProducts(); // Refresh product list
      } else {
        console.error('Failed to update product:', response.statusText);
      }
    } catch (error) {
      console.error('Error updating product:', error);
    }
  };

  const handleDeleteProduct = async (productId) => {
    if (window.confirm('Êtes-vous sûr de vouloir supprimer ce produit ?')) {
      try {
        const response = await authenticatedFetch(`${API_BASE_URL}/products/${productId}/`, {
          method: 'DELETE',
        });
        if (response.ok) {
          fetchProducts(); // Refresh product list
        } else {
          console.error('Failed to delete product:', response.statusText);
        }
      } catch (error) {
        console.error('Error deleting product:', error);
      }
    }
  };

  const filteredProducts = products.filter(product =>
    product.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    product.category.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const tabs = [
    { id: 'products', label: 'Produits', count: products.length },
    { id: 'stock', label: 'Stock', count: products.filter(p => p.is_low_stock).length },
    // Add counts for sales and expenses if you implement separate API endpoints for them
    { id: 'sales', label: 'Ventes', count: 0 }, 
    { id: 'expenses', label: 'Dépenses', count: 0 }
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
      <div className="akompta-primary px-6 py-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center">
              <img 
                src="/api/placeholder/40/40" 
                alt="Profile" 
                className="w-8 h-8 rounded-full"
              />
            </div>
            <div>
              <h1 className="text-xl font-bold text-white">Gestion</h1>
              <p className="text-white/80 text-sm">Page de gestion</p>
            </div>
          </div>
          <button
            onClick={() => setShowAddModal(true)}
            className="bg-white text-akompta-primary p-2 rounded-full shadow-lg hover:shadow-xl transition-shadow"
          >
            <Plus size={24} />
          </button>
        </div>

        {/* Tabs */}
        <div className="flex space-x-1 bg-white/10 rounded-lg p-1">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setSelectedTab(tab.id)}
              className={`flex-1 py-2 px-3 rounded-md text-sm font-medium transition-all ${
                selectedTab === tab.id
                  ? 'bg-white text-akompta-primary shadow-sm'
                  : 'text-white/80 hover:text-white hover:bg-white/10'
              }`}
            >
              {tab.label}
              {tab.count > 0 && (
                <span className={`ml-1 px-2 py-0.5 rounded-full text-xs ${
                  selectedTab === tab.id ? 'bg-akompta-secondary' : 'bg-white/20'
                }`}>
                  {tab.count}
                </span>
              )}
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
            placeholder="Rechercher un produit..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-3 bg-white rounded-lg shadow-sm border border-gray-200 focus:outline-none focus:ring-2 focus:ring-akompta-accent focus:border-transparent"
          />
        </div>

        {/* Products List */}
        <div className="space-y-4">
          {filteredProducts.map((product) => (
            <div key={product.id} className="product-card">
              <div className="flex items-center space-x-4">
                {/* Product Image */}
                <div className="w-16 h-16 bg-gray-100 rounded-lg overflow-hidden flex-shrink-0">
                  <img
                    src={product.image_url || '/api/placeholder/64/64'} // Fallback for image
                    alt={product.name}
                    className="w-full h-full object-cover"
                  />
                </div>

                {/* Product Info */}
                <div className="flex-1">
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="font-semibold text-gray-800">{product.name}</h3>
                      <p className="text-sm text-gray-600">{product.category}</p>
                      <div className="flex items-center space-x-4 mt-1">
                        <span className="text-lg font-bold text-akompta-primary">
                          {product.price.toLocaleString()} FCFA
                        </span>
                        <div className="flex items-center space-x-1">
                          <Package size={14} className="text-gray-400" />
                          <span className="text-sm text-gray-600">
                            {product.stock_quantity} unités
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="flex items-center space-x-2">
                      <button 
                        onClick={() => setEditingProduct(product)}
                        className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                      >
                        <Edit size={16} />
                      </button>
                      <button 
                        onClick={() => handleDeleteProduct(product.id)}
                        className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </div>

                  {/* Stock Status */}
                  <div className="flex items-center justify-between mt-3">
                    <div className="flex items-center space-x-2">
                      {product.is_low_stock && (
                        <div className="flex items-center space-x-1 text-orange-600">
                          <AlertCircle size={14} />
                          <span className="text-xs font-medium">Stock faible</span>
                        </div>
                      )}
                    </div>
                    
                    <div className="flex space-x-2">
                      <button className="px-3 py-1 bg-green-100 text-green-700 text-xs font-medium rounded-full hover:bg-green-200 transition-colors">
                        Vendre
                      </button>
                      <button className="px-3 py-1 bg-blue-100 text-blue-700 text-xs font-medium rounded-full hover:bg-blue-200 transition-colors">
                        Stock +
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {filteredProducts.length === 0 && (
          <div className="text-center py-12">
            <Package size={48} className="mx-auto text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-600 mb-2">Aucun produit trouvé</h3>
            <p className="text-gray-500">
              {searchTerm ? 'Essayez un autre terme de recherche' : 'Commencez par ajouter vos premiers produits'}
            </p>
          </div>
        )}
      </div>

      {/* Add Product Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg p-6 shadow-xl w-full max-w-md">
            <h2 className="text-xl font-bold mb-4">Ajouter un nouveau produit</h2>
            <form onSubmit={handleAddProduct} className="space-y-4">
              <input
                type="text"
                placeholder="Nom du produit"
                value={newProduct.name}
                onChange={(e) => setNewProduct({ ...newProduct, name: e.target.value })}
                className="form-input"
                required
              />
              <textarea
                placeholder="Description (optionnel)"
                value={newProduct.description}
                onChange={(e) => setNewProduct({ ...newProduct, description: e.target.value })}
                className="form-input"
              ></textarea>
              <input
                type="number"
                placeholder="Prix"
                value={newProduct.price}
                onChange={(e) => setNewProduct({ ...newProduct, price: e.target.value })}
                className="form-input"
                required
              />
              <input
                type="number"
                placeholder="Quantité en stock"
                value={newProduct.stock_quantity}
                onChange={(e) => setNewProduct({ ...newProduct, stock_quantity: e.target.value })}
                className="form-input"
                required
              />
              <input
                type="number"
                placeholder="Seuil de stock minimum"
                value={newProduct.min_stock_threshold}
                onChange={(e) => setNewProduct({ ...newProduct, min_stock_threshold: e.target.value })}
                className="form-input"
                required
              />
              <input
                type="text"
                placeholder="URL de l'image (optionnel)"
                value={newProduct.image_url}
                onChange={(e) => setNewProduct({ ...newProduct, image_url: e.target.value })}
                className="form-input"
              />
              <input
                type="text"
                placeholder="Catégorie (optionnel)"
                value={newProduct.category}
                onChange={(e) => setNewProduct({ ...newProduct, category: e.target.value })}
                className="form-input"
              />
              <div className="flex justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="btn-secondary"
                >
                  Annuler
                </button>
                <button type="submit" className="btn-primary">
                  Ajouter
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Edit Product Modal */}
      {editingProduct && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg p-6 shadow-xl w-full max-w-md">
            <h2 className="text-xl font-bold mb-4">Modifier le produit</h2>
            <form onSubmit={handleUpdateProduct} className="space-y-4">
              <input
                type="text"
                placeholder="Nom du produit"
                value={editingProduct.name}
                onChange={(e) => setEditingProduct({ ...editingProduct, name: e.target.value })}
                className="form-input"
                required
              />
              <textarea
                placeholder="Description (optionnel)"
                value={editingProduct.description || ''}
                onChange={(e) => setEditingProduct({ ...editingProduct, description: e.target.value })}
                className="form-input"
              ></textarea>
              <input
                type="number"
                placeholder="Prix"
                value={editingProduct.price}
                onChange={(e) => setEditingProduct({ ...editingProduct, price: e.target.value })}
                className="form-input"
                required
              />
              <input
                type="number"
                placeholder="Quantité en stock"
                value={editingProduct.stock_quantity}
                onChange={(e) => setEditingProduct({ ...editingProduct, stock_quantity: e.target.value })}
                className="form-input"
                required
              />
              <input
                type="number"
                placeholder="Seuil de stock minimum"
                value={editingProduct.min_stock_threshold}
                onChange={(e) => setEditingProduct({ ...editingProduct, min_stock_threshold: e.target.value })}
                className="form-input"
                required
              />
              <input
                type="text"
                placeholder="URL de l'image (optionnel)"
                value={editingProduct.image_url || ''}
                onChange={(e) => setEditingProduct({ ...editingProduct, image_url: e.target.value })}
                className="form-input"
              />
              <input
                type="text"
                placeholder="Catégorie (optionnel)"
                value={editingProduct.category || ''}
                onChange={(e) => setEditingProduct({ ...editingProduct, category: e.target.value })}
                className="form-input"
              />
              <div className="flex justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setEditingProduct(null)}
                  className="btn-secondary"
                >
                  Annuler
                </button>
                <button type="submit" className="btn-primary">
                  Mettre à jour
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Voice Command Interface */}
      <div className="fixed bottom-20 left-1/2 transform -translate-x-1/2 bg-white rounded-full shadow-lg p-4 border">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-akompta-primary rounded-full flex items-center justify-center">
            <Package size={16} className="text-white" />
          </div>
          <span className="text-sm text-gray-600">Commande vocale</span>
          <button className="bg-akompta-primary text-white px-4 py-2 rounded-full text-sm font-medium hover:bg-akompta-dark transition-colors">
            Activer
          </button>
        </div>
      </div>
    </div>
  );
};

export default ProductsPage;


