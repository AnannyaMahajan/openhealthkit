import React, { useEffect, useState } from 'react';
import { Navbar } from './components/Navbar';
import { DemoBanner } from './components/DemoBanner';
import { OverviewPage } from './pages/OverviewPage';
import { RecordsPage } from './pages/RecordsPage';
import { AlertsPage } from './pages/AlertsPage';
import { SyncPage } from './pages/SyncPage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { SettingsPage } from './pages/SettingsPage';
import { fetchAnalyticsSummary, fetchAlerts, fetchHealthStatus, fetchRecords, isDemoMode } from './api/client';
import { AnalyticsSummary, AlertItem, HealthRecord } from './types';
import { Language } from './i18n/translations';
import { AlertOctagon, RefreshCw } from 'lucide-react';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [lang, setLang] = useState<Language>('en');
  const [apiStatus, setApiStatus] = useState('checking');
  const [isError, setIsError] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);
  const [records, setRecords] = useState<HealthRecord[]>([]);
  const [alerts, setAlerts] = useState<AlertItem[]>([]);

  const loadData = async () => {
    setIsError(false);
    setApiStatus('checking');
    try {
      const health = await fetchHealthStatus();
      setApiStatus(health.status || 'healthy');

      const sum = await fetchAnalyticsSummary();
      setSummary(sum);

      const recs = await fetchRecords();
      setRecords(recs);

      const alrts = await fetchAlerts();
      setAlerts(alrts);
    } catch (err: any) {
      if (!isDemoMode) {
        setApiStatus('offline');
        setIsError(true);
        setErrorMessage(err?.message || 'Unable to connect to OpenHealthKit API backend.');
      }
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-['Plus_Jakarta_Sans',sans-serif]">
      {/* Top Synthetic Demo Banner (shows only when VITE_DEMO_MODE=true) */}
      <DemoBanner lang={lang} />

      {/* Main Navbar */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        lang={lang}
        setLang={setLang}
        apiStatus={apiStatus}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {isError && !isDemoMode ? (
          <div className="glass-card p-12 text-center max-w-xl mx-auto my-12 space-y-4 border-rose-500/30">
            <div className="w-16 h-16 rounded-full bg-rose-500/10 border border-rose-500/30 text-rose-400 flex items-center justify-center mx-auto">
              <AlertOctagon className="w-8 h-8" />
            </div>
            <h2 className="text-xl font-bold text-white">API Unavailable</h2>
            <p className="text-sm text-slate-400 leading-relaxed">
              OpenHealthKit dashboard could not reach the backend API at <code className="bg-slate-900 px-2 py-1 rounded text-teal-300">/api/v1</code>.
            </p>
            <p className="text-xs text-slate-500">{errorMessage}</p>
            <div className="pt-4 flex items-center justify-center gap-3">
              <button
                onClick={loadData}
                className="px-5 py-2.5 rounded-xl bg-teal-500 hover:bg-teal-400 text-slate-950 font-bold text-xs flex items-center gap-2 transition-all shadow-lg shadow-teal-500/20"
              >
                <RefreshCw className="w-4 h-4" />
                Retry Connection
              </button>
            </div>
          </div>
        ) : (
          <>
            {activeTab === 'overview' && (
              <OverviewPage summary={summary} alerts={alerts} lang={lang} />
            )}
            {activeTab === 'records' && (
              <RecordsPage records={records} onRefresh={loadData} lang={lang} />
            )}
            {activeTab === 'alerts' && (
              <AlertsPage alerts={alerts} onRefresh={loadData} lang={lang} />
            )}
            {activeTab === 'sync' && <SyncPage lang={lang} />}
            {activeTab === 'analytics' && <AnalyticsPage summary={summary} lang={lang} />}
            {activeTab === 'settings' && <SettingsPage lang={lang} setLang={setLang} />}
          </>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 bg-slate-900/60 py-6 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>OpenHealthKit Open-Source Toolkit &copy; 2026 Anannya Mahajan</span>
          <span>Released under Apache License 2.0</span>
        </div>
      </footer>
    </div>
  );
};

export default App;
