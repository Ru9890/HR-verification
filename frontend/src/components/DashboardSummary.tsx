import React from 'react';
import { 
  CheckCircle2, 
  AlertTriangle, 
  HelpCircle, 
  XCircle, 
  Lock, 
  Globe, 
  FileText, 
  Download, 
  RotateCcw,
  Sparkles,
  ExternalLink,
  ShieldCheck
} from 'lucide-react';
import { VerificationReportResponse } from '../types';
import { CoverageGauge } from './CoverageGauge';

interface DashboardSummaryProps {
  report: VerificationReportResponse;
  onReset: () => void;
  onExport: () => void;
  onViewResume: () => void;
}

export const DashboardSummary: React.FC<DashboardSummaryProps> = ({
  report,
  onReset,
  onExport,
  onViewResume,
}) => {
  const { summary, candidate } = report;

  return (
    <div className="space-y-6">
      
      {/* Candidate Banner & Actions Header */}
      <div className="glass-panel rounded-2xl p-6 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-96 bg-teal-500/5 rounded-full blur-3xl pointer-events-none"></div>

        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 relative z-10">
          
          <div className="space-y-1">
            <div className="flex items-center space-x-2">
              <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-teal-500/10 border border-teal-500/30 text-teal-400">
                VERIFICATION REPORT
              </span>
              <span className="text-xs text-slate-400">
                {new Date(report.created_at).toLocaleDateString(undefined, { dateStyle: 'medium' })}
              </span>
            </div>

            <h1 className="text-2xl sm:text-3xl font-extrabold text-white">
              {candidate.name || 'Candidate Resume'}
            </h1>

            <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-slate-400">
              {candidate.email && (
                <span>Email: <span className="text-slate-200">{candidate.email}</span></span>
              )}
              {candidate.phone && (
                <span>Phone: <span className="text-slate-200">{candidate.phone}</span></span>
              )}
              <span>File: <span className="text-slate-200 font-mono">{report.filename}</span></span>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-wrap items-center gap-2.5">
            <button
              onClick={onViewResume}
              className="flex items-center space-x-1.5 px-3 py-2 text-xs font-semibold rounded-xl bg-slate-800 hover:bg-slate-750 text-slate-200 border border-slate-700 hover:border-slate-600 transition shadow-sm"
            >
              <FileText className="w-3.5 h-3.5 text-teal-400" />
              <span>Resume Text</span>
            </button>

            <button
              onClick={onExport}
              className="flex items-center space-x-1.5 px-3.5 py-2 text-xs font-semibold rounded-xl bg-teal-500 hover:bg-teal-400 text-slate-950 font-bold transition shadow-lg shadow-teal-500/20 active:scale-95"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Export Report</span>
            </button>

            <button
              onClick={onReset}
              className="flex items-center space-x-1.5 px-3 py-2 text-xs font-semibold rounded-xl bg-slate-850 hover:bg-slate-800 text-slate-300 border border-slate-800 transition"
              title="Verify another resume"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>New Verify</span>
            </button>
          </div>

        </div>
      </div>

      {/* Metrics Cards Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
        
        {/* Coverage Gauge Card */}
        <div className="glass-panel rounded-2xl p-6 flex flex-col items-center justify-center text-center">
          <CoverageGauge percentage={summary.evidence_coverage_percentage} size={150} />
          <p className="text-[11px] text-slate-400 mt-2">
            Weighted verification percentage across extracted claims
          </p>
        </div>

        {/* URLs Analyzed Card */}
        <div className="glass-panel rounded-2xl p-5 flex flex-col justify-between space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
              URLs Discovered
            </span>
            <div className="w-7 h-7 rounded-lg bg-teal-500/10 border border-teal-500/20 flex items-center justify-center text-teal-400">
              <Globe className="w-4 h-4" />
            </div>
          </div>

          <div>
            <div className="text-3xl font-extrabold text-white">
              {summary.total_urls}
            </div>
            <div className="text-xs text-slate-400 mt-1">
              {summary.accessible_urls} Accessible across web & APIs
            </div>
          </div>

          <div className="space-y-1.5 pt-2 border-t border-slate-800/80 text-xs">
            <div className="flex items-center justify-between text-emerald-400">
              <span className="flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span> Accessible
              </span>
              <span className="font-semibold">{summary.accessible_urls}</span>
            </div>
            <div className="flex items-center justify-between text-purple-400">
              <span className="flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-purple-400"></span> Restricted / Auth
              </span>
              <span className="font-semibold">{summary.restricted_urls}</span>
            </div>
            <div className="flex items-center justify-between text-rose-400">
              <span className="flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-rose-400"></span> Broken (404/Error)
              </span>
              <span className="font-semibold">{summary.broken_urls}</span>
            </div>
          </div>
        </div>

        {/* Claims Breakdown Matrix (Spans 2 columns) */}
        <div className="glass-panel rounded-2xl p-5 lg:col-span-2 flex flex-col justify-between space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                Claims Analyzed
              </span>
              <div className="text-2xl sm:text-3xl font-extrabold text-white">
                {summary.total_claims} <span className="text-xs font-normal text-slate-400">statements verified</span>
              </div>
            </div>
            <div className="w-7 h-7 rounded-lg bg-teal-500/10 border border-teal-500/20 flex items-center justify-center text-teal-400">
              <ShieldCheck className="w-4 h-4" />
            </div>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5 pt-2 border-t border-slate-800/80">
            
            {/* Supported */}
            <div className="bg-slate-850/70 border border-emerald-500/20 rounded-xl p-2.5">
              <div className="flex items-center space-x-1.5 text-emerald-400 text-xs font-bold">
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>Supported</span>
              </div>
              <div className="text-2xl font-black text-white mt-1">
                {summary.supported_claims}
              </div>
            </div>

            {/* Partially Supported */}
            <div className="bg-slate-850/70 border border-amber-500/20 rounded-xl p-2.5">
              <div className="flex items-center space-x-1.5 text-amber-400 text-xs font-bold">
                <AlertTriangle className="w-3.5 h-3.5" />
                <span>Partial</span>
              </div>
              <div className="text-2xl font-black text-white mt-1">
                {summary.partially_supported_claims}
              </div>
            </div>

            {/* Unverified */}
            <div className="bg-slate-850/70 border border-slate-700/50 rounded-xl p-2.5">
              <div className="flex items-center space-x-1.5 text-slate-300 text-xs font-bold">
                <HelpCircle className="w-3.5 h-3.5 text-slate-400" />
                <span>Unverified</span>
              </div>
              <div className="text-2xl font-black text-white mt-1">
                {summary.unverified_claims}
              </div>
            </div>

            {/* Broken */}
            <div className="bg-slate-850/70 border border-rose-500/20 rounded-xl p-2.5">
              <div className="flex items-center space-x-1.5 text-rose-400 text-xs font-bold">
                <XCircle className="w-3.5 h-3.5" />
                <span>Broken</span>
              </div>
              <div className="text-2xl font-black text-white mt-1">
                {summary.broken_claims}
              </div>
            </div>

            {/* Restricted */}
            <div className="bg-slate-850/70 border border-purple-500/20 rounded-xl p-2.5 col-span-2 sm:col-span-1">
              <div className="flex items-center space-x-1.5 text-purple-400 text-xs font-bold">
                <Lock className="w-3.5 h-3.5" />
                <span>Restricted</span>
              </div>
              <div className="text-2xl font-black text-white mt-1">
                {summary.restricted_claims}
              </div>
            </div>

          </div>
        </div>

      </div>

    </div>
  );
};
