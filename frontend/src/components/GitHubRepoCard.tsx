import React, { useState } from 'react';
import { 
  Star, 
  GitFork, 
  Package, 
  GitCommit, 
  Users, 
  FolderTree, 
  ExternalLink,
  ChevronDown,
  ChevronUp,
  FileText,
  CheckCircle2
} from 'lucide-react';
import { DiscoveredUrl, GitHubRepoData } from '../types';
import { GithubIcon } from './Icons';

interface GitHubRepoCardProps {
  urlItem: DiscoveredUrl;
}

export const GitHubRepoCard: React.FC<GitHubRepoCardProps> = ({ urlItem }) => {
  const [isReadmeOpen, setIsReadmeOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<'manifests' | 'commits' | 'tree' | 'contributors'>('manifests');

  const gdata: GitHubRepoData | undefined = urlItem.github_data;

  if (!gdata) {
    return (
      <div className="glass-panel rounded-2xl p-5 border border-slate-800 space-y-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2 text-slate-300 font-mono text-sm">
            <GithubIcon className="w-4 h-4 text-slate-400" />
            <span>{urlItem.normalized_url}</span>
          </div>
          <span className="px-2 py-0.5 rounded text-xs font-semibold bg-rose-950/60 border border-rose-800/60 text-rose-300">
            {urlItem.status}
          </span>
        </div>
        <p className="text-xs text-rose-400">
          {urlItem.error_message || 'Could not fetch repository information.'}
        </p>
      </div>
    );
  }

  // Language colors palette
  const getLangColor = (lang: string) => {
    const map: Record<string, string> = {
      Python: '#3572A5',
      TypeScript: '#3178c6',
      JavaScript: '#f1e05a',
      HTML: '#e34c26',
      CSS: '#563d7c',
      Go: '#00ADD8',
      Rust: '#dea584',
      Java: '#b07219',
      'C++': '#f34b7d',
      Shell: '#89e051',
      Docker: '#384d54'
    };
    return map[lang] || '#14b8a6';
  };

  return (
    <div className="glass-panel rounded-2xl p-6 border border-slate-800 space-y-5">
      
      {/* Repo Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        
        <div className="space-y-1">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 rounded-lg bg-slate-800 flex items-center justify-center text-white shrink-0">
              <GithubIcon className="w-5 h-5" />
            </div>
            <div>
              <a
                href={urlItem.normalized_url}
                target="_blank"
                rel="noreferrer"
                className="text-base font-bold text-white hover:text-teal-300 transition flex items-center gap-1.5 font-mono"
              >
                <span>{gdata.full_name}</span>
                <ExternalLink className="w-3.5 h-3.5 text-slate-400" />
              </a>
              <p className="text-xs text-slate-400 line-clamp-1">
                {gdata.description || 'Public GitHub Repository'}
              </p>
            </div>
          </div>
        </div>

        {/* Badges / Stats */}
        <div className="flex flex-wrap items-center gap-2">
          <div className="flex items-center space-x-1 px-2.5 py-1 rounded-lg bg-slate-850 border border-slate-800 text-xs font-semibold text-amber-300">
            <Star className="w-3.5 h-3.5 text-amber-400 fill-amber-400" />
            <span>{gdata.stars.toLocaleString()}</span>
          </div>

          <div className="flex items-center space-x-1 px-2.5 py-1 rounded-lg bg-slate-850 border border-slate-800 text-xs font-semibold text-slate-300">
            <GitFork className="w-3.5 h-3.5 text-slate-400" />
            <span>{gdata.forks.toLocaleString()}</span>
          </div>

          <span className="px-2.5 py-1 rounded-lg text-xs font-bold bg-emerald-950/60 border border-emerald-800/60 text-emerald-300 flex items-center gap-1">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>Accessible</span>
          </span>
        </div>

      </div>

      {/* Language Breakdown Bar */}
      {Object.keys(gdata.language_percentages).length > 0 && (
        <div className="space-y-2">
          <div className="flex items-center justify-between text-xs text-slate-400 font-medium">
            <span>Languages</span>
            <span className="text-[11px] text-slate-500">From GitHub REST API</span>
          </div>

          {/* Progress Stack Bar */}
          <div className="h-2 w-full rounded-full bg-slate-800 overflow-hidden flex">
            {Object.entries(gdata.language_percentages).map(([lang, pct]) => (
              <div
                key={lang}
                style={{ width: `${pct}%`, backgroundColor: getLangColor(lang) }}
                title={`${lang}: ${pct}%`}
                className="h-full transition-all duration-300"
              />
            ))}
          </div>

          {/* Legend Items */}
          <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs">
            {Object.entries(gdata.language_percentages).map(([lang, pct]) => (
              <div key={lang} className="flex items-center space-x-1.5 font-mono text-[11px]">
                <span
                  className="w-2.5 h-2.5 rounded-full"
                  style={{ backgroundColor: getLangColor(lang) }}
                />
                <span className="text-slate-200 font-semibold">{lang}</span>
                <span className="text-slate-400">{pct}%</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Sub-Tabs: Manifests, Commits, File Tree, Contributors */}
      <div className="pt-2 border-t border-slate-800/80 space-y-3">
        
        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={() => setActiveTab('manifests')}
            className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
              activeTab === 'manifests'
                ? 'bg-teal-500/20 text-teal-300 border border-teal-500/40'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-850'
            }`}
          >
            <Package className="w-3.5 h-3.5" />
            <span>Dependencies ({gdata.dependencies.length})</span>
          </button>

          <button
            onClick={() => setActiveTab('commits')}
            className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
              activeTab === 'commits'
                ? 'bg-teal-500/20 text-teal-300 border border-teal-500/40'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-850'
            }`}
          >
            <GitCommit className="w-3.5 h-3.5" />
            <span>Commits ({gdata.total_commits ?? gdata.recent_commits.length})</span>
          </button>

          <button
            onClick={() => setActiveTab('tree')}
            className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
              activeTab === 'tree'
                ? 'bg-teal-500/20 text-teal-300 border border-teal-500/40'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-850'
            }`}
          >
            <FolderTree className="w-3.5 h-3.5" />
            <span>Files ({gdata.file_tree_summary.length})</span>
          </button>

          <button
            onClick={() => setActiveTab('contributors')}
            className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
              activeTab === 'contributors'
                ? 'bg-teal-500/20 text-teal-300 border border-teal-500/40'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-850'
            }`}
          >
            <Users className="w-3.5 h-3.5" />
            <span>Contributors ({gdata.contributors.length})</span>
          </button>
        </div>

        {/* Tab Content 1: Manifest Dependencies */}
        {activeTab === 'manifests' && (
          <div className="space-y-2">
            {gdata.dependencies.length > 0 ? (
              <div className="flex flex-wrap gap-1.5">
                {gdata.dependencies.map((dep, idx) => (
                  <span
                    key={idx}
                    className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-md bg-slate-900 border border-slate-800 text-xs font-mono text-slate-200"
                  >
                    <span className="text-teal-400 font-semibold">{dep.package_name}</span>
                    {dep.version_spec && (
                      <span className="text-slate-400 text-[10px]">{dep.version_spec}</span>
                    )}
                    <span className="text-[10px] text-slate-400 px-1 py-0.2 bg-slate-800 rounded">
                      {dep.file}
                    </span>
                  </span>
                ))}
              </div>
            ) : (
              <p className="text-xs text-slate-400 italic">No package manifests found (requirements.txt, package.json, etc.).</p>
            )}
          </div>
        )}

        {activeTab === 'commits' && (
          <div className="space-y-2">
            {gdata.total_commits != null && gdata.total_commits > gdata.recent_commits.length && (
              <p className="text-[10px] text-slate-400 italic px-1">
                Showing {gdata.recent_commits.length} most recent of{' '}
                <span className="text-teal-400 font-semibold">{gdata.total_commits}</span> total commits
              </p>
            )}
            <div className="max-h-48 overflow-y-auto pr-1 space-y-2">
            {gdata.recent_commits.length > 0 ? (
              gdata.recent_commits.map((c, idx) => (
                <div key={idx} className="p-2 rounded bg-slate-950/70 border border-slate-850 flex items-start justify-between gap-2 text-xs">
                  <div className="space-y-0.5 min-w-0">
                    <p className="font-mono text-slate-200 truncate">{c.message}</p>
                    <p className="text-[10px] text-slate-400">By <span className="text-slate-300 font-medium">{c.author}</span> • {c.date ? new Date(c.date).toLocaleDateString() : ''}</p>
                  </div>
                  <span className="font-mono text-[10px] text-teal-400 bg-slate-900 px-1.5 py-0.5 rounded border border-slate-800 shrink-0">
                    {c.sha}
                  </span>
                </div>
              ))
            ) : (
              <p className="text-xs text-slate-400 italic">No recent commit logs available.</p>
            )}
            </div>
          </div>
        )}

        {/* Tab Content 3: File Tree */}
        {activeTab === 'tree' && (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-1 max-h-48 overflow-y-auto pr-1">
            {gdata.file_tree_summary.map((fpath, idx) => (
              <div key={idx} className="font-mono text-xs text-slate-300 bg-slate-950/60 p-1.5 rounded border border-slate-850 truncate">
                📄 {fpath}
              </div>
            ))}
          </div>
        )}

        {/* Tab Content 4: Contributors */}
        {activeTab === 'contributors' && (
          <div className="flex flex-wrap gap-2">
            {gdata.contributors.map((ct, idx) => (
              <div key={idx} className="flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs">
                {ct.avatar_url ? (
                  <img src={ct.avatar_url} alt={ct.login} className="w-5 h-5 rounded-full" />
                ) : (
                  <div className="w-5 h-5 rounded-full bg-slate-800" />
                )}
                <span className="font-medium text-slate-200">{ct.login}</span>
                <span className="text-[10px] text-teal-400">({ct.contributions} commits)</span>
              </div>
            ))}
          </div>
        )}

      </div>

      {/* README Excerpt Accordion */}
      {gdata.readme_excerpt && (
        <div className="pt-2 border-t border-slate-800/80">
          <button
            onClick={() => setIsReadmeOpen(!isReadmeOpen)}
            className="flex items-center justify-between w-full text-xs font-semibold text-slate-300 hover:text-white"
          >
            <span className="flex items-center gap-1.5">
              <FileText className="w-3.5 h-3.5 text-teal-400" />
              README.md Preview
            </span>
            {isReadmeOpen ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </button>

          {isReadmeOpen && (
            <div className="mt-2 p-3 rounded-xl bg-slate-950 border border-slate-800 font-mono text-[11px] text-slate-300 whitespace-pre-wrap max-h-60 overflow-y-auto">
              {gdata.readme_excerpt}
            </div>
          )}
        </div>
      )}

    </div>
  );
};
