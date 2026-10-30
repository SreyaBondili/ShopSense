import React, { useState, useEffect } from 'react';
import { api } from '../api';
import { ShoppingBag, Search, ShoppingCart, CheckCircle, PackageCheck } from 'lucide-react';

export default function CustomerCatalogPage({ user }) {
  const [activeTab, setActiveTab] = useState('catalog'); // 'catalog' or 'orders'
  const [products, setProducts] = useState([]);
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [search, setSearch] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('All');

  // Purchase modal/state
  const [buyQuantities, setBuyQuantities] = useState({});

  useEffect(() => {
    loadProducts();
    if (activeTab === 'orders') {
      loadOrders();
    }
  }, [categoryFilter, activeTab]);

  const loadProducts = async () => {
    setLoading(true);
    try {
      const data = await api.getProducts({
        search: search.trim(),
        category: categoryFilter,
      });
      setProducts(data || []);
    } catch (err) {
      setError(err.message || 'Error loading catalog.');
    } finally {
      setLoading(false);
    }
  };

  const loadOrders = async () => {
    try {
      const data = await api.getTransactions();
      setOrders(data || []);
    } catch (err) {
      setError(err.message || 'Error loading orders.');
    }
  };

  const handleBuy = async (product) => {
    const qty = buyQuantities[product.product_id] || 1;
    setError('');
    setSuccess('');
    try {
      const resp = await api.createTransaction({
        product_id: product.product_id,
        quantity: Number(qty),
      });
      setSuccess(`🎉 Order placed successfully! Transaction ID: #${resp.transaction_id}`);
      loadProducts();
    } catch (err) {
      setError(err.message || 'Failed to place order.');
    }
  };

  return (
    <div>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 className="page-title">
            <span>🛍️</span> Customer Shopping Portal
          </h1>
          <p className="page-subtitle">Welcome, <strong>{user.name}</strong> • Browse marketplace catalog and track personal orders</p>
        </div>

        {/* Tab switch between Catalog and Orders */}
        <div style={{ display: 'flex', gap: '8px', background: '#1e293b', padding: '4px', borderRadius: '8px', border: '1px solid #334155' }}>
          <button
            className={`btn ${activeTab === 'catalog' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ padding: '8px 16px', fontSize: '13px' }}
            onClick={() => setActiveTab('catalog')}
          >
            <ShoppingBag size={15} /> Browse Catalog
          </button>
          <button
            className={`btn ${activeTab === 'orders' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ padding: '8px 16px', fontSize: '13px' }}
            onClick={() => setActiveTab('orders')}
          >
            <PackageCheck size={15} /> My Orders ({orders.length})
          </button>
        </div>
      </div>

      {error && <div className="alert alert-error"><span>⚠️</span><span>{error}</span></div>}
      {success && <div className="alert alert-success"><span>✅</span><span>{success}</span></div>}

      {/* CATALOG VIEW */}
      {activeTab === 'catalog' && (
        <>
          <div className="card" style={{ padding: '16px' }}>
            <div className="form-grid-2" style={{ margin: 0 }}>
              <div>
                <label className="form-label">Search items</label>
                <div style={{ display: 'flex', gap: '8px' }}>
                  <input
                    type="text"
                    className="form-input"
                    placeholder="Search by product name..."
                    value={search}
                    onChange={e => setSearch(e.target.value)}
                  />
                  <button type="button" className="btn btn-secondary" onClick={loadProducts}>
                    <Search size={14} />
                  </button>
                </div>
              </div>

              <div>
                <label className="form-label">Category</label>
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
            </div>
          </div>

          <div style={{ marginBottom: '16px', fontSize: '14px', color: '#94a3b8' }}>
            Showing <strong>{products.length}</strong> available products:
          </div>

          <div className="product-grid">
            {products.map(p => {
              const isOut = p.stock === 0;
              const isLow = p.stock > 0 && p.stock <= 10;
              const selectedQty = buyQuantities[p.product_id] || 1;

              return (
                <div key={p.product_id} className="product-card">
                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                      <span className="badge badge-info">{p.category}</span>
                      <span className={`badge ${isOut ? 'badge-danger' : isLow ? 'badge-warning' : 'badge-success'}`}>
                        {isOut ? 'OUT OF STOCK' : isLow ? `LOW (${p.stock})` : `IN STOCK (${p.stock})`}
                      </span>
                    </div>

                    <div className="product-card-title" style={{ marginTop: '12px' }}>
                      {p.product_name}
                    </div>
                    <div style={{ fontSize: '12px', color: '#94a3b8', marginBottom: '8px' }}>
                      Sold by: <strong>{p.vendor_name || `Vendor #${p.vendor_id}`}</strong>
                    </div>
                    <div className="product-card-price">
                      ₹{Number(p.price).toFixed(2)}
                    </div>
                  </div>

                  <div style={{ marginTop: '16px' }}>
                    {!isOut ? (
                      <div style={{ display: 'flex', gap: '8px' }}>
                        <input
                          type="number"
                          min="1"
                          max={p.stock}
                          value={selectedQty}
                          onChange={e => setBuyQuantities({
                            ...buyQuantities,
                            [p.product_id]: Math.min(p.stock, Math.max(1, Number(e.target.value)))
                          })}
                          style={{
                            width: '60px',
                            padding: '8px',
                            background: '#0f172a',
                            border: '1px solid #334155',
                            color: '#fff',
                            borderRadius: '6px',
                            fontSize: '13px',
                            textAlign: 'center'
                          }}
                        />
                        <button
                          className="btn btn-primary"
                          style={{ flex: 1, padding: '8px' }}
                          onClick={() => handleBuy(p)}
                        >
                          <ShoppingCart size={14} /> Buy Now
                        </button>
                      </div>
                    ) : (
                      <button className="btn btn-secondary" style={{ width: '100%', opacity: 0.5, cursor: 'not-allowed' }} disabled>
                        Out of Stock
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </>
      )}

      {/* MY ORDERS VIEW */}
      {activeTab === 'orders' && (
        <div className="card">
          <div className="card-title">
            <PackageCheck size={18} color="#10b981" />
            <span>Personal Order History ({orders.length} Orders)</span>
          </div>
          <div className="table-responsive">
            <table>
              <thead>
                <tr>
                  <th>Order ID</th>
                  <th>Product Name</th>
                  <th>Vendor</th>
                  <th>Quantity</th>
                  <th>Total Paid</th>
                  <th>Date</th>
                </tr>
              </thead>
              <tbody>
                {orders.map(o => (
                  <tr key={o.transaction_id}>
                    <td><strong>#{o.transaction_id}</strong></td>
                    <td style={{ fontWeight: '600' }}>{o.product_name}</td>
                    <td><span className="badge badge-info">{o.vendor_name || `Vendor #${o.vendor_id}`}</span></td>
                    <td style={{ fontWeight: '700' }}>{o.quantity}</td>
                    <td style={{ fontWeight: '700', color: '#34d399' }}>₹{Number(o.amount).toFixed(2)}</td>
                    <td style={{ color: '#94a3b8' }}>{new Date(o.transaction_date).toLocaleString()}</td>
                  </tr>
                ))}
                {orders.length === 0 && (
                  <tr>
                    <td colSpan="6" style={{ textAlign: 'center', padding: '40px', color: '#94a3b8' }}>
                      You haven't placed any orders yet. Browse our catalog to buy products!
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
