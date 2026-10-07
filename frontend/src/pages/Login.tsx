import React, { useState } from 'react';
import { Activity, Lock, User, AlertCircle } from 'lucide-react';
import { api } from '../services/api';

interface LoginProps {
  onLoginSuccess: (user: any) => void;
}

export const Login: React.FC<LoginProps> = ({ onLoginSuccess }) => {
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('admin123');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const data = await api.login(username, password);
      localStorage.setItem('shm_access_token', data.access_token);
      localStorage.setItem('shm_user', JSON.stringify(data.user));
      onLoginSuccess(data.user);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Authentication failed. Please verify credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0b0f17] flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-[#0f172a] border border-slate-800 rounded-2xl p-8 shadow-2xl space-y-6">
        <div className="text-center space-y-2">
          <div className="w-12 h-12 rounded-xl bg-cyan-950 border border-cyan-700/60 text-cyan-400 flex items-center justify-center mx-auto shadow-lg shadow-cyan-950/50">
            <Activity className="w-6 h-6 animate-pulse" />
          </div>
          <h1 className="text-lg font-bold text-slate-100 font-mono tracking-wide">
            SERVER HEALTH <span className="text-cyan-400">MONITOR</span>
          </h1>
          <p className="text-xs text-slate-400 font-mono">
            NOC Operations & Zabbix Telemetry Platform
          </p>
        </div>

        {error && (
          <div className="p-3 rounded-lg bg-red-950/60 border border-red-800 text-red-300 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4 text-xs font-mono">
          <div>
            <label className="block text-slate-400 mb-1.5 font-bold uppercase tracking-wider text-[10px]">
              Username
            </label>
            <div className="relative">
              <User className="w-4 h-4 absolute left-3 top-2.5 text-slate-500" />
              <input
                type="text"
                required
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full pl-9 pr-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-slate-200 focus:outline-none focus:border-cyan-500 font-mono"
              />
            </div>
          </div>

          <div>
            <label className="block text-slate-400 mb-1.5 font-bold uppercase tracking-wider text-[10px]">
              Password
            </label>
            <div className="relative">
              <Lock className="w-4 h-4 absolute left-3 top-2.5 text-slate-500" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full pl-9 pr-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-slate-200 focus:outline-none focus:border-cyan-500 font-mono"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white font-bold font-mono tracking-wide transition shadow-lg shadow-cyan-950/50 mt-2"
          >
            {loading ? 'Authenticating...' : 'Sign In to NOC Console'}
          </button>
        </form>

        <div className="text-center pt-2 text-[11px] font-mono text-slate-400">
          Default initial credentials: <code className="text-cyan-400">admin</code> / <code className="text-cyan-400">admin123</code>
        </div>
      </div>
    </div>
  );
};
