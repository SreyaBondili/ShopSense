import React, { useEffect } from 'react';
import { CheckCircle, XCircle, X } from 'lucide-react';

export default function Toast({ toasts, removeToast }) {
  return (
    <div style={{
      position: 'fixed', top: '20px', right: '20px', zIndex: 9999,
      display: 'flex', flexDirection: 'column', gap: '10px', maxWidth: '380px'
    }}>
      {toasts.map(t => (
        <ToastItem key={t.id} toast={t} onRemove={() => removeToast(t.id)} />
      ))}
    </div>
  );
}

function ToastItem({ toast, onRemove }) {
  useEffect(() => {
    const timer = setTimeout(onRemove, 4000);
    return () => clearTimeout(timer);
  }, []);

  const isSuccess = toast.type === 'success';
  return (
    <div style={{
      display: 'flex', alignItems: 'flex-start', gap: '10px',
      background: isSuccess ? 'rgba(16,185,129,0.12)' : 'rgba(239,68,68,0.12)',
      border: `1px solid ${isSuccess ? 'rgba(16,185,129,0.5)' : 'rgba(239,68,68,0.5)'}`,
      borderRadius: '10px', padding: '12px 16px',
      color: isSuccess ? '#34d399' : '#f87171',
      fontSize: '14px', lineHeight: '1.4',
      boxShadow: '0 4px 20px rgba(0,0,0,0.4)',
      animation: 'slideIn 0.2s ease'
    }}>
      {isSuccess ? <CheckCircle size={18} style={{ flexShrink: 0, marginTop: '1px' }} /> : <XCircle size={18} style={{ flexShrink: 0, marginTop: '1px' }} />}
      <span style={{ flex: 1 }}>{toast.message}</span>
      <button onClick={onRemove} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'inherit', padding: '0', lineHeight: 1 }}>
        <X size={14} />
      </button>
    </div>
  );
}
