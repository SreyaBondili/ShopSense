import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';

const CartContext = createContext(null);

export function CartProvider({ userEmail, children }) {
  const storageKey = userEmail ? `shopsense_cart_${userEmail}` : null;

  const loadCart = () => {
    if (!storageKey) return [];
    try { return JSON.parse(localStorage.getItem(storageKey) || '[]'); }
    catch { return []; }
  };

  const [items, setItems] = useState(loadCart);

  // Reload cart when user changes
  useEffect(() => {
    setItems(loadCart());
  }, [storageKey]);

  const persist = (newItems) => {
    if (storageKey) localStorage.setItem(storageKey, JSON.stringify(newItems));
    setItems(newItems);
  };

  const addToCart = useCallback((product, qty = 1) => {
    setItems(prev => {
      const existing = prev.find(i => i.product_id === product.product_id);
      let updated;
      if (existing) {
        updated = prev.map(i =>
          i.product_id === product.product_id
            ? { ...i, quantity: Math.min(i.quantity + qty, product.stock) }
            : i
        );
      } else {
        updated = [...prev, {
          product_id: product.product_id,
          product_name: product.product_name,
          category: product.category,
          price: product.price,
          stock: product.stock,
          vendor_id: product.vendor_id,
          vendor_name: product.vendor_name,
          quantity: qty
        }];
      }
      if (storageKey) localStorage.setItem(storageKey, JSON.stringify(updated));
      return updated;
    });
  }, [storageKey]);

  const updateQty = useCallback((productId, qty) => {
    setItems(prev => {
      const updated = prev.map(i => i.product_id === productId ? { ...i, quantity: qty } : i).filter(i => i.quantity > 0);
      if (storageKey) localStorage.setItem(storageKey, JSON.stringify(updated));
      return updated;
    });
  }, [storageKey]);

  const removeItem = useCallback((productId) => {
    setItems(prev => {
      const updated = prev.filter(i => i.product_id !== productId);
      if (storageKey) localStorage.setItem(storageKey, JSON.stringify(updated));
      return updated;
    });
  }, [storageKey]);

  const clearCart = useCallback(() => {
    if (storageKey) localStorage.removeItem(storageKey);
    setItems([]);
  }, [storageKey]);

  const totalItems = items.reduce((s, i) => s + i.quantity, 0);
  const totalAmount = items.reduce((s, i) => s + Number(i.price) * i.quantity, 0);

  return (
    <CartContext.Provider value={{ items, addToCart, updateQty, removeItem, clearCart, totalItems, totalAmount }}>
      {children}
    </CartContext.Provider>
  );
}

export function useCart() {
  const ctx = useContext(CartContext);
  if (!ctx) throw new Error('useCart must be inside CartProvider');
  return ctx;
}
