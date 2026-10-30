import React from 'react';
import { CheckCircle, ShoppingBag, Package } from 'lucide-react';
import { getProductImageUrl } from '../productImages';

export default function OrderSuccessPage({ orderData, onContinueShopping, onViewOrders }) {
  if (!orderData) return null;
  const { items, total, failedItems = [] } = orderData;
  const orderRef = `ORD-${Date.now().toString().slice(-6)}`;

  return (
    <div style={{ maxWidth: '700px', margin: '0 auto', padding: '20px' }}>
      {/* Success header */}
      <div style={{ textAlign: 'center', marginBottom: '32px' }}>
        <div style={{
          width: '72px', height: '72px', background: '#ECFDF5',
          borderRadius: '50%', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', marginBottom: '16px',
          border: '1px solid #A7F3D0'
        }}>
          <CheckCircle size={40} color="#059669" />
        </div>
        <h1 style={{ fontSize: '28px', fontWeight: '800', color: '#1E293B', marginBottom: '8px' }}>Order Placed Successfully!</h1>
        <p style={{ color: '#64748B', fontSize: '15px' }}>Thank you for your purchase. Your order has been confirmed.</p>
        <div style={{ display: 'inline-block', background: '#EEF2FF', border: '1px solid #C7D2FE', borderRadius: '8px', padding: '6px 16px', marginTop: '12px', color: '#4F46E5', fontSize: '14px', fontWeight: '600' }}>
          Reference: {orderRef}
        </div>
      </div>

      {/* Items */}
      <div style={{ background: '#FFFFFF', borderRadius: '14px', border: '1px solid #E9EAF3', overflow: 'hidden', marginBottom: '20px', boxShadow: '0 2px 8px rgba(0,0,0,0.04)' }}>
        <div style={{ padding: '16px 20px', borderBottom: '1px solid #E9EAF3', fontWeight: '700', fontSize: '15px', color: '#1E293B' }}>Items Ordered ({items.length})</div>
        {items.map((item, i) => {
          const imgUrl = getProductImageUrl(item.product_name, item.category);
          return (
            <div key={i} style={{ display: 'flex', gap: '14px', padding: '14px 20px', borderBottom: i < items.length - 1 ? '1px solid #F1F5F9' : 'none', alignItems: 'center' }}>
              <img src={imgUrl} alt={item.product_name}
                style={{ width: '60px', height: '48px', objectFit: 'cover', borderRadius: '8px', flexShrink: 0 }}
                onError={e => { e.target.src = 'https://images.unsplash.com/photo-1472851294608-062f824d29cc?w=400&h=300&fit=crop'; }} />
              <div style={{ flex: 1 }}>
                <div style={{ fontWeight: '600', fontSize: '14px', color: '#1E293B' }}>{item.product_name}</div>
                <div style={{ fontSize: '12px', color: '#64748B' }}>Qty: {item.quantity} × ₹{Number(item.price).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</div>
              </div>
              <div style={{ fontWeight: '700', color: '#059669', fontSize: '15px' }}>₹{Number(item.amount).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</div>
            </div>
          );
        })}
        <div style={{ padding: '14px 20px', background: '#F8FAFC', borderTop: '1px solid #E9EAF3', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span style={{ fontWeight: '700', fontSize: '16px', color: '#1E293B' }}>Total Paid</span>
          <span style={{ fontWeight: '800', fontSize: '22px', color: '#059669' }}>₹{total.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
        </div>
      </div>

      {failedItems.length > 0 && (
        <div style={{ background: '#FEF2F2', border: '1px solid #FECACA', borderRadius: '10px', padding: '14px 18px', marginBottom: '20px' }}>
          <div style={{ fontWeight: '700', color: '#DC2626', marginBottom: '6px' }}>⚠️ Some items could not be ordered:</div>
          {failedItems.map((f, i) => <div key={i} style={{ fontSize: '13px', color: '#64748B' }}>{f.item.product_name}: {f.error}</div>)}
        </div>
      )}

      <div style={{ display: 'flex', gap: '12px' }}>
        <button className="btn btn-secondary" style={{ flex: 1 }} onClick={onViewOrders}><Package size={16} /> View My Orders</button>
        <button className="btn btn-primary" style={{ flex: 1 }} onClick={onContinueShopping}><ShoppingBag size={16} /> Continue Shopping</button>
      </div>
    </div>
  );
}
