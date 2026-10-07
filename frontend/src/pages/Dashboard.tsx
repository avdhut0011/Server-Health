import React from 'react';
import { Link } from 'react-router-dom';
import {
  Server as ServerIcon,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  HelpCircle,
  ArrowUpRight
} from 'lucide-react';
import { DashboardSummary } from '../types';
import { HealthBadge } from '../components/HealthBadge';

interface DashboardProps {
  summary: DashboardSummary | null;
  loading: boolean;
  onRefresh?: () => void;
}

export const Dashboard: React.FC<DashboardProps> = ({ summary, loading }) => {
  if (loading && !summary) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center space-y-3">
          <div className="w-8 h-8 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="text-sm font-mono text-slate-400">Loading NOC Telemetry Matrix...</p>
        </div>
      </div>
    );
  }

  const hs = summary?.health_summary || {
    total_servers: 0,
    healthy: 0,
    warning: 0,
    critical: 0,
    down: 0,
    in_maintenance: 0,
  };

  return (
    <div className="space-y-6">
      {/* Top Banner / Health Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        {/* Total Servers */}
        <div className="p-4 rounded-xl bg-slate-900/90 border border-slate-800 shadow-lg">
          <div className="flex items-center justify-between text-slate-400 text-xs font-mono mb-2">
            <span>TOTAL SERVERS</span>
            <ServerIcon className="w-4 h-4 text-slate-400" />
          </div>
          <div className="text-2xl font-black text-slate-100 font-mono">{hs.total_servers}</div>
          <div className="text-[11px] text-slate-400 mt-1">{hs.in_maintenance} in maintenance</div>
        </div>

        {/* Healthy */}
        <div className="p-4 rounded-xl bg-emerald-950/20 border border-emerald-800/40 shadow-lg">
          <div className="flex items-center justify-between text-emerald-400 text-xs font-mono mb-2">
            <span>HEALTHY</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-black text-emerald-400 font-mono">{hs.healthy}</div>
          <div className="text-[11px] text-emerald-500/80 mt-1">Operating normally</div>
        </div>

        {/* Warning */}
        <div className="p-4 rounded-xl bg-amber-950/20 border border-amber-800/40 shadow-lg">
          <div className="flex items-center justify-between text-amber-400 text-xs font-mono mb-2">
            <span>WARNING</span>
            <AlertTriangle className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-black text-amber-400 font-mono">{hs.warning}</div>
          <div className="text-[11px] text-amber-500/80 mt-1">Threshold near limits</div>
        </div>

        {/* Critical */}
        <div className="p-4 rounded-xl bg-red-950/20 border border-red-800/40 shadow-lg">
          <div className="flex items-center justify-between text-red-400 text-xs font-mono mb-2">
            <span>CRITICAL</span>
            <XCircle className="w-4 h-4 text-red-400" />
          </div>
          <div className="text-2xl font-black text-red-400 font-mono">{hs.critical}</div>
          <div className="text-[11px] text-red-500/80 mt-1">Action required immediately</div>
        </div>

        {/* Down */}
        <div className="p-4 rounded-xl bg-slate-900 border border-slate-700 shadow-lg">
          <div className="flex items-center justify-between text-slate-400 text-xs font-mono mb-2">
            <span>OFFLINE / DOWN</span>
            <HelpCircle className="w-4 h-4 text-slate-400" />
          </div>
          <div className="text-2xl font-black text-slate-300 font-mono">{hs.down}</div>
          <div className="text-[11px] text-slate-400 mt-1">&gt; 3 failed heartbeats</div>
        </div>
      </div>

      {/* Main Monitoring Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Real-time Server Health Matrix Table (2 cols) */}
        <div className="lg:col-span-2 rounded-xl bg-[#0f172a] border border-slate-800 overflow-hidden shadow-lg">
          <div className="px-5 py-4 border-b border-slate-800 flex items-center justify-between bg-slate-900/40">
            <div>
              <h2 className="text-sm font-bold text-slate-100 tracking-wide font-mono">
                SERVER INFRASTRUCTURE MATRIX
              </h2>
              <p className="text-xs text-slate-400">Live operational telemetry status</p>
            </div>
            <Link
              to="/servers"
              className="text-xs text-cyan-400 hover:text-cyan-300 flex items-center gap-1 font-semibold transition"
            >
              <span>View Full Inventory</span>
              <ArrowUpRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-900/80 text-slate-400 font-mono uppercase tracking-wider border-b border-slate-800">
                <tr>
                  <th className="py-3 px-4">Server</th>
                  <th className="py-3 px-4">OS / IP</th>
                  <th className="py-3 px-4 text-center">CPU</th>
                  <th className="py-3 px-4 text-center">RAM</th>
                  <th className="py-3 px-4 text-center">Disk</th>
                  <th className="py-3 px-4 text-center">Status</th>
                  <th className="py-3 px-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono">
                {summary?.servers && summary.servers.length > 0 ? (
                  summary.servers.map((srv) => (
                    <tr key={srv.id} className="hover:bg-slate-800/40 transition">
                      <td className="py-3 px-4">
                        <div className="font-bold text-slate-200">{srv.display_name || srv.hostname}</div>
                        <div className="text-[10px] text-slate-400">{srv.hostname}</div>
                      </td>
                      <td className="py-3 px-4">
                        <div className="text-slate-300">{srv.os_type}</div>
                        <div className="text-[10px] text-slate-400">{srv.ip_address}</div>
                      </td>
                      <td className="py-3 px-4 text-center">
                        <span className={`font-bold ${srv.cpu_utilization >= 90 ? 'text-red-400' : srv.cpu_utilization >= 70 ? 'text-amber-400' : 'text-slate-300'}`}>
                          {srv.agent_status === 'OFFLINE' ? '-' : `${srv.cpu_utilization}%`}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-center">
                        <span className={`font-bold ${srv.memory_utilization >= 95 ? 'text-red-400' : srv.memory_utilization >= 80 ? 'text-amber-400' : 'text-slate-300'}`}>
                          {srv.agent_status === 'OFFLINE' ? '-' : `${srv.memory_utilization}%`}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-center">
                        <span className={`font-bold ${srv.disk_utilization >= 90 ? 'text-red-400' : srv.disk_utilization >= 80 ? 'text-amber-400' : 'text-slate-300'}`}>
                          {srv.agent_status === 'OFFLINE' ? '-' : `${srv.disk_utilization}%`}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-center">
                        <HealthBadge status={srv.overall_health} size="sm" />
                      </td>
                      <td className="py-3 px-4 text-right">
                        <Link
                          to={`/servers/${srv.id}`}
                          className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-cyan-400 border border-slate-700 transition"
                        >
                          Inspect
                        </Link>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={7} className="py-8 text-center text-slate-400 font-sans">
                      No monitored servers registered yet.{' '}
                      <Link to="/servers" className="text-cyan-400 underline font-semibold">
                        Add a Windows or Linux server
                      </Link>
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Active Operational Alerts Sidebar (1 col) */}
        <div className="rounded-xl bg-[#0f172a] border border-slate-800 overflow-hidden shadow-lg flex flex-col">
          <div className="px-5 py-4 border-b border-slate-800 flex items-center justify-between bg-slate-900/40">
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-amber-400" />
              <h2 className="text-sm font-bold text-slate-100 tracking-wide font-mono">
                ACTIVE ALERTS ({summary?.active_alerts_count || 0})
              </h2>
            </div>
            <Link to="/alerts" className="text-xs text-cyan-400 hover:text-cyan-300 font-semibold">
              Console
            </Link>
          </div>

          <div className="p-4 space-y-3 overflow-y-auto max-h-[500px]">
            {summary?.active_alerts && summary.active_alerts.length > 0 ? (
              summary.active_alerts.map((al) => (
                <div
                  key={al.id}
                  className="p-3.5 rounded-lg bg-slate-900/90 border border-slate-800 hover:border-slate-700 transition space-y-2"
                >
                  <div className="flex items-center justify-between">
                    <HealthBadge status={al.severity} size="sm" />
                    <span className="text-[10px] font-mono text-slate-400">
                      {new Date(al.started_at).toLocaleTimeString()}
                    </span>
                  </div>
                  <div>
                    <div className="text-xs font-bold text-slate-200">
                      {al.server_display_name || al.server_hostname}
                    </div>
                    <div className="text-xs text-slate-400 mt-0.5">{al.problem_title}</div>
                  </div>
                  <div className="flex items-center justify-between text-[11px] font-mono text-slate-400 pt-1 border-t border-slate-800/80">
                    <span>Val: <strong className="text-slate-200">{al.trigger_value}</strong></span>
                    <span>Thresh: <strong className="text-slate-200">{al.threshold_value}</strong></span>
                  </div>
                </div>
              ))
            ) : (
              <div className="py-12 text-center text-slate-400 space-y-2">
                <CheckCircle2 className="w-8 h-8 text-emerald-400 mx-auto" />
                <p className="text-xs font-medium text-slate-300">All Systems Nominal</p>
                <p className="text-[11px] text-slate-400">No active warning or critical alerts</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
