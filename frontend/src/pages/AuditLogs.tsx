import React, { useState, useEffect } from 'react';
import { RefreshCw } from 'lucide-react';
import { api } from '../services/api';
import { AuditLog } from '../types';

export const AuditLogs: React.FC = () => {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionFilter] = useState('');

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const data = await api.getAuditLogs({ action: actionFilter || undefined });
      setLogs(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, [actionFilter]);

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-100 tracking-wide font-mono">
            SECURITY & OPERATIONS AUDIT TRAIL
          </h2>
          <p className="text-xs text-slate-400">
            Immutable log of system modifications, logins, and alert acknowledgements
          </p>
        </div>
        <button
          onClick={() => fetchLogs()}
          className="p-2 rounded-lg bg-slate-900 border border-slate-800 hover:bg-slate-800 text-slate-300 transition self-start sm:self-auto"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      {/* Table */}
      <div className="rounded-xl bg-[#0f172a] border border-slate-800 overflow-hidden shadow-lg">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-slate-900/80 text-slate-400 uppercase tracking-wider border-b border-slate-800">
              <tr>
                <th className="py-3 px-4">Timestamp</th>
                <th className="py-3 px-4">Operator</th>
                <th className="py-3 px-4">Action</th>
                <th className="py-3 px-4">Resource</th>
                <th className="py-3 px-4">Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {logs.length > 0 ? (
                logs.map((l) => (
                  <tr key={l.id} className="hover:bg-slate-800/40 transition">
                    <td className="py-3 px-4 text-slate-400">
                      {new Date(l.created_at).toLocaleString()}
                    </td>
                    <td className="py-3 px-4 text-cyan-300 font-bold">
                      {l.username || 'System Engine'}
                    </td>
                    <td className="py-3 px-4">
                      <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-200 border border-slate-700 font-bold text-[10px]">
                        {l.action}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-slate-300">{l.resource_type || '-'}</td>
                    <td className="py-3 px-4 text-slate-400 font-mono text-[11px] truncate max-w-xs">
                      {l.new_values ? JSON.stringify(l.new_values) : '-'}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={5} className="py-8 text-center text-slate-400 font-sans">
                    {loading ? 'Reading audit trail records...' : 'No audit records recorded yet.'}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
