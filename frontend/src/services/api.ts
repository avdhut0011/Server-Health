import axios from 'axios';
import {
  DashboardSummary,
  Server,
  Alert,
  ServerHistoricalMetrics,
  MaintenanceWindow,
  AuditLog,
  ZabbixStatus,
  Component
} from '../types';

const API_BASE = '/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor to attach JWT token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('shm_access_token');
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const api = {
  // Auth
  async login(username: string, password: string) {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);
    const res = await apiClient.post('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    });
    return res.data;
  },

  // Dashboard
  async getDashboardSummary(): Promise<DashboardSummary> {
    const res = await apiClient.get<DashboardSummary>('/dashboard/summary');
    return res.data;
  },

  // Servers
  async getServers(params?: { environment?: string; health?: string; os_type?: string; search?: string }): Promise<Server[]> {
    const res = await apiClient.get<Server[]>('/servers', { params });
    return res.data;
  },

  async getServer(id: string): Promise<Server> {
    const res = await apiClient.get<Server>(`/servers/${id}`);
    return res.data;
  },

  async createServer(serverData: Partial<Server>): Promise<Server> {
    const res = await apiClient.post<Server>('/servers', serverData);
    return res.data;
  },

  async updateServer(id: string, serverData: Partial<Server>): Promise<Server> {
    const res = await apiClient.put<Server>(`/servers/${id}`, serverData);
    return res.data;
  },

  async deleteServer(id: string): Promise<void> {
    await apiClient.delete(`/servers/${id}`);
  },

  async getServerComponents(id: string): Promise<Component[]> {
    const res = await apiClient.get<Component[]>(`/servers/${id}/components`);
    return res.data;
  },

  async getServerHistory(id: string, timeRange: string = '1h'): Promise<ServerHistoricalMetrics> {
    const res = await apiClient.get<ServerHistoricalMetrics>(`/servers/${id}/history`, {
      params: { time_range: timeRange }
    });
    return res.data;
  },

  // Alerts
  async getAlerts(params?: { status_filter?: string; severity?: string; server_id?: string }): Promise<Alert[]> {
    const res = await apiClient.get<Alert[]>('/alerts', { params });
    return res.data;
  },

  async acknowledgeAlert(id: string, note?: string): Promise<Alert> {
    const res = await apiClient.post<Alert>(`/alerts/${id}/acknowledge`, { note });
    return res.data;
  },

  // Maintenance
  async getMaintenanceWindows(): Promise<MaintenanceWindow[]> {
    const res = await apiClient.get<MaintenanceWindow[]>('/maintenance');
    return res.data;
  },

  async createMaintenanceWindow(data: Partial<MaintenanceWindow>): Promise<MaintenanceWindow> {
    const res = await apiClient.post<MaintenanceWindow>('/maintenance', data);
    return res.data;
  },

  async deleteMaintenanceWindow(id: string): Promise<void> {
    await apiClient.delete(`/maintenance/${id}`);
  },

  // Audit Logs
  async getAuditLogs(params?: { action?: string; username?: string }): Promise<AuditLog[]> {
    const res = await apiClient.get<AuditLog[]>('/audit-logs', { params });
    return res.data;
  },

  // System & Zabbix
  async getZabbixStatus(): Promise<ZabbixStatus> {
    const res = await apiClient.get<ZabbixStatus>('/system/zabbix-status');
    return res.data;
  },

  async sendTestEmail(recipient: string): Promise<{ status: string; message: string }> {
    const res = await apiClient.post('/notifications/send-test-email', { recipient });
    return res.data;
  }
};
