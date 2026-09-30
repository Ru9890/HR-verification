import re
from urllib.parse import urlparse
from typing import Tuple, Dict, Any, Optional
from backend.app.schemas import UrlPlatform

GITHUB_REPO_REGEX = re.compile(
    r'^https?://(?:www\.)?github\.com/([a-zA-Z0-9_\-\.]+)/([a-zA-Z0-9_\-\.]+)(?:/.*)?$',
    re.IGNORECASE
)

GITHUB_USER_REGEX = re.compile(
    r'^https?://(?:www\.)?github\.com/([a-zA-Z0-9_\-\.]+)/?$',
    re.IGNORECASE
)

LINKEDIN_REGEX = re.compile(
    r'^https?://(?:[a-zA-Z0-9\-]+\.)?linkedin\.com/(?:in|company|school)/[a-zA-Z0-9_\-\.%]+',
    re.IGNORECASE
)

LEETCODE_REGEX = re.compile(
    r'^https?://(?:www\.)?leetcode\.com/(?:u/)?[a-zA-Z0-9_\-\.]+',
    re.IGNORECASE
)

KAGGLE_REGEX = re.compile(
    r'^https?://(?:www\.)?kaggle\.com/[a-zA-Z0-9_\-\.]+',
    re.IGNORECASE
)

HUGGINGFACE_REGEX = re.compile(
    r'^https?://(?:www\.)?huggingface\.co/[a-zA-Z0-9_\-\.]+',
    re.IGNORECASE
)

ARXIV_REGEX = re.compile(
    r'^https?://(?:www\.)?arxiv\.org/(?:abs|pdf)/[0-9\.]+',
    re.IGNORECASE
)

BLOG_DOMAINS = ["medium.com", "substack.com", "dev.to", "hashnode.dev", "hashnode.com", "towardsdatascience.com"]

def classify_url(url: str) -> Tuple[UrlPlatform, Dict[str, Any]]:
    """
    Classifies a normalized URL into its corresponding platform and extracts metadata parameters.
    """
    url = url.strip()
    parsed = urlparse(url)
    hostname = (parsed.hostname or "").lower()
    path = parsed.path.strip("/")
    
    # 1. GitHub Repository vs GitHub User Profile
    if "github.com" in hostname:
        repo_match = GITHUB_REPO_REGEX.match(url)
        if repo_match:
            owner, repo = repo_match.group(1), repo_match.group(2)
            # Filter out non-repo paths like 'settings', 'pricing', 'features', 'trending', 'explore', 'orgs'
            if owner.lower() not in ["settings", "pricing", "features", "trending", "explore", "about", "contact", "topics", "collections"]:
                clean_repo = repo[:-4] if repo.endswith(".git") else repo
                return UrlPlatform.GITHUB_REPO, {"owner": owner, "repo": clean_repo}
                
        user_match = GITHUB_USER_REGEX.match(url)
        if user_match:
            owner = user_match.group(1)
            if owner.lower() not in ["settings", "pricing", "features", "trending", "explore", "about", "contact", "topics", "collections"]:
                return UrlPlatform.GITHUB_USER, {"owner": owner}
        
        return UrlPlatform.GITHUB_REPO, {}

    # 2. LinkedIn
    if "linkedin.com" in hostname:
        return UrlPlatform.LINKEDIN, {"path": path}
        
    # 3. LeetCode
    if "leetcode.com" in hostname:
        return UrlPlatform.LEETCODE, {"path": path}
        
    # 4. Kaggle
    if "kaggle.com" in hostname:
        return UrlPlatform.KAGGLE, {"path": path}
        
    # 5. Hugging Face
    if "huggingface.co" in hostname:
        return UrlPlatform.HUGGINGFACE, {"path": path}
        
    # 6. arXiv
    if "arxiv.org" in hostname:
        return UrlPlatform.ARXIV, {"path": path}

    # 7. Tech Blogs
    if any(b in hostname for b in BLOG_DOMAINS):
        return UrlPlatform.DEV_BLOG, {"domain": hostname}

    # 8. Portfolio check
    # Check if domain looks like a personal portfolio (github.io, vercel.app, netlify.app, .me, .dev, or custom)
    if any(hostname.endswith(sfx) for sfx in [".github.io", ".vercel.app", ".netlify.app", ".me", ".dev", ".io", ".site", ".tech"]):
        return UrlPlatform.PORTFOLIO, {"domain": hostname}
        
    if "portfolio" in path.lower() or "resume" in path.lower() or "projects" in path.lower():
        return UrlPlatform.PORTFOLIO, {"domain": hostname}

    return UrlPlatform.OTHER, {"domain": hostname}
