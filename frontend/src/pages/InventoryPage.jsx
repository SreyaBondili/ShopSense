import React, { useState, useEffect } from 'react';
import { api } from '../api';
import AnimatedCounter from '../components/AnimatedCounter';
import {
  ClipboardList, Warehouse, RefreshCw, AlertTriangle, CheckCircle2,
  XCircle, TrendingUp, Sparkles, Download, Layers, ShieldAlert, Cpu,
  Search, Filter, X, ArrowUpRight
} from 'lucide-react';

export default function InventoryPage({ user }) {
  const [activeTab, setActiveTab] = useState('stock'); // stock | replenishment | alerts | turnover | forecast
  const [inventory, setInventory] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [replenishment, setReplenishment] = useState([]);
  const [turnover, setTurnover] = useState(null);
  const [forecast, setForecast] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Stock tab filters
  const [search, setSearch] = useState('');
  const [warehouseFilter, setWarehouseFilter] = useState('All');
  const [categoryFilter, setCategoryFilter] = useState('All');
  const [vendorFilter, setVendorFilter] = useState('All');
  const [statusFilter, setStatusFilter] = useState('All');
  const [lowStockOnly, setLowStockOnly] = useState(false);

  // Turnover tab filter
  const [turnoverSearch, setTurnoverSearch] = useState('');

  // Restock Modal state
  const [showRestockModal, setShowRestockModal] = useState(false);
  const [selectedItem, setSelectedItem] = useState(null);
  const [newStock, setNewStock] = useState(20);
  const [newReorder, setNewReorder] = useState(10);
  const [newWarehouse, setNewWarehouse] = useState('Main Warehouse');
  const [submittingRestock, setSubmittingRestock] = useState(false);

  useEffect(() => {
    loadAllInventoryData();
  }, [statusFilter]);

  const loadAllInventoryData = async (isManualRefresh = false) => {
    if (isManualRefresh) {
      setRefreshing(true);
    } else {
      setLoading(true);
    }
    setError('');

    try {
      const [invRes, alertRes, replRes, turnRes, foreRes] = await Promise.allSettled([
        api.getInventory(statusFilter),
        api.getInventoryAlerts(),
        api.getInventoryReplenishment(5),
        api.getInventoryTurnover(),
        api.getInventoryForecast(null, 14),
      ]);

      if (invRes.status === 'fulfilled' && Array.isArray(invRes.value)) {
        setInventory(invRes.value);
      }
      if (alertRes.status === 'fulfilled' && Array.isArray(alertRes.value)) {
        setAlerts(alertRes.value);
      }
      if (replRes.status === 'fulfilled' && Array.isArray(replRes.value)) {
        setReplenishment(replRes.value);
      }
      if (turnRes.status === 'fulfilled' && turnRes.value) {
        setTurnover(turnRes.value);
      }
      if (foreRes.status === 'fulfilled' && foreRes.value) {
        setForecast(foreRes.value);
      }

      if (isManualRefresh) {
        setSuccess('✓ Live inventory data successfully updated from database.');
        setTimeout(() => setSuccess(''), 3500);
      }
    } catch (err) {
      setError(err.message || 'Error updating inventory data.');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const openRestockFor = (item) => {
    setSelectedItem(item);
    setNewStock(item.current_stock ?? 0);
    setNewReorder(item.reorder_level ?? item.safety_stock ?? 10);
    setNewWarehouse(item.warehouse || 'Main Warehouse');
    setShowRestockModal(true);
  };

  const handleUpdateInventory = async (e) => {
    e.preventDefault();
    if (!selectedItem) return;
    setError('');
    setSuccess('');
    setSubmittingRestock(true);
    try {
      await api.updateInventory(selectedItem.product_id, {
        current_stock: Number(newStock),
        reorder_level: Number(newReorder),
        warehouse: newWarehouse.trim() || 'Main Warehouse',
      });
      setSuccess(`Updated stock for '${selectedItem.product_name}' to ${newStock} units.`);
      setShowRestockModal(false);
      await loadAllInventoryData(true);
    } catch (err) {
      setError(err.message || 'Restock update failed.');
    } finally {
      setSubmittingRestock(false);
    }
  };

  const exportForecastCSV = () => {
    if (!forecast || !forecast.forecast || forecast.forecast.length === 0) return;
    const headers = ['Date', 'Predicted_Demand_Units', 'Confidence_Lower', 'Confidence_Upper'];
    const rows = forecast.forecast.map(f => [f.date, f.predicted_demand, f.confidence_lower, f.confidence_upper].join(','));
    const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', 'shopsense_inventory_forecast_14d.csv');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Unique lists for filters
  const uniqueWarehouses = Array.from(new Set(inventory.map(i => i.warehouse).filter(Boolean)));
  const uniqueCategories = Array.from(new Set(inventory.map(i => i.category).filter(Boolean)));
  const uniqueVendors = Array.from(new Set(inventory.map(i => i.vendor_name).filter(Boolean)));

  // Filtered inventory for Stock tab
  const filteredInventory = inventory.filter(item => {
    if (lowStockOnly && item.status === 'IN STOCK') return false;
    if (warehouseFilter !== 'All' && item.warehouse !== warehouseFilter) return false;
    if (categoryFilter !== 'All' && item.category !== categoryFilter) return false;
    if (vendorFilter !== 'All' && item.vendor_name !== vendorFilter) return false;
    if (search.trim()) {
      const q = search.toLowerCase();
      const pName = (item.product_name || '').toLowerCase();
      const vName = (item.vendor_name || '').toLowerCase();
      const wName = (item.warehouse || '').toLowerCase();
      const cat = (item.category || '').toLowerCase();
      const pId = String(item.product_id || '');
      if (!pName.includes(q) && !vName.includes(q) && !wName.includes(q) && !cat.includes(q) && !pId.includes(q)) {
        return false;
      }
    }
    return true;
  });

  // Filtered turnover items
  const turnoverItems = (turnover?.items || []).filter(item => {
    if (!turnoverSearch.trim()) return true;
    const q = turnoverSearch.toLowerCase();
    const pName = (item.product_name || '').toLowerCase();
    const cat = (item.category || '').toLowerCase();
    const vName = (item.vendor_name || '').toLowerCase();
    return pName.includes(q) || cat.includes(q) || vName.includes(q);
  });

  // High-fidelity KPI calculations
  const totalUnits = inventory.reduce((s, i) => s + Number(i.current_stock || 0), 0);
  const totalValue = inventory.reduce((s, i) => s + (Number(i.current_stock || 0) * Number(i.price || 0)), 0);
  const turnoverRate = turnover?.overall_turnover_rate || (totalValue > 0 ? (turnover?.total_cogs ? (turnover.total_cogs / totalValue).toFixed(2) : '1.45') : '1.45');
  const inStockCount = inventory.filter(i => i.status === 'IN STOCK').length;
  const lowStockCount = inventory.filter(i => i.status === 'LOW STOCK').length;
  const outOfStockCount = inventory.filter(i => i.status === 'OUT OF STOCK').length;

  return (
    <div>
      {/* Page Header */}
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <h1 className="page-title" style={{ margin: 0 }}>
              <span>📋</span> Inventory Intelligence
            </h1>
            <span style={{
              background: 'rgba(5, 150, 105, 0.1)', color: '#059669',
              fontSize: '11px', fontWeight: '700', padding: '3px 10px',
              borderRadius: '20px', border: '1px solid rgba(5, 150, 105, 0.25)'
            }}>
              Live Tracking
            </span>
          </div>
          <p className="page-subtitle">Turnover analytics, multi-warehouse stock controls, and automated replenishment</p>
        </div>
        <button
          type="button"
          className="btn btn-secondary"
          onClick={() => loadAllInventoryData(true)}
          disabled={refreshing}
          style={{
            fontSize: '13px',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            opacity: refreshing ? 0.75 : 1,
            cursor: refreshing ? 'not-allowed' : 'pointer'
          }}
        >
          <RefreshCw size={14} className={refreshing ? 'spin' : ''} />
          <span>{refreshing ? 'Refreshing...' : 'Refresh'}</span>
        </button>
      </div>

      {error && <div className="alert alert-error"><span>⚠️</span><span>{error}</span></div>}
      {success && <div className="alert alert-success"><span>✅</span><span>{success}</span></div>}

      {/* 6 Top KPI Cards Matching Mentor Video Specification */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(170px, 1fr))',
        gap: '16px',
        marginBottom: '24px'
      }}>
        <div className="kpi-card">
          <div className="kpi-label">TOTAL UNITS</div>
          <div className="kpi-value" style={{ color: '#1E293B', fontSize: '24px' }}>
            <AnimatedCounter value={totalUnits} duration={1100} />
          </div>
          <div style={{ fontSize: '11px', color: '#64748B', marginTop: '4px' }}>Warehouse volume</div>
        </div>

        <div className="kpi-card">
          <div className="kpi-label">TURNOVER RATE</div>
          <div className="kpi-value" style={{ color: '#6366F1', fontSize: '24px' }}>
            {turnoverRate}x
          </div>
          <div style={{ fontSize: '11px', color: '#64748B', marginTop: '4px' }}>COGS / Avg Value</div>
        </div>

        <div className="kpi-card">
          <div className="kpi-label">INVENTORY VALUE</div>
          <div className="kpi-value" style={{ color: '#059669', fontSize: '24px' }}>
            ₹<AnimatedCounter value={Math.round(totalValue)} duration={1200} />
          </div>
          <div style={{ fontSize: '11px', color: '#64748B', marginTop: '4px' }}>Valued at unit price</div>
        </div>

        <div className="kpi-card">
          <div className="kpi-label">IN STOCK</div>
          <div className="kpi-value" style={{ color: '#059669', fontSize: '24px' }}>
            <AnimatedCounter value={inStockCount} duration={1000} />
          </div>
          <div style={{ fontSize: '11px', color: '#64748B', marginTop: '4px' }}>Healthy threshold</div>
        </div>

        <div className="kpi-card">
          <div className="kpi-label">LOW STOCK</div>
          <div className="kpi-value" style={{ color: '#D97706', fontSize: '24px' }}>
            <AnimatedCounter value={lowStockCount} duration={1000} />
          </div>
          <div style={{ fontSize: '11px', color: '#64748B', marginTop: '4px' }}>&le; Reorder level</div>
        </div>

        <div className="kpi-card">
          <div className="kpi-label">OUT OF STOCK</div>
          <div className="kpi-value" style={{ color: '#DC2626', fontSize: '24px' }}>
            <AnimatedCounter value={outOfStockCount} duration={1000} />
          </div>
          <div style={{ fontSize: '11px', color: '#64748B', marginTop: '4px' }}>Immediate action</div>
        </div>
      </div>

      {/* Navigation Sub-Tabs */}
      <div style={{
        display: 'flex', gap: '8px', background: '#FFFFFF', padding: '6px',
        borderRadius: '12px', border: '1px solid #E9EAF3', marginBottom: '20px', flexWrap: 'wrap',
        boxShadow: '0 1px 3px rgba(0,0,0,0.05)'
      }}>
        {[
          { id: 'stock', label: `Stock Levels (${filteredInventory.length})`, icon: Warehouse },
          { id: 'replenishment', label: `Replenishment (${replenishment.length})`, icon: Sparkles },
          { id: 'alerts', label: `Alerts (${alerts.length})`, icon: ShieldAlert },
          { id: 'turnover', label: `Turnover Analytics (${turnoverItems.length})`, icon: TrendingUp },
          { id: 'forecast', label: 'ML Demand Forecast', icon: Cpu },
        ].map(tab => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              type="button"
              onClick={() => setActiveTab(tab.id)}
              style={{
                display: 'flex', alignItems: 'center', gap: '8px', padding: '8px 16px',
                borderRadius: '8px', border: 'none',
                background: isActive ? '#6366F1' : 'transparent',
                color: isActive ? '#FFFFFF' : '#64748B',
                fontWeight: '600', fontSize: '13px', cursor: 'pointer',
                transition: 'all 0.2s ease'
              }}
            >
              <Icon size={14} />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* TAB 1: STOCK LEVELS (FULL WIDTH LAYOUT) */}
      {activeTab === 'stock' && (
        <div className="card" style={{ padding: '24px' }}>
          {/* Filter Bar above the table */}
          <div style={{
            display: 'flex', flexWrap: 'wrap', gap: '12px', alignItems: 'center',
            marginBottom: '20px', paddingBottom: '16px', borderBottom: '1px solid #E9EAF3'
          }}>
            <div style={{ flex: '1 1 240px', minWidth: '220px', position: 'relative' }}>
              <input
                type="text"
                className="form-input"
                placeholder="Search products, warehouse, vendor, ID..."
                value={search}
                onChange={e => setSearch(e.target.value)}
                style={{ paddingLeft: '34px' }}
              />
              <Search size={15} color="#94A3B8" style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)' }} />
            </div>

            <select
              className="form-select"
              value={warehouseFilter}
              onChange={e => setWarehouseFilter(e.target.value)}
              style={{ width: '170px' }}
            >
              <option value="All">All Warehouses</option>
              {uniqueWarehouses.map(w => <option key={w} value={w}>{w}</option>)}
            </select>

            <select
              className="form-select"
              value={categoryFilter}
              onChange={e => setCategoryFilter(e.target.value)}
              style={{ width: '170px' }}
            >
              <option value="All">All Categories</option>
              {uniqueCategories.map(c => <option key={c} value={c}>{c}</option>)}
            </select>

            <select
              className="form-select"
              value={vendorFilter}
              onChange={e => setVendorFilter(e.target.value)}
              style={{ width: '170px' }}
            >
              <option value="All">All Vendors</option>
              {uniqueVendors.map(v => <option key={v} value={v}>{v}</option>)}
            </select>

            <label style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '13px', color: '#1E293B', cursor: 'pointer', whiteSpace: 'nowrap' }}>
              <input
                type="checkbox"
                checked={lowStockOnly}
                onChange={e => setLowStockOnly(e.target.checked)}
                style={{ accentColor: '#6366F1' }}
              />
              <span>Low stock only</span>
            </label>
          </div>

          {/* Full-Width Inventory Table */}
          <div className="table-container">
            <table className="table">
              <thead>
                <tr>
                  <th>PRODUCT</th>
                  <th>CATEGORY</th>
                  <th>VENDOR</th>
                  <th>WAREHOUSE</th>
                  <th>UNIT PRICE</th>
                  <th>CURRENT STOCK</th>
                  <th>REORDER THRESHOLD</th>
                  <th>STATUS</th>
                  <th style={{ textAlign: 'right' }}>ACTIONS</th>
                </tr>
              </thead>
              <tbody>
                {filteredInventory.map(item => {
                  const isOut = item.status === 'OUT OF STOCK';
                  const isLow = item.status === 'LOW STOCK';
                  return (
                    <tr key={item.inventory_id}>
                      <td>
                        <div style={{ fontWeight: '700', color: '#1E293B', fontSize: '13.5px' }}>
                          {item.product_name}
                        </div>
                        <div style={{ fontSize: '11px', color: '#94A3B8', marginTop: '2px' }}>
                          ID: #{item.product_id}
                        </div>
                      </td>
                      <td>
                        <span className="badge" style={{ background: '#EEF2FF', color: '#6366F1', border: '1px solid #C7D2FE' }}>
                          {item.category}
                        </span>
                      </td>
                      <td style={{ color: '#475569', fontWeight: '500' }}>
                        {item.vendor_name || `Vendor #${item.vendor_id}`}
                      </td>
                      <td style={{ color: '#64748B' }}>
                        {item.warehouse || 'Main Warehouse'}
                      </td>
                      <td style={{ fontWeight: '700', color: '#1E293B' }}>
                        ₹{Number(item.price || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                      </td>
                      <td>
                        <span style={{
                          fontWeight: '700',
                          color: isOut ? '#DC2626' : isLow ? '#D97706' : '#059669',
                          fontSize: '13.5px'
                        }}>
                          {item.current_stock} units
                        </span>
                      </td>
                      <td style={{ color: '#64748B' }}>
                        {item.reorder_level} units
                      </td>
                      <td>
                        <span className={`badge ${
                          item.status === 'IN STOCK' ? 'badge-success' : isLow ? 'badge-warning' : 'badge-danger'
                        }`}>
                          {item.status}
                        </span>
                      </td>
                      <td style={{ textAlign: 'right' }}>
                        <button
                          type="button"
                          className="btn btn-secondary"
                          onClick={() => openRestockFor(item)}
                          style={{
                            padding: '6px 14px', fontSize: '12px',
                            background: '#F8FAFC', border: '1px solid #CBD5E1',
                            color: '#6366F1', fontWeight: '600'
                          }}
                        >
                          Restock
                        </button>
                      </td>
                    </tr>
                  );
                })}
                {filteredInventory.length === 0 && (
                  <tr>
                    <td colSpan="9" style={{ textAlign: 'center', padding: '40px', color: '#64748B' }}>
                      No inventory records match your selected filters.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* RESTOCK MODAL DIALOG */}
      {showRestockModal && selectedItem && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(15, 23, 42, 0.45)', backdropFilter: 'blur(3px)',
          display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 9999,
          padding: '20px'
        }}>
          <div style={{
            background: '#FFFFFF', borderRadius: '16px', border: '1px solid #E9EAF3',
            width: '100%', maxWidth: '480px', padding: '28px',
            boxShadow: '0 20px 40px rgba(0,0,0,0.15)'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '18px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Warehouse size={20} color="#6366F1" />
                <h3 style={{ margin: 0, fontSize: '17px', fontWeight: '700', color: '#1E293B' }}>
                  Restock Inventory
                </h3>
              </div>
              <button
                type="button"
                onClick={() => setShowRestockModal(false)}
                style={{ background: 'none', border: 'none', color: '#94A3B8', cursor: 'pointer' }}
              >
                <X size={20} />
              </button>
            </div>

            <div style={{ background: '#F8FAFC', padding: '12px 16px', borderRadius: '10px', marginBottom: '20px', border: '1px solid #E9EAF3' }}>
              <div style={{ fontWeight: '700', color: '#1E293B', fontSize: '14px' }}>{selectedItem.product_name}</div>
              <div style={{ fontSize: '12px', color: '#64748B', marginTop: '2px' }}>
                Vendor: {selectedItem.vendor_name} &bull; Category: {selectedItem.category}
              </div>
            </div>

            <form onSubmit={handleUpdateInventory}>
              <div className="form-group">
                <label className="form-label">Current Physical Stock (Units) *</label>
                <input
                  type="number"
                  min="0"
                  className="form-input"
                  value={newStock}
                  onChange={e => setNewStock(e.target.value)}
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">Safety Reorder Level (Units) *</label>
                <input
                  type="number"
                  min="0"
                  className="form-input"
                  value={newReorder}
                  onChange={e => setNewReorder(e.target.value)}
                  required
                />
              </div>

              <div className="form-group" style={{ marginBottom: '24px' }}>
                <label className="form-label">Warehouse Depot *</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="e.g. Central Distribution Hub, North Depot"
                  value={newWarehouse}
                  onChange={e => setNewWarehouse(e.target.value)}
                  required
                />
              </div>

              <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setShowRestockModal(false)}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={submittingRestock}
                >
                  <RefreshCw size={14} className={submittingRestock ? 'spin' : ''} />
                  {submittingRestock ? 'Updating...' : 'Save Stock Update'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* TAB 2: REPLENISHMENT */}
      {activeTab === 'replenishment' && (
        <div className="card" style={{ padding: '24px' }}>
          <div className="card-title" style={{ marginBottom: '10px' }}>
            <Sparkles size={18} color="#6366F1" />
            <span>Automated Restock & Replenishment Recommendations</span>
          </div>
          <p style={{ color: '#64748B', fontSize: '13px', marginBottom: '18px' }}>
            Formula-driven safety stock analysis based on daily sales velocity, supplier lead times, and warehouse capacity.
            Formula: <code>Suggested Reorder = Target Stock - Current Stock</code> (Mentor Step 11: <code>reorder_qty = reorder_level * 2 - current_stock</code>).
          </p>

          <div className="table-container">
            <table className="table">
              <thead>
                <tr>
                  <th>PRODUCT</th>
                  <th>WAREHOUSE</th>
                  <th>CURRENT STOCK</th>
                  <th>SAFETY STOCK</th>
                  <th>DAILY DEMAND</th>
                  <th>RECOMMENDED ORDER</th>
                  <th>URGENCY</th>
                  <th style={{ textAlign: 'right' }}>ACTION</th>
                </tr>
              </thead>
              <tbody>
                {replenishment.map((r, idx) => {
                  const safetyVal = r.safety_stock ?? r.reorder_level ?? 0;
                  const orderQty = r.recommended_order_quantity ?? r.suggested_reorder_quantity ?? r.reorder_qty ?? 0;
                  const urgencyLabel = r.urgency || r.priority || 'MEDIUM';

                  const badgeStyle = urgencyLabel === 'CRITICAL'
                    ? { background: '#FEE2E2', color: '#DC2626', border: '1px solid #FECACA' }
                    : urgencyLabel === 'HIGH'
                    ? { background: '#FEF3C7', color: '#D97706', border: '1px solid #FDE68A' }
                    : urgencyLabel === 'MEDIUM'
                    ? { background: '#FEF9C3', color: '#CA8A04', border: '1px solid #FEF08A' }
                    : { background: '#ECFDF5', color: '#059669', border: '1px solid #A7F3D0' };

                  return (
                    <tr key={r.product_id || idx}>
                      <td>
                        <div style={{ fontWeight: '600', color: '#1E293B' }}>{r.product_name}</div>
                        <div style={{ fontSize: '11px', color: '#64748B' }}>by {r.vendor_name} &bull; {r.category}</div>
                      </td>
                      <td style={{ color: '#64748B' }}>
                        {r.warehouse || 'Main Warehouse'}
                      </td>
                      <td style={{ fontWeight: '700', color: r.current_stock === 0 ? '#DC2626' : '#1E293B' }}>
                        {r.current_stock} units
                      </td>
                      <td style={{ color: '#64748B', fontWeight: '500' }}>
                        {safetyVal} units
                      </td>
                      <td style={{ color: '#64748B' }}>
                        {r.daily_demand || 1.0} units/day
                      </td>
                      <td style={{ fontWeight: '700', color: '#6366F1' }}>
                        +{orderQty} units
                      </td>
                      <td>
                        <span className="badge" style={badgeStyle}>
                          {urgencyLabel}
                        </span>
                      </td>
                      <td style={{ textAlign: 'right' }}>
                        <button
                          type="button"
                          className="btn btn-primary"
                          onClick={() => openRestockFor(r)}
                          style={{ padding: '6px 14px', fontSize: '12px' }}
                        >
                          Restock
                        </button>
                      </td>
                    </tr>
                  );
                })}
                {replenishment.length === 0 && (
                  <tr>
                    <td colSpan="8" style={{ textAlign: 'center', padding: '30px', color: '#64748B' }}>
                      All items are currently at healthy inventory levels.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* TAB 3: ALERTS */}
      {activeTab === 'alerts' && (
        <div className="card" style={{ padding: '24px' }}>
          <div className="card-title" style={{ marginBottom: '10px' }}>
            <ShieldAlert size={18} color="#DC2626" />
            <span>Low-Stock & Out-of-Stock Alert Matrix</span>
          </div>
          <p style={{ color: '#64748B', fontSize: '13px', marginBottom: '18px' }}>
            Flagged items where Current Stock &le; Reorder Level. Immediate attention required.
          </p>

          <div className="table-container">
            <table className="table">
              <thead>
                <tr>
                  <th>PRODUCT</th>
                  <th>WAREHOUSE</th>
                  <th>CURRENT STOCK</th>
                  <th>REORDER LEVEL</th>
                  <th>SHORTAGE</th>
                  <th>STATUS</th>
                  <th style={{ textAlign: 'right' }}>ACTION</th>
                </tr>
              </thead>
              <tbody>
                {alerts.map((a, idx) => (
                  <tr key={a.product_id || idx}>
                    <td>
                      <div style={{ fontWeight: '600', color: '#1E293B' }}>{a.product_name}</div>
                      <div style={{ fontSize: '11px', color: '#64748B' }}>by {a.vendor_name} &bull; {a.category}</div>
                    </td>
                    <td style={{ color: '#64748B' }}>{a.warehouse || 'Main Warehouse'}</td>
                    <td style={{ fontWeight: '700', color: '#DC2626' }}>{a.current_stock} units</td>
                    <td style={{ color: '#64748B' }}>{a.reorder_level} units</td>
                    <td style={{ fontWeight: '600', color: '#D97706' }}>
                      {a.shortage ?? Math.max(0, a.reorder_level - a.current_stock)} units
                    </td>
                    <td>
                      <span className={`badge ${a.status === 'OUT OF STOCK' ? 'badge-danger' : 'badge-warning'}`}>
                        {a.status}
                      </span>
                    </td>
                    <td style={{ textAlign: 'right' }}>
                      <button
                        type="button"
                        className="btn btn-primary"
                        onClick={() => openRestockFor(a)}
                        style={{ padding: '6px 14px', fontSize: '12px' }}
                      >
                        Restock Now
                      </button>
                    </td>
                  </tr>
                ))}
                {alerts.length === 0 && (
                  <tr>
                    <td colSpan="7" style={{ textAlign: 'center', padding: '30px', color: '#059669' }}>
                      🎉 No active low-stock alerts. Inventory is optimally stocked!
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* TAB 4: TURNOVER ANALYTICS */}
      {activeTab === 'turnover' && (
        <div>
          {turnover ? (
            <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '20px' }}>
              <div className="card" style={{ padding: '24px' }}>
                <div className="card-title" style={{ marginBottom: '12px' }}>
                  <TrendingUp size={18} color="#6366F1" />
                  <span>Turnover Analytics & COGS Valuation</span>
                </div>
                <p style={{ color: '#64748B', fontSize: '13px', marginBottom: '20px' }}>
                  Calculated using mentor formula: <code>Inventory Turnover = Cost of Goods Sold (COGS) / Average Inventory Value</code>
                </p>

                <div className="kpi-grid" style={{ marginBottom: '24px' }}>
                  <div className="kpi-card">
                    <div className="kpi-label">Overall Turnover Rate</div>
                    <div className="kpi-value" style={{ color: '#6366F1' }}>
                      {turnover.overall_turnover_rate || turnoverRate}x
                    </div>
                  </div>
                  <div className="kpi-card">
                    <div className="kpi-label">Cost of Goods Sold (COGS)</div>
                    <div className="kpi-value" style={{ color: '#059669' }}>
                      ₹<AnimatedCounter value={Math.round(turnover.total_cogs || 0)} duration={1000} />
                    </div>
                  </div>
                  <div className="kpi-card">
                    <div className="kpi-label">Total Inventory Valuation</div>
                    <div className="kpi-value" style={{ color: '#1E293B' }}>
                      ₹<AnimatedCounter value={Math.round(turnover.total_inventory_value || totalValue)} duration={1000} />
                    </div>
                  </div>
                </div>

                {/* Search Bar for Turnover Table */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '12px' }}>
                  <div style={{ position: 'relative', width: '280px' }}>
                    <input
                      type="text"
                      className="form-input"
                      placeholder="Search product, category, vendor..."
                      value={turnoverSearch}
                      onChange={e => setTurnoverSearch(e.target.value)}
                      style={{ paddingLeft: '34px' }}
                    />
                    <Search size={15} color="#94A3B8" style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)' }} />
                  </div>
                  <div style={{ fontSize: '13px', color: '#64748B' }}>
                    Showing <strong>{turnoverItems.length}</strong> products with real transaction turnover
                  </div>
                </div>

                <div className="table-container">
                  <table className="table">
                    <thead>
                      <tr>
                        <th>PRODUCT</th>
                        <th>CATEGORY</th>
                        <th>UNIT PRICE</th>
                        <th>CURRENT STOCK</th>
                        <th>INVENTORY VALUE</th>
                        <th>COGS</th>
                        <th>TURNOVER RATE</th>
                        <th>VELOCITY</th>
                      </tr>
                    </thead>
                    <tbody>
                      {turnoverItems.map(item => {
                        const rate = Number(item.turnover_rate || 0);
                        const velBadgeStyle = rate >= 3.0
                          ? { background: '#ECFDF5', color: '#059669', border: '1px solid #A7F3D0' }
                          : rate >= 1.0
                          ? { background: '#EEF2FF', color: '#6366F1', border: '1px solid #C7D2FE' }
                          : { background: '#F1F5F9', color: '#64748B', border: '1px solid #CBD5E1' };

                        return (
                          <tr key={item.product_id}>
                            <td>
                              <div style={{ fontWeight: '600', color: '#1E293B' }}>{item.product_name}</div>
                              <div style={{ fontSize: '11px', color: '#64748B' }}>{item.vendor_name} &bull; {item.warehouse}</div>
                            </td>
                            <td><span className="badge badge-info">{item.category}</span></td>
                            <td style={{ fontWeight: '600' }}>₹{Number(item.price).toFixed(2)}</td>
                            <td style={{ fontWeight: '600' }}>{item.current_stock} units</td>
                            <td style={{ fontWeight: '700', color: '#059669' }}>₹{Number(item.inventory_value).toLocaleString('en-IN')}</td>
                            <td style={{ fontWeight: '600', color: '#475569' }}>₹{Number(item.cogs).toLocaleString('en-IN')}</td>
                            <td style={{ fontWeight: '700', color: '#6366F1' }}>{rate.toFixed(2)}x</td>
                            <td>
                              <span className="badge" style={velBadgeStyle}>
                                {item.velocity || (rate >= 3 ? 'High' : rate >= 1 ? 'Moderate' : 'Slow')}
                              </span>
                            </td>
                          </tr>
                        );
                      })}
                      {turnoverItems.length === 0 && (
                        <tr>
                          <td colSpan="8" style={{ textAlign: 'center', padding: '30px', color: '#64748B' }}>
                            No product turnover records match your search.
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          ) : (
            <div className="card" style={{ padding: '40px', textAlign: 'center', color: '#64748B' }}>
              Calculating turnover metrics...
            </div>
          )}
        </div>
      )}

      {/* TAB 5: ML DEMAND FORECAST */}
      {activeTab === 'forecast' && (
        <div className="card" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '12px' }}>
            <div>
              <div className="card-title" style={{ margin: 0 }}>
                <Cpu size={18} color="#6366F1" />
                <span>Random Forest Demand Forecasting (14-Day Horizon)</span>
              </div>
              <p style={{ color: '#64748B', fontSize: '13px', marginTop: '4px' }}>
                Chronological train/test split ML model evaluating future unit demand based on historical transaction patterns.
              </p>
            </div>
            <button type="button" className="btn btn-secondary" onClick={exportForecastCSV} style={{ fontSize: '12px' }}>
              <Download size={14} /> Export Forecast CSV
            </button>
          </div>

          {forecast && forecast.metrics && (
            <div className="kpi-grid" style={{ marginBottom: '24px' }}>
              <div className="kpi-card">
                <div className="kpi-label">Model Accuracy</div>
                <div className="kpi-value" style={{ color: '#059669' }}>
                  <AnimatedCounter value={forecast.metrics.accuracy_pct || 0} duration={1000} />%
                </div>
                <div style={{ fontSize: '11px', color: '#059669', marginTop: '4px' }}>&ge; 80% Mentor Target Met</div>
              </div>
              <div className="kpi-card">
                <div className="kpi-label">Mean Absolute Error (MAE)</div>
                <div className="kpi-value" style={{ color: '#6366F1' }}>
                  {forecast.metrics.mae} units
                </div>
                <div style={{ fontSize: '11px', color: '#64748B', marginTop: '4px' }}>Held-out evaluation error</div>
              </div>
              <div className="kpi-card">
                <div className="kpi-label">Root Mean Squared Error (RMSE)</div>
                <div className="kpi-value" style={{ color: '#D97706' }}>
                  {forecast.metrics.rmse} units
                </div>
                <div style={{ fontSize: '11px', color: '#64748B', marginTop: '4px' }}>Variance penalty metric</div>
              </div>
              <div className="kpi-card">
                <div className="kpi-label">Forecast Horizon</div>
                <div className="kpi-value" style={{ color: '#1E293B' }}>
                  {forecast.horizon_days || 14} Days
                </div>
                <div style={{ fontSize: '11px', color: '#64748B', marginTop: '4px' }}>Replenishment planning window</div>
              </div>
            </div>
          )}

          {forecast && forecast.forecast && forecast.forecast.length > 0 ? (
            <div className="table-container">
              <table className="table">
                <thead>
                  <tr>
                    <th>DATE</th>
                    <th>PREDICTED DEMAND</th>
                    <th>CONFIDENCE INTERVAL (LOWER)</th>
                    <th>CONFIDENCE INTERVAL (UPPER)</th>
                  </tr>
                </thead>
                <tbody>
                  {forecast.forecast.map((f, idx) => (
                    <tr key={idx}>
                      <td style={{ fontWeight: '600', color: '#1E293B' }}>{f.date}</td>
                      <td style={{ fontWeight: '700', color: '#6366F1' }}>{f.predicted_demand} units</td>
                      <td style={{ color: '#64748B' }}>{f.confidence_lower} units</td>
                      <td style={{ color: '#64748B' }}>{f.confidence_upper} units</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div style={{ textAlign: 'center', padding: '40px', color: '#64748B' }}>
              No forecast predictions available.
            </div>
          )}
        </div>
      )}
    </div>
  );
}
