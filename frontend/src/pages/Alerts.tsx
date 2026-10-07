import React, { useState, useEffect } from 'react';
import { CheckSquare, RefreshCw } from 'lucide-react';
import { api } from '../services/api';
import { Alert } from '../types';
import { HealthBadge } from '../components/HealthBadge';

export const Alerts: React.FC = () => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('');
  const [severityFilter, setSeverityFilter] = useState('');
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null);
  const [ackNote, setAckNote] = useState('');
  const [isAckModalOpen, setIsAckModalOpen] = useState(false);

  const fetchAlerts = async () => {
    setLoading(true);
    try {
      const data = await api.getAlerts({
        status_filter: statusFilter || undefined,
        severity: severityFilter || undefined
      });
      setAlerts(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
  }, [statusFilter, severityFilter]);

  const handleOpenAckModal = (alertItem: Alert) => {
    setSelectedAlert(alertItem);
    setAckNote('');
    setIsAckModalOpen(true);
  };

  const handleConfirmAcknowledge = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedAlert) return;
    try {
      await api.acknowledgeAlert(selectedAlert.id, ackNote);
      setIsAckModalOpen(false);
      fetchAlerts();
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'Failed to acknowledge alert');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-100 tracking-wide font-mono">
            ALERT CONSOLE
          </h2>
          <p className="text-xs text-slate-400">
            Deduplicated incident stream and state transitions
          </p>
        </div>

        <button
          onClick={() => fetchAlerts()}
          className="p-2 rounded-lg bg-slate-900 border border-slate-800 hover:bg-slate-800 text-slate-300 transition self-start sm:self-auto"
          title="Refresh Alerts"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      {/* Filters */}
      <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-xs text-slate-300 font-mono focus:outline-none focus:border-cyan-500"
          >
            <option value="">All Statuses (Active, Acknowledged, Recovered)</option>
            <option value="ACTIVE">ACTIVE</option>
            <option value="ACKNOWLEDGED">ACKNOWLEDGED</option>
            <option value="RECOVERED">RECOVERED</option>
            <option value="SUPPRESSED">SUPPRESSED</option>
          </select>

          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-xs text-slate-300 font-mono focus:outline-none focus:border-cyan-500"
          >
            <option value="">All Severities</option>
            <option value="WARNING">WARNING</option>
            <option value="CRITICAL">CRITICAL</option>
            <option value="DOWN">DOWN</option>
          </select>
        </div>
      </div>

      {/* Alerts Table */}
      <div className="rounded-xl bg-[#0f172a] border border-slate-800 overflow-hidden shadow-lg">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900/80 text-slate-400 font-mono uppercase tracking-wider border-b border-slate-800">
              <tr>
                <th className="py-3 px-4">Severity / Status</th>
                <th className="py-3 px-4">Server</th>
                <th className="py-3 px-4">Problem Description</th>
                <th className="py-3 px-4">Metric / Value</th>
                <th className="py-3 px-4">Duration</th>
                <th className="py-3 px-4">Started At</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono">
              {alerts.length > 0 ? (
                alerts.map((al) => {
                  const durationMin = Math.floor(al.duration_seconds / 60);
                  const durationSec = al.duration_seconds % 60;
                  const durationDisplay =
                    al.status === 'RECOVERED'
                      ? `${durationMin}m ${durationSec}s`
                      : 'Active Incident';

                  return (
                    <tr key={al.id} className="hover:bg-slate-800/40 transition">
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-2">
                          <HealthBadge status={al.severity} size="sm" />
                          <span
                            className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                              al.status === 'ACTIVE'
                                ? 'bg-red-950 text-red-300 border border-red-800/60'
                                : al.status === 'ACKNOWLEDGED'
                                ? 'bg-amber-950 text-amber-300 border border-amber-800/60'
                                : 'bg-emerald-950 text-emerald-300 border border-emerald-800/60'
                            }`}
                          >
                            {al.status}
                          </span>
                        </div>
                      </td>
                      <td className="py-3 px-4 font-bold text-slate-200">
                        {al.server_display_name || al.server_hostname}
                      </td>
                      <td className="py-3 px-4 text-slate-300 font-sans max-w-xs">
                        {al.problem_title}
                        {al.acknowledge_note && (
                          <div className="text-[11px] text-amber-400 font-mono mt-0.5">
                            Note: {al.acknowledge_note} (by {al.acknowledged_by})
                          </div>
                        )}
                      </td>
                      <td className="py-3 px-4 text-slate-300">
                        <div>Val: <strong>{al.trigger_value}</strong></div>
                        <div className="text-[10px] text-slate-400">Limit: {al.threshold_value}</div>
                      </td>
                      <td className="py-3 px-4 text-slate-300">{durationDisplay}</td>
                      <td className="py-3 px-4 text-slate-400">
                        {new Date(al.started_at).toLocaleString()}
                      </td>
                      <td className="py-3 px-4 text-right">
                        {al.status === 'ACTIVE' && (
                          <button
                            onClick={() => handleOpenAckModal(al)}
                            className="px-2.5 py-1 rounded bg-amber-950/80 hover:bg-amber-900 border border-amber-800 text-amber-300 transition text-[11px] font-bold"
                          >
                            Acknowledge
                          </button>
                        )}
                      </td>
                    </tr>
                  );
                })
              ) : (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-slate-400 font-sans">
                    {loading ? 'Fetching alert records...' : 'No alerts matching specified filter.'}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Acknowledge Alert Modal */}
      {isAckModalOpen && selectedAlert && (
        <div className="fixed inset-0 z-50 bg-black/70 flex items-center justify-center p-4 backdrop-blur-sm">
          <div className="bg-[#0f172a] border border-slate-800 rounded-xl max-w-md w-full p-6 shadow-2xl space-y-4">
            <h3 className="text-sm font-bold text-slate-100 font-mono flex items-center gap-2">
              <CheckSquare className="w-4 h-4 text-amber-400" />
              <span>ACKNOWLEDGE INCIDENT</span>
            </h3>

            <div className="p-3 rounded bg-slate-900 border border-slate-800 text-xs font-mono space-y-1">
              <div className="text-slate-200 font-bold">{selectedAlert.problem_title}</div>
              <div className="text-slate-400">Server: {selectedAlert.server_display_name}</div>
            </div>

            <form onSubmit={handleConfirmAcknowledge} className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-400 mb-1 font-mono">
                  Operational Note / Remediation Reference
                </label>
                <textarea
                  rows={3}
                  required
                  placeholder="e.g. SRE team actively investigating memory leak. Remediation in progress."
                  value={ackNote}
                  onChange={(e) => setAckNote(e.target.value)}
                  className="w-full px-3 py-2 rounded bg-slate-950 border border-slate-800 text-slate-200 focus:outline-none focus:border-cyan-500 font-mono"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setIsAckModalOpen(false)}
                  className="px-4 py-1.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 font-mono"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-1.5 rounded bg-amber-600 hover:bg-amber-500 text-white font-mono font-bold"
                >
                  Confirm Ack
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
