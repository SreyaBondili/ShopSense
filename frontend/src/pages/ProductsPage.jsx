
import React, { useState, useEffect } from 'react';
import { api } from '../api';
import { Package, Plus, Search, Edit2, Trash2 } from 'lucide-react';

export default function ProductsPage({ user }) {
  const [products, setProducts] = useState([]);
  const [vendors, setVendors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [search, setSearch] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('All');

  // Form states
  const [showAddForm, setShowAddForm] = useState(false);
  const [newProduct, setNewProduct] = useState({
    product_name: '',
    category: 'Electronics',
    price: 49.99,
    stock: 20,
    vendor_id: '',
  });

  // Edit states
  const [selectedProdId, setSelectedProdId] = useState('');
  const [editPrice, setEditPrice] = useState(49.99);
  const [editStock, setEditStock] = useState(20);

  const isAdmin = user.role === 'ADMIN';

  useEffect(() => {
    loadProducts();
    if (isAdmin) {
      loadVendorsList();
    }
  }, [categoryFilter]);

  const loadVendorsList = async () => {
    try {
      const vList = await api.getVendors();
      setVendors(vList || []);
      if (vList && vList.length > 0 && !newProduct.vendor_id) {
        setNewProduct(prev => ({ ...prev, vendor_id: vList[0].vendor_id }));
      }
    } catch {
      // ignore
    }
  };

  const loadProducts = async () => {
    setLoading(true);
    try {
      const params = {
        search: search.trim(),
        category: categoryFilter,
      };
      if (!isAdmin) {
        params.vendor_id = user.vendor_id;
      }
      const data = await api.getProducts(params);
      setProducts(data || []);
      if (data && data.length > 0 && !selectedProdId) {
        setSelectedProdId(data[0].product_id);
        setEditPrice(data[0].price);
        setEditStock(data[0].stock);
      }
    } catch (err) {
      setError(err.message || 'Failed to load products.');
    } finally {
      setLoading(false);
    }
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    loadProducts();
  };

  const handleCreateProduct = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    try {
      const payload = {
        product_name: newProduct.product_name.trim(),
        category: newProduct.category,
        price: Number(newProduct.price),
        stock: Number(newProduct.stock),
      };
      if (isAdmin && newProduct.vendor_id) {
        payload.vendor_id = Number(newProduct.vendor_id);
      }

      await api.createProduct(payload);
      setSuccess(`Product '${newProduct.product_name}' successfully added and inventory initialized!`);
      setShowAddForm(false);
      setNewProduct(prev => ({ ...prev, product_name: '', price: 49.99, stock: 20 }));
      loadProducts();
    } catch (err) {
      const msg = err.message || '';
      if (msg.includes('409') || msg.includes('already exists')) {
        setError("⚠️ A product with that name already exists in this vendor's catalog. Use a different name or update the existing product.");
      } else {
        setError(`Product creation failed: ${msg}`);
      }
    }
  };

  const handleUpdateProduct = async () => {
    if (!selectedProdId) return;
    setError('');
    setSuccess('');
    try {
      await api.updateProduct(selectedProdId, {
        price: Number(editPrice),
        stock: Number(editStock),
      });
      setSuccess('Product and warehouse stock updated successfully!');
      loadProducts();
    } catch (err) {
      setError(err.message || 'Failed to update product.');
    }
  };

  const handleDeleteProduct = async () => {
    if (!selectedProdId) return;
    if (!window.confirm('Are you sure? Products with sales history cannot be deleted.')) return;
    setError('');
    setSuccess('');
    try {
      await api.deleteProduct(selectedProdId);
      setSuccess('Product deleted successfully.');
      loadProducts();
    } catch (err) {
      setError(err.message || 'Deletion failed. Product has transaction history and is protected.');
    }
  };

  return (
    <div>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 className="page-title">
            <span>📦</span> Product Catalog Management
          </h1>
          <p className="page-subtitle">Manage items, unit prices, warehouse stocks, and vendor product assignments</p>
        </div>
        <button
          className="btn btn-primary"
          onClick={() => setShowAddForm(!showAddForm)}
        >
          <Plus size={16} />
          {showAddForm ? 'Close Form' : 'Add New Product'}
        </button>
      </div>

      {error && <div className="alert alert-error"><span>⚠️</span><span>{error}</span></div>}
      {success && <div className="alert alert-success"><span>✅</span><span>{success}</span></div>}

      {/* Add Product Form */}
      {showAddForm && (
        <div className="card" style={{ border: '1px solid #6366f1' }}>
          <div className="card-title">
            <Package size={18} color="#6366f1" />
            <span>Add New Product to Catalog</span>
          </div>
          <form onSubmit={handleCreateProduct}>
            <div className="form-grid-3">
              <div>
                <label className="form-label">Product Name *</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="e.g. Wireless Noise-Canceling Headphones"
                  value={newProduct.product_name}
                  onChange={e => setNewProduct({ ...newProduct, product_name: e.target.value })}
                  required
                />
              </div>
              <div>
                <label className="form-label">Category *</label>
                <select
                  className="form-select"
                  value={newProduct.category}
                  onChange={e => setNewProduct({ ...newProduct, category: e.target.value })}
                >
                  <option value="Electronics">Electronics</option>
                  <option value="Fashion">Fashion</option>
                  <option value="Books">Books</option>
                  <option value="Home & Kitchen">Home & Kitchen</option>
                  <option value="Beauty & Personal Care">Beauty & Personal Care</option>
                  <option value="Sports & Fitness">Sports & Fitness</option>
                  <option value="Other">Other</option>
                </select>
              </div>
              <div>
                <label className="form-label">Unit Price (₹) *</label>
                <input
                  type="number"
                  step="0.01"
                  min="0.01"
                  className="form-input"
                  value={newProduct.price}
                  onChange={e => setNewProduct({ ...newProduct, price: e.target.value })}
                  required
                />
              </div>
            </div>

            <div className="form-grid-2">
              <div>
                <label className="form-label">Initial Inventory Stock *</label>
                <input
                  type="number"
                  min="0"
                  className="form-input"
                  value={newProduct.stock}
                  onChange={e => setNewProduct({ ...newProduct, stock: e.target.value })}
                  required
                />
              </div>
              {isAdmin && (
                <div>
                  <label className="form-label">Assign to Vendor *</label>
                  <select
                    className="form-select"
                    value={newProduct.vendor_id}
                    onChange={e => setNewProduct({ ...newProduct, vendor_id: e.target.value })}
                    required
                  >
                    {vendors.map(v => (
                      <option key={v.vendor_id} value={v.vendor_id}>
                        {v.business_name} (ID: {v.vendor_id})
                      </option>
                    ))}
                  </select>
                </div>
              )}
            </div>

            <button type="submit" className="btn btn-primary" style={{ marginTop: '10px' }}>
              Add Product to Catalog
            </button>
          </form>
        </div>
      )}

      {/* Filters */}
      <div className="card" style={{ padding: '16px' }}>
        <form onSubmit={handleSearchSubmit} className="form-grid-2" style={{ margin: 0 }}>
          <div>
            <label className="form-label">Search products</label>
            <div style={{ display: 'flex', gap: '8px' }}>
              <input
                type="text"
                className="form-input"
                placeholder="Search by product name, category..."
                value={search}
                onChange={e => setSearch(e.target.value)}
              />
              <button type="submit" className="btn btn-secondary">
                <Search size={14} />
              </button>
            </div>
          </div>
          <div>
            <label className="form-label">Category Filter</label>
            <select
              className="form-select"
              value={categoryFilter}
              onChange={e => setCategoryFilter(e.target.value)}
            >
              <option value="All">All Categories</option>
              <option value="Electronics">Electronics</option>
              <option value="Fashion">Fashion</option>
              <option value="Books">Books</option>
              <option value="Home & Kitchen">Home & Kitchen</option>
              <option value="Beauty & Personal Care">Beauty & Personal Care</option>
              <option value="Sports & Fitness">Sports & Fitness</option>
            </select>
          </div>
        </form>
      </div>

      {/* Products Table */}
      <div className="card">
        <div className="card-title">
          <span>Product Catalog ({products.length})</span>
        </div>
        <div className="table-responsive">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Product Name</th>
                <th>Category</th>
                <th>Unit Price</th>
                <th>Stock</th>
                <th>Vendor</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {products.map(p => (
                <tr
                  key={p.product_id}
                  onClick={() => {
                    setSelectedProdId(p.product_id);
                    setEditPrice(p.price);
                    setEditStock(p.stock);
                  }}
                  style={{ cursor: 'pointer' }}
                >
                  <td><strong>#{p.product_id}</strong></td>
                  <td style={{ fontWeight: '600', color: '#f8fafc' }}>{p.product_name}</td>
                  <td><span className="badge badge-info">{p.category}</span></td>
                  <td style={{ fontWeight: '700', color: '#34d399' }}>₹{Number(p.price).toFixed(2)}</td>
                  <td>
                    <span className={`badge ${
                      p.stock === 0 ? 'badge-danger' :
                      p.stock <= 10 ? 'badge-warning' : 'badge-success'
                    }`}>
                      {p.stock === 0 ? 'OUT OF STOCK (0)' :
                       p.stock <= 10 ? `LOW STOCK (${p.stock})` : `IN STOCK (${p.stock})`}
                    </span>
                  </td>
                  <td style={{ color: '#94a3b8' }}>{p.vendor_name || `Vendor #${p.vendor_id}`}</td>
                  <td>
                    <span className="badge badge-success">ACTIVE</span>
                  </td>
                </tr>
              ))}
              {products.length === 0 && (
                <tr>
                  <td colSpan="7" style={{ textAlign: 'center', padding: '30px', color: '#94a3b8' }}>
                    No products found matching criteria.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Edit Product Details */}
      {products.length > 0 && (
        <div className="card">
          <div className="card-title">
            <Edit2 size={16} color="#6366f1" />
            <span>Edit Product Details</span>
          </div>

          <div className="form-group">
            <label className="form-label">Select Product to Edit</label>
            <select
              className="form-select"
              value={selectedProdId}
              onChange={e => {
                const id = Number(e.target.value);
                setSelectedProdId(id);
                const found = products.find(p => p.product_id === id);
                if (found) {
                  setEditPrice(found.price);
                  setEditStock(found.stock);
                }
              }}
            >
              {products.map(p => (
                <option key={p.product_id} value={p.product_id}>
                  #{p.product_id} - {p.product_name} (₹{p.price} | Stock: {p.stock})
                </option>
              ))}
            </select>
          </div>

          <div className="form-grid-3" style={{ alignItems: 'flex-end' }}>
            <div>
              <label className="form-label">New Price (₹)</label>
              <input
                type="number"
                step="0.01"
                min="0.01"
                className="form-input"
                value={editPrice}
                onChange={e => setEditPrice(e.target.value)}
              />
            </div>

            <div>
              <label className="form-label">Sync Stock</label>
              <input
                type="number"
                min="0"
                className="form-input"
                value={editStock}
                onChange={e => setEditStock(e.target.value)}
              />
            </div>

            <div style={{ display: 'flex', gap: '8px' }}>
              <button type="button" className="btn btn-primary" style={{ flex: 1 }} onClick={handleUpdateProduct}>
                Save Edits
              </button>
              <button type="button" className="btn btn-danger" onClick={handleDeleteProduct}>
                <Trash2 size={16} />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
