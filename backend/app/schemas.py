from pydantic import BaseModel, Field, HttpUrl
from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime

class ClaimStatus(str, Enum):
    SUPPORTED = "Supported"
    PARTIALLY_SUPPORTED = "Partially Supported"
    UNVERIFIED = "Unverified"
    BROKEN_LINK = "Broken Link"
    RESTRICTED = "Restricted"

class UrlPlatform(str, Enum):
    GITHUB_REPO = "GitHub Repository"
    GITHUB_USER = "GitHub Profile"
    LINKEDIN = "LinkedIn"
    PORTFOLIO = "Portfolio Website"
    LEETCODE = "LeetCode"
    KAGGLE = "Kaggle"
    HUGGINGFACE = "Hugging Face"
    ARXIV = "arXiv"
    DEV_BLOG = "Tech Blog"
    OTHER = "Other Web URL"

class UrlStatus(str, Enum):
    ACCESSIBLE = "Accessible"
    BROKEN = "Broken"
    RESTRICTED = "Restricted"
    INVALID = "Invalid"
    TIMEOUT = "Timeout"

class EvidenceSnippet(BaseModel):
    source_type: str # e.g. "GitHub Manifest (requirements.txt)", "GitHub README", "GitHub Languages", "Web Content"
    source_url: str
    snippet: str
    matched_term: str
    confidence: float = 1.0 # 0.0 to 1.0
    location_detail: Optional[str] = None # e.g. "Line 14 in requirements.txt", "README.md header"

class GitHubDependency(BaseModel):
    file: str # e.g. "requirements.txt", "package.json", "go.mod"
    package_name: str
    version_spec: Optional[str] = None

class GitHubRepoData(BaseModel):
    owner: str
    name: str
    full_name: str
    description: Optional[str] = None
    stars: int = 0
    forks: int = 0
    default_branch: str = "main"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    pushed_at: Optional[str] = None
    is_fork: bool = False
    languages: Dict[str, int] = {} # language name -> bytes
    language_percentages: Dict[str, float] = {} # language name -> percentage
    readme_content: Optional[str] = None
    readme_excerpt: Optional[str] = None
    dependencies: List[GitHubDependency] = []
    file_tree_summary: List[str] = []
    recent_commits: List[Dict[str, Any]] = []
    total_commits: Optional[int] = None  # True total from Link header pagination
    contributors: List[Dict[str, Any]] = []
    status: str = "Active"

class WebPageData(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    h1_headings: List[str] = []
    h2_headings: List[str] = []
    discovered_projects: List[str] = []
    discovered_techs: List[str] = []
    outbound_links: List[str] = []
    raw_text_snippet: Optional[str] = None
    status_code: Optional[int] = None
    is_restricted: bool = False
    restriction_reason: Optional[str] = None

class DiscoveredUrl(BaseModel):
    raw_url: str
    normalized_url: str
    platform: UrlPlatform
    status: UrlStatus
    status_code: Optional[int] = None
    title: Optional[str] = None
    github_data: Optional[GitHubRepoData] = None
    web_data: Optional[WebPageData] = None
    error_message: Optional[str] = None

class ClaimItemBreakdown(BaseModel):
    item_name: str # e.g. "FastAPI"
    status: ClaimStatus # Supported, Partially Supported, Unverified
    evidence_source: Optional[str] = None
    evidence_snippet: Optional[str] = None

class ClaimVerification(BaseModel):
    id: str
    category: str # "project_tech", "skill", "experience", "metric", "certification", "repository_link"
    section: str # "Projects", "Skills", "Experience", "Certifications", "Header"
    claim_text: str
    claimed_items: List[str] = []
    status: ClaimStatus
    confidence: float # 0.0 - 1.0
    associated_url: Optional[str] = None
    items_breakdown: List[ClaimItemBreakdown] = []
    evidence_snippets: List[EvidenceSnippet] = []
    explanation: str

class VerificationSummary(BaseModel):
    evidence_coverage_percentage: float
    total_claims: int
    supported_claims: int
    partially_supported_claims: int
    unverified_claims: int
    broken_claims: int
    restricted_claims: int
    
    total_urls: int
    accessible_urls: int
    broken_urls: int
    restricted_urls: int

class CandidateInfo(BaseModel):
    name: Optional[str] = "Candidate"
    email: Optional[str] = None
    phone: Optional[str] = None
    title: Optional[str] = None
    raw_summary: Optional[str] = None

class VerificationReportResponse(BaseModel):
    id: str
    filename: str
    created_at: str
    candidate: CandidateInfo
    summary: VerificationSummary
    claims: List[ClaimVerification]
    urls: List[DiscoveredUrl]
    risk_notes: List[str] = []
    strengths: List[str] = []
    extracted_text_preview: Optional[str] = None

class VerificationSettingsUpdate(BaseModel):
    github_token: Optional[str] = None
    llm_provider: Optional[str] = None
    openai_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None
    ollama_base_url: Optional[str] = None

class TestConnectionResponse(BaseModel):
    service: str
    success: bool
    message: str
    details: Optional[Dict[str, Any]] = None
