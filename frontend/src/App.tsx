import React, { useState, useEffect } from 'react';
import confetti from 'canvas-confetti';
import { 
  ShieldCheck, 
  FileText, 
  Globe, 
  Layers, 
  Sparkles, 
  AlertTriangle, 
  CheckCircle2, 
  HelpCircle,
  Lock,
  XCircle,
  ExternalLink,
  ChevronRight,
  Radar
} from 'lucide-react';

import { 
  VerificationReportResponse, 
  SampleResumeInfo 
} from './types';
import { 
  uploadResumePdf, 
  verifySampleResume, 
  getSampleResumes 
} from './api/client';

import { Navbar } from './components/Navbar';
import { FileUpload } from './components/FileUpload';
import { VerificationProgress } from './components/VerificationProgress';
import { DashboardSummary } from './components/DashboardSummary';
import { ClaimsList } from './components/ClaimsList';
import { UrlEvidenceView } from './components/UrlEvidenceView';
import { SettingsModal } from './components/SettingsModal';
import { ReportExportModal } from './components/ReportExportModal';
import { ResumePreviewModal } from './components/ResumePreviewModal';
import { HistoryModal } from './components/HistoryModal';

export function App() {
  const [report, setReport] = useState<VerificationReportResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [loadingFilename, setLoadingFilename] = useState<string>('');
  const [activeMainTab, setActiveMainTab] = useState<'claims' | 'urls' | 'radar'>('claims');
  const [samples, setSamples] = useState<SampleResumeInfo[]>([]);

  // Modals state
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [isExportOpen, setIsExportOpen] = useState(false);
  const [isResumePreviewOpen, setIsResumePreviewOpen] = useState(false);
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);

  useEffect(() => {
    // Load sample resumes
    getSampleResumes().then(setSamples).catch(console.error);
  }, []);

  const triggerConfetti = () => {
    try {
      confetti({
        particleCount: 80,
        spread: 70,
        origin: { y: 0.6 }
      });
    } catch {
      // Ignore if canvas-confetti is not loaded
    }
  };

  const handleFileUpload = async (file: File) => {
    setIsLoading(true);
    setLoadingFilename(file.name);
    try {
      const rep = await uploadResumePdf(file);
      setReport(rep);
      if (rep.summary.evidence_coverage_percentage >= 60) {
        triggerConfetti();
      }
    } catch (err: any) {
      alert(err.message || 'Failed to verify resume document');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectSample = async (sampleId: string) => {
    setIsLoading(true);
    const sample = samples.find((s) => s.id === sampleId);
    setLoadingFilename(sample ? `${sample.name}_Resume.pdf` : 'Sample Resume.pdf');
    try {
      const rep = await verifySampleResume(sampleId);
      setReport(rep);
      if (rep.summary.evidence_coverage_percentage >= 60) {
        triggerConfetti();
      }
    } catch (err: any) {
      alert(err.message || 'Failed to verify sample resume');
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setReport(null);
    setActiveMainTab('claims');
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100 selection:bg-teal-500/30 selection:text-teal-200">
      
      {/* Top Navigation */}
      <Navbar
        onOpenSettings={() => setIsSettingsOpen(true)}
        onOpenHistory={() => setIsHistoryOpen(true)}
        onSelectSample={handleSelectSample}
        samples={samples}
        isLoading={isLoading}
        onReset={handleReset}
      />

      {/* Main App Content */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        
        {isLoading ? (
          <VerificationProgress filename={loadingFilename} />
        ) : !report ? (
          <FileUpload
            onFileUpload={handleFileUpload}
            onSelectSample={handleSelectSample}
            samples={samples}
            isLoading={isLoading}
          />
        ) : (
          <div className="space-y-6 animate-in fade-in duration-300">
            
            {/* Top Dashboard Summary & Metrics */}
            <DashboardSummary
              report={report}
              onReset={handleReset}
              onExport={() => setIsExportOpen(true)}
              onViewResume={() => setIsResumePreviewOpen(true)}
            />

            {/* Navigation Tabs */}
            <div className="flex items-center space-x-2 border-b border-slate-800 pb-2">
              <button
                onClick={() => setActiveMainTab('claims')}
                className={`flex items-center space-x-2 px-4 py-2.5 rounded-xl text-xs font-bold transition ${
                  activeMainTab === 'claims'
                    ? 'bg-teal-500 text-slate-950 shadow-md shadow-teal-500/20'
                    : 'text-slate-400 hover:text-white hover:bg-slate-900'
                }`}
              >
                <Layers className="w-4 h-4" />
                <span>Claims Verification ({report.claims.length})</span>
              </button>

              <button
                onClick={() => setActiveMainTab('urls')}
                className={`flex items-center space-x-2 px-4 py-2.5 rounded-xl text-xs font-bold transition ${
                  activeMainTab === 'urls'
                    ? 'bg-teal-500 text-slate-950 shadow-md shadow-teal-500/20'
                    : 'text-slate-400 hover:text-white hover:bg-slate-900'
                }`}
              >
                <Globe className="w-4 h-4" />
                <span>URLs & Evidence Matrix ({report.urls.length})</span>
              </button>

              <button
                onClick={() => setActiveMainTab('radar')}
                className={`flex items-center space-x-2 px-4 py-2.5 rounded-xl text-xs font-bold transition ${
                  activeMainTab === 'radar'
                    ? 'bg-teal-500 text-slate-950 shadow-md shadow-teal-500/20'
                    : 'text-slate-400 hover:text-white hover:bg-slate-900'
                }`}
              >
                <Radar className="w-4 h-4" />
                <span>Insights & Notes ({report.strengths.length + report.risk_notes.length})</span>
              </button>
            </div>

            {/* Active Tab View */}
            {activeMainTab === 'claims' && (
              <ClaimsList claims={report.claims} />
            )}

            {activeMainTab === 'urls' && (
              <UrlEvidenceView urls={report.urls} />
            )}

            {activeMainTab === 'radar' && (
              <div className="space-y-6">
                
                {/* Strengths / Public Corroboration */}
                <div className="glass-panel rounded-2xl p-6 space-y-3">
                  <h3 className="text-sm font-bold uppercase tracking-wider text-emerald-400 flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4" />
                    Corroborated Public Strengths
                  </h3>

                  {report.strengths.length > 0 ? (
                    <div className="space-y-2">
                      {report.strengths.map((str, idx) => (
                        <div
                          key={idx}
                          className="p-3 rounded-xl bg-emerald-950/30 border border-emerald-800/40 text-xs text-emerald-200 flex items-start space-x-2"
                        >
                          <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                          <span>{str}</span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-xs text-slate-400 italic">No strong public corrobations identified.</p>
                  )}
                </div>

                {/* Risk & Verification Notes */}
                <div className="glass-panel rounded-2xl p-6 space-y-3">
                  <h3 className="text-sm font-bold uppercase tracking-wider text-amber-400 flex items-center gap-2">
                    <AlertTriangle className="w-4 h-4" />
                    Verification & Access Observations
                  </h3>

                  {report.risk_notes.length > 0 ? (
                    <div className="space-y-2">
                      {report.risk_notes.map((note, idx) => (
                        <div
                          key={idx}
                          className="p-3 rounded-xl bg-amber-950/30 border border-amber-800/40 text-xs text-amber-200 flex items-start space-x-2"
                        >
                          <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                          <span>{note}</span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-xs text-slate-400 italic">No broken links or access restrictions detected.</p>
                  )}

                  <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 text-[11px] text-slate-400 space-y-1">
                    <p className="font-semibold text-slate-300">Policy Reminder on Unverified Claims:</p>
                    <p>
                      ResumeVerify AI adheres to strict objective principles: claims without public corroboration are labeled <span className="text-slate-200 font-semibold">Unverified</span> rather than "false" or "fake", as candidates frequently work on closed-source, proprietary enterprise repositories.
                    </p>
                  </div>
                </div>

              </div>
            )}

          </div>
        )}

      </main>

      {/* Footer */}
      <footer className="w-full border-t border-slate-900 bg-slate-950 py-6 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <p>© 2026 ResumeVerify AI • Evidence-Backed HR Intelligence Engine</p>
          <p className="text-[11px] text-slate-600">
            PyMuPDF • GitHub REST API • SSRF Protection Shield
          </p>
        </div>
      </footer>

      {/* Modals */}
      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
      />

      {report && (
        <ReportExportModal
          isOpen={isExportOpen}
          onClose={() => setIsExportOpen(false)}
          report={report}
        />
      )}

      {report && (
        <ResumePreviewModal
          isOpen={isResumePreviewOpen}
          onClose={() => setIsResumePreviewOpen(false)}
          rawText={report.extracted_text_preview || ''}
          filename={report.filename}
        />
      )}

      <HistoryModal
        isOpen={isHistoryOpen}
        onClose={() => setIsHistoryOpen(false)}
        onSelectReport={(rep) => {
          setReport(rep);
          setActiveMainTab('claims');
        }}
      />

    </div>
  );
}

export default App;
