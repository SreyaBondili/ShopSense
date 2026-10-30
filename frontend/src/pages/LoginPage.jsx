import React, { useState } from 'react';
import { api } from '../api';
import { LogIn, UserPlus, CheckCircle, ShoppingBag, Store, ShieldCheck, AlertTriangle } from 'lucide-react';

export default function LoginPage({ onLoginSuccess }) {
  // Three separate login portals: 'customer', 'vendor', 'admin'
  const [activePortal, setActivePortal] = useState('customer');
  // 'login' or 'register' within the selected portal
  const [mode, setMode] = useState('login');

  // Input states strictly initialized to empty string
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [successMsg, setSuccessMsg] = useState('');
  const [loading, setLoading] = useState(false);

  const blankReg = {
    full_name: '', email: '', password: '',
    admin_secret: '', phone: '', business_name: '', category: 'Electronics'
  };
  const [regData, setRegData] = useState(blankReg);

  // Clear fields whenever switching portals or mode to ensure zero residual data
  const switchPortal = (portal) => {
    setActivePortal(portal);
    setMode('login');
    setError('');
    setSuccessMsg('');
    setEmail('');
    setPassword('');
    setRegData(blankReg);
  };

  const switchMode = (newMode) => {
    setMode(newMode);
    setError('');
    setSuccessMsg('');
    setEmail('');
    setPassword('');
    setRegData(blankReg);
  };

  // Login handler
  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setSuccessMsg('');
    setLoading(true);

    try {
      const user = await api.login(email.trim(), password);
      onLoginSuccess(user);
    } catch (err) {
      setError(err.message || 'Login failed. Please verify your credentials.');
    } finally {
      setLoading(false);
    }
  };

  // Register handler
  const handleRegister = async (e) => {
    e.preventDefault();
    setError('');
    setSuccessMsg('');
    setLoading(true);

    try {
      const targetRole = activePortal.toUpperCase();
      const payload = {
        full_name: regData.full_name,
        email: regData.email.trim(),
        password: regData.password,
        role: targetRole,
      };

      if (targetRole === 'ADMIN') {
        payload.admin_secret = regData.admin_secret;
      }
      if (targetRole === 'VENDOR') {
        payload.phone = regData.phone;
        payload.business_name = regData.business_name;
        payload.category = regData.category;
      }

      await api.register(payload);
      
      // Reset registration data completely
      setRegData(blankReg);
      setEmail('');
      setPassword('');
      setMode('login');
      setSuccessMsg(`✓ ${activePortal.charAt(0).toUpperCase() + activePortal.slice(1)} account created! Please sign in.`);
    } catch (err) {
      setError(err.message || 'Registration failed.');
    } finally {
      setLoading(false);
    }
  };

  // Portal-specific visual configurations (Soft Lavender theme compliant)
  const portalConfig = {
    customer: {
      title: 'Customer Login',
      badge: 'Shopper Portal',
      subtitle: 'Browse products, manage shopping cart, and track orders',
      icon: ShoppingBag,
      gradient: 'linear-gradient(135deg, #6366F1, #4F46E5)',
      accentColor: '#6366F1',
      bgHighlight: '#EEF2FF',
      activeTabBg: '#EEF2FF',
      activeColor: '#4F46E5',
      activeBorder: '#C7D2FE'
    },
    vendor: {
      title: 'Vendor Portal Login',
      badge: 'Merchant Center',
      subtitle: 'Manage catalog products, restock inventory, and view sales performance',
      icon: Store,
      gradient: 'linear-gradient(135deg, #D97706, #B45309)',
      accentColor: '#D97706',
      bgHighlight: '#FEF3C7',
      activeTabBg: '#FEF3C7',
      activeColor: '#B45309',
      activeBorder: '#FDE68A'
    },
    admin: {
      title: 'Admin Executive Login',
      badge: 'Platform Administration',
      subtitle: 'Marketplace analytics, vendor management, and ML forecasting algorithms',
      icon: ShieldCheck,
      gradient: 'linear-gradient(135deg, #6366F1, #8B5CF6)',
      accentColor: '#6366F1',
      bgHighlight: '#EDE9FE',
      activeTabBg: '#EDE9FE',
      activeColor: '#6D28D9',
      activeBorder: '#DDD6FE'
    }
  };

  const currentCfg = portalConfig[activePortal];
  const PortalIcon = currentCfg.icon;

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'radial-gradient(circle at 50% 15%, #EEF2FF 0%, #F8FAFC 75%)',
      padding: '24px 16px'
    }}>
      {/* Brand Header */}
      <div style={{ textAlign: 'center', marginBottom: '20px' }}>
        <div style={{
          width: '56px', height: '56px',
          background: 'linear-gradient(135deg, #6366F1, #4F46E5)',
          borderRadius: '16px',
          display: 'inline-flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '28px',
          marginBottom: '10px',
          boxShadow: '0 8px 20px rgba(99,102,241,0.25)'
        }}>🛍️</div>
        <h1 style={{ fontSize: '26px', fontWeight: '800', letterSpacing: '-0.5px', color: '#1E293B' }}>
          ShopSense
        </h1>
        <p style={{ color: '#64748B', fontSize: '13px', marginTop: '3px' }}>
          Multi-Vendor E-Commerce Analytics Platform
        </p>
      </div>

      {/* 1. THREE DEDICATED LOGIN PORTAL TABS */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(3, 1fr)',
        gap: '8px',
        maxWidth: '520px',
        width: '100%',
        background: '#FFFFFF',
        padding: '6px',
        borderRadius: '14px',
        border: '1px solid #E9EAF3',
        boxShadow: '0 2px 6px rgba(0,0,0,0.03)',
        marginBottom: '16px'
      }}>
        <button
          type="button"
          onClick={() => switchPortal('customer')}
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '8px',
            padding: '10px 12px',
            borderRadius: '10px',
            border: activePortal === 'customer' ? '1px solid #C7D2FE' : '1px solid transparent',
            background: activePortal === 'customer' ? '#EEF2FF' : 'transparent',
            color: activePortal === 'customer' ? '#4F46E5' : '#64748B',
            fontWeight: '700',
            fontSize: '13px',
            cursor: 'pointer',
            transition: 'all 0.2s ease'
          }}
        >
          <ShoppingBag size={15} />
          <span>Customer</span>
        </button>

        <button
          type="button"
          onClick={() => switchPortal('vendor')}
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '8px',
            padding: '10px 12px',
            borderRadius: '10px',
            border: activePortal === 'vendor' ? '1px solid #FDE68A' : '1px solid transparent',
            background: activePortal === 'vendor' ? '#FEF3C7' : 'transparent',
            color: activePortal === 'vendor' ? '#B45309' : '#64748B',
            fontWeight: '700',
            fontSize: '13px',
            cursor: 'pointer',
            transition: 'all 0.2s ease'
          }}
        >
          <Store size={15} />
          <span>Vendor</span>
        </button>

        <button
          type="button"
          onClick={() => switchPortal('admin')}
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '8px',
            padding: '10px 12px',
            borderRadius: '10px',
            border: activePortal === 'admin' ? '1px solid #DDD6FE' : '1px solid transparent',
            background: activePortal === 'admin' ? '#EDE9FE' : 'transparent',
            color: activePortal === 'admin' ? '#6D28D9' : '#64748B',
            fontWeight: '700',
            fontSize: '13px',
            cursor: 'pointer',
            transition: 'all 0.2s ease'
          }}
        >
          <ShieldCheck size={15} />
          <span>Admin</span>
        </button>
      </div>

      {/* Main Authentication Card */}
      <div style={{
        width: '100%',
        maxWidth: '520px',
        background: '#FFFFFF',
        borderRadius: '18px',
        border: '1px solid #E9EAF3',
        padding: '32px',
        boxShadow: '0 20px 45px -10px rgba(99, 102, 241, 0.12)',
        position: 'relative',
        overflow: 'hidden'
      }}>
        {/* Portal Header */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px', marginBottom: '20px' }}>
          <div style={{
            width: '44px', height: '44px',
            borderRadius: '12px',
            background: currentCfg.gradient,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#FFFFFF',
            boxShadow: '0 4px 12px rgba(99,102,241,0.2)'
          }}>
            <PortalIcon size={20} />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <h2 style={{ fontSize: '19px', fontWeight: '800', color: '#1E293B', margin: 0 }}>
                {mode === 'login' ? currentCfg.title : `Register as ${activePortal.charAt(0).toUpperCase() + activePortal.slice(1)}`}
              </h2>
              <span style={{
                fontSize: '11px',
                fontWeight: '700',
                padding: '2px 8px',
                borderRadius: '12px',
                background: currentCfg.bgHighlight,
                color: currentCfg.activeColor,
                border: `1px solid ${currentCfg.activeBorder}`
              }}>
                {currentCfg.badge}
              </span>
            </div>
            <p style={{ color: '#64748B', fontSize: '12px', margin: '3px 0 0 0' }}>
              {currentCfg.subtitle}
            </p>
          </div>
        </div>

        {/* Mode Switcher (Sign In vs Create Account) */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          background: '#F1F5F9',
          padding: '4px',
          borderRadius: '10px',
          marginBottom: '20px'
        }}>
          <button
            type="button"
            onClick={() => switchMode('login')}
            style={{
              padding: '8px',
              borderRadius: '7px',
              border: 'none',
              background: mode === 'login' ? '#FFFFFF' : 'transparent',
              color: mode === 'login' ? '#1E293B' : '#64748B',
              boxShadow: mode === 'login' ? '0 1px 3px rgba(0,0,0,0.08)' : 'none',
              fontWeight: '700',
              fontSize: '13px',
              cursor: 'pointer',
              transition: 'all 0.2s ease'
            }}
          >
            🔐 Sign In
          </button>
          <button
            type="button"
            onClick={() => switchMode('register')}
            style={{
              padding: '8px',
              borderRadius: '7px',
              border: 'none',
              background: mode === 'register' ? '#FFFFFF' : 'transparent',
              color: mode === 'register' ? '#1E293B' : '#64748B',
              boxShadow: mode === 'register' ? '0 1px 3px rgba(0,0,0,0.08)' : 'none',
              fontWeight: '700',
              fontSize: '13px',
              cursor: 'pointer',
              transition: 'all 0.2s ease'
            }}
          >
            📝 Create {activePortal.charAt(0).toUpperCase() + activePortal.slice(1)} Account
          </button>
        </div>

        {/* In-App Feedback Messages */}
        {successMsg && (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            background: '#ECFDF5',
            border: '1px solid #A7F3D0',
            borderRadius: '8px',
            padding: '10px 14px',
            marginBottom: '16px',
            color: '#059669',
            fontSize: '13px'
          }}>
            <CheckCircle size={16} style={{ flexShrink: 0 }} />
            <span>{successMsg}</span>
          </div>
        )}

        {error && (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            background: '#FEF2F2',
            border: '1px solid #FECACA',
            borderRadius: '8px',
            padding: '10px 14px',
            marginBottom: '16px',
            color: '#DC2626',
            fontSize: '13px'
          }}>
            <AlertTriangle size={16} style={{ flexShrink: 0 }} />
            <span>{error}</span>
          </div>
        )}

        {/* LOGIN FORM */}
        {mode === 'login' && (
          <form onSubmit={handleLogin} autoComplete="off">
            {/* Hidden dummy inputs to capture aggressive browser autofill */}
            <input type="text" style={{ position: 'absolute', opacity: 0, height: 0, width: 0, pointerEvents: 'none' }} tabIndex="-1" readOnly />
            <input type="password" style={{ position: 'absolute', opacity: 0, height: 0, width: 0, pointerEvents: 'none' }} tabIndex="-1" readOnly />

            <div className="form-group">
              <label className="form-label" style={{ fontSize: '13px', fontWeight: '600', color: '#1E293B' }}>
                {activePortal === 'vendor' ? 'Store Email Address' : activePortal === 'admin' ? 'Admin Email Address' : 'Email Address'}
              </label>
              <input
                type="email"
                name={`ss_auth_${activePortal}_email`}
                className="form-input"
                placeholder="Enter your email address"
                value={email}
                onChange={e => setEmail(e.target.value)}
                autoComplete="new-password"
                readOnly
                onFocus={(e) => e.target.removeAttribute('readonly')}
                required
              />
            </div>

            <div className="form-group" style={{ marginBottom: '24px' }}>
              <label className="form-label" style={{ fontSize: '13px', fontWeight: '600', color: '#1E293B' }}>
                Password
              </label>
              <input
                type="password"
                name={`ss_auth_${activePortal}_pass`}
                className="form-input"
                placeholder="Enter your password"
                value={password}
                onChange={e => setPassword(e.target.value)}
                autoComplete="new-password"
                readOnly
                onFocus={(e) => e.target.removeAttribute('readonly')}
                required
              />
            </div>

            <button
              type="submit"
              className="btn btn-primary"
              style={{
                width: '100%',
                padding: '12px',
                background: currentCfg.gradient,
                boxShadow: `0 4px 14px ${currentCfg.accentColor}30`,
                fontSize: '14px',
                fontWeight: '700'
              }}
              disabled={loading}
            >
              <LogIn size={16} />
              {loading ? 'Authenticating...' : `Sign In to ${activePortal.charAt(0).toUpperCase() + activePortal.slice(1)} Portal`}
            </button>
          </form>
        )}

        {/* REGISTRATION FORM */}
        {mode === 'register' && (
          <form onSubmit={handleRegister} autoComplete="off">
            {/* Hidden dummy inputs to absorb browser autofill */}
            <input type="text" style={{ position: 'absolute', opacity: 0, height: 0, width: 0, pointerEvents: 'none' }} tabIndex="-1" readOnly />
            <input type="password" style={{ position: 'absolute', opacity: 0, height: 0, width: 0, pointerEvents: 'none' }} tabIndex="-1" readOnly />

            <div className="form-group">
              <label className="form-label">Full Name</label>
              <input
                type="text"
                name="reg_fullname_field"
                className="form-input"
                placeholder="Enter your full name"
                value={regData.full_name}
                onChange={e => setRegData({ ...regData, full_name: e.target.value })}
                autoComplete="new-password"
                readOnly
                onFocus={(e) => e.target.removeAttribute('readonly')}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">Email Address</label>
              <input
                type="email"
                name="reg_email_field"
                className="form-input"
                placeholder="Enter your email address"
                value={regData.email}
                onChange={e => setRegData({ ...regData, email: e.target.value })}
                autoComplete="new-password"
                readOnly
                onFocus={(e) => e.target.removeAttribute('readonly')}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">Password</label>
              <input
                type="password"
                name="reg_password_field"
                className="form-input"
                placeholder="Create a password (min. 6 characters)"
                value={regData.password}
                onChange={e => setRegData({ ...regData, password: e.target.value })}
                autoComplete="new-password"
                readOnly
                onFocus={(e) => e.target.removeAttribute('readonly')}
                required
              />
            </div>

            {/* Admin Specific Passcode */}
            {activePortal === 'admin' && (
              <div className="form-group">
                <label className="form-label">Admin Security Passcode</label>
                <input
                  type="password"
                  name="reg_admin_secret_field"
                  className="form-input"
                  placeholder="Enter administrator passcode"
                  value={regData.admin_secret}
                  onChange={e => setRegData({ ...regData, admin_secret: e.target.value })}
                  autoComplete="new-password"
                  readOnly
                  onFocus={(e) => e.target.removeAttribute('readonly')}
                  required
                />
              </div>
            )}

            {/* Vendor Specific Details */}
            {activePortal === 'vendor' && (
              <>
                <div className="form-group">
                  <label className="form-label">Business / Store Name</label>
                  <input
                    type="text"
                    name="reg_business_name_field"
                    className="form-input"
                    placeholder="e.g. Apex Electronics"
                    value={regData.business_name}
                    onChange={e => setRegData({ ...regData, business_name: e.target.value })}
                    autoComplete="new-password"
                    readOnly
                    onFocus={(e) => e.target.removeAttribute('readonly')}
                    required
                  />
                </div>
                <div className="form-grid-2">
                  <div>
                    <label className="form-label">Phone Number</label>
                    <input
                      type="text"
                      name="reg_phone_field"
                      className="form-input"
                      placeholder="10-15 digits"
                      value={regData.phone}
                      onChange={e => setRegData({ ...regData, phone: e.target.value })}
                      autoComplete="new-password"
                      readOnly
                      onFocus={(e) => e.target.removeAttribute('readonly')}
                      required
                    />
                  </div>
                  <div>
                    <label className="form-label">Store Category</label>
                    <select
                      className="form-select"
                      value={regData.category}
                      onChange={e => setRegData({ ...regData, category: e.target.value })}
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
                </div>
              </>
            )}

            <button
              type="submit"
              className="btn btn-primary"
              style={{
                width: '100%',
                padding: '12px',
                marginTop: '10px',
                background: currentCfg.gradient,
                fontSize: '14px',
                fontWeight: '700'
              }}
              disabled={loading}
            >
              <UserPlus size={16} />
              {loading ? 'Registering...' : `Complete ${activePortal.charAt(0).toUpperCase() + activePortal.slice(1)} Registration`}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
