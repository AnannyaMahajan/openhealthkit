import React from 'react';
import { Settings, Globe, Shield, Database, Server } from 'lucide-react';
import { translations, Language } from '../i18n/translations';

interface SettingsPageProps {
  lang: Language;
  setLang: (lang: Language) => void;
}

export const SettingsPage: React.FC<SettingsPageProps> = ({ lang, setLang }) => {
  const t = translations[lang];

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">{t.nav_settings}</h1>
        <p className="text-sm text-slate-400">Toolkit configuration &amp; localization preferences</p>
      </div>

      <div className="glass-card p-6 space-y-6 divide-y divide-slate-800">
        
        {/* Language Preferences */}
        <div className="space-y-3">
          <h2 className="text-sm font-bold text-white uppercase tracking-wider text-slate-400 flex items-center gap-2">
            <Globe className="w-4 h-4 text-teal-400" />
            Language &amp; Internationalization (i18n)
          </h2>
          <div className="flex items-center gap-4">
            <button
              onClick={() => setLang('en')}
              className={`px-4 py-2.5 rounded-xl border text-sm font-semibold transition-all ${
                lang === 'en'
                  ? 'bg-teal-500/20 text-teal-300 border-teal-500/40'
                  : 'bg-slate-900 text-slate-400 border-slate-800 hover:text-white'
              }`}
            >
              English (en)
            </button>
            <button
              onClick={() => setLang('hi')}
              className={`px-4 py-2.5 rounded-xl border text-sm font-semibold transition-all ${
                lang === 'hi'
                  ? 'bg-teal-500/20 text-teal-300 border-teal-500/40'
                  : 'bg-slate-900 text-slate-400 border-slate-800 hover:text-white'
              }`}
            >
              हिन्दी (Hindi - hi)
            </button>
          </div>
        </div>

        {/* API Backend Info */}
        <div className="pt-6 space-y-3">
          <h2 className="text-sm font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
            <Server className="w-4 h-4 text-indigo-400" />
            Connected Server Environment
          </h2>
          <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 space-y-2 text-xs font-mono">
            <div className="flex justify-between">
              <span className="text-slate-400">REST API URL:</span>
              <span className="text-teal-400">http://localhost:8000/api/v1</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Database Backend:</span>
              <span className="text-slate-200">SQLite (Dev) / PostgreSQL (Prod)</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Package Version:</span>
              <span className="text-slate-200">openhealthkit v0.1.0</span>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
};
