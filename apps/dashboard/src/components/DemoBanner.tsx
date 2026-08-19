import React from 'react';
import { Database } from 'lucide-react';
import { isDemoMode } from '../api/client';
import { translations, Language } from '../i18n/translations';

interface DemoBannerProps {
  lang: Language;
}

export const DemoBanner: React.FC<DemoBannerProps> = ({ lang }) => {
  if (!isDemoMode) return null;

  const t = translations[lang];

  return (
    <div className="bg-amber-500/10 border-b border-amber-500/30 px-4 py-2 text-xs font-medium text-amber-300 flex items-center justify-between">
      <div className="flex items-center gap-2 max-w-7xl mx-auto w-full">
        <span className="bg-amber-500/20 text-amber-400 px-2.5 py-0.5 rounded-full font-extrabold uppercase tracking-wider text-[10px] flex items-center gap-1 border border-amber-500/40">
          <Database className="w-3.5 h-3.5" />
          DEMO MODE — SYNTHETIC DATA
        </span>
        <span>{t.demo_notice}</span>
      </div>
    </div>
  );
};
