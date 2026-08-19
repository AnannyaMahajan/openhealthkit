import React from 'react';
import { BarChart3, Activity, AlertTriangle, ShieldCheck } from 'lucide-react';
import { AnalyticsSummary } from '../types';
import { translations, Language } from '../i18n/translations';

interface AnalyticsPageProps {
  summary: AnalyticsSummary | null;
  lang: Language;
}

export const AnalyticsPage: React.FC<AnalyticsPageProps> = ({ summary, lang }) => {
  const t = translations[lang];

  return (
    <div className="space-y-6">
      
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">{t.nav_analytics}</h1>
        <p className="text-sm text-slate-400">Public health metrics &amp; privacy-preserving aggregations</p>
      </div>

      {/* Analytics Charts & Visual Summaries */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* Observations by Category */}
        <div className="glass-card p-6 space-y-4">
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Activity className="w-5 h-5 text-indigo-400" />
            Observations by Category
          </h2>

          <div className="space-y-3 pt-2">
            {summary?.observations_by_type.map((item) => (
              <div key={item.category} className="space-y-1">
                <div className="flex justify-between text-xs font-semibold text-slate-300">
                  <span>{item.category}</span>
                  <span className="font-mono text-teal-400">{item.count} entries</span>
                </div>
                <div className="w-full h-2 rounded-full bg-slate-800 overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-teal-500 to-indigo-500 rounded-full"
                    style={{ width: `${Math.min(100, item.count * 5)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Alerts by Severity Distribution */}
        <div className="glass-card p-6 space-y-4">
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-rose-400" />
            Alert Severity Breakdown
          </h2>

          <div className="space-y-3 pt-2">
            {summary?.alerts_by_severity.map((item) => (
              <div key={item.severity} className="space-y-1">
                <div className="flex justify-between text-xs font-semibold text-slate-300">
                  <span>{item.severity}</span>
                  <span className="font-mono text-rose-400">{item.count} alerts</span>
                </div>
                <div className="w-full h-2 rounded-full bg-slate-800 overflow-hidden">
                  <div
                    className={`h-full rounded-full ${
                      item.severity === 'CRITICAL'
                        ? 'bg-rose-500'
                        : item.severity === 'HIGH'
                        ? 'bg-amber-500'
                        : 'bg-indigo-500'
                    }`}
                    style={{ width: `${Math.min(100, item.count * 20)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

      </div>

    </div>
  );
};
