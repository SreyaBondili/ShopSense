import React, { useState, useEffect } from 'react';
import { api } from '../api';
import { CreditCard, ShoppingCart, CheckCircle, AlertCircle } from 'lucide-react';

export default function TransactionsPage({ user }) {
  const [transactions, setTransactions] = useState([]);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Sale creation states
  const [showOrderForm, setShowOrderForm] = useState(false);
  const [selectedProductId, setSelectedProductId] = useState('');
  const [quantity, setQuantity] = useState(1);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [txData, prodData] = await Promise.all([
        api.getTransactions(),
        api.getProducts(),
      ]);
      setTransactions(txData || []);
      const inStock = (prodData || []).filter(p => p.stock > 0);
      setProducts(inStock);
      if (inStock.length > 0 && !selectedProductId) {
        setSelectedProductId(inStock[0].product_id);
      }
    } catch (err) {
      setError(err.message || 'Error loading transactions.');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTransaction = async (e) => {
    e.preventDefault();
    if (!selectedProductId) return;
    setError('');
    setSuccess('');
    try {
      const resp = await api.createTransaction({
        product_id: Number(selectedProductId),
        quantity: Number(quantity),
      });
      setSuccess(`Transaction #${resp.transaction_id} executed! Stock automatically decremented.`);
      setShowOrderForm(false);
      setQuantity(1);
      loadData();
    } catch (err) {
      setError(err.message || 'Transaction failed.');
    }
  };

  const selectedProduct = products.find(p => p.product_id === Number(selectedProductId));
  const estimatedTotal = selectedProduct ? (Number(selectedProduct.price) * quantity).toFixed(2) : '0.00';

  return (
    <div>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 className="page-title">
            <span>💳</span> Transaction Management & Sales Ledger
          </h1>
          <p className="page-subtitle">Immutable audit trail of marketplace orders with real-time stock deduction</p>
        </div>
        <button
          className="btn btn-primary"
          onClick={() => setShowOrderForm(!showOrderForm)}
        >
          <ShoppingCart size={16} />
          {showOrderForm ? 'Close Order Form' : 'Record New Sale / Order'}
        </button>
      </div>

      {error && <div className="alert alert-error"><span>⚠️</span><span>{error}</span></div>}
      {success && <div className="alert alert-success"><span>✅</span><span>{success}</span></div>}

      {/* Manual Order Creation Form */}
      {showOrderForm && (
        <div className="card" style={{ border: '1px solid #6366f1' }}>
          <div className="card-title">
            <CreditCard size={18} color="#6366f1" />
            <span>Record New Sale / Order</span>
          </div>

          {products.length > 0 ? (
            <form onSubmit={handleCreateTransaction}>
              <div className="form-group">
                <label className="form-label">Select Product to Sell</label>
                <select
                  className="form-select"
                  value={selectedProductId}
                  onChange={e => setSelectedProductId(e.target.value)}
                >
                  {products.map(p => (
                    <option key={p.product_id} value={p.product_id}>
                      {p.product_name} | Price: ₹{p.price} | Available: {p.stock} in stock ({p.vendor_name || `Vendor #${p.vendor_id}`})
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-grid-2" style={{ alignItems: 'center' }}>
                <div>
                  <label className="form-label">Quantity to Purchase</label>
                  <input
                    type="number"
                    min="1"
                    max={selectedProduct ? selectedProduct.stock : 999}
                    className="form-input"
                    value={quantity}
                    onChange={e => setQuantity(Math.max(1, Number(e.target.value)))}
                    required
                  />
                </div>
                <div style={{ padding: '10px 16px', background: '#0f172a', borderRadius: '8px', border: '1px solid #334155' }}>
                  <div style={{ fontSize: '11px', color: '#94a3b8', textTransform: 'uppercase', fontWeight: '600' }}>
                    Total Transaction Value
                  </div>
                  <div style={{ fontSize: '20px', fontWeight: '800', color: '#34d399' }}>
                    ₹{estimatedTotal}
                  </div>
                </div>
              </div>

              <button type="submit" className="btn btn-primary" style={{ marginTop: '16px' }}>
                Confirm & Complete Transaction
              </button>
            </form>
          ) : (
            <div style={{ color: '#fbbf24', padding: '20px', textAlign: 'center' }}>
              All products are currently out of stock. Please restock items via the Inventory tab.
            </div>
          )}
        </div>
      )}

      {/* Transactions Table */}
      <div className="card">
        <div className="card-title">
          <span>Sales History ({transactions.length} Total Transactions)</span>
        </div>
        <div className="table-responsive">
          <table>
            <thead>
              <tr>
                <th>Tx ID</th>
                <th>Product Name</th>
                <th>Vendor</th>
                <th>Quantity</th>
                <th>Amount</th>
                <th>Transaction Date</th>
              </tr>
            </thead>
            <tbody>
              {transactions.map(t => (
                <tr key={t.transaction_id}>
                  <td><strong>#{t.transaction_id}</strong></td>
                  <td style={{ fontWeight: '600', color: '#f8fafc' }}>{t.product_name}</td>
                  <td><span className="badge badge-info">{t.vendor_name || `Vendor #${t.vendor_id}`}</span></td>
                  <td style={{ fontWeight: '700' }}>{t.quantity}</td>
                  <td style={{ fontWeight: '700', color: '#34d399' }}>₹{Number(t.amount).toFixed(2)}</td>
                  <td style={{ color: '#94a3b8', fontSize: '12px' }}>
                    {new Date(t.transaction_date).toLocaleString()}
                  </td>
                </tr>
              ))}
              {transactions.length === 0 && (
                <tr>
                  <td colSpan="6" style={{ textAlign: 'center', padding: '30px', color: '#94a3b8' }}>
                    No transaction records found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
