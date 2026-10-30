import React, { useState, useEffect, useCallback } from 'react';
import { api } from './api';
import { CartProvider, useCart } from './CartContext';
import Toast from './components/Toast';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import VendorsPage from './pages/VendorsPage';
import ProductsPage from './pages/ProductsPage';
import InventoryPage from './pages/InventoryPage';
import TransactionsPage from './pages/TransactionsPage';
import AnalyticsPage from './pages/AnalyticsPage';
import ShopPage from './pages/ShopPage';
import CartPage from './pages/CartPage';
import MyOrdersPage from './pages/MyOrdersPage';
import OrderSuccessPage from './pages/OrderSuccessPage';
import {
  LayoutDashboard, Users, Package, Boxes, CreditCard,
  BarChart3, ShoppingBag, ShoppingCart, PackageCheck, LogOut
} from 'lucide-react';

export default function App() {
  const [user, setUser] = useState(null);
  const [currentPage, setCurrentPage] = useState('');
  const [toasts, setToasts] = useState([]);
  const [orderData, setOrderData] = useState(null);

  useEffect(() => {
    const savedUser = api.getUser();
    if (savedUser && localStorage.getItem('shopsense_token')) {
      setUser(savedUser);
      setCurrentPage(savedUser.role === 'CUSTOMER' ? 'Shop' : 'Dashboard');
    }
  }, []);

  const addToast = useCallback((message, type = 'success') => {
    const id = Date.now();
    setToasts(prev => [...prev, { id, message, type }]);
  }, []);

  const removeToast = useCallback((id) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  }, []);

  const handleLoginSuccess = (userData) => {
    const u = { email: userData.email, name: userData.full_name, role: userData.role, vendor_id: userData.vendor_id };
    setUser(u);
    setCurrentPage(u.role === 'CUSTOMER' ? 'Shop' : 'Dashboard');
    addToast(`Welcome back, ${userData.full_name}! 🎉`);
  };

  const handleLogout = () => {
    api.logout();
    setUser(null);
    setCurrentPage('');
    setOrderData(null);
  };

  const handleOrderSuccess = (data) => {
    setOrderData(data);
    setCurrentPage('OrderSuccess');
    addToast(`Order placed! ${data.items.length} item(s) confirmed. 🎉`);
  };

  if (!user) return <LoginPage onLoginSuccess={handleLoginSuccess} />;

  const getNavItems = () => {
    if (user.role === 'CUSTOMER') return [
      { id: 'Shop', label: 'Shop', icon: ShoppingBag },
      { id: 'Cart', label: 'My Cart', icon: ShoppingCart, showBadge: true },
      { id: 'MyOrders', label: 'My Orders', icon: PackageCheck },
    ];
    if (user.role === 'ADMIN') return [
      { id: 'Dashboard', label: 'Dashboard', icon: LayoutDashboard },
      { id: 'Vendors', label: 'Vendors', icon: Users },
      { id: 'Products', label: 'Products', icon: Package },
      { id: 'Inventory', label: 'Inventory', icon: Boxes },
      { id: 'Transactions', label: 'Transactions', icon: CreditCard },
      { id: 'Analytics', label: 'Analytics', icon: BarChart3 },
    ];
    return [
      { id: 'Dashboard', label: 'Dashboard', icon: LayoutDashboard },
      { id: 'Products', label: 'My Products', icon: Package },
      { id: 'Inventory', label: 'Inventory', icon: Boxes },
      { id: 'Transactions', label: 'Transactions', icon: CreditCard },
      { id: 'Analytics', label: 'Analytics', icon: BarChart3 },
    ];
  };

  return (
    <CartProvider userEmail={user.email}>
      <Toast toasts={toasts} removeToast={removeToast} />
      <AppShell
        user={user}
        currentPage={currentPage}
        setCurrentPage={setCurrentPage}
        handleLogout={handleLogout}
        handleOrderSuccess={handleOrderSuccess}
        orderData={orderData}
        getNavItems={getNavItems}
      />
    </CartProvider>
  );
}

function AppShell({ user, currentPage, setCurrentPage, handleLogout, handleOrderSuccess, orderData, getNavItems }) {
  const { totalItems } = useCart();
  const navItems = getNavItems();

  return (
    <div className="app-container">
      <aside className="sidebar">
        <div className="sidebar-header">
          <div className="logo-row">
            <div className="logo-icon">🛍️</div>
            <div className="logo-text">ShopSense</div>
          </div>
          <div className="user-badge-card">
            <span className={`user-role-pill ${
              user.role === 'ADMIN' ? 'role-admin' : user.role === 'VENDOR' ? 'role-vendor' : 'role-customer'
            }`}>{user.role}</span>
            <div className="user-name">{user.name}</div>
            <div className="user-email">{user.email}</div>
          </div>
        </div>

        <nav className="sidebar-nav">
          {navItems.map(item => {
            const Icon = item.icon;
            const isActive = currentPage === item.id;
            return (
              <button key={item.id}
                className={`nav-link ${isActive ? 'active' : ''}`}
                onClick={() => setCurrentPage(item.id)}
                style={{ position: 'relative' }}
              >
                <Icon size={18} />
                <span>{item.label}</span>
                {item.showBadge && totalItems > 0 && (
                  <span style={{
                    position: 'absolute', right: '12px', top: '50%', transform: 'translateY(-50%)',
                    background: '#ef4444', color: '#fff', fontSize: '11px', fontWeight: '700',
                    borderRadius: '50%', minWidth: '20px', height: '20px',
                    display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '0 4px'
                  }}>{totalItems}</span>
                )}
              </button>
            );
          })}
        </nav>

        <div className="sidebar-footer">
          <button className="logout-btn" onClick={handleLogout}>
            <LogOut size={16} /><span>Sign Out</span>
          </button>
        </div>
      </aside>

      <main className="main-content">
        {user.role === 'CUSTOMER' && (
          <>
            {currentPage === 'Shop' && <ShopPage />}
            {currentPage === 'Cart' && <CartPage onOrderSuccess={handleOrderSuccess} onNavigate={setCurrentPage} />}
            {currentPage === 'MyOrders' && <MyOrdersPage />}
            {currentPage === 'OrderSuccess' && (
              <OrderSuccessPage
                orderData={orderData}
                onContinueShopping={() => setCurrentPage('Shop')}
                onViewOrders={() => setCurrentPage('MyOrders')}
              />
            )}
          </>
        )}
        {user.role !== 'CUSTOMER' && (
          <>
            {currentPage === 'Dashboard' && <DashboardPage user={user} />}
            {currentPage === 'Vendors' && <VendorsPage user={user} />}
            {currentPage === 'Products' && <ProductsPage user={user} />}
            {currentPage === 'Inventory' && <InventoryPage user={user} />}
            {currentPage === 'Transactions' && <TransactionsPage user={user} />}
            {currentPage === 'Analytics' && <AnalyticsPage user={user} />}
          </>
        )}
      </main>
    </div>
  );
}
