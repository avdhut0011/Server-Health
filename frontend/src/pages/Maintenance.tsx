import React, { useState, useEffect } from 'react';
import { Wrench, Plus, Trash2, RefreshCw } from 'lucide-react';
import { api } from '../services/api';
import { MaintenanceWindow, Server } from '../types';

export const Maintenance: React.FC = () => {
  const [windows, setWindows] = useState<MaintenanceWindow[]>([]);
  const [servers, setServers] = useState<Server[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);

  const [formData, setFormData] = useState({
    server_id: '',
    title: '',
    description: '',
    start_time: new Date().toISOString().slice(0, 16),
    end_time: new Date(Date.now() + 2 * 3600 * 1000).toISOString().slice(0, 16),
    suppress_alerts: true,
  });

  const fetchData = async () => {
    setLoading(true);
    try {
      const [w, s] = await Promise.all([api.getMaintenanceWindows(), api.getServers()]);
      setWindows(w);
      setServers(s);
      if (s.length > 0 && !formData.server_id) {
        setFormData((prev) => ({ ...prev, server_id: s[0].id }));
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.createMaintenanceWindow({
        ...formData,
        start_time: new Date(formData.start_time).toISOString(),
        end_time: new Date(formData.end_time).toISOString(),
      });
      setShowModal(false);
      fetchData();
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'Failed to schedule maintenance window');
    }
  };

  const handleDelete = async (id: string) => {
    if (confirm('Delete this maintenance schedule?')) {
      try {
        await api.deleteMaintenanceWindow(id);
        fetchData();
      } catch (err: any) {
        alert(err?.response?.data?.detail || 'Failed to delete');
      }
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-100 tracking-wide font-mono">
            MAINTENANCE WINDOWS
          </h2>
          <p className="text-xs text-slate-400">
            Scheduled maintenance periods with automatic alert suppression
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => fetchData()}
            className="p-2 rounded-lg bg-slate-900 border border-slate-800 hover:bg-slate-800 text-slate-300 transition"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
          <button
            onClick={() => setShowModal(true)}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-bold font-mono tracking-wide transition shadow-lg shadow-cyan-950/50"
          >
            <Plus className="w-4 h-4" />
            <span>SCHEDULE WINDOW</span>
          </button>
        </div>
      </div>

      {/* Windows Table */}
      <div className="rounded-xl bg-[#0f172a] border border-slate-800 overflow-hidden shadow-lg">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900/80 text-slate-400 font-mono uppercase tracking-wider border-b border-slate-800">
              <tr>
                <th className="py-3 px-4">Title / Target Host</th>
                <th className="py-3 px-4">Start Time</th>
                <th className="py-3 px-4">End Time</th>
                <th className="py-3 px-4">Alert Suppression</th>
                <th className="py-3 px-4">Scheduled By</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono">
              {windows.length > 0 ? (
                windows.map((w) => (
                  <tr key={w.id} className="hover:bg-slate-800/40 transition">
                    <td className="py-3 px-4">
                      <div className="font-bold text-slate-100">{w.title}</div>
                      <div className="text-[10px] text-cyan-400">{w.server_hostname}</div>
                    </td>
                    <td className="py-3 px-4 text-slate-300">
                      {new Date(w.start_time).toLocaleString()}
                    </td>
                    <td className="py-3 px-4 text-slate-300">
                      {new Date(w.end_time).toLocaleString()}
                    </td>
                    <td className="py-3 px-4">
                      <span className="px-2 py-0.5 rounded bg-purple-950/80 border border-purple-800 text-purple-300 text-[10px] font-bold">
                        {w.suppress_alerts ? 'ACTIVE SUPPRESSION' : 'NOTIFICATION ON'}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-slate-400">{w.created_by || 'Admin'}</td>
                    <td className="py-3 px-4 text-right">
                      <button
                        onClick={() => handleDelete(w.id)}
                        className="p-1 rounded text-slate-500 hover:text-red-400 hover:bg-slate-800 transition"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={6} className="py-8 text-center text-slate-400 font-sans">
                    {loading ? 'Loading maintenance schedules...' : 'No maintenance windows currently scheduled.'}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Schedule Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 bg-black/70 flex items-center justify-center p-4 backdrop-blur-sm">
          <div className="bg-[#0f172a] border border-slate-800 rounded-xl max-w-md w-full p-6 shadow-2xl space-y-4">
            <h3 className="text-sm font-bold text-slate-100 font-mono flex items-center gap-2">
              <Wrench className="w-4 h-4 text-cyan-400" />
              <span>SCHEDULE MAINTENANCE WINDOW</span>
            </h3>

            <form onSubmit={handleCreate} className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-400 mb-1 font-mono">Target Server *</label>
                <select
                  required
                  value={formData.server_id}
                  onChange={(e) => setFormData({ ...formData, server_id: e.target.value })}
                  className="w-full px-3 py-2 rounded bg-slate-950 border border-slate-800 text-slate-200 focus:outline-none focus:border-cyan-500 font-mono"
                >
                  {servers.map((s) => (
                    <option key={s.id} value={s.id}>
                      {s.display_name} ({s.hostname})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-slate-400 mb-1 font-mono">Title *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. OS Kernel & Security Patching"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  className="w-full px-3 py-2 rounded bg-slate-950 border border-slate-800 text-slate-200 focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-400 mb-1 font-mono">Start Time *</label>
                  <input
                    type="datetime-local"
                    required
                    value={formData.start_time}
                    onChange={(e) => setFormData({ ...formData, start_time: e.target.value })}
                    className="w-full px-3 py-2 rounded bg-slate-950 border border-slate-800 text-slate-200 focus:outline-none focus:border-cyan-500 font-mono"
                  />
                </div>
                <div>
                  <label className="block text-slate-400 mb-1 font-mono">End Time *</label>
                  <input
                    type="datetime-local"
                    required
                    value={formData.end_time}
                    onChange={(e) => setFormData({ ...formData, end_time: e.target.value })}
                    className="w-full px-3 py-2 rounded bg-slate-950 border border-slate-800 text-slate-200 focus:outline-none focus:border-cyan-500 font-mono"
                  />
                </div>
              </div>

              <div className="flex items-center gap-2 pt-2">
                <input
                  type="checkbox"
                  id="suppress_alerts"
                  checked={formData.suppress_alerts}
                  onChange={(e) => setFormData({ ...formData, suppress_alerts: e.target.checked })}
                  className="rounded bg-slate-950 border-slate-800 text-cyan-500 focus:ring-0"
                />
                <label htmlFor="suppress_alerts" className="text-slate-300 font-mono text-xs">
                  Suppress email notifications during maintenance
                </label>
              </div>

              <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 font-mono"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded bg-cyan-600 hover:bg-cyan-500 text-white font-mono font-bold"
                >
                  Schedule Window
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
