import React, { useState, useEffect } from 'react';
import { Server, Mail, CheckCircle2, XCircle, Send, RefreshCw } from 'lucide-react';
import { api } from '../services/api';
import { ZabbixStatus } from '../types';

export const Settings: React.FC = () => {
  const [zabbixStatus, setZabbixStatus] = useState<ZabbixStatus | null>(null);
  const [testingZabbix, setTestingZabbix] = useState(false);
  const [testEmailRecipient, setTestEmailRecipient] = useState('');
  const [emailStatus, setEmailStatus] = useState<{ type: 'success' | 'error'; message: string } | null>(null);
  const [sendingEmail, setSendingEmail] = useState(false);

  const checkZabbix = async () => {
    setTestingZabbix(true);
    try {
      const s = await api.getZabbixStatus();
      setZabbixStatus(s);
    } catch (e: any) {
      setZabbixStatus({
        connected: false,
        url: 'http://localhost:8080/api_jsonrpc.php',
        authenticated: false,
        error_message: e.message,
      });
    } finally {
      setTestingZabbix(false);
    }
  };

  useEffect(() => {
    checkZabbix();
  }, []);

  const handleSendTestEmail = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!testEmailRecipient) return;
    setSendingEmail(true);
    setEmailStatus(null);
    try {
      const res = await api.sendTestEmail(testEmailRecipient);
      setEmailStatus({ type: 'success', message: res.message });
    } catch (err: any) {
      setEmailStatus({
        type: 'error',
        message: err?.response?.data?.detail || 'Failed to dispatch test email via SMTP',
      });
    } finally {
      setSendingEmail(false);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h2 className="text-xl font-bold text-slate-100 tracking-wide font-mono">
          SYSTEM CONFIGURATION & INTEGRATIONS
        </h2>
        <p className="text-xs text-slate-400">
          Zabbix JSON-RPC API connection parameters and generic SMTP notification channels
        </p>
      </div>

      {/* Zabbix Core Engine Status */}
      <div className="p-6 rounded-xl bg-[#0f172a] border border-slate-800 space-y-4 shadow-lg">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Server className="w-5 h-5 text-cyan-400" />
            <div>
              <h3 className="text-sm font-bold text-slate-100 font-mono">ZABBIX ENGINE INTEGRATION</h3>
              <p className="text-xs text-slate-400">Core metrics collection, agent poller, and trigger engine</p>
            </div>
          </div>
          <button
            onClick={checkZabbix}
            disabled={testingZabbix}
            className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs text-slate-200 border border-slate-700 font-mono transition"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${testingZabbix ? 'animate-spin' : ''}`} />
            <span>Test Connection</span>
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2 text-xs font-mono">
          <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 space-y-2">
            <div className="flex justify-between">
              <span className="text-slate-400">API Endpoint:</span>
              <span className="text-slate-200 truncate">{zabbixStatus?.url || 'http://localhost:8080/api_jsonrpc.php'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">API Version:</span>
              <span className="text-slate-200">{zabbixStatus?.api_version || 'Zabbix 7.0 LTS'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Latency:</span>
              <span className="text-slate-200">{zabbixStatus?.latency_ms ? `${zabbixStatus.latency_ms} ms` : '-'}</span>
            </div>
          </div>

          <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-slate-400">Connection State:</span>
              <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${zabbixStatus?.connected ? 'bg-emerald-950 text-emerald-300 border border-emerald-800' : 'bg-amber-950 text-amber-300 border border-amber-800'}`}>
                {zabbixStatus?.connected ? 'CONNECTED' : 'DISCONNECTED / MOCK'}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-400">Authentication:</span>
              <span className="text-slate-200 font-bold">{zabbixStatus?.authenticated ? 'VALID' : 'PENDING'}</span>
            </div>
            {zabbixStatus?.error_message && (
              <div className="text-[10px] text-amber-400 truncate pt-1 border-t border-slate-800">
                Notice: {zabbixStatus.error_message}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Generic SMTP Notification Settings */}
      <div className="p-6 rounded-xl bg-[#0f172a] border border-slate-800 space-y-4 shadow-lg">
        <div className="flex items-center gap-3">
          <Mail className="w-5 h-5 text-cyan-400" />
          <div>
            <h3 className="text-sm font-bold text-slate-100 font-mono">GENERIC SMTP EMAIL NOTIFICATIONS</h3>
            <p className="text-xs text-slate-400">
              Configured notification channel for automated Problem & Recovery dispatches
            </p>
          </div>
        </div>

        <form onSubmit={handleSendTestEmail} className="space-y-4 text-xs">
          <div>
            <label className="block text-slate-400 mb-1 font-mono">
              Test Recipient Email Address
            </label>
            <div className="flex gap-2">
              <input
                type="email"
                required
                placeholder="sre-team@datacenter.local"
                value={testEmailRecipient}
                onChange={(e) => setTestEmailRecipient(e.target.value)}
                className="flex-1 px-3 py-2 rounded bg-slate-950 border border-slate-800 text-slate-200 focus:outline-none focus:border-cyan-500 font-mono"
              />
              <button
                type="submit"
                disabled={sendingEmail}
                className="flex items-center gap-2 px-4 py-2 rounded bg-cyan-600 hover:bg-cyan-500 text-white font-mono font-bold transition shadow-lg shadow-cyan-950/50"
              >
                <Send className="w-3.5 h-3.5" />
                <span>{sendingEmail ? 'Sending...' : 'Send Test Notification'}</span>
              </button>
            </div>
          </div>

          {emailStatus && (
            <div
              className={`p-3 rounded-lg border text-xs font-mono flex items-center gap-2 ${
                emailStatus.type === 'success'
                  ? 'bg-emerald-950/60 border-emerald-800 text-emerald-300'
                  : 'bg-red-950/60 border-red-800 text-red-300'
              }`}
            >
              {emailStatus.type === 'success' ? (
                <CheckCircle2 className="w-4 h-4" />
              ) : (
                <XCircle className="w-4 h-4" />
              )}
              <span>{emailStatus.message}</span>
            </div>
          )}
        </form>
      </div>
    </div>
  );
};
