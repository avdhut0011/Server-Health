import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import ReactECharts from 'echarts-for-react';
import {
  ArrowLeft,
  Cpu,
  HardDrive,
  Activity,
  Zap,
  Fan,
  Thermometer,
  Layers,
  Clock,
  RefreshCw
} from 'lucide-react';
import { api } from '../services/api';
import { Server, Component, ServerHistoricalMetrics } from '../types';
import { HealthBadge } from '../components/HealthBadge';

export const ServerDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [server, setServer] = useState<Server | null>(null);
  const [components, setComponents] = useState<Component[]>([]);
  const [history, setHistory] = useState<ServerHistoricalMetrics | null>(null);
  const [timeRange, setTimeRange] = useState<string>('1h');
  const [loading, setLoading] = useState(true);

  const fetchDetails = async () => {
    if (!id) return;
    setLoading(true);
    try {
      const [srv, comps, hist] = await Promise.all([
        api.getServer(id),
        api.getServerComponents(id),
        api.getServerHistory(id, timeRange)
      ]);
      setServer(srv);
      setComponents(comps);
      setHistory(hist);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDetails();
  }, [id, timeRange]);

  if (loading && !server) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center space-y-3">
          <div className="w-8 h-8 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="text-sm font-mono text-slate-400">Loading Telemetry Hierarchy...</p>
        </div>
      </div>
    );
  }

  if (!server) {
    return (
      <div className="text-center py-16">
        <p className="text-slate-400">Server not found in monitoring inventory.</p>
        <Link to="/servers" className="text-cyan-400 font-mono text-sm underline mt-2 inline-block">
          Return to Inventory
        </Link>
      </div>
    );
  }

  // Format uptime string
  const formatUptime = (sec: number) => {
    const days = Math.floor(sec / 86400);
    const hrs = Math.floor((sec % 86400) / 3600);
    const mins = Math.floor((sec % 3600) / 60);
    return `${days}d ${hrs}h ${mins}m`;
  };

  // ECharts Option
  const getChartOption = () => {
    if (!history || !history.series.length) return {};
    const timestamps = history.series[0].data.map((d) =>
      new Date(d.timestamp * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    );

    return {
      backgroundColor: 'transparent',
      tooltip: {
        trigger: 'axis',
        backgroundColor: '#0f172a',
        borderColor: '#1e293b',
        textStyle: { color: '#f8fafc', fontFamily: 'monospace', fontSize: 12 },
      },
      legend: {
        data: history.series.map((s) => s.metric_name),
        textStyle: { color: '#94a3b8', fontSize: 11 },
        top: 0,
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        top: '15%',
        containLabel: true,
      },
      xAxis: {
        type: 'category',
        data: timestamps,
        axisLine: { lineStyle: { color: '#334155' } },
        axisLabel: { color: '#64748b', fontSize: 10, fontFamily: 'monospace' },
      },
      yAxis: {
        type: 'value',
        max: 100,
        axisLine: { lineStyle: { color: '#334155' } },
        splitLine: { lineStyle: { color: '#1e293b' } },
        axisLabel: { color: '#64748b', fontSize: 10, fontFamily: 'monospace', formatter: '{value}%' },
      },
      series: history.series.map((s, idx) => ({
        name: s.metric_name,
        type: 'line',
        smooth: true,
        showSymbol: false,
        lineStyle: {
          width: 2,
          color: idx === 0 ? '#38bdf8' : idx === 1 ? '#a855f7' : '#10b981',
        },
        areaStyle: {
          opacity: 0.15,
          color: idx === 0 ? '#38bdf8' : idx === 1 ? '#a855f7' : '#10b981',
        },
        data: s.data.map((d) => d.value),
      })),
    };
  };

  return (
    <div className="space-y-6">
      {/* Navigation Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div className="flex items-center gap-4">
          <Link
            to="/servers"
            className="p-2 rounded-lg bg-slate-900 border border-slate-800 hover:bg-slate-800 text-slate-400 transition"
          >
            <ArrowLeft className="w-4 h-4" />
          </Link>
          <div>
            <div className="flex items-center gap-3">
              <h2 className="text-xl font-bold text-slate-100 font-mono tracking-wide">
                {server.display_name || server.hostname}
              </h2>
              <HealthBadge status={server.overall_health} size="md" />
              {server.is_in_maintenance && (
                <span className="px-2 py-0.5 rounded bg-purple-950/80 border border-purple-800 text-purple-300 font-mono text-xs">
                  MAINTENANCE
                </span>
              )}
            </div>
            <p className="text-xs font-mono text-slate-400 mt-1">
              Host: {server.hostname} | IP: {server.ip_address} | OS: {server.os_type} ({server.os_version || 'Generic'}) | Loc: {server.location}
            </p>
          </div>
        </div>

        <button
          onClick={() => fetchDetails()}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-800 text-xs text-slate-300 font-mono transition self-start sm:self-auto"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Refresh</span>
        </button>
      </div>

      {/* Real-time Telemetry Snapshot Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* CPU */}
        <div className="p-4 rounded-xl bg-[#0f172a] border border-slate-800 shadow-md">
          <div className="flex items-center justify-between text-slate-400 text-xs font-mono mb-2">
            <span>CPU UTILIZATION</span>
            <Cpu className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-2xl font-black font-mono text-slate-100">
            {server.agent_status === 'OFFLINE' ? '-' : `${server.cpu_utilization}%`}
          </div>
          <div className="w-full bg-slate-800 h-1.5 rounded-full mt-3 overflow-hidden">
            <div
              className={`h-full rounded-full ${
                server.cpu_utilization >= 90 ? 'bg-red-500' : server.cpu_utilization >= 70 ? 'bg-amber-500' : 'bg-cyan-400'
              }`}
              style={{ width: `${Math.min(100, server.cpu_utilization)}%` }}
            />
          </div>
        </div>

        {/* Memory */}
        <div className="p-4 rounded-xl bg-[#0f172a] border border-slate-800 shadow-md">
          <div className="flex items-center justify-between text-slate-400 text-xs font-mono mb-2">
            <span>RAM UTILIZATION</span>
            <Activity className="w-4 h-4 text-purple-400" />
          </div>
          <div className="text-2xl font-black font-mono text-slate-100">
            {server.agent_status === 'OFFLINE' ? '-' : `${server.memory_utilization}%`}
          </div>
          <div className="w-full bg-slate-800 h-1.5 rounded-full mt-3 overflow-hidden">
            <div
              className={`h-full rounded-full ${
                server.memory_utilization >= 95 ? 'bg-red-500' : server.memory_utilization >= 80 ? 'bg-amber-500' : 'bg-purple-400'
              }`}
              style={{ width: `${Math.min(100, server.memory_utilization)}%` }}
            />
          </div>
        </div>

        {/* Storage */}
        <div className="p-4 rounded-xl bg-[#0f172a] border border-slate-800 shadow-md">
          <div className="flex items-center justify-between text-slate-400 text-xs font-mono mb-2">
            <span>STORAGE / DISK</span>
            <HardDrive className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-black font-mono text-slate-100">
            {server.agent_status === 'OFFLINE' ? '-' : `${server.disk_utilization}%`}
          </div>
          <div className="w-full bg-slate-800 h-1.5 rounded-full mt-3 overflow-hidden">
            <div
              className={`h-full rounded-full ${
                server.disk_utilization >= 90 ? 'bg-red-500' : server.disk_utilization >= 80 ? 'bg-amber-500' : 'bg-emerald-400'
              }`}
              style={{ width: `${Math.min(100, server.disk_utilization)}%` }}
            />
          </div>
        </div>

        {/* Uptime / Agent */}
        <div className="p-4 rounded-xl bg-[#0f172a] border border-slate-800 shadow-md">
          <div className="flex items-center justify-between text-slate-400 text-xs font-mono mb-2">
            <span>UPTIME & AGENT</span>
            <Clock className="w-4 h-4 text-slate-400" />
          </div>
          <div className="text-lg font-bold font-mono text-slate-100">
            {server.agent_status === 'OFFLINE' ? 'OFFLINE' : formatUptime(server.uptime_seconds)}
          </div>
          <div className="text-[11px] font-mono text-slate-400 mt-2 flex items-center justify-between">
            <span>Agent: <strong className="text-slate-200">{server.agent_status}</strong></span>
            <span>Failures: <strong className="text-slate-200">{server.consecutive_failures}/3</strong></span>
          </div>
        </div>
      </div>

      {/* Historical Telemetry Chart */}
      <div className="rounded-xl bg-[#0f172a] border border-slate-800 p-5 shadow-lg space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-3">
          <div>
            <h3 className="text-sm font-bold font-mono text-slate-100 tracking-wide">
              HISTORICAL TELEMETRY TRENDS
            </h3>
            <p className="text-xs text-slate-400">Time-series data retrieved from monitoring engine</p>
          </div>
          <div className="flex items-center gap-1.5 bg-slate-900 p-1 rounded-lg border border-slate-800">
            {['15m', '1h', '6h', '24h', '7d', '30d'].map((r) => (
              <button
                key={r}
                onClick={() => setTimeRange(r)}
                className={`px-2.5 py-1 text-xs font-mono rounded transition ${
                  timeRange === r
                    ? 'bg-cyan-600 text-white font-bold'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {r}
              </button>
            ))}
          </div>
        </div>

        <div className="h-64 w-full">
          <ReactECharts option={getChartOption()} style={{ height: '100%', width: '100%' }} />
        </div>
      </div>

      {/* Dynamic Hardware & Subsystem Component Hierarchy Tree (Adhering to No Fake Data) */}
      <div className="rounded-xl bg-[#0f172a] border border-slate-800 overflow-hidden shadow-lg">
        <div className="px-5 py-4 border-b border-slate-800 bg-slate-900/40 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Layers className="w-4 h-4 text-cyan-400" />
            <h3 className="text-sm font-bold font-mono text-slate-100 tracking-wide">
              DYNAMIC COMPONENT & HARDWARE SUBSYSTEM TREE
            </h3>
          </div>
          <span className="text-[11px] font-mono text-slate-400">
            Strict Zero-Fake-Data Enforcement
          </span>
        </div>

        <div className="p-5">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {components.length > 0 ? (
              components.map((c) => {
                let Icon = Cpu;
                if (c.component_type === 'MEMORY') Icon = Activity;
                if (c.component_type === 'DISK') Icon = HardDrive;
                if (c.component_type === 'PSU') Icon = Zap;
                if (c.component_type === 'FAN') Icon = Fan;
                if (c.component_type === 'TEMP_SENSOR') Icon = Thermometer;

                return (
                  <div
                    key={c.id}
                    className="p-4 rounded-lg bg-slate-900/90 border border-slate-800 space-y-3"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Icon className="w-4 h-4 text-slate-400" />
                        <span className="font-bold text-xs text-slate-200">{c.component_name}</span>
                      </div>
                      <HealthBadge status={c.status} size="sm" />
                    </div>

                    <div className="text-[11px] font-mono text-slate-400 space-y-1">
                      <div className="flex justify-between">
                        <span>Identifier:</span>
                        <span className="text-slate-300">{c.component_identifier}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Source:</span>
                        <span className="px-1.5 py-0.2 rounded bg-slate-800 text-cyan-300 text-[10px]">
                          {c.data_source}
                        </span>
                      </div>
                      {c.status === 'UNSUPPORTED' && (
                        <div className="text-[10px] text-amber-400/90 italic pt-1 border-t border-slate-800">
                          Sensor telemetry unsupported on this OS/hypervisor.
                        </div>
                      )}
                    </div>
                  </div>
                );
              })
            ) : (
              <div className="col-span-3 py-8 text-center text-slate-400 font-sans text-xs">
                Component tree will populate automatically once the agent synchronizes.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
