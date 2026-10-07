import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  Server as ServerIcon,
  Plus,
  Search,
  Monitor,
  Trash2,
  RefreshCw
} from 'lucide-react';
import { api } from '../services/api';
import { Server } from '../types';
import { HealthBadge } from '../components/HealthBadge';

export const Servers: React.FC = () => {
  const [servers, setServers] = useState<Server[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [envFilter, setEnvFilter] = useState('');
  const [healthFilter, setHealthFilter] = useState('');
  const [showAddModal, setShowAddModal] = useState(false);

  // New server form state
  const [formData, setFormData] = useState<{
    hostname: string;
    display_name: string;
    ip_address: string;
    os_type: 'WINDOWS' | 'LINUX';
    os_version: string;
    environment: string;
    location: string;
    rack: string;
    vendor: string;
    model: string;
    zabbix_hostid: string;
  }>({
    hostname: '',
    display_name: '',
    ip_address: '',
    os_type: 'WINDOWS',
    os_version: 'Windows 11 Pro',
    environment: 'Production',
    location: 'Data Center 1',
    rack: 'Rack-A1',
    vendor: 'Dell / Generic',
    model: 'PowerEdge / Workstation',
    zabbix_hostid: ''
  });

  const fetchServers = async () => {
    setLoading(true);
    try {
      const data = await api.getServers({
        search: search || undefined,
        environment: envFilter || undefined,
        health: healthFilter || undefined,
      });
      setServers(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchServers();
  }, [envFilter, healthFilter]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchServers();
  };

  const handleCreateServer = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.createServer(formData);
      setShowAddModal(false);
      setFormData({
        hostname: '',
        display_name: '',
        ip_address: '',
        os_type: 'WINDOWS',
        os_version: 'Windows 11 Pro',
        environment: 'Production',
        location: 'Data Center 1',
        rack: 'Rack-A1',
        vendor: 'Dell / Generic',
        model: 'PowerEdge / Workstation',
        zabbix_hostid: ''
      });
      fetchServers();
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'Failed to add server');
    }
  };

  const handleDeleteServer = async (id: string, name: string) => {
    if (confirm(`Are you sure you want to remove server '${name}' from inventory?`)) {
      try {
        await api.deleteServer(id);
        fetchServers();
      } catch (err: any) {
        alert(err?.response?.data?.detail || 'Failed to delete server');
      }
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-100 tracking-wide font-mono">
            SERVER INVENTORY
          </h2>
          <p className="text-xs text-slate-400">
            Registered physical and virtual node endpoints
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => fetchServers()}
            className="p-2 rounded-lg bg-slate-900 border border-slate-800 hover:bg-slate-800 text-slate-300 transition"
            title="Refresh Inventory"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
          <button
            onClick={() => setShowAddModal(true)}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-bold font-mono tracking-wide transition shadow-lg shadow-cyan-950/50"
          >
            <Plus className="w-4 h-4" />
            <span>REGISTER SERVER</span>
          </button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 flex flex-wrap items-center justify-between gap-4">
        <form onSubmit={handleSearchSubmit} className="flex items-center gap-2 flex-1 max-w-md">
          <div className="relative w-full">
            <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-500" />
            <input
              type="text"
              placeholder="Search hostname, IP, display name, location..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-9 pr-3 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500 font-mono"
            />
          </div>
          <button
            type="submit"
            className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs text-slate-200 border border-slate-700 font-mono"
          >
            Search
          </button>
        </form>

        <div className="flex items-center gap-3">
          {/* Environment Filter */}
          <select
            value={envFilter}
            onChange={(e) => setEnvFilter(e.target.value)}
            className="px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-xs text-slate-300 font-mono focus:outline-none focus:border-cyan-500"
          >
            <option value="">All Environments</option>
            <option value="Production">Production</option>
            <option value="Development">Development</option>
            <option value="Testing">Testing</option>
            <option value="DR">DR</option>
          </select>

          {/* Health Filter */}
          <select
            value={healthFilter}
            onChange={(e) => setHealthFilter(e.target.value)}
            className="px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-xs text-slate-300 font-mono focus:outline-none focus:border-cyan-500"
          >
            <option value="">All Health States</option>
            <option value="HEALTHY">Healthy</option>
            <option value="WARNING">Warning</option>
            <option value="CRITICAL">Critical</option>
            <option value="DOWN">Down</option>
          </select>
        </div>
      </div>

      {/* Servers Inventory List */}
      <div className="rounded-xl bg-[#0f172a] border border-slate-800 overflow-hidden shadow-lg">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900/80 text-slate-400 font-mono uppercase tracking-wider border-b border-slate-800">
              <tr>
                <th className="py-3 px-4">Display Name / Hostname</th>
                <th className="py-3 px-4">IP Address</th>
                <th className="py-3 px-4">OS / Environment</th>
                <th className="py-3 px-4">Location / Rack</th>
                <th className="py-3 px-4">Zabbix Host ID</th>
                <th className="py-3 px-4 text-center">Health</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono">
              {servers.length > 0 ? (
                servers.map((srv) => (
                  <tr key={srv.id} className="hover:bg-slate-800/40 transition">
                    <td className="py-3 px-4">
                      <div className="font-bold text-slate-100 flex items-center gap-2">
                        <Monitor className="w-3.5 h-3.5 text-cyan-400" />
                        <span>{srv.display_name || srv.hostname}</span>
                      </div>
                      <div className="text-[10px] text-slate-400 pl-5">{srv.hostname}</div>
                    </td>
                    <td className="py-3 px-4 text-slate-300">{srv.ip_address}</td>
                    <td className="py-3 px-4">
                      <span className="px-2 py-0.5 rounded bg-slate-800 border border-slate-700 text-[10px] font-bold text-slate-300 mr-2">
                        {srv.os_type}
                      </span>
                      <span className="text-[11px] text-slate-400">{srv.environment}</span>
                    </td>
                    <td className="py-3 px-4 text-slate-300">
                      <div>{srv.location}</div>
                      <div className="text-[10px] text-slate-400">{srv.rack || 'Unassigned'}</div>
                    </td>
                    <td className="py-3 px-4">
                      {srv.zabbix_hostid ? (
                        <span className="px-2 py-0.5 rounded bg-cyan-950/80 border border-cyan-800 text-cyan-300 text-[10px]">
                          ID: {srv.zabbix_hostid}
                        </span>
                      ) : (
                        <span className="text-[10px] text-slate-400">Unlinked</span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-center">
                      <HealthBadge status={srv.overall_health} size="sm" />
                    </td>
                    <td className="py-3 px-4 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <Link
                          to={`/servers/${srv.id}`}
                          className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-cyan-400 border border-slate-700 transition"
                        >
                          View
                        </Link>
                        <button
                          onClick={() => handleDeleteServer(srv.id, srv.hostname)}
                          className="p-1 rounded text-slate-500 hover:text-red-400 hover:bg-slate-800 transition"
                          title="Delete Server"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-slate-400 font-sans">
                    {loading ? 'Fetching server inventory...' : 'No matching servers found in inventory.'}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Add Server Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 bg-black/70 flex items-center justify-center p-4 backdrop-blur-sm">
          <div className="bg-[#0f172a] border border-slate-800 rounded-xl max-w-lg w-full p-6 shadow-2xl space-y-4">
            <h3 className="text-base font-bold text-slate-100 font-mono flex items-center gap-2">
              <ServerIcon className="w-5 h-5 text-cyan-400" />
              <span>REGISTER NEW SERVER</span>
            </h3>

            <form onSubmit={handleCreateServer} className="space-y-3 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-400 mb-1 font-mono">Hostname *</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. srv-win-01"
                    value={formData.hostname}
                    onChange={(e) => setFormData({ ...formData, hostname: e.target.value })}
                    className="w-full px-3 py-2 rounded bg-slate-950 border border-slate-800 text-slate-200 focus:outline-none focus:border-cyan-500 font-mono"
                  />
                </div>
                <div>
                  <label className="block text-slate-400 mb-1 font-mono">Display Name *</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Windows 11 Host"
                    value={formData.display_name}
                    onChange={(e) => setFormData({ ...formData, display_name: e.target.value })}
                    className="w-full px-3 py-2 rounded bg-slate-950 border border-slate-800 text-slate-200 focus:outline-none focus:border-cyan-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-400 mb-1 font-mono">IP Address *</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. 192.168.1.50"
                    value={formData.ip_address}
                    onChange={(e) => setFormData({ ...formData, ip_address: e.target.value })}
                    className="w-full px-3 py-2 rounded bg-slate-950 border border-slate-800 text-slate-200 focus:outline-none focus:border-cyan-500 font-mono"
                  />
                </div>
                <div>
                  <label className="block text-slate-400 mb-1 font-mono">Operating System *</label>
                  <select
                    value={formData.os_type}
                    onChange={(e) => setFormData({ ...formData, os_type: e.target.value as 'WINDOWS' | 'LINUX' })}
                    className="w-full px-3 py-2 rounded bg-slate-950 border border-slate-800 text-slate-200 focus:outline-none focus:border-cyan-500 font-mono"
                  >
                    <option value="WINDOWS">WINDOWS</option>
                    <option value="LINUX">LINUX</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-400 mb-1 font-mono">Environment</label>
                  <select
                    value={formData.environment}
                    onChange={(e) => setFormData({ ...formData, environment: e.target.value })}
                    className="w-full px-3 py-2 rounded bg-slate-950 border border-slate-800 text-slate-200 focus:outline-none focus:border-cyan-500 font-mono"
                  >
                    <option value="Production">Production</option>
                    <option value="Development">Development</option>
                    <option value="Testing">Testing</option>
                    <option value="DR">DR</option>
                  </select>
                </div>
                <div>
                  <label className="block text-slate-400 mb-1 font-mono">Location</label>
                  <input
                    type="text"
                    placeholder="e.g. Lab / Data Center 1"
                    value={formData.location}
                    onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                    className="w-full px-3 py-2 rounded bg-slate-950 border border-slate-800 text-slate-200 focus:outline-none focus:border-cyan-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-slate-400 mb-1 font-mono">Zabbix Host ID (Optional)</label>
                <input
                  type="text"
                  placeholder="e.g. 10084 (Links to Zabbix Agent telemetry)"
                  value={formData.zabbix_hostid}
                  onChange={(e) => setFormData({ ...formData, zabbix_hostid: e.target.value })}
                  className="w-full px-3 py-2 rounded bg-slate-950 border border-slate-800 text-slate-200 focus:outline-none focus:border-cyan-500 font-mono"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 font-mono transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded bg-cyan-600 hover:bg-cyan-500 text-white font-mono font-bold transition shadow-lg shadow-cyan-950/50"
                >
                  Save Server
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
