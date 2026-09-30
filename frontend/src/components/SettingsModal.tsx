import React, { useState, useEffect } from 'react';
import { X, Key, Sparkles, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';
import { getSettings, updateSettings, testGitHubConnection } from '../api/client';
import { AppSettings } from '../types';
import { GithubIcon } from './Icons';

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const SettingsModal: React.FC<SettingsModalProps> = ({ isOpen, onClose }) => {
  const [settings, setSettings] = useState<AppSettings | null>(null);
  const [githubToken, setGithubToken] = useState('');
  const [llmProvider, setLlmProvider] = useState('rule_based');
  const [openaiKey, setOpenaiKey] = useState('');
  const [geminiKey, setGeminiKey] = useState('');
  const [groqKey, setGroqKey] = useState('');
  const [ollamaUrl, setOllamaUrl] = useState('http://localhost:11434/v1');
  
  const [isSaving, setIsSaving] = useState(false);
  const [isTestingGitHub, setIsTestingGitHub] = useState(false);
  const [testResult, setTestResult] = useState<{ success: boolean; message: string; details?: any } | null>(null);
  const [saveSuccess, setSaveSuccess] = useState(false);

  useEffect(() => {
    if (isOpen) {
      loadSettings();
      setTestResult(null);
      setSaveSuccess(false);
    }
  }, [isOpen]);

  const loadSettings = async () => {
    try {
      const data = await getSettings();
      setSettings(data);
      setLlmProvider(data.llm_provider || 'rule_based');
      setOllamaUrl(data.ollama_base_url || 'http://localhost:11434/v1');
    } catch (e) {
      console.error(e);
    }
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    setSaveSuccess(false);
    try {
      await updateSettings({
        github_token: githubToken.trim() ? githubToken.trim() : undefined,
        llm_provider: llmProvider,
        openai_api_key: openaiKey.trim() ? openaiKey.trim() : undefined,
        gemini_api_key: geminiKey.trim() ? geminiKey.trim() : undefined,
        groq_api_key: groqKey.trim() ? groqKey.trim() : undefined,
        ollama_base_url: ollamaUrl.trim() ? ollamaUrl.trim() : undefined,
      });
      setSaveSuccess(true);
      await loadSettings();
      setGithubToken('');
    } catch (err: any) {
      alert(err.message || 'Failed to save settings');
    } finally {
      setIsSaving(false);
    }
  };

  const handleTestGitHub = async () => {
    setIsTestingGitHub(true);
    setTestResult(null);
    try {
      const res = await testGitHubConnection();
      setTestResult(res);
    } catch (e: any) {
      setTestResult({ success: false, message: e.message || 'Connection failed' });
    } finally {
      setIsTestingGitHub(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-in fade-in">
      <div className="glass-panel rounded-2xl w-full max-w-lg overflow-hidden shadow-2xl border border-slate-800">
        
        {/* Modal Header */}
        <div className="p-5 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 rounded-lg bg-teal-500/10 border border-teal-500/30 flex items-center justify-center text-teal-400">
              <Key className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white">System & API Configuration</h3>
              <p className="text-xs text-slate-400">GitHub REST API & Modular AI Settings</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-lg bg-slate-850 hover:bg-slate-800 flex items-center justify-center text-slate-400 hover:text-white transition"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Modal Body */}
        <form onSubmit={handleSave} className="p-6 space-y-5 max-h-[75vh] overflow-y-auto">
          
          {/* GitHub Token Section */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <label className="text-xs font-semibold text-slate-200 flex items-center gap-1.5">
                <GithubIcon className="w-3.5 h-3.5 text-slate-400" />
                GitHub Personal Access Token (PAT)
              </label>
              {settings?.has_github_token && (
                <span className="text-[10px] text-emerald-400 font-mono">
                  Active: {settings.github_token_masked}
                </span>
              )}
            </div>

            <input
              type="password"
              placeholder={settings?.has_github_token ? "Enter new token to update..." : "ghp_xxxxxxxxxxxxxxxxxxxx"}
              value={githubToken}
              onChange={(e) => setGithubToken(e.target.value)}
              className="w-full bg-slate-950/80 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 font-mono focus:outline-none focus:border-teal-500/60"
            />
            
            <p className="text-[11px] text-slate-400 leading-normal">
              Public repos work without a token (60 req/hr). Adding a GitHub Token raises your rate limit to <span className="text-teal-400 font-semibold">5,000 req/hr</span>. Token is stored securely in backend and never exposed.
            </p>

            <div className="pt-1 flex items-center gap-2">
              <button
                type="button"
                onClick={handleTestGitHub}
                disabled={isTestingGitHub}
                className="px-3 py-1.5 rounded-lg bg-slate-850 hover:bg-slate-800 border border-slate-700 text-xs font-medium text-slate-200 flex items-center gap-1.5 disabled:opacity-50"
              >
                {isTestingGitHub ? <Loader2 className="w-3 h-3 animate-spin text-teal-400" /> : <GithubIcon className="w-3 h-3 text-teal-400" />}
                <span>Test GitHub API Rate Limit</span>
              </button>
            </div>

            {testResult && (
              <div className={`p-3 rounded-lg text-xs border ${
                testResult.success 
                  ? 'bg-emerald-950/40 border-emerald-800/50 text-emerald-300' 
                  : 'bg-rose-950/40 border-rose-800/50 text-rose-300'
              }`}>
                <div className="font-semibold flex items-center gap-1.5">
                  {testResult.success ? <CheckCircle2 className="w-3.5 h-3.5" /> : <AlertCircle className="w-3.5 h-3.5" />}
                  {testResult.message}
                </div>
              </div>
            )}
          </div>

          {/* Modular AI Provider Selector */}
          <div className="space-y-2 pt-3 border-t border-slate-800">
            <label className="text-xs font-semibold text-slate-200 flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5 text-teal-400" />
              Claim Extraction AI Provider
            </label>

            <select
              value={llmProvider}
              onChange={(e) => setLlmProvider(e.target.value)}
              className="w-full bg-slate-950/80 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-teal-500/60"
            >
              <option value="rule_based">Smart Rule Engine + NLP Regex (Built-in, Zero Keys Required)</option>
              <option value="openai">OpenAI (GPT-4o mini)</option>
              <option value="gemini">Google Gemini (Gemini 1.5 Flash)</option>
              <option value="groq">Groq (Llama 3.1 70B Fast)</option>
              <option value="ollama">Ollama (Local LLM)</option>
            </select>

            {llmProvider === 'openai' && (
              <input
                type="password"
                placeholder="sk-..."
                value={openaiKey}
                onChange={(e) => setOpenaiKey(e.target.value)}
                className="w-full bg-slate-950/80 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 font-mono"
              />
            )}

            {llmProvider === 'gemini' && (
              <input
                type="password"
                placeholder="Gemini API Key..."
                value={geminiKey}
                onChange={(e) => setGeminiKey(e.target.value)}
                className="w-full bg-slate-950/80 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 font-mono"
              />
            )}

            {llmProvider === 'groq' && (
              <input
                type="password"
                placeholder="gsk_..."
                value={groqKey}
                onChange={(e) => setGroqKey(e.target.value)}
                className="w-full bg-slate-950/80 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 font-mono"
              />
            )}

            {llmProvider === 'ollama' && (
              <input
                type="text"
                placeholder="http://localhost:11434/v1"
                value={ollamaUrl}
                onChange={(e) => setOllamaUrl(e.target.value)}
                className="w-full bg-slate-950/80 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 font-mono"
              />
            )}
          </div>

          {/* Save Status & Action */}
          <div className="pt-3 border-t border-slate-800 flex items-center justify-between">
            {saveSuccess && (
              <span className="text-xs text-emerald-400 flex items-center gap-1 font-medium">
                <CheckCircle2 className="w-3.5 h-3.5" />
                Settings saved!
              </span>
            )}
            {!saveSuccess && <span></span>}

            <div className="flex items-center space-x-2">
              <button
                type="button"
                onClick={onClose}
                className="px-3 py-1.5 rounded-xl bg-slate-850 hover:bg-slate-800 text-xs font-semibold text-slate-300 transition"
              >
                Close
              </button>
              <button
                type="submit"
                disabled={isSaving}
                className="px-4 py-1.5 rounded-xl bg-teal-500 hover:bg-teal-400 text-slate-950 text-xs font-bold transition flex items-center gap-1.5 shadow-lg shadow-teal-500/20 disabled:opacity-50"
              >
                {isSaving && <Loader2 className="w-3 h-3 animate-spin" />}
                <span>Save Settings</span>
              </button>
            </div>
          </div>

        </form>

      </div>
    </div>
  );
};
