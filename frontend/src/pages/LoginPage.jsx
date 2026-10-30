import React, { useState } from 'react';
import { api } from '../api';
import {
  ShieldCheck, Store, User, Mail, Lock, Eye, EyeOff,
  ArrowRight, CheckCircle, AlertTriangle
} from 'lucide-react';

export default function LoginPage({ onLoginSuccess }) {
  // Three portal roles in the requested format: 'admin', 'vendor', 'customer'
  const [activePortal, setActivePortal] = useState('admin');
  const [mode, setMode] = useState('login'); // 'login' or 'register'

  // Form input states
  const [email, setEmail] = useState('bsreya1610@gmail.com');
  const [password, setPassword] = useState('Admin@123');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [successMsg, setSuccessMsg] = useState('');
  const [loading, setLoading] = useState(false);

  // Registration data
  const blankReg = {
    full_name: '', email: '', password: '',
    admin_secret: '', phone: '', business_name: '', category: 'Electronics'
  };
  const [regData, setRegData] = useState(blankReg);

  // Switch between Admin, Vendor, Customer tabs in purple theme
  const handlePortalSwitch = (portal) => {
    setActivePortal(portal);
    setError('');
    setSuccessMsg('');
    if (portal === 'admin') {
      setEmail('bsreya1610@gmail.com');
      setPassword('Admin@123');
    } else {
      setEmail('');
      setPassword('');
    }
  };

  const executeLogin = async (loginEmail, loginPass) => {
    setError('');
    setSuccessMsg('');
    setLoading(true);
    try {
      const user = await api.login(loginEmail.trim(), loginPass);
      onLoginSuccess(user);
    } catch (err) {
      setError(err.message || 'Login failed. Please check credentials.');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (mode === 'login') {
      executeLogin(email, password);
    } else {
      handleRegister();
    }
  };

  const handleOneClickAccess = () => {
    if (activePortal === 'admin') {
      executeLogin('bsreya1610@gmail.com', 'Admin@123');
    }
  };

  const handleRegister = async () => {
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
      if (targetRole === 'ADMIN') payload.admin_secret = regData.admin_secret;
      if (targetRole === 'VENDOR') {
        payload.phone = regData.phone;
        payload.business_name = regData.business_name;
        payload.category = regData.category;
      }
      await api.register(payload);
      setRegData(blankReg);
      setMode('login');
      setSuccessMsg(`✓ Account created! Please sign in with your credentials.`);
    } catch (err) {
      setError(err.message || 'Registration failed.');
    } finally {
      setLoading(false);
    }
  };

  // Portal metadata in Soft Lavender & Purple palette
  const portalInfo = {
    admin: {
      roleLabel: 'Admin',
      emailLabel: 'ADMIN EMAIL ADDRESS',
      placeholderEmail: 'admin@shopsense.com',
      icon: ShieldCheck,
    },
    vendor: {
      roleLabel: 'Vendor',
      emailLabel: 'VENDOR EMAIL ADDRESS',
      placeholderEmail: 'vendor@shopsense.com',
      icon: Store,
    },
    customer: {
      roleLabel: 'Customer',
      emailLabel: 'CUSTOMER EMAIL ADDRESS',
      placeholderEmail: 'customer@shopsense.com',
      icon: User,
    }
  };

  const currentPortal = portalInfo[activePortal];

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'radial-gradient(circle at 50% 15%, #EEF2FF 0%, #F8FAFC 75%)',
      padding: '24px 16px',
      fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
    }}>
      {/* Centered White Card Container */}
      <div style={{
        width: '100%',
        maxWidth: '460px',
        background: '#FFFFFF',
        borderRadius: '24px',
        boxShadow: '0 20px 45px -10px rgba(99, 102, 241, 0.14)',
        border: '1px solid #E9EAF3',
        padding: '36px 36px 32px 36px',
        boxSizing: 'border-box'
      }}>
        {/* Brand Header with Purple Gradient Icon */}
        <div style={{ textAlign: 'center', marginBottom: '22px' }}>
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '8px',
            marginBottom: '6px'
          }}>
            <div style={{
              width: '42px',
              height: '42px',
              borderRadius: '12px',
              background: 'linear-gradient(135deg, #6366F1, #4F46E5)',
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 4px 14px rgba(99, 102, 241, 0.3)',
              color: '#FFFFFF'
            }}>
              <Store size={22} />
            </div>
            <h1 style={{
              fontSize: '26px',
              fontWeight: '800',
              letterSpacing: '-0.5px',
              color: '#1E293B',
              margin: 0
            }}>
              ShopSense
            </h1>
          </div>
          <p style={{
            color: '#6366F1',
            fontSize: '12.5px',
            fontWeight: '600',
            margin: 0,
            letterSpacing: '0.2px'
          }}>
            Multi-Vendor E-Commerce Analytics Platform
          </p>
        </div>

        {/* 3 Portal Role Selection Tabs (Format from user reference, in Purple Palette) */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr 1fr',
          gap: '6px',
          background: '#F1F5F9',
          padding: '4px',
          borderRadius: '14px',
          marginBottom: '16px'
        }}>
          {[
            { id: 'admin', label: 'Admin', icon: ShieldCheck },
            { id: 'vendor', label: 'Vendor', icon: Store },
            { id: 'customer', label: 'Customer', icon: User },
          ].map(tab => {
            const Icon = tab.icon;
            const isActive = activePortal === tab.id;
            return (
              <button
                key={tab.id}
                type="button"
                onClick={() => handlePortalSwitch(tab.id)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '6px',
                  padding: '9px 10px',
                  borderRadius: '10px',
                  border: 'none',
                  background: isActive ? '#6366F1' : 'transparent',
                  color: isActive ? '#FFFFFF' : '#64748B',
                  fontWeight: isActive ? '700' : '600',
                  fontSize: '13px',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                  boxShadow: isActive ? '0 2px 8px rgba(99, 102, 241, 0.3)' : 'none'
                }}
              >
                <Icon size={15} color={isActive ? '#FFFFFF' : '#6366F1'} />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>



        {/* Feedback Messages */}
        {successMsg && (
          <div style={{
            display: 'flex', alignItems: 'center', gap: '8px',
            background: 'rgba(5, 150, 105, 0.1)', border: '1px solid rgba(5, 150, 105, 0.3)',
            borderRadius: '10px', padding: '10px 12px', marginBottom: '16px',
            color: '#059669', fontSize: '13px', fontWeight: '500'
          }}>
            <CheckCircle size={16} style={{ flexShrink: 0 }} />
            <span>{successMsg}</span>
          </div>
        )}

        {error && (
          <div style={{
            display: 'flex', alignItems: 'center', gap: '8px',
            background: 'rgba(220, 38, 38, 0.08)', border: '1px solid rgba(220, 38, 38, 0.25)',
            borderRadius: '10px', padding: '10px 12px', marginBottom: '16px',
            color: '#DC2626', fontSize: '13px', fontWeight: '500'
          }}>
            <AlertTriangle size={16} style={{ flexShrink: 0 }} />
            <span>{error}</span>
          </div>
        )}

        {/* LOGIN FORM */}
        {mode === 'login' && (
          <form onSubmit={handleSubmit}>
            {/* EMAIL INPUT */}
            <div style={{ marginBottom: '16px' }}>
              <label style={{
                display: 'block',
                fontSize: '11px',
                fontWeight: '700',
                color: '#4F46E5',
                marginBottom: '6px',
                letterSpacing: '0.5px'
              }}>
                {currentPortal.emailLabel}
              </label>
              <div style={{ position: 'relative' }}>
                <Mail
                  size={16}
                  color="#6366F1"
                  style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)' }}
                />
                <input
                  type="email"
                  className="form-input"
                  placeholder={currentPortal.placeholderEmail}
                  value={email}
                  onChange={e => setEmail(e.target.value)}
                  required
                  style={{
                    width: '100%',
                    padding: '11px 12px 11px 36px',
                    borderRadius: '10px',
                    border: '1px solid #CBD5E1',
                    fontSize: '13.5px',
                    color: '#1E293B',
                    boxSizing: 'border-box'
                  }}
                />
              </div>
            </div>

            {/* PASSWORD INPUT */}
            <div style={{ marginBottom: '20px' }}>
              <label style={{
                display: 'block',
                fontSize: '11px',
                fontWeight: '700',
                color: '#4F46E5',
                marginBottom: '6px',
                letterSpacing: '0.5px'
              }}>
                PASSWORD
              </label>
              <div style={{ position: 'relative' }}>
                <Lock
                  size={16}
                  color="#6366F1"
                  style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)' }}
                />
                <input
                  type={showPassword ? 'text' : 'password'}
                  className="form-input"
                  placeholder="Enter your password"
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  required
                  style={{
                    width: '100%',
                    padding: '11px 36px 11px 36px',
                    borderRadius: '10px',
                    border: '1px solid #CBD5E1',
                    fontSize: '13.5px',
                    color: '#1E293B',
                    boxSizing: 'border-box'
                  }}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  style={{
                    position: 'absolute',
                    right: '12px',
                    top: '50%',
                    transform: 'translateY(-50%)',
                    background: 'none',
                    border: 'none',
                    color: '#94A3B8',
                    cursor: 'pointer',
                    padding: 0
                  }}
                >
                  {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            {/* MAIN ACTION BUTTON: Purple Gradient with Arrow */}
            <button
              type="submit"
              disabled={loading}
              style={{
                width: '100%',
                padding: '13px 20px',
                borderRadius: '10px',
                border: 'none',
                background: 'linear-gradient(135deg, #6366F1 0%, #4F46E5 100%)',
                color: '#FFFFFF',
                fontSize: '14.5px',
                fontWeight: '700',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                boxShadow: '0 4px 14px rgba(99, 102, 241, 0.35)',
                transition: 'all 0.2s ease',
                marginBottom: '12px'
              }}
            >
              <span>{loading ? 'Authenticating...' : `Sign In as ${currentPortal.roleLabel}`}</span>
              <ArrowRight size={16} />
            </button>

            {/* 1-CLICK QUICK ACCESS BUTTON (Soft Lavender Card) - ADMIN ONLY */}
            {activePortal === 'admin' && (
              <button
                type="button"
                onClick={handleOneClickAccess}
                disabled={loading}
                style={{
                  width: '100%',
                  padding: '11px 16px',
                  borderRadius: '10px',
                  border: '1px solid #C7D2FE',
                  background: '#FFFFFF',
                  color: '#4F46E5',
                  fontSize: '13px',
                  fontWeight: '600',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '8px',
                  transition: 'all 0.2s ease'
                }}
                onMouseEnter={e => {
                  e.currentTarget.style.background = '#EEF2FF';
                  e.currentTarget.style.borderColor = '#6366F1';
                }}
                onMouseLeave={e => {
                  e.currentTarget.style.background = '#FFFFFF';
                  e.currentTarget.style.borderColor = '#C7D2FE';
                }}
              >
                <ShieldCheck size={15} color="#6366F1" />
                <span>1-Click Admin Access</span>
              </button>
            )}
          </form>
        )}

        {/* REGISTER FORM */}
        {mode === 'register' && (
          <form onSubmit={handleSubmit}>
            <div style={{ marginBottom: '14px' }}>
              <label className="form-label">Full Name *</label>
              <input
                type="text"
                className="form-input"
                placeholder="Enter your full name"
                value={regData.full_name}
                onChange={e => setRegData({ ...regData, full_name: e.target.value })}
                required
                style={{ width: '100%', padding: '10px 12px', borderRadius: '10px', border: '1px solid #CBD5E1' }}
              />
            </div>

            <div style={{ marginBottom: '14px' }}>
              <label className="form-label">Email Address *</label>
              <input
                type="email"
                className="form-input"
                placeholder="Enter email address"
                value={regData.email}
                onChange={e => setRegData({ ...regData, email: e.target.value })}
                required
                style={{ width: '100%', padding: '10px 12px', borderRadius: '10px', border: '1px solid #CBD5E1' }}
              />
            </div>

            <div style={{ marginBottom: '14px' }}>
              <label className="form-label">Password *</label>
              <input
                type="password"
                className="form-input"
                placeholder="Create password (min 6 characters)"
                value={regData.password}
                onChange={e => setRegData({ ...regData, password: e.target.value })}
                required
                style={{ width: '100%', padding: '10px 12px', borderRadius: '10px', border: '1px solid #CBD5E1' }}
              />
            </div>

            {activePortal === 'admin' && (
              <div style={{ marginBottom: '14px' }}>
                <label className="form-label">Admin Passcode *</label>
                <input
                  type="password"
                  className="form-input"
                  placeholder="Enter admin passcode"
                  value={regData.admin_secret}
                  onChange={e => setRegData({ ...regData, admin_secret: e.target.value })}
                  required
                  style={{ width: '100%', padding: '10px 12px', borderRadius: '10px', border: '1px solid #CBD5E1' }}
                />
              </div>
            )}

            {activePortal === 'vendor' && (
              <>
                <div style={{ marginBottom: '14px' }}>
                  <label className="form-label">Store / Business Name *</label>
                  <input
                    type="text"
                    className="form-input"
                    placeholder="e.g. Janani Boutique"
                    value={regData.business_name}
                    onChange={e => setRegData({ ...regData, business_name: e.target.value })}
                    required
                    style={{ width: '100%', padding: '10px 12px', borderRadius: '10px', border: '1px solid #CBD5E1' }}
                  />
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', marginBottom: '14px' }}>
                  <div>
                    <label className="form-label">Phone *</label>
                    <input
                      type="text"
                      className="form-input"
                      placeholder="Phone number"
                      value={regData.phone}
                      onChange={e => setRegData({ ...regData, phone: e.target.value })}
                      required
                      style={{ width: '100%', padding: '10px 12px', borderRadius: '10px', border: '1px solid #CBD5E1' }}
                    />
                  </div>
                  <div>
                    <label className="form-label">Category *</label>
                    <select
                      className="form-select"
                      value={regData.category}
                      onChange={e => setRegData({ ...regData, category: e.target.value })}
                      style={{ width: '100%', padding: '10px 12px', borderRadius: '10px', border: '1px solid #CBD5E1' }}
                    >
                      <option value="Electronics">Electronics</option>
                      <option value="Fashion">Fashion</option>
                      <option value="Books">Books</option>
                      <option value="Home & Kitchen">Home & Kitchen</option>
                      <option value="Beauty & Personal Care">Beauty & Personal Care</option>
                      <option value="Sports & Fitness">Sports & Fitness</option>
                    </select>
                  </div>
                </div>
              </>
            )}

            <button
              type="submit"
              disabled={loading}
              style={{
                width: '100%',
                padding: '13px 20px',
                borderRadius: '10px',
                border: 'none',
                background: 'linear-gradient(135deg, #6366F1 0%, #4F46E5 100%)',
                color: '#FFFFFF',
                fontSize: '14px',
                fontWeight: '700',
                cursor: 'pointer',
                marginBottom: '12px',
                boxShadow: '0 4px 14px rgba(99, 102, 241, 0.35)'
              }}
            >
              {loading ? 'Registering...' : `Register as ${currentPortal.roleLabel}`}
            </button>
          </form>
        )}

        {/* Toggle between Login and Register Mode */}
        <div style={{
          textAlign: 'center',
          marginTop: '18px',
          paddingTop: '16px',
          borderTop: '1px solid #F1F5F9',
          fontSize: '12.5px',
          color: '#64748B'
        }}>
          {mode === 'login' ? (
            <span>
              Don't have an account?{' '}
              <button
                type="button"
                onClick={() => { setMode('register'); setError(''); setSuccessMsg(''); }}
                style={{
                  background: 'none',
                  border: 'none',
                  color: '#6366F1',
                  fontWeight: '700',
                  cursor: 'pointer',
                  padding: 0
                }}
              >
                Register Here
              </button>
            </span>
          ) : (
            <span>
              Already registered?{' '}
              <button
                type="button"
                onClick={() => { setMode('login'); setError(''); setSuccessMsg(''); }}
                style={{
                  background: 'none',
                  border: 'none',
                  color: '#6366F1',
                  fontWeight: '700',
                  cursor: 'pointer',
                  padding: 0
                }}
              >
                Back to Sign In
              </button>
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
