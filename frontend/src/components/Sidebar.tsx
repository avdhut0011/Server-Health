import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Server,
  AlertTriangle,
  Wrench,
  FileText,
  Settings,
  Cpu
} from 'lucide-react';

export const Sidebar: React.FC = () => {
  const navItems = [
    { to: '/', label: 'NOC Overview', icon: LayoutDashboard },
    { to: '/servers', label: 'Server Inventory', icon: Server },
    { to: '/alerts', label: 'Active Alerts', icon: AlertTriangle },
    { to: '/maintenance', label: 'Maintenance', icon: Wrench },
    { to: '/audit-logs', label: 'Audit Trail', icon: FileText },
    { to: '/settings', label: 'System Settings', icon: Settings },
  ];

  return (
    <aside className="w-64 bg-[#0d1322] border-r border-slate-800 flex flex-col justify-between p-4 min-h-[calc(100vh-4rem)]">
      <div className="space-y-6">
        <div>
          <p className="text-[11px] font-mono uppercase tracking-wider text-slate-400 px-3 mb-2 font-bold">
            Telemetry & Ops
          </p>
          <nav className="space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.to}
                  to={item.to}
                  className={({ isActive }) =>
                    `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition ${
                      isActive
                        ? 'bg-cyan-950/80 text-cyan-300 border border-cyan-800/60'
                        : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
                    }`
                  }
                >
                  <Icon className="w-4 h-4" />
                  <span>{item.label}</span>
                </NavLink>
              );
            })}
          </nav>
        </div>

        {/* Quick Infrastructure Scope */}
        <div className="p-3.5 rounded-lg bg-slate-900/80 border border-slate-800 text-xs space-y-2">
          <div className="flex items-center gap-2 text-slate-300 font-semibold">
            <Cpu className="w-3.5 h-3.5 text-cyan-400" />
            <span>Target Environment</span>
          </div>
          <div className="font-mono text-[11px] text-slate-400 space-y-1">
            <div className="flex justify-between">
              <span>Host Node:</span>
              <span className="text-slate-200 font-bold">Windows 11</span>
            </div>
            <div className="flex justify-between">
              <span>VM Node:</span>
              <span className="text-slate-200 font-bold">Linux VM</span>
            </div>
            <div className="flex justify-between">
              <span>Zabbix Core:</span>
              <span className="text-emerald-400 font-bold">Active</span>
            </div>
          </div>
        </div>
      </div>

      <div className="pt-4 border-t border-slate-800/80 text-[11px] font-mono text-slate-400 text-center">
        Server Health Monitor v1.0.0
      </div>
    </aside>
  );
};
