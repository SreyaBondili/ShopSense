// API Client for ShopSense FastAPI Backend

const API_BASE = '';

export const api = {
  async request(endpoint, options = {}) {
    const token = localStorage.getItem('shopsense_token');
    const headers = {
      'Content-Type': 'application/json',
      ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
      ...options.headers,
    };

    const res = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers,
    });

    if (!res.ok) {
      let errorMsg = `HTTP Error ${res.status}`;
      try {
        const err = await res.json();
        if (typeof err.detail === 'string') {
          errorMsg = err.detail;
        } else if (Array.isArray(err.detail)) {
          errorMsg = err.detail.join(', ');
        } else if (err.detail && typeof err.detail === 'object') {
          errorMsg = JSON.stringify(err.detail);
        }
      } catch (e) {
        // keep fallback message
      }
      throw new Error(errorMsg);
    }

    return res.json();
  },

  // Auth
  async login(email, password) {
    const data = await this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    localStorage.setItem('shopsense_token', data.access_token);
    localStorage.setItem('shopsense_user', JSON.stringify({
      email: data.email,
      name: data.full_name,
      role: data.role,
      vendor_id: data.vendor_id,
    }));
    return data;
  },

  async register(userData) {
    return this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  },

  logout() {
    localStorage.removeItem('shopsense_token');
    localStorage.removeItem('shopsense_user');
  },

  getUser() {
    try {
      const u = localStorage.getItem('shopsense_user');
      return u ? JSON.parse(u) : null;
    } catch {
      return null;
    }
  },

  // Analytics
  async getSummary(vendorId = null) {
    const q = vendorId ? `?vendor_id=${vendorId}` : '';
    return this.request(`/api/analytics/summary${q}`);
  },

  async getRevenueTrend(vendorId = null) {
    const q = vendorId ? `?vendor_id=${vendorId}` : '';
    return this.request(`/api/analytics/revenue-trend${q}`);
  },

  async getCategoryPerformance(vendorId = null) {
    const q = vendorId ? `?vendor_id=${vendorId}` : '';
    return this.request(`/api/analytics/category-performance${q}`);
  },

  async getVendorPerformance() {
    return this.request('/api/analytics/vendor-performance');
  },

  async getProductPerformance(vendorId = null) {
    const q = vendorId ? `?vendor_id=${vendorId}` : '';
    return this.request(`/api/analytics/product-performance${q}`);
  },

  // Vendors
  async getVendors(params = {}) {
    const q = new URLSearchParams();
    if (params.search) q.append('search', params.search);
    if (params.category && params.category !== 'All') q.append('category', params.category);
    if (params.status && params.status !== 'All') q.append('status', params.status);
    const qs = q.toString() ? `?${q.toString()}` : '';
    return this.request(`/api/vendors${qs}`);
  },

  async createVendor(data) {
    return this.request('/api/vendors', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async updateVendor(id, data) {
    return this.request(`/api/vendors/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  async deleteVendor(id) {
    return this.request(`/api/vendors/${id}`, {
      method: 'DELETE',
    });
  },

  // Products
  async getProducts(params = {}) {
    const q = new URLSearchParams();
    if (params.search) q.append('search', params.search);
    if (params.category && params.category !== 'All') q.append('category', params.category);
    if (params.vendor_id) q.append('vendor_id', params.vendor_id);
    const qs = q.toString() ? `?${q.toString()}` : '';
    return this.request(`/api/products${qs}`);
  },

  async createProduct(data) {
    return this.request('/api/products', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async updateProduct(id, data) {
    return this.request(`/api/products/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  async deleteProduct(id) {
    return this.request(`/api/products/${id}`, {
      method: 'DELETE',
    });
  },

  // Inventory
  async getInventory(status = 'All') {
    const q = status && status !== 'All' ? `?status=${status}` : '';
    return this.request(`/api/inventory${q}`);
  },

  async updateInventory(productId, data) {
    return this.request(`/api/inventory/${productId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  async getInventoryAlerts() {
    return this.request('/api/inventory/alerts');
  },

  async getInventoryTurnover() {
    return this.request('/api/inventory/turnover');
  },

  async getInventoryForecast(productId = null, horizon = 14) {
    const q = new URLSearchParams();
    if (productId) q.append('product_id', productId);
    if (horizon) q.append('horizon', horizon);
    const qs = q.toString() ? `?${q.toString()}` : '';
    return this.request(`/api/inventory/forecast${qs}`);
  },

  async getInventoryReplenishment(leadTimeDays = 5) {
    return this.request(`/api/inventory/replenishment?lead_time_days=${leadTimeDays}`);
  },

  // Customer Analytics (Milestone 2)
  async getCustomerBehavior() {
    return this.request('/api/analytics/customers');
  },

  async getCustomerSegments() {
    return this.request('/api/analytics/segments');
  },

  // Recommendations (Milestone 2)
  async getRecommendations(limit = 5) {
    return this.request(`/api/recommendations?limit=${limit}`);
  },

  async getRecommendationEvaluation(k = 5) {
    return this.request(`/api/recommendations/evaluation?k=${k}`);
  },

  // Transactions
  async getTransactions() {
    return this.request('/api/transactions');
  },

  async createTransaction(data) {
    return this.request('/api/transactions', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  // Milestone 3: Advanced Revenue & Benchmarking
  async getAdvancedRevenue(vendorId = null) {
    const q = vendorId ? `?vendor_id=${vendorId}` : '';
    return this.request(`/api/analytics/revenue${q}`);
  },

  // Milestone 3: MLflow Model Tracking & Operations
  async getMLflowStatus() {
    return this.request('/api/analytics/mlflow-status');
  },

  async retrainMLflowModel() {
    return this.request('/api/analytics/mlflow-retrain', {
      method: 'POST',
    });
  },

  // Milestone 3: Workflow Automation & APScheduler
  async getSchedulerStatus() {
    return this.request('/api/scheduler/status');
  },

  async triggerSchedulerJob(jobType = 'all') {
    return this.request(`/api/scheduler/trigger?job_type=${encodeURIComponent(jobType)}`, {
      method: 'POST',
    });
  },

  // Milestone 3: Report Downloads (PDF & Excel)
  async downloadReport(reportType = 'revenue', format = 'pdf') {
    const token = localStorage.getItem('shopsense_token');
    const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
    const res = await fetch(`/api/reports/${format}?type=${encodeURIComponent(reportType)}`, { headers });
    if (!res.ok) {
      throw new Error(`Failed to download ${format.toUpperCase()} report: ${res.statusText}`);
    }
    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ShopSense_${reportType}_Report.${format === 'pdf' ? 'pdf' : 'xlsx'}`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  },
};
