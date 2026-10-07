import React, { useState, useEffect, useCallback } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Navbar } from './components/Navbar';
import { Sidebar } from './components/Sidebar';
import { Dashboard } from './pages/Dashboard';
import { Servers } from './pages/Servers';
import { ServerDetails } from './pages/ServerDetails';
import { Alerts } from './pages/Alerts';
import { Maintenance } from './pages/Maintenance';
import { AuditLogs } from './pages/AuditLogs';
import { Settings } from './pages/Settings';
import { Login } from './pages/Login';
import { useWebSocket } from './hooks/useWebSocket';
import { api } from './services/api';
import { DashboardSummary } from './types';

export const App: React.FC = () => {
  const [user, setUser] = useState<any>(() => {
    const saved = localStorage.getItem('shm_user');
    return saved ? JSON.parse(saved) : null;
  });

  const [dashboardSummary, setDashboardSummary] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(false);

  const fetchSummary = useCallback(async () => {
    if (!user) return;
    setLoading(true);
    try {
      const data = await api.getDashboardSummary();
      setDashboardSummary(data);
    } catch (e) {
      console.error('Failed to fetch dashboard summary', e);
    } finally {
      setLoading(false);
    }
  }, [user]);

  // WebSocket message receiver
  const handleWsMessage = useCallback((_msg: any) => {
    // When real-time telemetry updates or alerts arrive, refresh summary state
    fetchSummary();
  }, [fetchSummary]);

  const { isConnected } = useWebSocket('dashboard', handleWsMessage);

  useEffect(() => {
    if (user) {
      fetchSummary();
      // Regular polling fallback every 15s
      const interval = setInterval(fetchSummary, 15000);
      return () => clearInterval(interval);
    }
  }, [user, fetchSummary]);

  const handleLogout = () => {
    localStorage.removeItem('shm_access_token');
    localStorage.removeItem('shm_user');
    setUser(null);
  };

  if (!user) {
    return <Login onLoginSuccess={(u) => setUser(u)} />;
  }

  return (
    <BrowserRouter>
      <div className="min-h-screen bg-[#0b0f17] flex flex-col font-sans">
        <Navbar
          wsConnected={isConnected}
          onRefresh={fetchSummary}
          userRole={user.role}
          onLogout={handleLogout}
        />

        <div className="flex flex-1">
          <Sidebar />
          <main className="flex-1 p-6 overflow-y-auto max-w-7xl mx-auto w-full">
            <Routes>
              <Route
                path="/"
                element={
                  <Dashboard
                    summary={dashboardSummary}
                    loading={loading}
                    onRefresh={fetchSummary}
                  />
                }
              />
              <Route path="/servers" element={<Servers />} />
              <Route path="/servers/:id" element={<ServerDetails />} />
              <Route path="/alerts" element={<Alerts />} />
              <Route path="/maintenance" element={<Maintenance />} />
              <Route path="/audit-logs" element={<AuditLogs />} />
              <Route path="/settings" element={<Settings />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
        </div>
      </div>
    </BrowserRouter>
  );
};
