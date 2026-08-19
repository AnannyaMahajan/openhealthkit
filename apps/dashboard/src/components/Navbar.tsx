import React from 'react';
import { 
  Activity, 
  FileText, 
  AlertTriangle, 
  RefreshCw, 
  BarChart3, 
  Settings, 
  ShieldCheck, 
  Globe 
} from 'lucide-react';
import { translations, Language } from '../i18n/translations';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  lang: Language;
  setLang: (lang: Language) => void;
  apiStatus: string;
}

export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  setActiveTab,
  lang,
  setLang,
  apiStatus,
}) => {
  const t = translations[lang];

  const navItems = [
    { id: 'overview', label: t.nav_overview, icon: Activity },
    { id: 'records', label: t.nav_records, icon: FileText },
    { id: 'alerts', label: t.nav_alerts, icon: AlertTriangle },
    { id: 'sync', label: t.nav_sync, icon: RefreshCw },
    { id: 'analytics', label: t.nav_analytics, icon: BarChart3 },
    { id: 'settings', label: t.nav_settings, icon: Settings },
  ];

  return (
    <header className="border-b border-slate-800 bg-slate-900/90 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          
          {/* Logo & Brand */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-teal-500 to-emerald-400 flex items-center justify-center shadow-lg shadow-teal-500/20 text-slate-950 font-black text-xl">
              OHK
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-lg text-white tracking-tight">{t.app_name}</span>
                <span className="text-[10px] font-semibold bg-teal-500/10 text-teal-400 px-2 py-0.5 rounded-full border border-teal-500/20">
                  v0.1.0-oss
                </span>
              </div>
              <p className="text-xs text-slate-400 hidden sm:block">Toolkit Dashboard</p>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center gap-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                    isActive
                      ? 'bg-teal-500/10 text-teal-400 border border-teal-500/20 shadow-sm'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {item.label}
                </button>
              );
            })}
          </nav>

          {/* Controls: Health Status & Language Switcher */}
          <div className="flex items-center gap-3">
            
            {/* Server Status Badge */}
            <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-800 border border-slate-700 text-xs text-slate-300">
              <span className={`w-2 h-2 rounded-full ${apiStatus === 'healthy' ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400'}`} />
              <span className="hidden sm:inline">API:</span>
              <span className="font-semibold capitalize text-slate-200">{apiStatus}</span>
            </div>

            {/* i18n Switcher */}
            <div className="flex items-center bg-slate-800 rounded-lg p-1 border border-slate-700">
              <button
                onClick={() => setLang('en')}
                className={`px-2 py-1 text-xs font-semibold rounded ${lang === 'en' ? 'bg-teal-500 text-slate-950' : 'text-slate-400 hover:text-white'}`}
              >
                EN
              </button>
              <button
                onClick={() => setLang('hi')}
                className={`px-2 py-1 text-xs font-semibold rounded ${lang === 'hi' ? 'bg-teal-500 text-slate-950' : 'text-slate-400 hover:text-white'}`}
              >
                HI
              </button>
            </div>

          </div>

        </div>
      </div>
    </header>
  );
};
