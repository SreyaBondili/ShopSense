import React, { useState } from 'react';
import { useCart } from '../CartContext';
import { getProductImageUrl } from '../productImages';
import { api } from '../api';
import { Trash2, Plus, Minus, ShoppingBag, CheckCircle } from 'lucide-react';

export default function CartPage({ onOrderSuccess, onNavigate }) {
  const { items, updateQty, removeItem, clearCart, totalAmount } = useCart();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handlePlaceOrder = async () => {
    if (items.length === 0) return;
    setError('');
    setLoading(true);
    const results = [];
    const failed = [];
    try {
      // Process each cart item as a separate transaction
      for (const item of items) {
        try {
          const resp = await api.createTransaction({
            product_id: item.product_id,
            quantity: item.quantity,
          });
          results.push({ ...item, transaction_id: resp.transaction_id, amount: resp.amount });
        } catch (err) {
          failed.push({ item, error: err.message });
        }
      }
      if (results.length === 0) {
        setError('All items failed to order. ' + failed.map(f => `${f.item.product_name}: ${f.error}`).join('; '));
        return;
      }
      // Clear only successfully ordered items
      results.forEach(r => removeItem(r.product_id));
      onOrderSuccess({ items: results, total: results.reduce((s, r) => s + Number(r.amount), 0), failedItems: failed });
    } finally {
      setLoading(false);
    }
  };

  if (items.length === 0) {
    return (
      <div>
        <div className="page-header">
          <h1 className="page-title"><span>🛒</span> My Cart</h1>
        </div>
        <div style={{ textAlign: 'center', padding: '80px 20px' }}>
          <div style={{ fontSize: '64px', marginBottom: '16px' }}>🛒</div>
          <div style={{ fontSize: '20px', fontWeight: '600', color: '#f8fafc', marginBottom: '8px' }}>Your cart is empty</div>
          <p style={{ color: '#64748b', marginBottom: '24px' }}>Add products from the Shop to get started</p>
          <button className="btn btn-primary" onClick={() => onNavigate('Shop')}>
            <ShoppingBag size={16} /> Browse Shop
          </button>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 className="page-title"><span>🛒</span> My Cart</h1>
          <p className="page-subtitle">{items.length} item{items.length !== 1 ? 's' : ''} ready to order</p>
        </div>
        <button className="btn btn-secondary" onClick={clearCart} style={{ fontSize: '13px' }}>
          <Trash2 size={14} /> Clear Cart
        </button>
      </div>

      {error && <div className="alert alert-error"><span>⚠️</span><span>{error}</span></div>}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: '24px', alignItems: 'start' }}>
        {/* Cart items */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          {items.map(item => {
            const imgUrl = getProductImageUrl(item.product_name, item.category);
            const subtotal = Number(item.price) * item.quantity;
            return (
              <div key={item.product_id} style={{
                background: '#1e293b', borderRadius: '14px', border: '1px solid #334155',
                padding: '16px', display: 'flex', gap: '16px', alignItems: 'center'
              }}>
                <img src={imgUrl} alt={item.product_name}
                  style={{ width: '90px', height: '70px', objectFit: 'cover', borderRadius: '10px', flexShrink: 0 }}
                  onError={e => { e.target.src = 'https://images.unsplash.com/photo-1472851294608-062f824d29cc?w=400&h=300&fit=crop'; }} />
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontWeight: '700', fontSize: '15px', color: '#f8fafc', marginBottom: '2px' }}>{item.product_name}</div>
                  <div style={{ fontSize: '12px', color: '#64748b', marginBottom: '8px' }}>by {item.vendor_name || `Vendor #${item.vendor_id}`}</div>
                  <div style={{ fontSize: '13px', color: '#34d399', fontWeight: '600' }}>₹{Number(item.price).toLocaleString('en-IN', { minimumFractionDigits: 2 })} each</div>
                </div>
                {/* Quantity controls */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <button onClick={() => updateQty(item.product_id, item.quantity - 1)}
                    style={{ width: '30px', height: '30px', background: '#334155', border: 'none', borderRadius: '6px', color: '#fff', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Minus size={12} />
                  </button>
                  <span style={{ minWidth: '28px', textAlign: 'center', fontWeight: '700', fontSize: '15px' }}>{item.quantity}</span>
                  <button onClick={() => updateQty(item.product_id, Math.min(item.stock, item.quantity + 1))}
                    style={{ width: '30px', height: '30px', background: '#334155', border: 'none', borderRadius: '6px', color: '#fff', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Plus size={12} />
                  </button>
                </div>
                <div style={{ minWidth: '90px', textAlign: 'right' }}>
                  <div style={{ fontWeight: '800', fontSize: '16px', color: '#f8fafc' }}>₹{subtotal.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</div>
                </div>
                <button onClick={() => removeItem(item.product_id)}
                  style={{ background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)', borderRadius: '8px', color: '#ef4444', cursor: 'pointer', padding: '8px' }}>
                  <Trash2 size={14} />
                </button>
              </div>
            );
          })}
        </div>

        {/* Order Summary */}
        <div style={{ background: '#1e293b', borderRadius: '14px', border: '1px solid #334155', padding: '24px', position: 'sticky', top: '20px' }}>
          <div style={{ fontWeight: '700', fontSize: '18px', marginBottom: '20px' }}>Order Summary</div>
          {items.map(item => (
            <div key={item.product_id} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px', color: '#94a3b8', marginBottom: '8px' }}>
              <span style={{ maxWidth: '160px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{item.product_name} × {item.quantity}</span>
              <span>₹{(Number(item.price) * item.quantity).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
            </div>
          ))}
          <div style={{ borderTop: '1px solid #334155', marginTop: '16px', paddingTop: '16px', display: 'flex', justifyContent: 'space-between', fontWeight: '800', fontSize: '20px' }}>
            <span>Total</span>
            <span style={{ color: '#34d399' }}>₹{totalAmount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
          </div>
          <p style={{ fontSize: '12px', color: '#64748b', marginTop: '8px', marginBottom: '20px' }}>Demo checkout — no payment required</p>
          <button className="btn btn-primary" style={{ width: '100%', padding: '14px', fontSize: '15px' }}
            onClick={handlePlaceOrder} disabled={loading}>
            <CheckCircle size={16} />
            {loading ? 'Placing Order...' : 'Place Order'}
          </button>
        </div>
      </div>
    </div>
  );
}
