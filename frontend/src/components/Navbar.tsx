import React from 'react';
import { ShieldCheck, Settings as SettingsIcon, History, Sparkles } from 'lucide-react';
import { SampleResumeInfo } from '../types';

interface NavbarProps {
  onOpenSettings: () => void;
  onOpenHistory: () => void;
  onSelectSample: (sampleId: string) => void;
  samples: SampleResumeInfo[];
  isLoading: boolean;
  onReset: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  onOpenSettings,
  onOpenHistory,
  onSelectSample,
  samples,
  isLoading,
  onReset,
}) => {
  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-800/80 bg-slate-950/85 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        
        {/* Logo and Brand */}
        <div 
          onClick={onReset}
          className="flex items-center space-x-3 cursor-pointer group select-none"
        >
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-teal-500 to-emerald-400 p-[1px] shadow-lg shadow-teal-500/20 group-hover:shadow-teal-500/40 transition-all duration-300">
            <div className="w-full h-full bg-slate-950 rounded-xl flex items-center justify-center">
              <ShieldCheck className="w-6 h-6 text-teal-400 group-hover:scale-110 transition-transform duration-300" />
            </div>
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-extrabold text-lg tracking-tight bg-gradient-to-r from-slate-100 via-teal-100 to-teal-300 bg-clip-text text-transparent">
                ResumeVerify
              </span>
              <span className="px-1.5 py-0.5 text-[10px] font-bold tracking-wider uppercase bg-teal-500/10 border border-teal-500/30 text-teal-400 rounded-md">
                AI
              </span>
            </div>
            <p className="text-[11px] text-slate-400 font-medium leading-none">
              Public Evidence Corroboration Engine
            </p>
          </div>
        </div>

        {/* Right Navigation & Quick Actions */}
        <div className="flex items-center space-x-3">
          
          {/* Sample Resumes Quick Selector */}
          {samples.length > 0 && (
            <div className="hidden md:flex items-center space-x-1.5 bg-slate-900/80 border border-slate-800 rounded-lg p-1">
              <span className="px-2 text-xs text-slate-400 font-medium flex items-center gap-1">
                <Sparkles className="w-3.5 h-3.5 text-teal-400" />
                Samples:
              </span>
              {samples.map((s) => (
                <button
                  key={s.id}
                  disabled={isLoading}
                  onClick={() => onSelectSample(s.id)}
                  className="px-2.5 py-1 text-xs font-medium rounded-md text-slate-300 hover:text-white hover:bg-slate-800 active:bg-slate-700 transition disabled:opacity-50"
                  title={s.description}
                >
                  {s.name.split(' ')[0]}
                </button>
              ))}
            </div>
          )}

          {/* Past Reports History */}
          <button
            onClick={onOpenHistory}
            className="flex items-center space-x-1.5 px-3 py-1.5 text-xs font-medium text-slate-300 hover:text-white bg-slate-900/80 hover:bg-slate-800 border border-slate-800 hover:border-slate-700 rounded-lg transition"
            title="View Past Verification Reports"
          >
            <History className="w-3.5 h-3.5 text-slate-400" />
            <span className="hidden sm:inline">History</span>
          </button>

          {/* Settings Button */}
          <button
            onClick={onOpenSettings}
            className="flex items-center space-x-1.5 px-3 py-1.5 text-xs font-medium text-slate-300 hover:text-white bg-slate-900/80 hover:bg-slate-800 border border-slate-800 hover:border-slate-700 rounded-lg transition"
            title="Configure GitHub Token & AI Models"
          >
            <SettingsIcon className="w-3.5 h-3.5 text-teal-400" />
            <span className="hidden sm:inline">Settings</span>
          </button>
        </div>

      </div>
    </header>
  );
};
