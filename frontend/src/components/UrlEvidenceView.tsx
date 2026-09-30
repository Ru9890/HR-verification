import React, { useState } from 'react';
import { 
  Globe, 
  Code2, 
  ExternalLink, 
  CheckCircle2, 
  XCircle, 
  Lock
} from 'lucide-react';
import { DiscoveredUrl, UrlPlatform } from '../types';
import { GitHubRepoCard } from './GitHubRepoCard';
import { GithubIcon, LinkedinIcon } from './Icons';

interface UrlEvidenceViewProps {
  urls: DiscoveredUrl[];
}

export const UrlEvidenceView: React.FC<UrlEvidenceViewProps> = ({ urls }) => {
  const [selectedPlatform, setSelectedPlatform] = useState<string>('ALL');

  const githubRepos = urls.filter((u) => u.platform === 'GitHub Repository');
  const otherUrls = urls.filter((u) => u.platform !== 'GitHub Repository');

  const platforms = ['ALL', ...Array.from(new Set(urls.map((u) => u.platform)))];

  const filteredUrls = urls.filter((u) => {
    if (selectedPlatform === 'ALL') return true;
    return u.platform === selectedPlatform;
  });

  const getPlatformIcon = (platform: UrlPlatform) => {
    switch (platform) {
      case 'GitHub Repository':
      case 'GitHub Profile':
        return <GithubIcon className="w-4 h-4 text-white" />;
      case 'LinkedIn':
        return <LinkedinIcon className="w-4 h-4 text-blue-400" />;
      case 'LeetCode':
      case 'Kaggle':
      case 'Hugging Face':
        return <Code2 className="w-4 h-4 text-amber-400" />;
      default:
        return <Globe className="w-4 h-4 text-teal-400" />;
    }
  };

  const getStatusBadge = (url: DiscoveredUrl) => {
    switch (url.status) {
      case 'Accessible':
        return (
          <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-emerald-950/60 border border-emerald-800/60 text-emerald-300 flex items-center gap-1">
            <CheckCircle2 className="w-3 h-3" />
            <span>Accessible</span>
          </span>
        );
      case 'Restricted':
        return (
          <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-purple-950/60 border border-purple-800/60 text-purple-300 flex items-center gap-1">
            <Lock className="w-3 h-3" />
            <span>Restricted / Sign-in</span>
          </span>
        );
      default:
        return (
          <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-rose-950/60 border border-rose-800/60 text-rose-300 flex items-center gap-1">
            <XCircle className="w-3 h-3" />
            <span>{url.status}</span>
          </span>
        );
    }
  };

  return (
    <div className="space-y-6">
      
      {/* Platform Filter Tabs */}
      <div className="glass-panel rounded-2xl p-4 flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap items-center gap-1.5">
          {platforms.map((p) => (
            <button
              key={p}
              onClick={() => setSelectedPlatform(p)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                selectedPlatform === p
                  ? 'bg-slate-800 text-white border border-slate-700'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
              }`}
            >
              {p} ({p === 'ALL' ? urls.length : urls.filter((u) => u.platform === p).length})
            </button>
          ))}
        </div>

        <span className="text-xs text-slate-400">
          Total {urls.length} URLs identified by PyMuPDF
        </span>
      </div>

      {/* GitHub Repositories Section */}
      {(selectedPlatform === 'ALL' || selectedPlatform === 'GitHub Repository') && githubRepos.length > 0 && (
        <div className="space-y-3">
          <h3 className="text-sm font-bold uppercase tracking-wider text-teal-400 flex items-center gap-2">
            <GithubIcon className="w-4 h-4" />
            GitHub Repositories Deep Inspection ({githubRepos.length})
          </h3>

          <div className="space-y-4">
            {githubRepos.map((repoUrl, idx) => (
              <GitHubRepoCard key={idx} urlItem={repoUrl} />
            ))}
          </div>
        </div>
      )}

      {/* Other URLs (LinkedIn, Portfolio, Web, LeetCode) */}
      {(selectedPlatform !== 'GitHub Repository') && otherUrls.length > 0 && (
        <div className="space-y-3 pt-2">
          <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
            <Globe className="w-4 h-4 text-teal-400" />
            Web, Portfolio & Profile Links ({otherUrls.length})
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {filteredUrls.filter((u) => u.platform !== 'GitHub Repository').map((item, idx) => (
              <div key={idx} className="glass-panel rounded-2xl p-5 border border-slate-800 space-y-3">
                
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-center space-x-2">
                    <div className="w-7 h-7 rounded-lg bg-slate-800 flex items-center justify-center shrink-0">
                      {getPlatformIcon(item.platform)}
                    </div>
                    <div>
                      <span className="text-[10px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded bg-slate-800 text-slate-400">
                        {item.platform}
                      </span>
                      <h4 className="text-sm font-bold text-white truncate max-w-[280px]">
                        {item.title || item.normalized_url}
                      </h4>
                    </div>
                  </div>

                  {getStatusBadge(item)}
                </div>

                {/* URL Link */}
                <div>
                  <a
                    href={item.normalized_url}
                    target="_blank"
                    rel="noreferrer"
                    className="text-xs font-mono text-teal-400 hover:underline flex items-center gap-1 truncate"
                  >
                    <span>{item.normalized_url}</span>
                    <ExternalLink className="w-3 h-3 shrink-0" />
                  </a>
                </div>

                {/* Web metadata if available */}
                {item.web_data && (
                  <div className="space-y-2 pt-2 border-t border-slate-800/80 text-xs">
                    {item.web_data.description && (
                      <p className="text-slate-400 text-xs line-clamp-2">
                        {item.web_data.description}
                      </p>
                    )}

                    {item.web_data.restriction_reason && (
                      <div className="p-2.5 rounded-lg bg-purple-950/40 border border-purple-800/50 text-[11px] text-purple-300">
                        🔒 <span className="font-semibold">Access Notice:</span> {item.web_data.restriction_reason}
                      </div>
                    )}

                    {item.web_data.discovered_techs && item.web_data.discovered_techs.length > 0 && (
                      <div className="space-y-1">
                        <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500">
                          Discovered Technologies:
                        </span>
                        <div className="flex flex-wrap gap-1">
                          {item.web_data.discovered_techs.map((tech, tidx) => (
                            <span
                              key={tidx}
                              className="px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-[11px] font-mono text-teal-300"
                            >
                              {tech}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {item.error_message && (
                  <div className="p-2 rounded bg-rose-950/40 border border-rose-800/50 text-xs text-rose-400">
                    {item.error_message}
                  </div>
                )}

              </div>
            ))}
          </div>
        </div>
      )}

    </div>
  );
};
