import React, { useState, useEffect } from 'react';
import { Activity, RefreshCw, LogOut, User as UserIcon } from 'lucide-react';
import { api } from '../services/api';
import { ZabbixStatus } from '../types';

interface NavbarProps {
  wsConnected: boolean;
  onRefresh?: () => void;
  userRole?: string;
  onLogout: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ wsConnected, onRefresh, userRole = 'ADMIN', onLogout }) => {
  const [zabbixStatus, setZabbixStatus] = useState<ZabbixStatus | null>(null);

  useEffect(() => {
    const fetchZabbix = async () => {
      try {
        const s = await api.getZabbixStatus();
        setZabbixStatus(s);
      } catch {
        setZabbixStatus({ connected: false, url: '', authenticated: false });
      }
    };
    fetchZabbix();
    const interval = setInterval(fetchZabbix, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="h-16 bg-[#0f172a] border-b border-slate-800 flex items-center justify-between px-6 sticky top-0 z-30">
      <div className="flex items-center gap-3">
        <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-cyan-950 border border-cyan-700/50 text-cyan-400">
          <Activity className="w-5 h-5 animate-pulse" />
        </div>
        <div>
          <h1 className="text-base font-bold text-slate-100 tracking-wide">
            SERVER HEALTH <span className="text-cyan-400 font-extrabold">MONITOR</span>
          </h1>
          <p className="text-[11px] text-slate-400 font-mono flex items-center gap-2">
            NOC Telemetry Platform <span className="text-slate-600">|</span> Zabbix Core Engine
          </p>
        </div>
      </div>

      <div className="flex items-center gap-4">
        {/* Real-time WebSocket indicator */}
        <div className="flex items-center gap-2 px-3 py-1 rounded-md bg-slate-900 border border-slate-800 text-xs font-mono">
          <span className={`w-2 h-2 rounded-full ${wsConnected ? 'bg-emerald-400 animate-ping' : 'bg-red-500'}`} />
          <span className="text-slate-300">WS Live: {wsConnected ? 'Connected' : 'Reconnecting'}</span>
        </div>

        {/* Zabbix Connection Indicator */}
        <div className="flex items-center gap-2 px-3 py-1 rounded-md bg-slate-900 border border-slate-800 text-xs font-mono">
          <span className={`w-2 h-2 rounded-full ${zabbixStatus?.connected ? 'bg-emerald-400' : 'bg-amber-400'}`} />
          <span className="text-slate-300">
            Zabbix: {zabbixStatus?.connected ? `v${zabbixStatus.api_version || '7.0'}` : 'Offline/Mock'}
          </span>
        </div>

        {onRefresh && (
          <button
            onClick={onRefresh}
            className="p-2 rounded-md bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition"
            title="Refresh Telemetry"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        )}

        {/* User Role Badge & Logout */}
        <div className="flex items-center gap-3 pl-3 border-l border-slate-800">
          <div className="flex items-center gap-2 text-xs">
            <UserIcon className="w-4 h-4 text-cyan-400" />
            <span className="px-2 py-0.5 rounded bg-cyan-950 border border-cyan-800/80 text-cyan-300 font-mono uppercase font-bold text-[10px]">
              {userRole}
            </span>
          </div>
          <button
            onClick={onLogout}
            className="p-1.5 rounded text-slate-400 hover:text-red-400 hover:bg-slate-800 transition"
            title="Sign out"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </header>
  );
};
