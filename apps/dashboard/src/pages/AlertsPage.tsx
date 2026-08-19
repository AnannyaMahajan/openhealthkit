import React, { useState } from 'react';
import { AlertTriangle, CheckCircle, Clock, ShieldAlert } from 'lucide-react';
import { AlertItem } from '../types';
import { updateAlertStatus } from '../api/client';
import { translations, Language } from '../i18n/translations';

interface AlertsPageProps {
  alerts: AlertItem[];
  onRefresh: () => void;
  lang: Language;
}

export const AlertsPage: React.FC<AlertsPageProps> = ({ alerts, onRefresh, lang }) => {
  const t = translations[lang];
  const [filterSeverity, setFilterSeverity] = useState('ALL');

  const handleUpdateStatus = async (alertId: string, status: string) => {
    try {
      await updateAlertStatus(alertId, status);
      onRefresh();
    } catch (err) {
      alert('Failed to update alert: ' + err);
    }
  };

  const filtered = alerts.filter(a => 
    filterSeverity === 'ALL' || a.severity === filterSeverity
  );

  return (
    <div className="space-y-6">
      
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">{t.nav_alerts}</h1>
          <p className="text-sm text-slate-400">Rule-based alert evaluation and notification management</p>
        </div>

        {/* Severity Filter Tabs */}
        <div className="flex items-center gap-1 bg-slate-900 p-1 rounded-xl border border-slate-800">
          {['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map((sev) => (
            <button
              key={sev}
              onClick={() => setFilterSeverity(sev)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                filterSeverity === sev
                  ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {sev}
            </button>
          ))}
        </div>
      </div>

      {/* Alerts Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {filtered.length === 0 ? (
          <div className="md:col-span-2 glass-card p-12 text-center text-slate-500">
            <CheckCircle className="w-8 h-8 text-emerald-500 mx-auto mb-2 opacity-80" />
            <p className="text-sm font-medium">No alerts matching filter.</p>
          </div>
        ) : (
          filtered.map((alert) => (
            <div key={alert.id} className="glass-card p-5 space-y-4 relative overflow-hidden">
              <div className="flex items-start justify-between gap-3">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span
                      className={`text-[10px] font-extrabold px-2 py-0.5 rounded border uppercase ${
                        alert.severity === 'CRITICAL'
                          ? 'bg-rose-500/20 text-rose-400 border-rose-500/30'
                          : alert.severity === 'HIGH'
                          ? 'bg-amber-500/20 text-amber-400 border-amber-500/30'
                          : 'bg-indigo-500/20 text-indigo-400 border-indigo-500/30'
                      }`}
                    >
                      {alert.severity}
                    </span>
                    <span className="text-xs text-slate-400 font-mono">
                      Rule: {alert.rule_id ? alert.rule_id.substring(0, 8) : 'Threshold'}
                    </span>
                  </div>
                  <h3 className="font-bold text-slate-100 text-base">{alert.title}</h3>
                </div>

                <span
                  className={`text-xs font-bold px-2.5 py-1 rounded-lg border ${
                    alert.status === 'OPEN'
                      ? 'bg-rose-500/10 text-rose-400 border-rose-500/20'
                      : alert.status === 'ACKNOWLEDGED'
                      ? 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                      : 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                  }`}
                >
                  {alert.status}
                </span>
              </div>

              <p className="text-xs text-slate-300 bg-slate-950/60 p-3 rounded-xl border border-slate-800/80 leading-relaxed">
                {alert.description}
              </p>

              <div className="flex items-center justify-between pt-2 border-t border-slate-800 text-xs">
                <div className="flex items-center gap-1.5 text-slate-500">
                  <Clock className="w-3.5 h-3.5" />
                  <span>{new Date(alert.created_at).toLocaleString()}</span>
                </div>

                {alert.status === 'OPEN' && (
                  <button
                    onClick={() => handleUpdateStatus(alert.id, 'ACKNOWLEDGED')}
                    className="px-3 py-1 rounded-lg bg-amber-500/20 text-amber-300 hover:bg-amber-500/30 border border-amber-500/30 font-semibold text-xs transition-all"
                  >
                    Acknowledge
                  </button>
                )}
                {alert.status === 'ACKNOWLEDGED' && (
                  <button
                    onClick={() => handleUpdateStatus(alert.id, 'RESOLVED')}
                    className="px-3 py-1 rounded-lg bg-emerald-500/20 text-emerald-300 hover:bg-emerald-500/30 border border-emerald-500/30 font-semibold text-xs transition-all"
                  >
                    Resolve
                  </button>
                )}
              </div>
            </div>
          ))
        )}
      </div>

    </div>
  );
};
