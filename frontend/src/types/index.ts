export type ServerHealth = 'HEALTHY' | 'WARNING' | 'CRITICAL' | 'DOWN';
export type AgentStatus = 'ONLINE' | 'OFFLINE' | 'UNKNOWN';
export type AlertSeverity = 'INFO' | 'WARNING' | 'CRITICAL' | 'DOWN';
export type AlertStatus = 'ACTIVE' | 'ACKNOWLEDGED' | 'RECOVERED' | 'SUPPRESSED';

export interface User {
  id: string;
  username: string;
  email: string;
  role: 'ADMIN' | 'OPERATOR' | 'VIEWER';
  full_name?: string;
}

export interface ServerGroup {
  id: string;
  name: string;
  description?: string;
  environment: string;
  created_at: string;
}

export interface Component {
  id: string;
  server_id: string;
  component_type: 'CPU' | 'MEMORY' | 'DISK' | 'RAID_CONTROLLER' | 'PHYSICAL_DISK' | 'PSU' | 'FAN' | 'TEMP_SENSOR' | 'NIC';
  component_name: string;
  component_identifier: string;
  status: 'HEALTHY' | 'WARNING' | 'CRITICAL' | 'FAILED' | 'NOT_PRESENT' | 'UNSUPPORTED';
  vendor?: string;
  model?: string;
  serial_number?: string;
  metrics_metadata: Record<string, any>;
  data_source: 'ZABBIX_AGENT' | 'IPMI' | 'SNMP' | 'REDFISH' | 'OS';
  updated_at: string;
}

export interface Server {
  id: string;
  group_id?: string;
  hostname: string;
  display_name: string;
  ip_address: string;
  os_type: 'WINDOWS' | 'LINUX';
  os_version?: string;
  environment: string;
  location: string;
  rack?: string;
  vendor?: string;
  model?: string;
  serial_number?: string;
  zabbix_hostid?: string;
  agent_status: AgentStatus;
  overall_health: ServerHealth;
  consecutive_failures: number;
  is_in_maintenance: boolean;
  last_seen_at?: string;
  uptime_seconds: number;
  cpu_utilization: number;
  memory_utilization: number;
  disk_utilization: number;
  network_status: string;
  custom_thresholds?: Record<string, any>;
  created_at: string;
  updated_at: string;
  group?: ServerGroup;
  components?: Component[];
}

export interface AlertHistory {
  id: string;
  from_state?: string;
  to_state: string;
  current_value?: string;
  note?: string;
  created_at: string;
}

export interface Alert {
  id: string;
  server_id: string;
  component_id?: string;
  dedup_key: string;
  problem_title: string;
  metric_name?: string;
  trigger_value?: string;
  threshold_value?: string;
  severity: AlertSeverity;
  status: AlertStatus;
  acknowledged_by?: string;
  acknowledged_at?: string;
  acknowledge_note?: string;
  started_at: string;
  recovered_at?: string;
  duration_seconds: number;
  notification_count: number;
  last_notified_at?: string;
  updated_at: string;
  server_hostname?: string;
  server_display_name?: string;
  history?: AlertHistory[];
}

export interface HealthSummary {
  total_servers: number;
  healthy: number;
  warning: number;
  critical: number;
  down: number;
  in_maintenance: number;
}

export interface DashboardSummary {
  health_summary: HealthSummary;
  active_alerts_count: number;
  unacknowledged_alerts_count: number;
  servers: Server[];
  active_alerts: Alert[];
}

export interface MetricHistoryPoint {
  timestamp: number;
  value: number;
}

export interface MetricSeries {
  metric_name: string;
  unit: string;
  data: MetricHistoryPoint[];
}

export interface ServerHistoricalMetrics {
  server_id: string;
  time_range: string;
  series: MetricSeries[];
}

export interface MaintenanceWindow {
  id: string;
  server_id: string;
  title: string;
  description?: string;
  start_time: string;
  end_time: string;
  suppress_alerts: boolean;
  created_by?: string;
  created_at: string;
  server_hostname?: string;
}

export interface AuditLog {
  id: string;
  user_id?: string;
  username?: string;
  action: string;
  resource_type?: string;
  resource_id?: string;
  client_ip?: string;
  old_values?: Record<string, any>;
  new_values?: Record<string, any>;
  created_at: string;
}

export interface ZabbixStatus {
  connected: boolean;
  url: string;
  api_version?: string;
  authenticated: boolean;
  latency_ms?: number;
  error_message?: string;
}
