import React from 'react';
import { ServerHealth, AlertSeverity } from '../types';

interface HealthBadgeProps {
  status: ServerHealth | AlertSeverity | string;
  className?: string;
  size?: 'sm' | 'md' | 'lg';
}

export const HealthBadge: React.FC<HealthBadgeProps> = ({ status, className = '', size = 'md' }) => {
  const normalized = status.toUpperCase();

  let bgClass = 'bg-slate-800 text-slate-300 border-slate-700';
  let dotClass = 'bg-slate-400';

  if (normalized === 'HEALTHY' || normalized === 'ONLINE' || normalized === 'RECOVERED') {
    bgClass = 'bg-emerald-950/70 text-emerald-300 border-emerald-800/60 noc-glow-healthy';
    dotClass = 'bg-emerald-400';
  } else if (normalized === 'WARNING') {
    bgClass = 'bg-amber-950/70 text-amber-300 border-amber-800/60 noc-glow-warning';
    dotClass = 'bg-amber-400';
  } else if (normalized === 'CRITICAL' || normalized === 'FAILED') {
    bgClass = 'bg-red-950/70 text-red-300 border-red-800/60 noc-glow-critical animate-pulse';
    dotClass = 'bg-red-500';
  } else if (normalized === 'DOWN' || normalized === 'OFFLINE') {
    bgClass = 'bg-slate-900 text-slate-400 border-slate-700';
    dotClass = 'bg-slate-500';
  } else if (normalized === 'UNSUPPORTED' || normalized === 'NOT_PRESENT') {
    bgClass = 'bg-slate-900/40 text-slate-500 border-slate-800';
    dotClass = 'bg-slate-600';
  }

  const sizeClasses = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-2.5 py-1 text-xs font-semibold',
    lg: 'px-3.5 py-1.5 text-sm font-bold'
  };

  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full border ${bgClass} ${sizeClasses[size]} tracking-wide ${className}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${dotClass}`} />
      {normalized}
    </span>
  );
};
