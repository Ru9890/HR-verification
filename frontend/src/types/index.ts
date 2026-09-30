export type ClaimStatus = 
  | 'Supported'
  | 'Partially Supported'
  | 'Unverified'
  | 'Broken Link'
  | 'Restricted';

export type UrlPlatform = 
  | 'GitHub Repository'
  | 'GitHub Profile'
  | 'LinkedIn'
  | 'Portfolio Website'
  | 'LeetCode'
  | 'Kaggle'
  | 'Hugging Face'
  | 'arXiv'
  | 'Tech Blog'
  | 'Other Web URL';

export type UrlStatus = 
  | 'Accessible'
  | 'Broken'
  | 'Restricted'
  | 'Invalid'
  | 'Timeout';

export interface EvidenceSnippet {
  source_type: string;
  source_url: string;
  snippet: string;
  matched_term: string;
  confidence: number;
  location_detail?: string;
}

export interface GitHubDependency {
  file: string;
  package_name: string;
  version_spec?: string;
}

export interface GitHubRepoData {
  owner: string;
  name: string;
  full_name: string;
  description?: string;
  stars: number;
  forks: number;
  default_branch: string;
  created_at?: string;
  updated_at?: string;
  pushed_at?: string;
  is_fork: boolean;
  languages: Record<string, number>;
  language_percentages: Record<string, number>;
  readme_content?: string;
  readme_excerpt?: string;
  dependencies: GitHubDependency[];
  file_tree_summary: string[];
  recent_commits: Array<{
    sha: string;
    message: string;
    author: string;
    date: string;
  }>;
  total_commits?: number;
  contributors: Array<{
    login: string;
    contributions: number;
    avatar_url: string;
  }>;
  status: string;
}

export interface WebPageData {
  title?: string;
  description?: string;
  h1_headings: string[];
  h2_headings: string[];
  discovered_projects: string[];
  discovered_techs: string[];
  outbound_links: string[];
  raw_text_snippet?: string;
  status_code?: number;
  is_restricted: boolean;
  restriction_reason?: string;
}

export interface DiscoveredUrl {
  raw_url: string;
  normalized_url: string;
  platform: UrlPlatform;
  status: UrlStatus;
  status_code?: number;
  title?: string;
  github_data?: GitHubRepoData;
  web_data?: WebPageData;
  error_message?: string;
}

export interface ClaimItemBreakdown {
  item_name: string;
  status: ClaimStatus;
  evidence_source?: string;
  evidence_snippet?: string;
}

export interface ClaimVerification {
  id: string;
  category: string;
  section: string;
  claim_text: string;
  claimed_items: string[];
  status: ClaimStatus;
  confidence: number;
  associated_url?: string;
  items_breakdown: ClaimItemBreakdown[];
  evidence_snippets: EvidenceSnippet[];
  explanation: string;
}

export interface VerificationSummary {
  evidence_coverage_percentage: number;
  total_claims: number;
  supported_claims: number;
  partially_supported_claims: number;
  unverified_claims: number;
  broken_claims: number;
  restricted_claims: number;
  
  total_urls: number;
  accessible_urls: number;
  broken_urls: number;
  restricted_urls: number;
}

export interface CandidateInfo {
  name?: string;
  email?: string;
  phone?: string;
  title?: string;
  raw_summary?: string;
}

export interface VerificationReportResponse {
  id: string;
  filename: string;
  created_at: string;
  candidate: CandidateInfo;
  summary: VerificationSummary;
  claims: ClaimVerification[];
  urls: DiscoveredUrl[];
  risk_notes: string[];
  strengths: string[];
  extracted_text_preview?: string;
}

export interface SampleResumeInfo {
  id: string;
  name: string;
  title: string;
  description: string;
  email: string;
}

export interface AppSettings {
  app_name: string;
  app_version: string;
  has_github_token: boolean;
  github_token_masked?: string;
  llm_provider: string;
  openai_configured: boolean;
  gemini_configured: boolean;
  groq_configured: boolean;
  ollama_base_url: string;
  http_timeout: number;
  openai_api_key?: string;
  gemini_api_key?: string;
  groq_api_key?: string;
}
