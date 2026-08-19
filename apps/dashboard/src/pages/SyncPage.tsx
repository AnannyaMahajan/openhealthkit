import React, { useState } from 'react';
import { RefreshCw, Database, CheckCircle2, AlertTriangle, ArrowUpRight, ArrowDownLeft } from 'lucide-react';
import { SyncItem } from '../types';
import { translations, Language } from '../i18n/translations';

interface SyncPageProps {
  lang: Language;
}

export const SyncPage: React.FC<SyncPageProps> = ({ lang }) => {
  const t = translations[lang];

  // Simulation state for offline queue inspector
  const [syncQueue, setSyncQueue] = useState<SyncItem[]>([
    {
      id: 'sync-rec-101',
      entity_type: 'health_record',
      entity_id: 'SYNTH-PATIENT-1002',
      action: 'CREATE',
      state: 'PENDING',
      client_timestamp: new Date().toISOString(),
      payload: { patient_identifier: 'SYNTH-PATIENT-1002', age_years: 42, gender: 'Female' },
    },
    {
      id: 'sync-rec-102',
      entity_type: 'observation',
      entity_id: 'obs-uuid-8812',
      action: 'CREATE',
      state: 'PENDING',
      client_timestamp: new Date().toISOString(),
      payload: { observation_type: 'water_turbidity_ntu', value_number: 6.8, unit: 'NTU' },
    },
    {
      id: 'sync-rec-103',
      entity_type: 'health_record',
      entity_id: 'SYNTH-PATIENT-1003',
      action: 'UPDATE',
      state: 'CONFLICT',
      client_timestamp: new Date(Date.now() - 3600000).toISOString(),
      payload: { age_years: 43 },
    },
  ]);

  const [isPushing, setIsPushing] = useState(false);

  const handleSimulateSync = () => {
    setIsPushing(true);
    setTimeout(() => {
      setSyncQueue(prev =>
        prev.map(item => ({
          ...item,
          state: item.state === 'PENDING' ? 'SYNCED' : item.state,
        }))
      );
      setIsPushing(false);
    }, 1200);
  };

  return (
    <div className="space-y-6">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">{t.nav_sync}</h1>
          <p className="text-sm text-slate-400">Offline SQLite Queue &amp; Server Synchronization Control</p>
        </div>

        <button
          onClick={handleSimulateSync}
          disabled={isPushing}
          className="flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-teal-500 hover:bg-teal-400 text-slate-950 font-bold text-sm transition-all shadow-lg shadow-teal-500/20 disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${isPushing ? 'animate-spin' : ''}`} />
          {t.btn_sync_now}
        </button>
      </div>

      {/* Sync Strategy Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="glass-card p-5 space-y-2 border-teal-500/20">
          <div className="flex items-center justify-between text-teal-400 font-semibold text-xs uppercase">
            <span>Local Store</span>
            <Database className="w-4 h-4" />
          </div>
          <p className="text-xl font-bold text-white">SQLite Engine</p>
          <p className="text-xs text-slate-400">Maintains transactional offline queue when disconnected.</p>
        </div>

        <div className="glass-card p-5 space-y-2 border-amber-500/20">
          <div className="flex items-center justify-between text-amber-400 font-semibold text-xs uppercase">
            <span>Conflict Resolution</span>
            <AlertTriangle className="w-4 h-4" />
          </div>
          <p className="text-xl font-bold text-white">SERVER_WINS</p>
          <p className="text-xs text-slate-400">Configurable (SERVER_WINS / CLIENT_WINS / LAST_WRITE_WINS).</p>
        </div>

        <div className="glass-card p-5 space-y-2 border-indigo-500/20">
          <div className="flex items-center justify-between text-indigo-400 font-semibold text-xs uppercase">
            <span>Remote Backend</span>
            <ArrowUpRight className="w-4 h-4" />
          </div>
          <p className="text-xl font-bold text-white">PostgreSQL API</p>
          <p className="text-xs text-slate-400">FastAPI delta push/pull via /api/v1/sync/push.</p>
        </div>
      </div>

      {/* Queue Inspector */}
      <div className="glass-card p-6 space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <RefreshCw className="w-5 h-5 text-teal-400" />
            Client Pending Queue (SQLite Buffer)
          </h2>
          <span className="text-xs font-semibold bg-slate-800 text-slate-300 px-2.5 py-1 rounded-full border border-slate-700">
            {syncQueue.filter(i => i.state === 'PENDING').length} Pending Items
          </span>
        </div>

        <div className="space-y-3">
          {syncQueue.map((item) => (
            <div
              key={item.id}
              className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 flex items-center justify-between gap-4"
            >
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="font-mono font-bold text-xs text-teal-400">{item.action}</span>
                  <span className="font-semibold text-sm text-slate-200">{item.entity_type}</span>
                  <span className="text-xs text-slate-500 font-mono">({item.entity_id})</span>
                </div>
                <pre className="text-[11px] text-slate-400 font-mono bg-slate-900 px-2 py-1 rounded border border-slate-800">
                  {JSON.stringify(item.payload)}
                </pre>
              </div>

              <div className="flex items-center gap-3">
                <span
                  className={`text-xs font-extrabold px-3 py-1 rounded-lg border uppercase ${
                    item.state === 'SYNCED'
                      ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                      : item.state === 'CONFLICT'
                      ? 'bg-rose-500/10 text-rose-400 border-rose-500/20'
                      : 'bg-amber-500/10 text-amber-400 border-amber-500/20 animate-pulse'
                  }`}
                >
                  {item.state}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

    </div>
  );
};
