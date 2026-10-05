import {
  Analysis,
  AnalysisListResponse,
  AuthTokens,
  SupportedLanguage,
  User,
} from '../types';

const API_BASE = '/api/v1';

class ApiService {
  private accessToken: string | null = null;
  private refreshToken: string | null = null;

  constructor() {
    this.accessToken = localStorage.getItem('devlens_access_token');
    this.refreshToken = localStorage.getItem('devlens_refresh_token');
  }

  public setTokens(access: string, refresh?: string) {
    this.accessToken = access;
    localStorage.setItem('devlens_access_token', access);
    if (refresh) {
      this.refreshToken = refresh;
      localStorage.setItem('devlens_refresh_token', refresh);
    }
  }

  public clearTokens() {
    this.accessToken = null;
    this.refreshToken = null;
    localStorage.removeItem('devlens_access_token');
    localStorage.removeItem('devlens_refresh_token');
  }

  public isAuthenticated(): boolean {
    return !!this.accessToken;
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...((options.headers as Record<string, string>) || {}),
    };

    if (this.accessToken) {
      headers['Authorization'] = `Bearer ${this.accessToken}`;
    }

    let response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers,
    });

    // Auto-refresh token if 401 and refresh token exists
    if (response.status === 401 && this.refreshToken && !endpoint.includes('/auth/')) {
      const refreshed = await this.tryRefreshToken();
      if (refreshed) {
        headers['Authorization'] = `Bearer ${this.accessToken}`;
        response = await fetch(`${API_BASE}${endpoint}`, {
          ...options,
          headers,
        });
      }
    }

    if (!response.ok) {
      let errorMsg = `HTTP Error ${response.status}`;
      try {
        const errorData = await response.json();
        errorMsg = errorData.detail || errorData.message || errorMsg;
      } catch {
        // Fallback to status text
        errorMsg = response.statusText || errorMsg;
      }
      throw new Error(errorMsg);
    }

    return response.json() as Promise<T>;
  }

  private async tryRefreshToken(): Promise<boolean> {
    if (!this.refreshToken) return false;
    try {
      const res = await fetch(`${API_BASE}/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: this.refreshToken }),
      });
      if (res.ok) {
        const data: AuthTokens = await res.json();
        this.setTokens(data.access_token);
        return true;
      } else {
        this.clearTokens();
        return false;
      }
    } catch {
      this.clearTokens();
      return false;
    }
  }

  // --- Auth Endpoints ---

  public async register(email: string, password: string, fullName?: string): Promise<User> {
    return this.request<User>('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password, full_name: fullName }),
    });
  }

  public async login(email: string, password: string): Promise<AuthTokens> {
    const data = await this.request<AuthTokens>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    // If backend returns cookie for refresh token or token object
    this.setTokens(data.access_token);
    return data;
  }

  public async getMe(): Promise<User> {
    return this.request<User>('/auth/me');
  }

  public async logout(): Promise<{ message: string }> {
    try {
      if (this.refreshToken) {
        await this.request<{ message: string }>('/auth/logout', {
          method: 'POST',
          body: JSON.stringify({ refresh_token: this.refreshToken }),
        });
      }
    } finally {
      this.clearTokens();
    }
    return { message: 'Logged out successfully' };
  }

  public async deleteAccount(): Promise<{ message: string }> {
    const res = await this.request<{ message: string }>('/auth/account', {
      method: 'DELETE',
    });
    this.clearTokens();
    return res;
  }

  // --- Analysis Endpoints ---

  public async analyzeCode(
    code: string,
    language: SupportedLanguage,
    title?: string,
    enableAi = true
  ): Promise<Analysis> {
    return this.request<Analysis>('/analyses/', {
      method: 'POST',
      body: JSON.stringify({
        code,
        language,
        title: title || `${language.toUpperCase()} Analysis`,
        enable_ai: enableAi,
      }),
    });
  }

  public async listAnalyses(page = 1, pageSize = 20): Promise<AnalysisListResponse> {
    return this.request<AnalysisListResponse>(`/analyses/?page=${page}&page_size=${pageSize}`);
  }

  public async getAnalysis(id: string): Promise<Analysis> {
    return this.request<Analysis>(`/analyses/${id}`);
  }

  public async deleteAnalysis(id: string): Promise<{ message: string }> {
    return this.request<{ message: string }>(`/analyses/${id}`, {
      method: 'DELETE',
    });
  }

  public async exportAnalysis(id: string, format: 'json' | 'markdown'): Promise<Blob> {
    const headers: Record<string, string> = {};
    if (this.accessToken) {
      headers['Authorization'] = `Bearer ${this.accessToken}`;
    }

    const response = await fetch(`${API_BASE}/analyses/${id}/export?format=${format}`, {
      headers,
    });

    if (!response.ok) {
      throw new Error(`Export failed with HTTP ${response.status}`);
    }

    return response.blob();
  }

  public async checkHealth(): Promise<{ status: string; version: string }> {
    return this.request<{ status: string; version: string }>('/health');
  }
}

export const api = new ApiService();
