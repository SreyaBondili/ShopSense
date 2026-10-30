import React, { useState, useEffect } from 'react';
import { api } from '../api';
import AnimatedCounter from '../components/AnimatedCounter';
import { Package, Plus, Search, Edit2, Trash2, X, CheckCircle, Tag, Layers, DollarSign } from 'lucide-react';

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
    price: 499.00,
    stock: 25,
    vendor_id: '',
  });

  // Edit states
  const [selectedProdId, setSelectedProdId] = useState('');
  const [editPrice, setEditPrice] = useState(499.00);
  const [editStock, setEditStock] = useState(25);

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
      setSuccess(`Product '${newProduct.product_name}' successfully added to catalog!`);
      setShowAddForm(false);
      setNewProduct(prev => ({ ...prev, product_name: '', price: 499.00, stock: 25 }));
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
      setSuccess('Product unit price and warehouse stock updated successfully!');
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

  // Metrics
  const totalProds = products.length;
  const totalCategories = new Set(products.map(p => p.category)).size;
  const totalStockUnits = products.reduce((s, p) => s + Number(p.stock || 0), 0);
  const avgPrice = totalProds > 0
    ? (products.reduce((s, p) => s + Number(p.price || 0), 0) / totalProds).toFixed(2)
    : 0;

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
          {showAddForm ? <X size={16} /> : <Plus size={16} />}
          {showAddForm ? 'Close Form' : 'Add New Product'}
        </button>
      </div>

      {error && <div className="alert alert-error"><span>⚠️</span><span>{error}</span></div>}
      {success && <div className="alert alert-success"><span>✅</span><span>{success}</span></div>}

      {/* KPI Cards */}
      <div className="kpi-grid">
        <div className="kpi-card">
          <div className="kpi-label">Catalog Products</div>
          <div className="kpi-value" style={{ color: '#1E293B' }}>
            <AnimatedCounter value={totalProds} duration={1000} />
          </div>
        </div>
        <div className="kpi-card">
          <div className="kpi-label">Active Categories</div>
          <div className="kpi-value" style={{ color: '#6366F1' }}>
            <AnimatedCounter value={totalCategories} duration={1000} />
          </div>
        </div>
        <div className="kpi-card">
          <div className="kpi-label">In-Stock Units</div>
          <div className="kpi-value" style={{ color: '#059669' }}>
            <AnimatedCounter value={totalStockUnits} duration={1100} />
          </div>
        </div>
        <div className="kpi-card">
          <div className="kpi-label">Average Unit Price</div>
          <div className="kpi-value" style={{ color: '#1E293B' }}>
            ₹{avgPrice}
          </div>
        </div>
      </div>

      {/* Add Product Form — Clean Multi-Column Horizontal Card */}
      {showAddForm && (
        <div className="card" style={{ border: '1px solid #C7D2FE', marginBottom: '24px', background: '#FFFFFF', boxShadow: '0 4px 12px rgba(99, 102, 241, 0.08)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '18px', paddingBottom: '12px', borderBottom: '1px solid #E9EAF3' }}>
            <div className="card-title" style={{ margin: 0 }}>
              <Package size={18} color="#6366F1" />
              <span>Add New Product to Catalog</span>
            </div>
            <button
              onClick={() => setShowAddForm(false)}
              style={{ background: 'none', border: 'none', color: '#64748B', cursor: 'pointer', padding: '4px' }}
            >
              <X size={18} />
            </button>
          </div>

          <form onSubmit={handleCreateProduct}>
            <div className="form-grid-3" style={{ marginBottom: '16px' }}>
              <div>
                <label className="form-label">Product Name *</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="e.g. Wireless Ergonomic Mouse"
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
                  min="1"
                  className="form-input"
                  value={newProduct.price}
                  onChange={e => setNewProduct({ ...newProduct, price: e.target.value })}
                  required
                />
              </div>
            </div>

            <div className="form-grid-2" style={{ marginBottom: '20px' }}>
              <div>
                <label className="form-label">Initial Inventory Units *</label>
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
                  <label className="form-label">Assign to Registered Vendor *</label>
                  <select
                    className="form-select"
                    value={newProduct.vendor_id}
                    onChange={e => setNewProduct({ ...newProduct, vendor_id: e.target.value })}
                    required
                  >
                    {vendors.map(v => (
                      <option key={v.vendor_id} value={v.vendor_id}>
                        {v.business_name} (ID: #{v.vendor_id} - {v.owner_name})
                      </option>
                    ))}
                  </select>
                </div>
              )}
            </div>

            <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end', borderTop: '1px solid #E9EAF3', paddingTop: '16px' }}>
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => setShowAddForm(false)}
              >
                Cancel
              </button>
              <button type="submit" className="btn btn-primary">
                <CheckCircle size={16} /> Add Product to Catalog
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Filter Bar */}
      <div className="card" style={{ padding: '16px 20px', marginBottom: '20px' }}>
        <form onSubmit={handleSearchSubmit} className="form-grid-2" style={{ margin: 0 }}>
          <div>
            <label className="form-label">Search Products</label>
            <div style={{ display: 'flex', gap: '8px' }}>
              <input
                type="text"
                className="form-input"
                placeholder="Search by product name..."
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

      {/* Products Table with Thumbnails */}
      <div className="card" style={{ padding: '24px', marginBottom: '24px' }}>
        <div className="card-title" style={{ marginBottom: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span>Product Catalog ({products.length})</span>
          <span style={{ fontSize: '12px', color: '#64748B', fontWeight: 'normal' }}>Click row to edit pricing/stock</span>
        </div>
        <div className="table-container">
          <table className="table">
            <thead>
              <tr>
                <th>PRODUCT</th>
                <th>CATEGORY</th>
                <th>UNIT PRICE</th>
                <th>STOCK LEVEL</th>
                <th>VENDOR</th>
                <th>STATUS</th>
              </tr>
            </thead>
            <tbody>
              {products.map(p => {
                const isSelected = String(selectedProdId) === String(p.product_id);
                const isOut = p.stock === 0;
                const isLow = p.stock > 0 && p.stock <= 10;
                return (
                  <tr
                    key={p.product_id}
                    onClick={() => {
                      setSelectedProdId(p.product_id);
                      setEditPrice(p.price);
                      setEditStock(p.stock);
                    }}
                    style={{
                      cursor: 'pointer',
                      background: isSelected ? '#F1F5F9' : undefined
                    }}
                  >
                    <td>
                      <div style={{ fontWeight: '700', color: '#1E293B', fontSize: '13.5px' }}>
                        {p.product_name}
                      </div>
                      <div style={{ fontSize: '11px', color: '#94A3B8', marginTop: '2px' }}>
                        ID: #{p.product_id}
                      </div>
                    </td>
                    <td>
                      <span className="badge" style={{ background: '#EEF2FF', color: '#6366F1', border: '1px solid #C7D2FE' }}>
                        {p.category}
                      </span>
                    </td>
                    <td style={{ fontWeight: '700', color: '#059669', fontSize: '14px' }}>
                      ₹{Number(p.price).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                    </td>
                    <td>
                      <span className={`badge ${
                        isOut ? 'badge-danger' : isLow ? 'badge-warning' : 'badge-success'
                      }`}>
                        {isOut ? 'OUT OF STOCK (0)' : isLow ? `LOW STOCK (${p.stock})` : `IN STOCK (${p.stock})`}
                      </span>
                    </td>
                    <td style={{ color: '#475569', fontWeight: '500' }}>
                      {p.vendor_name || `Vendor #${p.vendor_id}`}
                    </td>
                    <td>
                      <span className="badge badge-success">ACTIVE</span>
                    </td>
                  </tr>
                );
              })}
              {products.length === 0 && (
                <tr>
                  <td colSpan="7" style={{ textAlign: 'center', padding: '40px', color: '#64748B' }}>
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
        <div className="card" style={{ padding: '24px' }}>
          <div className="card-title" style={{ marginBottom: '16px' }}>
            <Edit2 size={16} color="#6366F1" />
            <span>Edit Product Details</span>
          </div>

          <div className="form-grid-3" style={{ alignItems: 'end' }}>
            <div className="form-group" style={{ margin: 0 }}>
              <label className="form-label">Select Product to Edit</label>
              <select
                className="form-select"
                value={selectedProdId}
                onChange={e => {
                  const id = Number(e.target.value);
                  setSelectedProdId(id);
                  const p = products.find(item => item.product_id === id);
                  if (p) {
                    setEditPrice(p.price);
                    setEditStock(p.stock);
                  }
                }}
              >
                {products.map(p => (
                  <option key={p.product_id} value={p.product_id}>
                    {p.product_name} (ID: #{p.product_id} - ₹{Number(p.price).toFixed(2)})
                  </option>
                ))}
              </select>
            </div>

            <div style={{ display: 'flex', gap: '8px' }}>
              <div style={{ flex: 1 }}>
                <label className="form-label">Unit Price (₹)</label>
                <input
                  type="number"
                  step="0.01"
                  min="0.01"
                  className="form-input"
                  value={editPrice}
                  onChange={e => setEditPrice(e.target.value)}
                />
              </div>
              <div style={{ flex: 1 }}>
                <label className="form-label">Warehouse Stock</label>
                <input
                  type="number"
                  min="0"
                  className="form-input"
                  value={editStock}
                  onChange={e => setEditStock(e.target.value)}
                />
              </div>
            </div>

            <div style={{ display: 'flex', gap: '8px' }}>
              <button
                type="button"
                className="btn btn-primary"
                onClick={handleUpdateProduct}
                style={{ flex: 1 }}
              >
                Save Changes
              </button>
              <button
                type="button"
                className="btn btn-danger"
                onClick={handleDeleteProduct}
                title="Delete Product"
              >
                <Trash2 size={16} />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
