import React, { useState, useEffect } from 'react';
import { api } from '../api';
import { useCart } from '../CartContext';
import { getProductImageUrl } from '../productImages';
import { Search, ShoppingCart, CheckCircle, Sparkles } from 'lucide-react';

export default function ShopPage() {
  const { addToCart, items } = useCart();
  const [products, setProducts] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [search, setSearch] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('All');
  const [addedMap, setAddedMap] = useState({});
  const [qtyMap, setQtyMap] = useState({});

  useEffect(() => {
    loadProductsAndRecommendations();
  }, [categoryFilter]);

  const loadProductsAndRecommendations = async () => {
    setLoading(true);
    try {
      const [prodData, recData] = await Promise.all([
        api.getProducts({ search: search.trim(), category: categoryFilter }),
        api.getRecommendations(4).catch(() => [])
      ]);
      setProducts(prodData || []);
      setRecommendations(recData || []);
    } catch (err) {
      setError(err.message || 'Error loading shop items.');
    } finally {
      setLoading(false);
    }
  };

  const handleAddToCart = (product) => {
    const qty = qtyMap[product.product_id] || 1;
    addToCart(product, qty);
    setAddedMap(m => ({ ...m, [product.product_id]: true }));
    setTimeout(() => setAddedMap(m => ({ ...m, [product.product_id]: false })), 1500);
  };

  const cartProductIds = new Set(items.map(i => i.product_id));

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title"><span>🛒</span> Shop</h1>
        <p className="page-subtitle">Smart marketplace catalog & AI-powered product recommendations</p>
      </div>

      {error && <div className="alert alert-error"><span>⚠️</span><span>{error}</span></div>}

      {/* RECOMMENDED FOR YOU SECTION */}
      {recommendations.length > 0 && categoryFilter === 'All' && !search && (
        <div style={{ marginBottom: '32px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
            <Sparkles size={20} color="#6366F1" />
            <h2 style={{ fontSize: '18px', fontWeight: '800', color: '#1E293B', margin: 0 }}>
              Recommended For You
            </h2>
            <span style={{
              fontSize: '11px', fontWeight: '700', padding: '2px 8px', borderRadius: '12px',
              background: '#EEF2FF', color: '#4F46E5', border: '1px solid #C7D2FE'
            }}>AI Personalized</span>
          </div>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))',
            gap: '18px'
          }}>
            {recommendations.map(p => {
              const imgUrl = getProductImageUrl(p.product_name, p.category);
              const inCart = cartProductIds.has(p.product_id);
              const justAdded = addedMap[p.product_id];

              return (
                <div key={p.product_id} style={{
                  background: '#FFFFFF',
                  borderRadius: '14px',
                  border: '1px solid #C7D2FE',
                  boxShadow: '0 4px 14px rgba(99, 102, 241, 0.08)',
                  overflow: 'hidden',
                  display: 'flex',
                  flexDirection: 'column'
                }}>
                  <div style={{ position: 'relative', height: '140px', overflow: 'hidden', background: '#F8FAFC' }}>
                    <img src={imgUrl} alt={p.product_name}
                      style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                      onError={e => { e.target.src = 'https://images.unsplash.com/photo-1472851294608-062f824d29cc?w=400&h=300&fit=crop'; }} />
                    <div style={{
                      position: 'absolute', top: '8px', left: '8px',
                      background: 'rgba(255, 255, 255, 0.92)', backdropFilter: 'blur(4px)',
                      color: '#4F46E5', fontSize: '10px', fontWeight: '700',
                      padding: '3px 8px', borderRadius: '10px', border: '1px solid #C7D2FE'
                    }}>
                      ⭐ Top Pick
                    </div>
                  </div>

                  <div style={{ padding: '16px', flex: 1, display: 'flex', flexDirection: 'column' }}>
                    <div style={{ fontSize: '11px', color: '#6366F1', fontWeight: '600', marginBottom: '4px' }}>
                      {p.recommendation_reason}
                    </div>
                    <div style={{ fontWeight: '700', fontSize: '14px', color: '#1E293B', marginBottom: '2px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                      {p.product_name}
                    </div>
                    <div style={{ fontSize: '11px', color: '#64748B', marginBottom: '8px' }}>
                      by {p.vendor_name}
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 'auto', paddingTop: '8px' }}>
                      <span style={{ fontSize: '16px', fontWeight: '800', color: '#059669' }}>
                        ₹{Number(p.price).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                      </span>
                      <button
                        className="btn btn-primary"
                        style={{ padding: '6px 12px', fontSize: '12px' }}
                        onClick={() => handleAddToCart(p)}
                      >
                        {justAdded ? 'Added!' : inCart ? 'In Cart' : '+ Add'}
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Filter and Search Bar */}
      <div className="card" style={{ padding: '20px', marginBottom: '24px' }}>
        <div className="form-grid-2" style={{ margin: 0 }}>
          <div>
            <label className="form-label">Search Catalog</label>
            <div style={{ display: 'flex', gap: '8px' }}>
              <input type="text" className="form-input" placeholder="Search products..."
                value={search} onChange={e => setSearch(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && loadProductsAndRecommendations()} />
              <button className="btn btn-secondary" onClick={loadProductsAndRecommendations}><Search size={14} /></button>
            </div>
          </div>
          <div>
            <label className="form-label">Category Filter</label>
            <select className="form-select" value={categoryFilter} onChange={e => setCategoryFilter(e.target.value)}>
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

      {loading ? (
        <div style={{ textAlign: 'center', padding: '60px', color: '#64748B' }}>Loading products...</div>
      ) : (
        <>
          <div style={{ marginBottom: '16px', fontSize: '14px', color: '#64748B' }}>
            Showing <strong style={{ color: '#1E293B' }}>{products.length}</strong> products
          </div>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))',
            gap: '20px'
          }}>
            {products.map(p => {
              const isOut = p.stock === 0;
              const isLow = p.stock > 0 && p.stock <= 10;
              const qty = qtyMap[p.product_id] || 1;
              const justAdded = addedMap[p.product_id];
              const inCart = cartProductIds.has(p.product_id);
              const imgUrl = getProductImageUrl(p.product_name, p.category);

              return (
                <div key={p.product_id} style={{
                  background: '#FFFFFF',
                  borderRadius: '14px',
                  border: inCart ? '1px solid #6366F1' : '1px solid #E9EAF3',
                  boxShadow: '0 2px 8px rgba(0,0,0,0.04)',
                  overflow: 'hidden',
                  display: 'flex',
                  flexDirection: 'column',
                  transition: 'border-color 0.2s, box-shadow 0.2s'
                }}>
                  <div style={{ position: 'relative', height: '180px', overflow: 'hidden', background: '#F8FAFC' }}>
                    <img src={imgUrl} alt={p.product_name}
                      style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                      onError={e => { e.target.src = 'https://images.unsplash.com/photo-1472851294608-062f824d29cc?w=400&h=300&fit=crop'; }} />
                    <div style={{
                      position: 'absolute', top: '8px', right: '8px',
                      background: isOut ? '#DC2626' : isLow ? '#D97706' : '#059669',
                      color: '#FFFFFF', fontSize: '11px', fontWeight: '700',
                      padding: '3px 8px', borderRadius: '20px'
                    }}>
                      {isOut ? 'OUT OF STOCK' : isLow ? `LOW: ${p.stock}` : `IN STOCK`}
                    </div>
                    {inCart && (
                      <div style={{
                        position: 'absolute', top: '8px', left: '8px',
                        background: '#6366F1', color: '#FFFFFF', fontSize: '11px', fontWeight: '700',
                        padding: '3px 8px', borderRadius: '20px'
                      }}>IN CART</div>
                    )}
                  </div>

                  <div style={{ padding: '16px', flex: 1, display: 'flex', flexDirection: 'column' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                      <span style={{
                        fontSize: '11px', fontWeight: '700', textTransform: 'uppercase',
                        color: '#4F46E5', background: '#EEF2FF',
                        padding: '2px 8px', borderRadius: '20px'
                      }}>{p.category}</span>
                    </div>
                    <div style={{ fontWeight: '700', fontSize: '15px', color: '#1E293B', marginBottom: '4px', lineHeight: '1.3' }}>
                      {p.product_name}
                    </div>
                    <div style={{ fontSize: '12px', color: '#64748B', marginBottom: '12px' }}>
                      by {p.vendor_name || `Vendor #${p.vendor_id}`}
                    </div>
                    <div style={{ fontSize: '20px', fontWeight: '800', color: '#059669', marginBottom: '14px' }}>
                      ₹{Number(p.price).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                    </div>

                    {!isOut ? (
                      <div style={{ display: 'flex', gap: '8px', marginTop: 'auto' }}>
                        <input type="number" min={1} max={p.stock} value={qty}
                          onChange={e => setQtyMap(m => ({ ...m, [p.product_id]: Math.min(p.stock, Math.max(1, Number(e.target.value))) }))}
                          style={{
                            width: '60px', padding: '8px', background: '#F8FAFC',
                            border: '1px solid #E9EAF3', color: '#1E293B',
                            borderRadius: '8px', fontSize: '14px', textAlign: 'center'
                          }} />
                        <button
                          className="btn btn-primary"
                          style={{ flex: 1, fontSize: '13px', gap: '6px',
                            background: justAdded ? '#059669' : undefined }}
                          onClick={() => handleAddToCart(p)}>
                          {justAdded ? <><CheckCircle size={14} /> Added!</> : <><ShoppingCart size={14} /> Add to Cart</>}
                        </button>
                      </div>
                    ) : (
                      <button disabled className="btn btn-secondary"
                        style={{ width: '100%', opacity: 0.5, cursor: 'not-allowed', marginTop: 'auto' }}>
                        Out of Stock
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
          {products.length === 0 && (
            <div style={{ textAlign: 'center', padding: '60px', color: '#64748B' }}>
              No products found. Try a different search or category.
            </div>
          )}
        </>
      )}
    </div>
  );
}
