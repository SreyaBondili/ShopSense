import React from 'react';
import { ShieldAlert, ArrowLeft } from 'lucide-react';

export default function ProtectedRoute({ user, onRedirectHome }) {
  const homeLabel = user?.role === 'CUSTOMER' ? 'Customer Store' : 'Dashboard';

  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: '60vh',
      padding: '2rem'
    }}>
      <div style={{
        background: '#ffffff',
        border: '1px solid #fee2e2',
        borderRadius: '16px',
        padding: '2.5rem',
        maxWidth: '520px',
        width: '100%',
        textAlign: 'center',
        boxShadow: '0 10px 25px -5px rgba(239, 68, 68, 0.1)'
      }}>
        <div style={{
          width: '64px',
          height: '64px',
          background: '#fef2f2',
          borderRadius: '50%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          margin: '0 auto 1.5rem',
          color: '#ef4444'
        }}>
          <ShieldAlert size={36} />
        </div>

        <h2 style={{
          fontSize: '1.5rem',
          fontWeight: '700',
          color: '#1f2937',
          marginBottom: '0.75rem'
        }}>
          Access Restricted
        </h2>

        <p style={{
          color: '#6b7280',
          fontSize: '0.95rem',
          lineHeight: '1.5',
          marginBottom: '1.75rem'
        }}>
          You don't have access to this page. Your role (<strong>{user?.role || 'Guest'}</strong>) is not authorized to view or manage these resources.
        </p>

        <button
          onClick={onRedirectHome}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.5rem',
            background: '#7c3aed',
            color: '#ffffff',
            padding: '0.75rem 1.5rem',
            borderRadius: '10px',
            fontWeight: '600',
            fontSize: '0.95rem',
            border: 'none',
            cursor: 'pointer',
            transition: 'background 0.2s ease'
          }}
          onMouseEnter={e => e.currentTarget.style.background = '#6d28d9'}
          onMouseLeave={e => e.currentTarget.style.background = '#7c3aed'}
        >
          <ArrowLeft size={18} />
          <span>Return to {homeLabel}</span>
        </button>
      </div>
    </div>
  );
}
