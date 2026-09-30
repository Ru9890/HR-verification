import React, { useState, useRef } from 'react';
import { UploadCloud, FileText, Sparkles, CheckCircle2, AlertCircle, Shield, ArrowRight, Lock, HelpCircle, Code2, Globe } from 'lucide-react';
import { SampleResumeInfo } from '../types';

interface FileUploadProps {
  onFileUpload: (file: File) => void;
  onSelectSample: (sampleId: string) => void;
  samples: SampleResumeInfo[];
  isLoading: boolean;
}

export const FileUpload: React.FC<FileUploadProps> = ({
  onFileUpload,
  onSelectSample,
  samples,
  isLoading,
}) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = () => {
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    setErrorMessage(null);

    const files = e.dataTransfer.files;
    if (files.length > 0) {
      validateAndUpload(files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setErrorMessage(null);
    if (e.target.files && e.target.files.length > 0) {
      validateAndUpload(e.target.files[0]);
    }
  };

  const validateAndUpload = (file: File) => {
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setErrorMessage('Please upload a valid PDF document (.pdf)');
      return;
    }
    if (file.size > 15 * 1024 * 1024) {
      setErrorMessage('PDF file size must be under 15MB');
      return;
    }
    onFileUpload(file);
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 sm:py-12">
      
      {/* Hero Header */}
      <div className="text-center space-y-4 mb-10">
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-teal-500/10 border border-teal-500/20 text-teal-300 text-xs font-medium">
          <Shield className="w-3.5 h-3.5" />
          <span>Evidence-Based Verification • Zero Speculation</span>
        </div>
        
        <h1 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-white">
          Show What Evidence <br className="hidden sm:inline" />
          <span className="bg-gradient-to-r from-teal-400 via-emerald-300 to-cyan-400 bg-clip-text text-transparent">
            Publicly Supports
          </span>{' '}
          a Resume
        </h1>

        <p className="text-slate-400 text-sm sm:text-base max-w-2xl mx-auto leading-relaxed">
          Extract claims, detect URLs, query the official GitHub REST API for manifests,
          codebases & languages, and corroborate resume statements against public proof.
        </p>
      </div>

      {/* Upload Dropzone */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => !isLoading && fileInputRef.current?.click()}
        className={`relative group cursor-pointer rounded-2xl border-2 border-dashed p-8 sm:p-12 text-center transition-all duration-300 ${
          isDragOver
            ? 'border-teal-400 bg-teal-950/30 scale-[1.01]'
            : 'border-slate-800 hover:border-teal-500/50 bg-slate-900/50 hover:bg-slate-900/80'
        } ${isLoading ? 'opacity-60 pointer-events-none' : ''}`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,application/pdf"
          onChange={handleFileChange}
          className="hidden"
          disabled={isLoading}
        />

        <div className="flex flex-col items-center justify-center space-y-4">
          <div className="w-16 h-16 rounded-2xl bg-teal-500/10 border border-teal-500/30 flex items-center justify-center text-teal-400 group-hover:scale-110 group-hover:bg-teal-500/20 transition-all duration-300">
            <UploadCloud className="w-8 h-8" />
          </div>

          <div className="space-y-1">
            <p className="text-base font-semibold text-slate-200">
              Drag & drop candidate resume PDF, or{' '}
              <span className="text-teal-400 underline decoration-teal-500/50 underline-offset-4">browse</span>
            </p>
            <p className="text-xs text-slate-400">
              PyMuPDF parses text, embedded hyperlinks, GitHub repos & portfolios • Max 15MB
            </p>
          </div>
        </div>

        {errorMessage && (
          <div className="mt-4 inline-flex items-center space-x-2 text-rose-400 bg-rose-950/40 border border-rose-800/60 px-3 py-1.5 rounded-lg text-xs">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{errorMessage}</span>
          </div>
        )}
      </div>

      {/* Verification Status Standard Badges */}
      <div className="mt-8 grid grid-cols-2 sm:grid-cols-5 gap-2.5">
        <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3 flex items-center space-x-2.5">
          <div className="w-2.5 h-2.5 rounded-full bg-emerald-400 shadow-sm shadow-emerald-500/50"></div>
          <div>
            <div className="text-xs font-semibold text-slate-200">Supported</div>
            <div className="text-[10px] text-slate-400">Corroborated in code/web</div>
          </div>
        </div>

        <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3 flex items-center space-x-2.5">
          <div className="w-2.5 h-2.5 rounded-full bg-amber-400 shadow-sm shadow-amber-500/50"></div>
          <div>
            <div className="text-xs font-semibold text-slate-200">Partially Supported</div>
            <div className="text-[10px] text-slate-400">Partial evidence found</div>
          </div>
        </div>

        <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3 flex items-center space-x-2.5">
          <div className="w-2.5 h-2.5 rounded-full bg-slate-400 shadow-sm"></div>
          <div>
            <div className="text-xs font-semibold text-slate-200">Unverified</div>
            <div className="text-[10px] text-slate-400">No public evidence found</div>
          </div>
        </div>

        <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3 flex items-center space-x-2.5">
          <div className="w-2.5 h-2.5 rounded-full bg-rose-400 shadow-sm shadow-rose-500/50"></div>
          <div>
            <div className="text-xs font-semibold text-slate-200">Broken Link</div>
            <div className="text-[10px] text-slate-400">404 / connection error</div>
          </div>
        </div>

        <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3 flex items-center space-x-2.5 col-span-2 sm:col-span-1">
          <div className="w-2.5 h-2.5 rounded-full bg-purple-400 shadow-sm shadow-purple-500/50"></div>
          <div>
            <div className="text-xs font-semibold text-slate-200">Restricted</div>
            <div className="text-[10px] text-slate-400">Private / sign-in gated</div>
          </div>
        </div>
      </div>

      {/* 1-Click Sample Resumes Section */}
      <div className="mt-10">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <Sparkles className="w-4 h-4 text-teal-400" />
            <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider">
              Or Test Instantly with Built-in Resumes
            </h3>
          </div>
          <span className="text-xs text-slate-400">Preloaded real scenarios</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {samples.map((sample) => (
            <div
              key={sample.id}
              onClick={() => !isLoading && onSelectSample(sample.id)}
              className="glass-card rounded-xl p-4 cursor-pointer group hover:scale-[1.01] hover:border-teal-500/40 transition-all duration-200"
            >
              <div className="flex items-start justify-between">
                <div className="space-y-1">
                  <div className="flex items-center space-x-2">
                    <h4 className="text-sm font-bold text-white group-hover:text-teal-300 transition">
                      {sample.name}
                    </h4>
                    <span className="text-[11px] px-2 py-0.5 rounded-full bg-slate-800 text-teal-400 font-medium">
                      {sample.title}
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 line-clamp-2">
                    {sample.description}
                  </p>
                </div>
                <div className="w-8 h-8 rounded-lg bg-slate-800 group-hover:bg-teal-500/20 group-hover:text-teal-400 flex items-center justify-center text-slate-400 transition shrink-0 ml-3">
                  <ArrowRight className="w-4 h-4" />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

    </div>
  );
};
