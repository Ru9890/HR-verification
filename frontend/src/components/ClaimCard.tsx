import React, { useState } from 'react';
import { 
  CheckCircle2, 
  AlertTriangle, 
  HelpCircle, 
  XCircle, 
  Lock, 
  ChevronDown, 
  ChevronUp, 
  ExternalLink, 
  Search,
  Code,
  FileCode,
  Layers,
  Sparkles,
  Info
} from 'lucide-react';
import { ClaimVerification, ClaimStatus } from '../types';

interface ClaimCardProps {
  claim: ClaimVerification;
  index: number;
}

export const ClaimCard: React.FC<ClaimCardProps> = ({ claim, index }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const getStatusBadge = (status: ClaimStatus) => {
    switch (status) {
      case 'Supported':
        return {
          icon: <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />,
          label: 'Supported',
          bg: 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30',
          indicator: 'bg-emerald-400',
        };
      case 'Partially Supported':
        return {
          icon: <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />,
          label: 'Partially Supported',
          bg: 'bg-amber-500/10 text-amber-300 border-amber-500/30',
          indicator: 'bg-amber-400',
        };
      case 'Broken Link':
        return {
          icon: <XCircle className="w-3.5 h-3.5 text-rose-400" />,
          label: 'Broken Link',
          bg: 'bg-rose-500/10 text-rose-300 border-rose-500/30',
          indicator: 'bg-rose-400',
        };
      case 'Restricted':
        return {
          icon: <Lock className="w-3.5 h-3.5 text-purple-400" />,
          label: 'Restricted',
          bg: 'bg-purple-500/10 text-purple-300 border-purple-500/30',
          indicator: 'bg-purple-400',
        };
      default:
        return {
          icon: <HelpCircle className="w-3.5 h-3.5 text-slate-400" />,
          label: 'Unverified',
          bg: 'bg-slate-800 text-slate-300 border-slate-700',
          indicator: 'bg-slate-400',
        };
    }
  };

  const badge = getStatusBadge(claim.status);

  return (
    <div className={`glass-card rounded-xl border transition-all duration-200 overflow-hidden ${
      isExpanded ? 'border-slate-700 shadow-lg' : 'hover:border-slate-700/80'
    }`}>
      
      {/* Main Claim Header Row */}
      <div 
        onClick={() => setIsExpanded(!isExpanded)}
        className="p-4 cursor-pointer flex flex-col sm:flex-row sm:items-center justify-between gap-3 select-none"
      >
        <div className="flex items-start space-x-3 min-w-0">
          
          <div className="mt-0.5 shrink-0">
            <span className={`inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-md text-xs font-semibold border ${badge.bg}`}>
              {badge.icon}
              <span>{badge.label}</span>
            </span>
          </div>

          <div className="space-y-1 min-w-0">
            <div className="flex items-center space-x-2">
              <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-slate-800 text-slate-400">
                {claim.section}
              </span>
              {claim.associated_url && (
                <a
                  href={claim.associated_url}
                  target="_blank"
                  rel="noreferrer"
                  onClick={(e) => e.stopPropagation()}
                  className="inline-flex items-center space-x-1 text-[11px] text-teal-400 hover:text-teal-300 font-mono underline decoration-teal-500/40 truncate max-w-[260px]"
                >
                  <span>{claim.associated_url.replace('https://', '')}</span>
                  <ExternalLink className="w-2.5 h-2.5 shrink-0" />
                </a>
              )}
            </div>

            <p className="text-sm font-medium text-slate-100 leading-snug">
              {claim.claim_text}
            </p>
          </div>

        </div>

        {/* Right Action / Chevron */}
        <div className="flex items-center justify-between sm:justify-end space-x-3 shrink-0 pt-2 sm:pt-0 border-t sm:border-t-0 border-slate-800/60">
          
          {/* Item pills preview */}
          {claim.items_breakdown.length > 0 && (
            <div className="flex flex-wrap gap-1">
              {claim.items_breakdown.slice(0, 3).map((item, idx) => (
                <span
                  key={idx}
                  className={`text-[10px] px-1.5 py-0.5 rounded font-mono ${
                    item.status === 'Supported'
                      ? 'bg-emerald-950/60 text-emerald-300 border border-emerald-800/50'
                      : item.status === 'Partially Supported'
                      ? 'bg-amber-950/60 text-amber-300 border border-amber-800/50'
                      : 'bg-slate-800/80 text-slate-400'
                  }`}
                >
                  {item.item_name}
                </span>
              ))}
              {claim.items_breakdown.length > 3 && (
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400">
                  +{claim.items_breakdown.length - 3}
                </span>
              )}
            </div>
          )}

          <div className="w-7 h-7 rounded-lg bg-slate-800/80 flex items-center justify-center text-slate-400 hover:text-white transition">
            {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </div>
        </div>

      </div>

      {/* Expandable Evidence Drawer */}
      {isExpanded && (
        <div className="p-4 bg-slate-900/90 border-t border-slate-800/80 space-y-4 animate-in fade-in duration-200">
          
          {/* Explanation note */}
          <div className="flex items-start space-x-2.5 p-3 rounded-lg bg-slate-850/90 border border-slate-800 text-xs text-slate-300">
            <Info className="w-4 h-4 text-teal-400 shrink-0 mt-0.5" />
            <div>
              <span className="font-semibold text-white">Verification Finding: </span>
              {claim.explanation}
            </div>
          </div>

          {/* Item-by-Item Breakdown Table */}
          {claim.items_breakdown.length > 0 && (
            <div className="space-y-2">
              <h5 className="text-[11px] font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                <Layers className="w-3.5 h-3.5 text-teal-400" />
                Claimed Technology & Entity Breakdown
              </h5>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {claim.items_breakdown.map((item, idx) => {
                  const itemBadge = getStatusBadge(item.status);
                  return (
                    <div
                      key={idx}
                      className="p-2.5 rounded-lg bg-slate-850/60 border border-slate-800 flex items-center justify-between gap-2"
                    >
                      <span className="text-xs font-mono font-medium text-slate-200 truncate">
                        {item.item_name}
                      </span>
                      <span className={`inline-flex items-center space-x-1 px-2 py-0.5 rounded text-[11px] font-medium border ${itemBadge.bg}`}>
                        {itemBadge.icon}
                        <span>{itemBadge.label}</span>
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Specific Supporting Evidence Snippets */}
          {claim.evidence_snippets.length > 0 ? (
            <div className="space-y-2 pt-1">
              <h5 className="text-[11px] font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                <FileCode className="w-3.5 h-3.5 text-emerald-400" />
                Public Evidence Corroboration & Snippets
              </h5>

              <div className="space-y-2">
                {claim.evidence_snippets.map((ev, idx) => (
                  <div
                    key={idx}
                    className="p-3 rounded-lg bg-slate-950/80 border border-slate-800 font-mono text-xs space-y-1.5"
                  >
                    <div className="flex flex-wrap items-center justify-between text-[11px] gap-2">
                      <span className="text-emerald-400 font-semibold flex items-center gap-1">
                        <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                        {ev.source_type}
                      </span>
                      {ev.location_detail && (
                        <span className="text-slate-400 text-[10px]">
                          {ev.location_detail}
                        </span>
                      )}
                    </div>

                    <div className="text-slate-300 bg-slate-900 p-2 rounded border border-slate-800/80 text-[11px] whitespace-pre-wrap">
                      {ev.snippet}
                    </div>

                    <div className="flex items-center justify-between text-[10px] text-slate-400 pt-1">
                      <span>Source: <a href={ev.source_url} target="_blank" rel="noreferrer" className="text-teal-400 hover:underline">{ev.source_url}</a></span>
                      <span className="text-teal-300 font-semibold">Confidence: {Math.round(ev.confidence * 100)}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="text-xs text-slate-400 italic bg-slate-850/40 p-3 rounded-lg border border-slate-800">
              No public repository code, README, or web evidence corroborated this claim. Evidence may exist in private employer systems or internal repositories.
            </div>
          )}

        </div>
      )}

    </div>
  );
};
