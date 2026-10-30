import React, { useState, useEffect } from 'react';
import { api } from '../api';
import { getProductImageUrl } from '../productImages';
import { RefreshCw } from 'lucide-react';

export default function MyOrdersPage() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => { loadOrders(); }, []);

  const loadOrders = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await api.getTransactions();
      setOrders(data || []);
    } catch (err) {
      setError(err.message || 'Failed to load orders.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 className="page-title"><span>📦</span> My Orders</h1>
          <p className="page-subtitle">{orders.length} order{orders.length !== 1 ? 's' : ''} placed</p>
        </div>
        <button className="btn btn-secondary" onClick={loadOrders} style={{ fontSize: '13px' }}>
          <RefreshCw size={14} /> Refresh
        </button>
      </div>

      {error && <div className="alert alert-error"><span>⚠️</span><span>{error}</span></div>}

      {loading ? (
        <div style={{ textAlign: 'center', padding: '60px', color: '#64748B' }}>Loading orders...</div>
      ) : orders.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '80px 20px' }}>
          <div style={{ fontSize: '64px', marginBottom: '16px' }}>📭</div>
          <div style={{ fontSize: '20px', fontWeight: '700', color: '#1E293B', marginBottom: '8px' }}>No orders yet</div>
          <p style={{ color: '#64748B' }}>Head to the Shop to place your first order!</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          {orders.map(o => {
            const imgUrl = getProductImageUrl(o.product_name || '', '');
            return (
              <div key={o.transaction_id} style={{
                background: '#FFFFFF', borderRadius: '14px', border: '1px solid #E9EAF3',
                padding: '16px', display: 'flex', gap: '16px', alignItems: 'center',
                boxShadow: '0 2px 6px rgba(0,0,0,0.03)'
              }}>
                <img src={imgUrl} alt={o.product_name}
                  style={{ width: '80px', height: '64px', objectFit: 'cover', borderRadius: '10px', flexShrink: 0 }}
                  onError={e => { e.target.src = 'https://images.unsplash.com/photo-1472851294608-062f824d29cc?w=400&h=300&fit=crop'; }} />
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontWeight: '700', fontSize: '15px', color: '#1E293B', marginBottom: '2px' }}>{o.product_name || 'Product'}</div>
                  <div style={{ fontSize: '12px', color: '#64748B', marginBottom: '6px' }}>by {o.vendor_name || `Vendor #${o.vendor_id}`}</div>
                  <div style={{ display: 'flex', gap: '16px', fontSize: '13px', color: '#64748B' }}>
                    <span>Qty: <strong style={{ color: '#1E293B' }}>{o.quantity}</strong></span>
                    <span>Date: <strong style={{ color: '#1E293B' }}>{new Date(o.transaction_date).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })}</strong></span>
                  </div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontWeight: '800', fontSize: '18px', color: '#059669' }}>₹{Number(o.amount).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</div>
                  <div style={{ display: 'inline-block', background: '#ECFDF5', color: '#059669', fontSize: '11px', fontWeight: '700', padding: '2px 8px', borderRadius: '20px', marginTop: '4px', border: '1px solid #A7F3D0' }}>DELIVERED</div>
                </div>
                <div style={{ textAlign: 'right', minWidth: '70px' }}>
                  <div style={{ fontSize: '12px', color: '#64748B' }}>Order</div>
                  <div style={{ fontWeight: '700', color: '#6366F1', fontSize: '14px' }}>#{o.transaction_id}</div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
