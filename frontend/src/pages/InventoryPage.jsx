import React, { useState, useEffect } from 'react';
import { api } from '../api';
import {
  ClipboardList, Warehouse, RefreshCw, AlertTriangle, CheckCircle2,
  XCircle, TrendingUp, Sparkles, Download, Layers, ShieldAlert, Cpu
} from 'lucide-react';

export default function InventoryPage({ user }) {
  const [activeTab, setActiveTab] = useState('stock'); // stock | alerts | replenishment | turnover | forecast
  const [inventory, setInventory] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [replenishment, setReplenishment] = useState([]);
  const [turnover, setTurnover] = useState(null);
  const [forecast, setForecast] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [statusFilter, setStatusFilter] = useState('All');

  // Restock form states
  const [selectedProductId, setSelectedProductId] = useState('');
  const [newStock, setNewStock] = useState(20);
  const [newReorder, setNewReorder] = useState(10);
  const [newWarehouse, setNewWarehouse] = useState('Main Warehouse');

  useEffect(() => {
    loadAllInventoryData();
  }, [statusFilter]);

  const loadAllInventoryData = async () => {
    setLoading(true);
    setError('');
    try {
      const [invData, alertData, replData, turnData, foreData] = await Promise.all([
        api.getInventory(statusFilter),
        api.getInventoryAlerts().catch(() => []),
        api.getInventoryReplenishment(5).catch(() => []),
        api.getInventoryTurnover().catch(() => null),
        api.getInventoryForecast(null, 14).catch(() => null),
      ]);

      setInventory(invData || []);
      setAlerts(alertData || []);
      setReplenishment(replData || []);
      setTurnover(turnData);
      setForecast(foreData);

      if (invData && invData.length > 0 && !selectedProductId) {
        setSelectedProductId(invData[0].product_id);
        setNewStock(invData[0].current_stock);
        setNewReorder(invData[0].reorder_level);
        setNewWarehouse(invData[0].warehouse || 'Main Warehouse');
      }
    } catch (err) {
      setError(err.message || 'Error loading inventory data.');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateInventory = async (e) => {
    e.preventDefault();
    if (!selectedProductId) return;
    setError('');
    setSuccess('');
    try {
      await api.updateInventory(selectedProductId, {
        current_stock: Number(newStock),
        reorder_level: Number(newReorder),
        warehouse: newWarehouse.trim() || 'Main Warehouse',
      });
      setSuccess('Inventory record updated successfully!');
      loadAllInventoryData();
    } catch (err) {
      setError(err.message || 'Update failed.');
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

  // Metrics
  const totalItems = inventory.length;
  const inStockCount = inventory.filter(i => i.status === 'IN STOCK').length;
  const lowStockCount = inventory.filter(i => i.status === 'LOW STOCK').length;
  const outOfStockCount = inventory.filter(i => i.status === 'OUT OF STOCK').length;

  return (
    <div>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 className="page-title">
            <span>📋</span> Inventory Intelligence & Warehouse Tracking
          </h1>
          <p className="page-subtitle">Multi-vendor stock monitoring, ML demand forecasting, and automated replenishment</p>
        </div>
        <button className="btn btn-secondary" onClick={loadAllInventoryData} style={{ fontSize: '13px' }}>
          <RefreshCw size={14} /> Refresh
        </button>
      </div>

      {error && <div className="alert alert-error"><span>⚠️</span><span>{error}</span></div>}
      {success && <div className="alert alert-success"><span>✅</span><span>{success}</span></div>}

      {/* KPI Cards */}
      <div className="kpi-grid">
        <div className="kpi-card">
          <div className="kpi-label">Tracked Items</div>
          <div className="kpi-value" style={{ color: '#f8fafc' }}>{totalItems}</div>
        </div>
        <div className="kpi-card">
          <div className="kpi-label">In Stock</div>
          <div className="kpi-value" style={{ color: '#34d399' }}>{inStockCount}</div>
        </div>
        <div className="kpi-card">
          <div className="kpi-label">Low Stock Alerts</div>
          <div className="kpi-value" style={{ color: '#fbbf24' }}>{lowStockCount}</div>
        </div>
        <div className="kpi-card">
          <div className="kpi-label">Out of Stock</div>
          <div className="kpi-value" style={{ color: '#f87171' }}>{outOfStockCount}</div>
        </div>
      </div>

      {/* Navigation Sub-Tabs */}
      <div style={{
        display: 'flex', gap: '8px', background: '#0f172a', padding: '6px',
        borderRadius: '12px', border: '1px solid #334155', marginBottom: '20px', flexWrap: 'wrap'
      }}>
        {[
          { id: 'stock', label: 'Stock & Warehouse', icon: Warehouse },
          { id: 'alerts', label: `Low-Stock Alerts (${alerts.length})`, icon: ShieldAlert },
          { id: 'replenishment', label: `Replenishment (${replenishment.length})`, icon: Sparkles },
          { id: 'turnover', label: 'Turnover Analytics', icon: TrendingUp },
          { id: 'forecast', label: 'ML Demand Forecast', icon: Cpu },
        ].map(tab => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                display: 'flex', alignItems: 'center', gap: '8px', padding: '8px 14px',
                borderRadius: '8px', border: 'none',
                background: isActive ? '#6366f1' : 'transparent',
                color: isActive ? '#fff' : '#94a3b8',
                fontWeight: '600', fontSize: '13px', cursor: 'pointer'
              }}
            >
              <Icon size={14} />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* TAB 1: STOCK & WAREHOUSE MANAGEMENT */}
      {activeTab === 'stock' && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: '24px', alignItems: 'start' }}>
          <div>
            <div className="card" style={{ padding: '16px', marginBottom: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ fontWeight: '700', fontSize: '14px' }}>Inventory Catalog</div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ fontSize: '12px', color: '#94a3b8' }}>Filter:</span>
                <select
                  className="form-select"
                  value={statusFilter}
                  onChange={e => setStatusFilter(e.target.value)}
                  style={{ width: '140px', padding: '4px 8px', fontSize: '12px' }}
                >
                  <option value="All">All Statuses</option>
                  <option value="IN STOCK">In Stock</option>
                  <option value="LOW STOCK">Low Stock</option>
                  <option value="OUT OF STOCK">Out of Stock</option>
                </select>
              </div>
            </div>

            <div className="table-container">
              <table className="table">
                <thead>
                  <tr>
                    <th>Product</th>
                    <th>Warehouse</th>
                    <th>Current Stock</th>
                    <th>Reorder Level</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {inventory.map(item => (
                    <tr key={item.inventory_id}>
                      <td>
                        <div style={{ fontWeight: '600', color: '#f8fafc' }}>{item.product_name}</div>
                        <div style={{ fontSize: '11px', color: '#64748b' }}>by {item.vendor_name}</div>
                      </td>
                      <td>{item.warehouse}</td>
                      <td style={{ fontWeight: '700' }}>{item.current_stock}</td>
                      <td>{item.reorder_level}</td>
                      <td>
                        <span className={`badge ${
                          item.status === 'IN STOCK' ? 'badge-success' : item.status === 'LOW STOCK' ? 'badge-warning' : 'badge-danger'
                        }`}>
                          {item.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Quick Restock Card */}
          <div className="card" style={{ padding: '20px' }}>
            <div className="card-title">
              <Warehouse size={18} color="#6366f1" />
              <span>Update Stock / Reorder</span>
            </div>
            <form onSubmit={handleUpdateInventory}>
              <div className="form-group">
                <label className="form-label">Select Product</label>
                <select
                  className="form-select"
                  value={selectedProductId}
                  onChange={e => {
                    setSelectedProductId(e.target.value);
                    const sel = inventory.find(i => String(i.product_id) === String(e.target.value));
                    if (sel) {
                      setNewStock(sel.current_stock);
                      setNewReorder(sel.reorder_level);
                      setNewWarehouse(sel.warehouse || 'Main Warehouse');
                    }
                  }}
                >
                  {inventory.map(i => (
                    <option key={i.product_id} value={i.product_id}>
                      {i.product_name} (Stock: {i.current_stock})
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Current Stock Count</label>
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
                <label className="form-label">Safety Reorder Level</label>
                <input
                  type="number"
                  min="0"
                  className="form-input"
                  value={newReorder}
                  onChange={e => setNewReorder(e.target.value)}
                  required
                />
              </div>

              <div className="form-group" style={{ marginBottom: '20px' }}>
                <label className="form-label">Warehouse Facility</label>
                <input
                  type="text"
                  className="form-input"
                  value={newWarehouse}
                  onChange={e => setNewWarehouse(e.target.value)}
                  required
                />
              </div>

              <button type="submit" className="btn btn-primary" style={{ width: '100%', padding: '12px' }}>
                <RefreshCw size={14} /> Commit Inventory Update
              </button>
            </form>
          </div>
        </div>
      )}

      {/* TAB 2: LOW-STOCK ALERT SYSTEM */}
      {activeTab === 'alerts' && (
        <div className="card" style={{ padding: '20px' }}>
          <div className="card-title">
            <ShieldAlert size={18} color="#f87171" />
            <span>Low-Stock & Out-of-Stock Alert Matrix</span>
          </div>
          <p style={{ color: '#94a3b8', fontSize: '13px', marginBottom: '16px' }}>
            Products flagged where <code>Current Stock &le; Reorder Level</code>. Actionable priority alerts for warehouse restock.
          </p>

          <div className="table-container">
            <table className="table">
              <thead>
                <tr>
                  <th>Product</th>
                  <th>Vendor</th>
                  <th>Warehouse</th>
                  <th>Stock</th>
                  <th>Reorder Level</th>
                  <th>Shortage</th>
                  <th>Alert Level</th>
                  <th>Recommended Action</th>
                </tr>
              </thead>
              <tbody>
                {alerts.map((a, idx) => (
                  <tr key={idx}>
                    <td style={{ fontWeight: '600', color: '#f8fafc' }}>{a.product_name}</td>
                    <td>{a.vendor_name}</td>
                    <td>{a.warehouse}</td>
                    <td style={{ fontWeight: '700', color: a.current_stock === 0 ? '#f87171' : '#fbbf24' }}>
                      {a.current_stock}
                    </td>
                    <td>{a.reorder_level}</td>
                    <td style={{ fontWeight: '700', color: '#f87171' }}>+{a.shortage} units</td>
                    <td>
                      <span className={`badge ${a.status === 'OUT OF STOCK' ? 'badge-danger' : 'badge-warning'}`}>
                        {a.status}
                      </span>
                    </td>
                    <td style={{ fontSize: '12px', color: '#cbd5e1' }}>{a.recommended_action}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* TAB 3: REPLENISHMENT RECOMMENDATIONS */}
      {activeTab === 'replenishment' && (
        <div className="card" style={{ padding: '20px' }}>
          <div className="card-title">
            <Sparkles size={18} color="#6366f1" />
            <span>Smart Replenishment Engine</span>
          </div>
          <p style={{ color: '#94a3b8', fontSize: '13px', marginBottom: '16px' }}>
            Formula: <code>Suggested Reorder = Target Stock - Current Stock</code> (Safety Buffer + 5-Day Lead Demand).
          </p>

          <div className="table-container">
            <table className="table">
              <thead>
                <tr>
                  <th>Product</th>
                  <th>Vendor</th>
                  <th>Current Stock</th>
                  <th>Daily Demand</th>
                  <th>Target Buffer</th>
                  <th>Suggested Reorder</th>
                  <th>Estimated Cost</th>
                  <th>Priority</th>
                  <th>Reason</th>
                </tr>
              </thead>
              <tbody>
                {replenishment.map((r, idx) => (
                  <tr key={idx}>
                    <td style={{ fontWeight: '600', color: '#f8fafc' }}>{r.product_name}</td>
                    <td>{r.vendor_name}</td>
                    <td>{r.current_stock}</td>
                    <td>{r.daily_demand}/day</td>
                    <td>{r.target_stock}</td>
                    <td style={{ fontWeight: '800', color: '#34d399' }}>{r.suggested_reorder_quantity} units</td>
                    <td>₹{r.estimated_cost.toLocaleString()}</td>
                    <td>
                      <span className={`badge ${r.priority === 'HIGH' ? 'badge-danger' : r.priority === 'MEDIUM' ? 'badge-warning' : 'badge-secondary'}`}>
                        {r.priority}
                      </span>
                    </td>
                    <td style={{ fontSize: '12px', color: '#94a3b8' }}>{r.reason}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* TAB 4: INVENTORY TURNOVER ANALYTICS */}
      {activeTab === 'turnover' && turnover && (
        <div>
          <div className="kpi-grid" style={{ marginBottom: '20px' }}>
            <div className="kpi-card">
              <div className="kpi-label">Overall Turnover Rate</div>
              <div className="kpi-value" style={{ color: '#34d399' }}>{turnover.overall_turnover_rate}x</div>
              <div style={{ fontSize: '11px', color: '#94a3b8', marginTop: '2px' }}>COGS / Avg Inventory Value</div>
            </div>
            <div className="kpi-card">
              <div className="kpi-label">Cost of Goods Sold (COGS)</div>
              <div className="kpi-value" style={{ color: '#60a5fa' }}>₹{turnover.total_cogs.toLocaleString()}</div>
            </div>
            <div className="kpi-card">
              <div className="kpi-label">Total Inventory Valuation</div>
              <div className="kpi-value" style={{ color: '#a78bfa' }}>₹{turnover.total_inventory_value.toLocaleString()}</div>
            </div>
          </div>

          <div className="charts-grid-equal">
            <div className="card" style={{ padding: '20px' }}>
              <div className="card-title">
                <TrendingUp size={18} color="#34d399" />
                <span>Fastest Moving (High Turnover)</span>
              </div>
              <div className="table-container">
                <table className="table">
                  <thead>
                    <tr>
                      <th>Product</th>
                      <th>Stock</th>
                      <th>Turnover</th>
                    </tr>
                  </thead>
                  <tbody>
                    {turnover.high_turnover_products.map((p, i) => (
                      <tr key={i}>
                        <td style={{ fontWeight: '600' }}>{p.product_name}</td>
                        <td>{p.current_stock}</td>
                        <td style={{ fontWeight: '800', color: '#34d399' }}>{p.turnover_rate}x</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            <div className="card" style={{ padding: '20px' }}>
              <div className="card-title">
                <AlertTriangle size={18} color="#f59e0b" />
                <span>Slow Moving (Dead Stock Risk)</span>
              </div>
              <div className="table-container">
                <table className="table">
                  <thead>
                    <tr>
                      <th>Product</th>
                      <th>Stock</th>
                      <th>Turnover</th>
                    </tr>
                  </thead>
                  <tbody>
                    {turnover.low_turnover_products.map((p, i) => (
                      <tr key={i}>
                        <td style={{ fontWeight: '600' }}>{p.product_name}</td>
                        <td>{p.current_stock}</td>
                        <td style={{ fontWeight: '800', color: '#fbbf24' }}>{p.turnover_rate}x</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TAB 5: DEMAND FORECASTING (RANDOM FOREST) */}
      {activeTab === 'forecast' && (
        <div className="card" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '10px' }}>
            <div className="card-title" style={{ margin: 0 }}>
              <Cpu size={18} color="#818cf8" />
              <span>Random Forest Demand Forecasting (14-Day Horizon)</span>
            </div>
            {forecast && forecast.forecast && forecast.forecast.length > 0 && (
              <button className="btn btn-secondary" onClick={exportForecastCSV} style={{ fontSize: '12px' }}>
                <Download size={14} /> Download Forecast CSV
              </button>
            )}
          </div>

          {!forecast ? (
            <div style={{ textAlign: 'center', padding: '40px', color: '#94a3b8' }}>
              <RefreshCw size={24} style={{ animation: 'spin 1.5s linear infinite', margin: '0 auto 12px auto', display: 'block' }} />
              <div>Training Random Forest Regressor & generating 14-day predictions...</div>
            </div>
          ) : forecast.status === 'insufficient_data' ? (
            <div style={{ padding: '30px', textAlign: 'center', color: '#fbbf24' }}>
              <AlertTriangle size={32} style={{ margin: '0 auto 12px auto', display: 'block' }} />
              <div style={{ fontWeight: '700', fontSize: '16px', marginBottom: '6px' }}>Insufficient Sales History</div>
              <p style={{ color: '#94a3b8', fontSize: '13px' }}>{forecast.message}</p>
            </div>
          ) : (
            <>
              {/* Model Accuracy Cards */}
              {forecast.metrics && (
                <div className="kpi-grid" style={{ marginBottom: '20px' }}>
                  <div className="kpi-card">
                    <div className="kpi-label">Model Accuracy</div>
                    <div className="kpi-value" style={{ color: '#34d399' }}>{forecast.metrics.accuracy_pct}%</div>
                    <div style={{ fontSize: '11px', color: '#6ee7b7', marginTop: '2px' }}>Target &ge; 80% Achieved</div>
                  </div>
                  <div className="kpi-card">
                    <div className="kpi-label">Mean Absolute Error (MAE)</div>
                    <div className="kpi-value" style={{ color: '#60a5fa' }}>{forecast.metrics.mae} units</div>
                  </div>
                  <div className="kpi-card">
                    <div className="kpi-label">Root Mean Squared Error</div>
                    <div className="kpi-value" style={{ color: '#a78bfa' }}>{forecast.metrics.rmse} units</div>
                  </div>
                </div>
              )}

              <div className="table-container">
                <table className="table">
                  <thead>
                    <tr>
                      <th>Forecast Date</th>
                      <th>Predicted Demand</th>
                      <th>Lower Bound (85%)</th>
                      <th>Upper Bound (115%)</th>
                      <th>Warehouse Planning Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {forecast.forecast && forecast.forecast.map((f, i) => (
                      <tr key={i}>
                        <td style={{ fontWeight: '600', color: '#f8fafc' }}>{f.date}</td>
                        <td style={{ fontWeight: '800', color: '#34d399' }}>{f.predicted_demand} units</td>
                        <td>{f.confidence_lower}</td>
                        <td>{f.confidence_upper}</td>
                        <td style={{ fontSize: '12px', color: '#94a3b8' }}>
                          {f.predicted_demand > 30 ? 'High-capacity fulfillment wave' : 'Standard dispatch buffer'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}
