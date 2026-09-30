import React, { useEffect, useState } from 'react';
import { Loader2, CheckCircle2 } from 'lucide-react';

interface VerificationProgressProps {
  filename?: string;
}

const PIPELINE_STEPS = [
  { title: 'PyMuPDF Parser', desc: 'Extracting text, structure & embedded link annotations' },
  { title: 'Claim & Entity Engine', desc: 'Identifying project, skill & experience statements' },
  { title: 'URL Classifier & SSRF Shield', desc: 'Validating IP safety, categorizing domains' },
  { title: 'GitHub REST API Inspector', desc: 'Querying repo manifests, languages & commits' },
  { title: 'Evidence Matcher', desc: 'Corroborating claims against gathered evidence' },
  { title: 'Report Compiler', desc: 'Calculating coverage % and discrepancy radar' },
];

export const VerificationProgress: React.FC<VerificationProgressProps> = ({ filename }) => {
  const [currentStep, setCurrentStep] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentStep((prev) => (prev < PIPELINE_STEPS.length - 1 ? prev + 1 : prev));
    }, 1200);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="max-w-xl mx-auto px-4 py-16 text-center">
      <div className="glass-panel rounded-2xl p-8 space-y-6 shadow-2xl relative overflow-hidden">
        
        {/* Glow Header */}
        <div className="w-16 h-16 rounded-2xl bg-teal-500/10 border border-teal-500/30 flex items-center justify-center text-teal-400 mx-auto animate-pulse">
          <Loader2 className="w-8 h-8 animate-spin text-teal-400" />
        </div>

        <div className="space-y-1.5">
          <h2 className="text-xl font-bold text-white">
            Verifying Resume Evidence...
          </h2>
          {filename && (
            <p className="text-xs text-teal-400 font-mono">
              {filename}
            </p>
          )}
          <p className="text-xs text-slate-400">
            Querying official public APIs and cross-referencing code dependencies.
          </p>
        </div>

        {/* Pipeline Step List */}
        <div className="space-y-3 text-left pt-2">
          {PIPELINE_STEPS.map((step, idx) => {
            const isDone = idx < currentStep;
            const isCurrent = idx === currentStep;

            return (
              <div
                key={idx}
                className={`flex items-start space-x-3 p-2.5 rounded-lg border transition-all duration-300 ${
                  isCurrent
                    ? 'bg-teal-950/40 border-teal-500/40 text-teal-200'
                    : isDone
                    ? 'bg-slate-900/40 border-slate-800 text-slate-300'
                    : 'opacity-40 border-transparent text-slate-500'
                }`}
              >
                <div className="mt-0.5 shrink-0">
                  {isDone ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  ) : isCurrent ? (
                    <Loader2 className="w-4 h-4 text-teal-400 animate-spin" />
                  ) : (
                    <div className="w-4 h-4 rounded-full border border-slate-700 flex items-center justify-center text-[10px]">
                      {idx + 1}
                    </div>
                  )}
                </div>

                <div className="flex-1 min-w-0">
                  <div className="text-xs font-semibold">{step.title}</div>
                  <div className="text-[11px] text-slate-400">{step.desc}</div>
                </div>
              </div>
            );
          })}
        </div>

      </div>
    </div>
  );
};
