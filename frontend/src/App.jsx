import React, { useState, useEffect, useCallback } from 'react';
import { api } from './api';
import { CartProvider, useCart } from './CartContext';
import Toast from './components/Toast';
import ProtectedRoute from './components/ProtectedRoute';
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

const ROLE_ALLOWED_PAGES = {
  ADMIN: ['Dashboard', 'Vendors', 'Products', 'Inventory', 'Transactions', 'Analytics'],
  VENDOR: ['Dashboard', 'Products', 'Inventory', 'Transactions', 'Analytics'],
  CUSTOMER: ['Shop', 'Cart', 'MyOrders', 'OrderSuccess']
};

// 60 minutes of inactivity timeout threshold
const INACTIVITY_TIMEOUT_MS = 60 * 60 * 1000;

export default function App() {
  const [user, setUser] = useState(() => api.getUser());
  const [currentPage, setCurrentPage] = useState(() => {
    const saved = api.getUser();
    if (!saved) return '';
    const hash = window.location.hash.replace(/^#\/?/, '').toLowerCase();
    const map = {
      '': saved.role === 'CUSTOMER' ? 'Shop' : 'Dashboard',
      'shop': 'Shop',
      'cart': 'Cart',
      'myorders': 'MyOrders',
      'orders': 'MyOrders',
      'dashboard': 'Dashboard',
      'vendors': 'Vendors',
      'products': 'Products',
      'inventory': 'Inventory',
      'transactions': 'Transactions',
      'analytics': 'Analytics'
    };
    const target = map[hash] || (saved.role === 'CUSTOMER' ? 'Shop' : 'Dashboard');
    const allowed = ROLE_ALLOWED_PAGES[saved.role] || [];
    return allowed.includes(target) ? target : (saved.role === 'CUSTOMER' ? 'Shop' : 'Dashboard');
  });
  const [toasts, setToasts] = useState([]);
  const [orderData, setOrderData] = useState(null);

  const addToast = useCallback((message, type = 'success') => {
    const id = Date.now();
    setToasts(prev => [...prev, { id, message, type }]);
  }, []);

  const removeToast = useCallback((id) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  }, []);

  const handleLogout = useCallback(() => {
    api.logout();
    setUser(null);
    setCurrentPage('');
    setOrderData(null);
    window.location.hash = '';
  }, []);

  // Sync state from URL hash with RBAC validation
  const syncPageFromUrl = useCallback((currentUser) => {
    if (!currentUser) return;
    const hash = window.location.hash.replace(/^#\/?/, '').toLowerCase();
    const map = {
      '': currentUser.role === 'CUSTOMER' ? 'Shop' : 'Dashboard',
      'shop': 'Shop',
      'cart': 'Cart',
      'myorders': 'MyOrders',
      'orders': 'MyOrders',
      'dashboard': 'Dashboard',
      'vendors': 'Vendors',
      'products': 'Products',
      'inventory': 'Inventory',
      'transactions': 'Transactions',
      'analytics': 'Analytics'
    };
    const targetPage = map[hash] || (currentUser.role === 'CUSTOMER' ? 'Shop' : 'Dashboard');
    const allowed = ROLE_ALLOWED_PAGES[currentUser.role] || [];
    if (allowed.includes(targetPage)) {
      setCurrentPage(targetPage);
    } else {
      const fallback = currentUser.role === 'CUSTOMER' ? 'Shop' : 'Dashboard';
      setCurrentPage(fallback);
      window.location.hash = `#/${fallback.toLowerCase()}`;
    }
  }, []);

  // Session activity tracker & automatic background token refresh
  useEffect(() => {
    let lastActivity = Date.now();
    let lastRefresh = Date.now();

    const recordActivity = () => {
      lastActivity = Date.now();
    };

    const activityEvents = ['mousedown', 'keydown', 'scroll', 'touchstart', 'click'];
    activityEvents.forEach(evt => window.addEventListener(evt, recordActivity, { passive: true }));

    // Periodic session check: validates inactivity timeout & handles background token refresh
    const sessionInterval = setInterval(() => {
      const currentUser = api.getUser();
      if (!currentUser) {
        if (user) {
          handleLogout();
        }
        return;
      }

      const now = Date.now();
      const idleTime = now - lastActivity;

      // Inactivity timeout check (60 minutes without user activity)
      if (idleTime >= INACTIVITY_TIMEOUT_MS) {
        sessionStorage.setItem(
          'shopsense_session_expired_msg',
          'Your session has expired due to 60 minutes of inactivity. Please sign in again.'
        );
        handleLogout();
        return;
      }

      // Check if JWT token expired
      if (api.isTokenExpired()) {
        sessionStorage.setItem(
          'shopsense_session_expired_msg',
          'Your authentication session has expired. Please sign in again.'
        );
        handleLogout();
        return;
      }

      // Proactive token refresh every 15 minutes during active user sessions
      if (now - lastRefresh > 15 * 60 * 1000 && idleTime < 15 * 60 * 1000) {
        lastRefresh = now;
        api.refreshToken();
      }
    }, 15000);

    const onHashChange = () => {
      const u = api.getUser();
      if (u) syncPageFromUrl(u);
    };
    window.addEventListener('hashchange', onHashChange);

    // Global 401 and 403 event listener
    const onAuthError = (e) => {
      const { status, message } = e.detail || {};
      if (status === 401) {
        sessionStorage.setItem('shopsense_session_expired_msg', message || 'Your session has expired. Please sign in again.');
        handleLogout();
      } else if (status === 403) {
        addToast(message || 'Access Denied: Insufficient permissions.', 'error');
      }
    };
    window.addEventListener('shopsense-auth-error', onAuthError);

    return () => {
      activityEvents.forEach(evt => window.removeEventListener(evt, recordActivity));
      clearInterval(sessionInterval);
      window.removeEventListener('hashchange', onHashChange);
      window.removeEventListener('shopsense-auth-error', onAuthError);
    };
  }, [user, syncPageFromUrl, handleLogout, addToast]);

  const navigateTo = (pageId) => {
    setCurrentPage(pageId);
    window.location.hash = `#/${pageId.toLowerCase()}`;
  };

  const handleLoginSuccess = (userData) => {
    const u = { email: userData.email, name: userData.full_name, role: userData.role, vendor_id: userData.vendor_id };
    sessionStorage.removeItem('shopsense_session_expired_msg');
    setUser(u);
    const targetHome = u.role === 'CUSTOMER' ? 'Shop' : 'Dashboard';
    setCurrentPage(targetHome);
    window.location.hash = `#/${targetHome.toLowerCase()}`;
    addToast(`Welcome back, ${userData.full_name}! 🎉`);
  };

  const handleOrderSuccess = (data) => {
    setOrderData(data);
    setCurrentPage('OrderSuccess');
    addToast(`Order placed! ${data.items.length} item(s) confirmed. 🎉`);
  };

  const getNavItems = () => {
    if (!user) return [];
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
    <CartProvider userEmail={user?.email || null}>
      <Toast toasts={toasts} removeToast={removeToast} />
      {!user ? (
        <LoginPage onLoginSuccess={handleLoginSuccess} />
      ) : (
        <AppShell
          user={user}
          currentPage={currentPage}
          setCurrentPage={navigateTo}
          handleLogout={handleLogout}
          handleOrderSuccess={handleOrderSuccess}
          orderData={orderData}
          getNavItems={getNavItems}
          allowedPages={ROLE_ALLOWED_PAGES[user.role] || []}
        />
      )}
    </CartProvider>
  );
}

function AppShell({ user, currentPage, setCurrentPage, handleLogout, handleOrderSuccess, orderData, getNavItems, allowedPages }) {
  const { totalItems } = useCart();
  const navItems = getNavItems();
  const isPageAuthorized = allowedPages.includes(currentPage);
  const homeTarget = user.role === 'CUSTOMER' ? 'Shop' : 'Dashboard';

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
        {!isPageAuthorized ? (
          <ProtectedRoute user={user} onRedirectHome={() => setCurrentPage(homeTarget)} />
        ) : (
          <>
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
          </>
        )}
      </main>
    </div>
  );
}
