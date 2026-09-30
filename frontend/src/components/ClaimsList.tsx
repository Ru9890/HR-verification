import React, { useState, useMemo } from 'react';
import { Search, Filter, CheckCircle2, AlertTriangle, HelpCircle, XCircle, Lock, Layers } from 'lucide-react';
import { ClaimVerification, ClaimStatus } from '../types';
import { ClaimCard } from './ClaimCard';

interface ClaimsListProps {
  claims: ClaimVerification[];
}

export const ClaimsList: React.FC<ClaimsListProps> = ({ claims }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedStatus, setSelectedStatus] = useState<string>('ALL');
  const [selectedSection, setSelectedSection] = useState<string>('ALL');

  // Distinct sections
  const sections = useMemo(() => {
    const set = new Set(claims.map((c) => c.section));
    return ['ALL', ...Array.from(set)];
  }, [claims]);

  // Status counts
  const statusCounts = useMemo(() => {
    return {
      ALL: claims.length,
      Supported: claims.filter((c) => c.status === 'Supported').length,
      'Partially Supported': claims.filter((c) => c.status === 'Partially Supported').length,
      Unverified: claims.filter((c) => c.status === 'Unverified').length,
      'Broken Link': claims.filter((c) => c.status === 'Broken Link').length,
      Restricted: claims.filter((c) => c.status === 'Restricted').length,
    };
  }, [claims]);

  // Filtered claims
  const filteredClaims = useMemo(() => {
    return claims.filter((c) => {
      // Status filter
      if (selectedStatus !== 'ALL' && c.status !== selectedStatus) {
        return false;
      }
      // Section filter
      if (selectedSection !== 'ALL' && c.section !== selectedSection) {
        return false;
      }
      // Search query
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const matchesText = c.claim_text.toLowerCase().includes(q);
        const matchesSection = c.section.toLowerCase().includes(q);
        const matchesItems = c.claimed_items.some((i) => i.toLowerCase().includes(q));
        const matchesUrl = c.associated_url ? c.associated_url.toLowerCase().includes(q) : false;
        return matchesText || matchesSection || matchesItems || matchesUrl;
      }
      return true;
    });
  }, [claims, selectedStatus, selectedSection, searchQuery]);

  return (
    <div className="space-y-4">
      
      {/* Search and Filters Bar */}
      <div className="glass-panel rounded-2xl p-4 space-y-3">
        
        <div className="flex flex-col sm:flex-row items-center gap-3">
          
          {/* Search Box */}
          <div className="relative flex-1 w-full">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search claims, technologies (e.g. FastAPI, Python, Docker)..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-slate-950/80 border border-slate-800 rounded-xl pl-9 pr-4 py-2 text-xs text-slate-200 placeholder:text-slate-500 focus:outline-none focus:border-teal-500/60 focus:ring-1 focus:ring-teal-500/40"
            />
          </div>

          {/* Section Filter Dropdown */}
          <div className="flex items-center space-x-2 w-full sm:w-auto">
            <Filter className="w-3.5 h-3.5 text-slate-400 shrink-0" />
            <select
              value={selectedSection}
              onChange={(e) => setSelectedSection(e.target.value)}
              className="bg-slate-950/80 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-teal-500/60"
            >
              {sections.map((sec) => (
                <option key={sec} value={sec}>
                  {sec === 'ALL' ? 'All Sections' : sec}
                </option>
              ))}
            </select>
          </div>

        </div>

        {/* Status Filter Tabs */}
        <div className="flex flex-wrap items-center gap-1.5 pt-1 border-t border-slate-800/80">
          
          <button
            onClick={() => setSelectedStatus('ALL')}
            className={`px-3 py-1 text-xs font-semibold rounded-lg transition ${
              selectedStatus === 'ALL'
                ? 'bg-slate-800 text-white border border-slate-700'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
            }`}
          >
            All ({statusCounts.ALL})
          </button>

          <button
            onClick={() => setSelectedStatus('Supported')}
            className={`flex items-center space-x-1.5 px-3 py-1 text-xs font-semibold rounded-lg transition ${
              selectedStatus === 'Supported'
                ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
                : 'text-slate-400 hover:text-emerald-300 hover:bg-emerald-950/30'
            }`}
          >
            <CheckCircle2 className="w-3 h-3 text-emerald-400" />
            <span>Supported ({statusCounts.Supported})</span>
          </button>

          <button
            onClick={() => setSelectedStatus('Partially Supported')}
            className={`flex items-center space-x-1.5 px-3 py-1 text-xs font-semibold rounded-lg transition ${
              selectedStatus === 'Partially Supported'
                ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
                : 'text-slate-400 hover:text-amber-300 hover:bg-amber-950/30'
            }`}
          >
            <AlertTriangle className="w-3 h-3 text-amber-400" />
            <span>Partial ({statusCounts['Partially Supported']})</span>
          </button>

          <button
            onClick={() => setSelectedStatus('Unverified')}
            className={`flex items-center space-x-1.5 px-3 py-1 text-xs font-semibold rounded-lg transition ${
              selectedStatus === 'Unverified'
                ? 'bg-slate-700/60 text-slate-200 border border-slate-600'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
            }`}
          >
            <HelpCircle className="w-3 h-3 text-slate-400" />
            <span>Unverified ({statusCounts.Unverified})</span>
          </button>

          {statusCounts['Broken Link'] > 0 && (
            <button
              onClick={() => setSelectedStatus('Broken Link')}
              className={`flex items-center space-x-1.5 px-3 py-1 text-xs font-semibold rounded-lg transition ${
                selectedStatus === 'Broken Link'
                  ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40'
                  : 'text-slate-400 hover:text-rose-300 hover:bg-rose-950/30'
              }`}
            >
              <XCircle className="w-3 h-3 text-rose-400" />
              <span>Broken ({statusCounts['Broken Link']})</span>
            </button>
          )}

          {statusCounts.Restricted > 0 && (
            <button
              onClick={() => setSelectedStatus('Restricted')}
              className={`flex items-center space-x-1.5 px-3 py-1 text-xs font-semibold rounded-lg transition ${
                selectedStatus === 'Restricted'
                  ? 'bg-purple-500/20 text-purple-300 border border-purple-500/40'
                  : 'text-slate-400 hover:text-purple-300 hover:bg-purple-950/30'
              }`}
            >
              <Lock className="w-3 h-3 text-purple-400" />
              <span>Restricted ({statusCounts.Restricted})</span>
            </button>
          )}

        </div>

      </div>

      {/* Claims List Header */}
      <div className="flex items-center justify-between text-xs text-slate-400 px-1">
        <span>Showing {filteredClaims.length} of {claims.length} claims</span>
        <span>Click any card to expand supporting evidence</span>
      </div>

      {/* Claims Card Render */}
      <div className="space-y-3">
        {filteredClaims.length > 0 ? (
          filteredClaims.map((claim, idx) => (
            <ClaimCard key={claim.id || idx} claim={claim} index={idx} />
          ))
        ) : (
          <div className="glass-panel rounded-2xl p-8 text-center space-y-2">
            <HelpCircle className="w-8 h-8 text-slate-500 mx-auto" />
            <p className="text-sm font-semibold text-slate-300">No claims match the selected filters</p>
            <p className="text-xs text-slate-500">Try resetting the status filter or clearing your search query.</p>
          </div>
        )}
      </div>

    </div>
  );
};
