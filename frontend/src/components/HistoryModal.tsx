import React, { useState, useEffect } from 'react';
import { X, History, Trash2, ArrowRight, ShieldCheck, CheckCircle2, AlertTriangle, Loader2 } from 'lucide-react';
import { getRecentReports, deleteReport, getReport } from '../api/client';
import { VerificationReportResponse } from '../types';

interface HistoryModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectReport: (report: VerificationReportResponse) => void;
}

export const HistoryModal: React.FC<HistoryModalProps> = ({
  isOpen,
  onClose,
  onSelectReport,
}) => {
  const [reports, setReports] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [loadingReportId, setLoadingReportId] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      loadReports();
    }
  }, [isOpen]);

  const loadReports = async () => {
    setLoading(true);
    try {
      const data = await getRecentReports();
      setReports(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleSelect = async (id: string) => {
    setLoadingReportId(id);
    try {
      const fullReport = await getReport(id);
      onSelectReport(fullReport);
      onClose();
    } catch (e: any) {
      alert(e.message || 'Failed to load report');
    } finally {
      setLoadingReportId(null);
    }
  };

  const handleDelete = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    if (confirm('Delete this verification report?')) {
      await deleteReport(id);
      setReports((prev) => prev.filter((r) => r.id !== id));
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-in fade-in">
      <div className="glass-panel rounded-2xl w-full max-w-xl overflow-hidden shadow-2xl border border-slate-800 flex flex-col max-h-[80vh]">
        
        {/* Header */}
        <div className="p-5 border-b border-slate-800 flex items-center justify-between shrink-0">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 rounded-lg bg-teal-500/10 border border-teal-500/30 flex items-center justify-center text-teal-400">
              <History className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white">Verification History</h3>
              <p className="text-xs text-slate-400">Past candidate verification runs</p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="w-8 h-8 rounded-lg bg-slate-850 hover:bg-slate-800 flex items-center justify-center text-slate-400 hover:text-white transition"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* List */}
        <div className="p-6 overflow-y-auto space-y-3">
          {loading ? (
            <div className="py-12 flex flex-col items-center justify-center space-y-2 text-slate-400">
              <Loader2 className="w-6 h-6 animate-spin text-teal-400" />
              <p className="text-xs">Loading past reports...</p>
            </div>
          ) : reports.length > 0 ? (
            reports.map((rep) => (
              <div
                key={rep.id}
                onClick={() => handleSelect(rep.id)}
                className="p-4 rounded-xl bg-slate-850/80 border border-slate-800 hover:border-teal-500/40 cursor-pointer group transition flex items-center justify-between gap-3"
              >
                <div className="space-y-1 min-w-0">
                  <div className="flex items-center space-x-2">
                    <h4 className="text-sm font-bold text-white group-hover:text-teal-300 truncate">
                      {rep.candidate_name || rep.filename}
                    </h4>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-teal-400 font-semibold">
                      {rep.evidence_coverage_percentage}% Coverage
                    </span>
                  </div>

                  <div className="flex items-center space-x-3 text-xs text-slate-400">
                    <span>{rep.total_claims} claims</span>
                    <span>•</span>
                    <span className="text-emerald-400 font-medium">{rep.supported_claims} supported</span>
                    <span>•</span>
                    <span>{rep.created_at ? new Date(rep.created_at).toLocaleDateString() : ''}</span>
                  </div>
                </div>

                <div className="flex items-center space-x-2 shrink-0">
                  <button
                    onClick={(e) => handleDelete(e, rep.id)}
                    className="p-2 rounded-lg bg-slate-900 hover:bg-rose-950/60 text-slate-400 hover:text-rose-400 border border-slate-800 transition"
                    title="Delete report"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>

                  <div className="w-8 h-8 rounded-lg bg-slate-800 group-hover:bg-teal-500/20 group-hover:text-teal-400 flex items-center justify-center text-slate-400 transition">
                    {loadingReportId === rep.id ? (
                      <Loader2 className="w-4 h-4 animate-spin text-teal-400" />
                    ) : (
                      <ArrowRight className="w-4 h-4" />
                    )}
                  </div>
                </div>
              </div>
            ))
          ) : (
            <div className="py-12 text-center text-slate-400 space-y-1">
              <p className="text-xs">No verification reports saved in history yet.</p>
              <p className="text-[11px] text-slate-500">Upload a resume or run a sample to generate your first report.</p>
            </div>
          )}
        </div>

      </div>
    </div>
  );
};
