import React from 'react';
import { 
  FileText, 
  Activity, 
  AlertTriangle, 
  RefreshCw, 
  Wifi, 
  CheckCircle2, 
  Clock, 
  AlertCircle 
} from 'lucide-react';
import { KPICard } from '../components/KPICard';
import { AnalyticsSummary, AlertItem } from '../types';
import { translations, Language } from '../i18n/translations';

interface OverviewPageProps {
  summary: AnalyticsSummary | null;
  alerts: AlertItem[];
  lang: Language;
}

export const OverviewPage: React.FC<OverviewPageProps> = ({ summary, alerts, lang }) => {
  const t = translations[lang];

  return (
    <div className="space-y-6">
      
      {/* Header Banner */}
      <div className="p-6 rounded-3xl bg-gradient-to-r from-teal-900/40 via-slate-900 to-slate-900 border border-teal-500/20 glass-card">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-white tracking-tight">{t.welcome}</h1>
            <p className="text-sm text-slate-400 mt-1">{t.tagline}</p>
          </div>
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-teal-500/10 border border-teal-500/30 text-teal-300 text-xs font-semibold">
              <Wifi className="w-4 h-4 text-teal-400" />
              Offline Sync Engine: Active (SQLite &amp; Server)
            </div>
          </div>
        </div>
      </div>

      {/* Top Key Metrics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          title={t.kpi_records}
          value={summary ? summary.total_health_records : '...'}
          subtitle="Community Patient Records"
          icon={FileText}
          color="teal"
        />
        <KPICard
          title={t.kpi_observations}
          value={summary ? summary.total_observations : '...'}
          subtitle="Vital signs & environmental checks"
          icon={Activity}
          color="indigo"
        />
        <KPICard
          title={t.kpi_alerts}
          value={summary ? summary.active_alerts_count : '...'}
          subtitle="Requires attention"
          icon={AlertTriangle}
          color="rose"
        />
        <KPICard
          title={t.kpi_sync}
          value={summary ? `${summary.sync_metrics.pending_count} Pending` : '...'}
          subtitle={`${summary?.sync_metrics.synced_count || 0} Synced successfully`}
          icon={RefreshCw}
          color="amber"
        />
      </div>

      {/* Main Content Layout: Active Alerts & Sync Queue */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Active Alerts Summary */}
        <div className="lg:col-span-2 glass-card p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-amber-400" />
              Active System Alerts
            </h2>
            <span className="text-xs font-semibold bg-slate-800 text-slate-300 px-2.5 py-1 rounded-full border border-slate-700">
              {alerts.length} Total
            </span>
          </div>

          <div className="space-y-3">
            {alerts.length === 0 ? (
              <div className="p-8 text-center text-slate-500 rounded-xl bg-slate-950/50 border border-slate-800/50">
                <CheckCircle2 className="w-8 h-8 text-emerald-500 mx-auto mb-2 opacity-80" />
                <p className="text-sm font-medium">No open critical alerts.</p>
              </div>
            ) : (
              alerts.slice(0, 5).map((alert) => (
                <div
                  key={alert.id}
                  className="p-4 rounded-xl bg-slate-950/60 border border-slate-800/80 flex items-start justify-between gap-4 hover:border-slate-700 transition-all"
                >
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span
                        className={`text-[10px] font-extrabold px-2 py-0.5 rounded uppercase border ${
                          alert.severity === 'CRITICAL'
                            ? 'bg-rose-500/20 text-rose-400 border-rose-500/30'
                            : alert.severity === 'HIGH'
                            ? 'bg-amber-500/20 text-amber-400 border-amber-500/30'
                            : 'bg-indigo-500/20 text-indigo-400 border-indigo-500/30'
                        }`}
                      >
                        {alert.severity}
                      </span>
                      <h3 className="font-semibold text-sm text-slate-200">{alert.title}</h3>
                    </div>
                    <p className="text-xs text-slate-400 leading-relaxed">{alert.description}</p>
                    <div className="flex items-center gap-2 text-[11px] text-slate-500 pt-1">
                      <Clock className="w-3 h-3" />
                      <span>{new Date(alert.created_at).toLocaleString()}</span>
                    </div>
                  </div>

                  <span className="text-xs font-semibold px-2.5 py-1 rounded-lg bg-amber-500/10 text-amber-400 border border-amber-500/20 shrink-0">
                    {alert.status}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Sync Status Sidebar Widget */}
        <div className="glass-card p-6 space-y-4">
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <RefreshCw className="w-5 h-5 text-teal-400" />
            Sync Engine Status
          </h2>

          <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 space-y-3">
            <div className="flex items-center justify-between text-xs">
              <span className="text-slate-400">Target Server:</span>
              <span className="font-mono text-teal-300">FastAPI Remote Endpoint</span>
            </div>
            <div className="flex items-center justify-between text-xs">
              <span className="text-slate-400">Local Engine:</span>
              <span className="font-mono text-slate-300">SQLite Client Queue</span>
            </div>
            <div className="flex items-center justify-between text-xs">
              <span className="text-slate-400">Conflict Strategy:</span>
              <span className="font-mono text-amber-400 font-bold">SERVER_WINS</span>
            </div>
          </div>

          <div className="space-y-2">
            <div className="flex justify-between text-xs text-slate-400">
              <span>Queue Sync Progress</span>
              <span>92% Synced</span>
            </div>
            <div className="w-full h-2 rounded-full bg-slate-800 overflow-hidden">
              <div className="h-full bg-gradient-to-r from-teal-500 to-emerald-400 w-[92%]" />
            </div>
          </div>

          <div className="p-3 rounded-xl bg-teal-500/5 border border-teal-500/20 text-xs text-teal-300 flex items-start gap-2">
            <AlertCircle className="w-4 h-4 text-teal-400 shrink-0 mt-0.5" />
            <span>OpenHealthKit automatically buffers mutations offline when connection drops.</span>
          </div>
        </div>

      </div>

    </div>
  );
};
