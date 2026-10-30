import React, { useState, useEffect } from 'react';
import { api } from '../api';
import { UserCheck, Plus, Search, ShieldAlert, CheckCircle, Ban, Trash2 } from 'lucide-react';

export default function VendorsPage({ user }) {
  const [vendors, setVendors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [search, setSearch] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('All');
  const [statusFilter, setStatusFilter] = useState('All');

  // Form states
  const [showAddForm, setShowAddForm] = useState(false);
  const [newVendor, setNewVendor] = useState({
    business_name: '',
    owner_name: '',
    email: '',
    phone: '',
    category: 'Electronics',
    commission_rate: 10.0,
  });

  // Action states
  const [selectedVendorId, setSelectedVendorId] = useState('');
  const [newStatus, setNewStatus] = useState('ACTIVE');
  const [newCommission, setNewCommission] = useState(10.0);

  useEffect(() => {
    loadVendors();
  }, [categoryFilter, statusFilter]);

  const loadVendors = async () => {
    setLoading(true);
    try {
      const data = await api.getVendors({
        search: search.trim(),
        category: categoryFilter,
        status: statusFilter,
      });
      setVendors(data || []);
      if (data && data.length > 0 && !selectedVendorId) {
        setSelectedVendorId(data[0].vendor_id);
        setNewStatus(data[0].status);
        setNewCommission(data[0].commission_rate);
      }
    } catch (err) {
      setError(err.message || 'Error loading vendors.');
    } finally {
      setLoading(false);
    }
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    loadVendors();
  };

  const handleCreateVendor = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    try {
      await api.createVendor({
        ...newVendor,
        commission_rate: Number(newVendor.commission_rate),
        status: 'ACTIVE'
      });
      setSuccess(`Vendor '${newVendor.business_name}' successfully onboarded!`);
      setShowAddForm(false);
      setNewVendor({
        business_name: '',
        owner_name: '',
        email: '',
        phone: '',
        category: 'Electronics',
        commission_rate: 10.0,
      });
      loadVendors();
    } catch (err) {
      const msg = err.message || '';
      if (msg.includes('409') || msg.includes('already registered')) {
        setError('⚠️ A vendor with that email is already registered. If they self-registered, you can find them below and change status to ACTIVE.');
      } else {
        setError(`Vendor onboarding error: ${msg}`);
      }
    }
  };

  const handleUpdateStatus = async () => {
    if (!selectedVendorId) return;
    setError('');
    setSuccess('');
    try {
      await api.updateVendor(selectedVendorId, { status: newStatus });
      setSuccess('Vendor status updated successfully!');
      loadVendors();
    } catch (err) {
      setError(err.message || 'Failed to update vendor status.');
    }
  };

  const handleUpdateCommission = async () => {
    if (!selectedVendorId) return;
    setError('');
    setSuccess('');
    try {
      await api.updateVendor(selectedVendorId, { commission_rate: Number(newCommission) });
      setSuccess('Commission rate updated!');
      loadVendors();
    } catch (err) {
      setError(err.message || 'Failed to update commission.');
    }
  };

  const handleDeleteVendor = async () => {
    if (!selectedVendorId) return;
    if (!window.confirm('Are you sure you want to delete this vendor? This will fail if they have sales history.')) return;
    setError('');
    setSuccess('');
    try {
      await api.deleteVendor(selectedVendorId);
      setSuccess('Vendor deleted successfully.');
      loadVendors();
    } catch (err) {
      setError(err.message || 'Failed to delete vendor. Vendors with sales history cannot be deleted.');
    }
  };

  return (
    <div>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 className="page-title">
            <span>🏢</span> Vendor Management & Onboarding
          </h1>
          <p className="page-subtitle">Oversee registered sellers, verify applications, and adjust commissions</p>
        </div>
        <button
          className="btn btn-primary"
          onClick={() => setShowAddForm(!showAddForm)}
        >
          <Plus size={16} />
          {showAddForm ? 'Close Form' : 'Onboard New Vendor'}
        </button>
      </div>

      {error && <div className="alert alert-error"><span>⚠️</span><span>{error}</span></div>}
      {success && <div className="alert alert-success"><span>✅</span><span>{success}</span></div>}

      {/* Onboard Form */}
      {showAddForm && (
        <div className="card" style={{ border: '1px solid #C7D2FE', marginBottom: '24px' }}>
          <div className="card-title" style={{ marginBottom: '18px' }}>
            <UserCheck size={18} color="#6366F1" />
            <span>Onboard New Vendor</span>
          </div>
          <form onSubmit={handleCreateVendor}>
            <div className="form-grid-3">
              <div>
                <label className="form-label">Business Name *</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="e.g. Aura Fashion Hub"
                  value={newVendor.business_name}
                  onChange={e => setNewVendor({ ...newVendor, business_name: e.target.value })}
                  required
                />
              </div>
              <div>
                <label className="form-label">Owner Name *</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="e.g. Sarah Miller"
                  value={newVendor.owner_name}
                  onChange={e => setNewVendor({ ...newVendor, owner_name: e.target.value })}
                  required
                />
              </div>
              <div>
                <label className="form-label">Vendor Email *</label>
                <input
                  type="email"
                  className="form-input"
                  placeholder="vendor@example.com"
                  value={newVendor.email}
                  onChange={e => setNewVendor({ ...newVendor, email: e.target.value })}
                  required
                />
              </div>
            </div>

            <div className="form-grid-3">
              <div>
                <label className="form-label">Phone Number *</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="10-15 digits"
                  value={newVendor.phone}
                  onChange={e => setNewVendor({ ...newVendor, phone: e.target.value })}
                  required
                />
              </div>
              <div>
                <label className="form-label">Category *</label>
                <select
                  className="form-select"
                  value={newVendor.category}
                  onChange={e => setNewVendor({ ...newVendor, category: e.target.value })}
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
              <div>
                <label className="form-label">Commission Rate (%)</label>
                <input
                  type="number"
                  step="0.5"
                  className="form-input"
                  value={newVendor.commission_rate}
                  onChange={e => setNewVendor({ ...newVendor, commission_rate: e.target.value })}
                  required
                />
              </div>
            </div>

            <button type="submit" className="btn btn-primary" style={{ marginTop: '12px' }}>
              Register & Activate Vendor
            </button>
          </form>
        </div>
      )}

      {/* Filters */}
      <div className="card" style={{ padding: '20px', marginBottom: '20px' }}>
        <form onSubmit={handleSearchSubmit} className="form-grid-3" style={{ margin: 0 }}>
          <div>
            <label className="form-label">Search vendors</label>
            <div style={{ display: 'flex', gap: '8px' }}>
              <input
                type="text"
                className="form-input"
                placeholder="Search by name, owner, email..."
                value={search}
                onChange={e => setSearch(e.target.value)}
              />
              <button type="submit" className="btn btn-secondary">
                <Search size={14} />
              </button>
            </div>
          </div>
          <div>
            <label className="form-label">Category Filter</label>
            <select
              className="form-select"
              value={categoryFilter}
              onChange={e => setCategoryFilter(e.target.value)}
            >
              <option value="All">All Categories</option>
              <option value="Electronics">Electronics</option>
              <option value="Fashion">Fashion</option>
              <option value="Books">Books</option>
              <option value="Home & Kitchen">Home & Kitchen</option>
              <option value="Beauty & Personal Care">Beauty & Personal Care</option>
              <option value="Sports & Fitness">Sports & Fitness</option>
            </select>
          </div>
          <div>
            <label className="form-label">Status Filter</label>
            <select
              className="form-select"
              value={statusFilter}
              onChange={e => setStatusFilter(e.target.value)}
            >
              <option value="All">All Statuses</option>
              <option value="ACTIVE">ACTIVE</option>
              <option value="PENDING">PENDING</option>
              <option value="SUSPENDED">SUSPENDED</option>
            </select>
          </div>
        </form>
      </div>

      {/* Vendors Table */}
      <div className="card" style={{ padding: '24px', marginBottom: '24px' }}>
        <div className="card-title" style={{ marginBottom: '16px' }}>
          <span>Registered Vendors ({vendors.length})</span>
        </div>
        <div className="table-responsive">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Business Name</th>
                <th>Owner Name</th>
                <th>Email</th>
                <th>Phone</th>
                <th>Category</th>
                <th>Commission</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {vendors.map(v => (
                <tr key={v.vendor_id} onClick={() => {
                  setSelectedVendorId(v.vendor_id);
                  setNewStatus(v.status);
                  setNewCommission(v.commission_rate);
                }} style={{ cursor: 'pointer' }}>
                  <td><strong>#{v.vendor_id}</strong></td>
                  <td style={{ fontWeight: '600', color: '#1E293B' }}>{v.business_name}</td>
                  <td style={{ color: '#1E293B' }}>{v.owner_name}</td>
                  <td style={{ color: '#64748B' }}>{v.email}</td>
                  <td style={{ color: '#64748B' }}>{v.phone}</td>
                  <td><span className="badge badge-info">{v.category}</span></td>
                  <td style={{ fontWeight: '600', color: '#1E293B' }}>{v.commission_rate}%</td>
                  <td>
                    <span className={`badge ${
                      v.status === 'ACTIVE' ? 'badge-success' :
                      v.status === 'PENDING' ? 'badge-warning' : 'badge-danger'
                    }`}>
                      {v.status}
                    </span>
                  </td>
                </tr>
              ))}
              {vendors.length === 0 && (
                <tr>
                  <td colSpan="8" style={{ textAlign: 'center', padding: '30px', color: '#64748B' }}>
                    No vendors found matching criteria.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Vendor Actions Box */}
      {vendors.length > 0 && (
        <div className="card" style={{ padding: '24px' }}>
          <div className="card-title" style={{ marginBottom: '16px' }}>
            <span>⚙️ Vendor Actions</span>
          </div>
          <div className="form-group">
            <label className="form-label">Select Vendor to Manage</label>
            <select
              className="form-select"
              value={selectedVendorId}
              onChange={e => {
                const id = Number(e.target.value);
                setSelectedVendorId(id);
                const found = vendors.find(v => v.vendor_id === id);
                if (found) {
                  setNewStatus(found.status);
                  setNewCommission(found.commission_rate);
                }
              }}
            >
              {vendors.map(v => (
                <option key={v.vendor_id} value={v.vendor_id}>
                  Vendor #{v.vendor_id} - {v.business_name} ({v.owner_name})
                </option>
              ))}
            </select>
          </div>

          <div className="form-grid-3" style={{ alignItems: 'flex-end' }}>
            <div>
              <label className="form-label">Change Status</label>
              <div style={{ display: 'flex', gap: '8px' }}>
                <select
                  className="form-select"
                  value={newStatus}
                  onChange={e => setNewStatus(e.target.value)}
                >
                  <option value="ACTIVE">ACTIVE</option>
                  <option value="PENDING">PENDING</option>
                  <option value="SUSPENDED">SUSPENDED</option>
                </select>
                <button type="button" className="btn btn-secondary" onClick={handleUpdateStatus}>
                  Update Status
                </button>
              </div>
            </div>

            <div>
              <label className="form-label">Update Commission (%)</label>
              <div style={{ display: 'flex', gap: '8px' }}>
                <input
                  type="number"
                  step="0.5"
                  className="form-input"
                  value={newCommission}
                  onChange={e => setNewCommission(e.target.value)}
                />
                <button type="button" className="btn btn-secondary" onClick={handleUpdateCommission}>
                  Save Commission
                </button>
              </div>
            </div>

            <div>
              <label className="form-label">Danger Zone</label>
              <button type="button" className="btn btn-danger" style={{ width: '100%' }} onClick={handleDeleteVendor}>
                <Trash2 size={16} /> Delete Vendor
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
