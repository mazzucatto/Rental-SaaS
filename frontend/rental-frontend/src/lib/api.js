// Configuração da API
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

class ApiClient {
  constructor() {
    this.baseURL = API_BASE_URL;
    this.token = localStorage.getItem('access_token');
  }

  setToken(token) {
    this.token = token;
    if (token) {
      localStorage.setItem('access_token', token);
    } else {
      localStorage.removeItem('access_token');
    }
  }

  getHeaders() {
    const headers = {
      'Content-Type': 'application/json',
    };

    if (this.token) {
      headers.Authorization = `Bearer ${this.token}`;
    }

    return headers;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: this.getHeaders(),
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (response.status === 401) {
        // Token expirado, tentar renovar
        const refreshed = await this.refreshToken();
        if (refreshed) {
          // Tentar novamente com o novo token
          config.headers = this.getHeaders();
          const retryResponse = await fetch(url, config);
          return await this.handleResponse(retryResponse);
        } else {
          // Falha na renovação, redirecionar para login
          this.logout();
          throw new Error('Sessão expirada');
        }
      }

      return await this.handleResponse(response);
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  }

  async handleResponse(response) {
    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.error || 'Erro na requisição');
    }

    return data;
  }

  async refreshToken() {
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) return false;

    try {
      const response = await fetch(`${this.baseURL}/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${refreshToken}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        this.setToken(data.access_token);
        return true;
      }
    } catch (error) {
      console.error('Refresh token error:', error);
    }

    return false;
  }

  logout() {
    this.setToken(null);
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    localStorage.removeItem('tenant');
    window.location.href = '/login';
  }

  // Métodos de autenticação
  async login(email, password) {
    const response = await this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });

    if (response.access_token) {
      this.setToken(response.access_token);
      localStorage.setItem('refresh_token', response.refresh_token);
      localStorage.setItem('user', JSON.stringify(response.user));
      localStorage.setItem('tenant', JSON.stringify(response.tenant));
    }

    return response;
  }

  async register(userData) {
    const response = await this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });

    if (response.access_token) {
      this.setToken(response.access_token);
      localStorage.setItem('refresh_token', response.refresh_token);
      localStorage.setItem('user', JSON.stringify(response.user));
      localStorage.setItem('tenant', JSON.stringify(response.tenant));
    }

    return response;
  }

  async getCurrentUser() {
    return await this.request('/auth/me');
  }

  // Métodos para itens de locação
  async getItems(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return await this.request(`/rental/items?${queryString}`);
  }

  async getItem(id) {
    return await this.request(`/rental/items/${id}`);
  }

  async createItem(itemData) {
    return await this.request('/rental/items', {
      method: 'POST',
      body: JSON.stringify(itemData),
    });
  }

  async updateItem(id, itemData) {
    return await this.request(`/rental/items/${id}`, {
      method: 'PUT',
      body: JSON.stringify(itemData),
    });
  }

  // Métodos para categorias
  async getCategories() {
    return await this.request('/rental/categories');
  }

  async createCategory(categoryData) {
    return await this.request('/rental/categories', {
      method: 'POST',
      body: JSON.stringify(categoryData),
    });
  }

  // Métodos para clientes
  async getCustomers(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return await this.request(`/rental/customers?${queryString}`);
  }

  async createCustomer(customerData) {
    return await this.request('/rental/customers', {
      method: 'POST',
      body: JSON.stringify(customerData),
    });
  }

  // Métodos para reservas
  async getReservations(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return await this.request(`/rental/reservations?${queryString}`);
  }

  async createReservation(reservationData) {
    return await this.request('/rental/reservations', {
      method: 'POST',
      body: JSON.stringify(reservationData),
    });
  }

  async confirmReservation(id) {
    return await this.request(`/rental/reservations/${id}/confirm`, {
      method: 'POST',
    });
  }

  // Métodos para calendário
  async getCalendar(startDate, endDate) {
    return await this.request(`/rental/calendar?start_date=${startDate}&end_date=${endDate}`);
  }

  // Métodos para dashboard
  async getDashboard() {
    return await this.request('/rental/dashboard');
  }

  // Métodos para tenant
  async getTenant() {
    return await this.request('/tenants/');
  }

  async updateTenant(tenantData) {
    return await this.request('/tenants/', {
      method: 'PUT',
      body: JSON.stringify(tenantData),
    });
  }

  async getTenantStats() {
    return await this.request('/tenants/stats');
  }
}

export const api = new ApiClient();
export default api;

