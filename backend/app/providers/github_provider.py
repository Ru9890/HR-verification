import httpx
import base64
import json
import re
import logging
from typing import Dict, Any, List, Optional, Tuple
from backend.app.config import settings
from backend.app.schemas import GitHubRepoData, GitHubDependency, UrlStatus
from backend.app.services.ssrf_validator import is_safe_url

logger = logging.getLogger("resume_verify.github")

GITHUB_API_BASE = "https://api.github.com"

class GitHubProvider:
    def __init__(self, token: Optional[str] = None):
        self.token = token or settings.GITHUB_TOKEN
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "ResumeVerifyAI/1.0"
        }
        if self.token:
            self.headers["Authorization"] = f"Bearer {self.token}"

    async def _get(self, client: httpx.AsyncClient, url: str) -> httpx.Response:
        """Wrapper that logs every GitHub API call and its result for debugging."""
        try:
            res = await client.get(url, headers=self.headers)
            remaining = res.headers.get("x-ratelimit-remaining", "?")
            logger.info(f"GitHub API  {res.status_code}  [{remaining} reqs left]  {url}")
            return res
        except Exception as exc:
            logger.warning(f"GitHub API ERROR  {url}  -> {exc}")
            raise

    async def inspect_repository(self, owner: str, repo: str) -> Tuple[UrlStatus, Optional[GitHubRepoData], Optional[str]]:
        """
        Inspects a GitHub repository using the official GitHub REST API.
        Extracts metadata, languages, README, manifests, dependencies, file tree, commits, and contributors.
        """
        repo_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}"

        async with httpx.AsyncClient(timeout=settings.HTTP_TIMEOUT_SECONDS, follow_redirects=True) as client:
            # 1. Check Repo existence & metadata
            try:
                res = await self._get(client, repo_url)
            except Exception as e:
                return UrlStatus.BROKEN, None, f"Network connection error: {str(e)}"

            if res.status_code == 404:
                return UrlStatus.BROKEN, None, f"Repository '{owner}/{repo}' not found (404)"
            elif res.status_code in (401, 403):
                remaining = res.headers.get("x-ratelimit-remaining", "0")
                if remaining == "0":
                    reset_time = res.headers.get("x-ratelimit-reset", "soon")
                    return UrlStatus.RESTRICTED, None, f"GitHub API rate limit reached (Reset: {reset_time}). Add GITHUB_TOKEN in settings to increase limit to 5000 req/hr."
                return UrlStatus.RESTRICTED, None, f"Access restricted/private repository (HTTP {res.status_code})"
            elif res.status_code != 200:
                return UrlStatus.BROKEN, None, f"GitHub returned HTTP {res.status_code}"

            repo_info = res.json()
            default_branch = repo_info.get("default_branch", "main")
            is_empty = repo_info.get("size", -1) == 0  # size==0 means repo has no commits yet

            # 2. Fetch Languages
            languages_dict: Dict[str, int] = {}
            lang_pct: Dict[str, float] = {}
            try:
                lang_res = await self._get(client, f"{repo_url}/languages")
                if lang_res.status_code == 200:
                    languages_dict = lang_res.json()
                    total_bytes = sum(languages_dict.values())
                    if total_bytes > 0:
                        for lang, b_count in languages_dict.items():
                            lang_pct[lang] = round((b_count / total_bytes) * 100, 1)
                else:
                    logger.warning(f"Languages fetch failed: HTTP {lang_res.status_code}")
            except Exception as exc:
                logger.warning(f"Languages fetch exception: {exc}")

            # 3. Fetch README
            readme_text = None
            readme_excerpt = None
            try:
                readme_res = await self._get(client, f"{repo_url}/readme")
                if readme_res.status_code == 200:
                    readme_data = readme_res.json()
                    if "content" in readme_data:
                        raw_bytes = base64.b64decode(readme_data["content"])
                        readme_text = raw_bytes.decode("utf-8", errors="ignore")
                        readme_excerpt = readme_text[:1500] if readme_text else None
                else:
                    logger.info(f"README not found: HTTP {readme_res.status_code}")
            except Exception as exc:
                logger.warning(f"README fetch exception: {exc}")

            # 4. Fetch Dependencies from Manifests
            dependencies: List[GitHubDependency] = []
            if not is_empty:
                manifest_files = [
                    "requirements.txt",
                    "pyproject.toml",
                    "Pipfile",
                    "package.json",
                    "go.mod",
                    "Cargo.toml",
                    "Dockerfile"
                ]
                for manifest_name in manifest_files:
                    try:
                        m_res = await self._get(client, f"{repo_url}/contents/{manifest_name}")
                        if m_res.status_code == 200:
                            m_json = m_res.json()
                            if "content" in m_json:
                                raw_content = base64.b64decode(m_json["content"]).decode("utf-8", errors="ignore")
                                parsed_deps = self._parse_manifest_content(manifest_name, raw_content)
                                dependencies.extend(parsed_deps)
                        elif m_res.status_code not in (404,):
                            logger.warning(f"Manifest {manifest_name}: HTTP {m_res.status_code}")
                    except Exception as exc:
                        logger.warning(f"Manifest {manifest_name} exception: {exc}")
                        continue

            # 5. Fetch File Tree summary
            # GitHub returns 409 for empty repos — skip gracefully
            file_tree: List[str] = []
            if not is_empty:
                try:
                    tree_res = await self._get(client, f"{repo_url}/git/trees/{default_branch}?recursive=1")
                    if tree_res.status_code == 200:
                        tree_data = tree_res.json().get("tree", [])
                        for item in tree_data[:60]:
                            path = item.get("path", "")
                            if not any(ign in path for ign in ["node_modules", ".git", ".idea", "__pycache__", "dist", "build"]):
                                file_tree.append(path)
                    elif tree_res.status_code == 409:
                        logger.info(f"File tree 409 (empty/unborn repo): {owner}/{repo}")
                    else:
                        logger.warning(f"File tree HTTP {tree_res.status_code}: {owner}/{repo}")
                except Exception as exc:
                    logger.warning(f"File tree exception: {exc}")

            # 6. Fetch Commits (up to 100 per page) + parse Link header for true total
            # GitHub returns 409 for empty repos — skip gracefully
            recent_commits: List[Dict[str, Any]] = []
            total_commits: Optional[int] = None
            if not is_empty:
                try:
                    commits_res = await self._get(client, f"{repo_url}/commits?per_page=100")
                    if commits_res.status_code == 200:
                        for c in commits_res.json():
                            commit_obj = c.get("commit", {})
                            author_obj = commit_obj.get("author", {})
                            recent_commits.append({
                                "sha": c.get("sha", "")[:7],
                                "message": commit_obj.get("message", "").split("\n")[0],
                                "author": author_obj.get("name", "Unknown"),
                                "date": author_obj.get("date", "")
                            })
                        # Parse Link header to get true total commit count
                        # Format: <url?page=N>; rel="last"
                        link_header = commits_res.headers.get("link", "")
                        if link_header:
                            import re as _re
                            last_match = _re.search(r'[?&]page=(\d+)[^>]*>\s*;\s*rel="last"', link_header)
                            if last_match:
                                last_page = int(last_match.group(1))
                                # All pages full except possibly the last
                                # We know first page has 100 → total ≈ (last_page-1)*100 + len(last page)
                                # Safest estimate: last_page * 100 is a ceiling, actual from first page size
                                total_commits = (last_page - 1) * 100 + len(recent_commits)
                                # But first page IS page 1, so if there are more pages:
                                # actual = (last_page-1)*100 + size_of_last_page
                                # We don't know last page size without fetching it, so fetch it
                                if last_page > 1:
                                    last_res = await self._get(client, f"{repo_url}/commits?per_page=100&page={last_page}")
                                    if last_res.status_code == 200:
                                        last_page_commits = last_res.json()
                                        total_commits = (last_page - 1) * 100 + len(last_page_commits)
                            else:
                                # No last page in Link header → all commits fit in first page
                                total_commits = len(recent_commits)
                        else:
                            # No Link header → all commits fit in one page
                            total_commits = len(recent_commits)
                    elif commits_res.status_code == 409:
                        logger.info(f"Commits 409 (empty/unborn repo): {owner}/{repo}")
                    else:
                        logger.warning(f"Commits HTTP {commits_res.status_code}: {owner}/{repo}")
                except Exception as exc:
                    logger.warning(f"Commits fetch exception: {exc}")

            # 7. Fetch Contributors
            contributors: List[Dict[str, Any]] = []
            if not is_empty:
                try:
                    contrib_res = await self._get(client, f"{repo_url}/contributors?per_page=20")
                    if contrib_res.status_code == 200:
                        for ct in contrib_res.json():
                            contributors.append({
                                "login": ct.get("login", ""),
                                "contributions": ct.get("contributions", 0),
                                "avatar_url": ct.get("avatar_url", "")
                            })
                    elif contrib_res.status_code == 204:
                        logger.info(f"Contributors: empty repo (204): {owner}/{repo}")
                    elif contrib_res.status_code == 409:
                        logger.info(f"Contributors 409 (empty/unborn repo): {owner}/{repo}")
                    else:
                        logger.warning(f"Contributors HTTP {contrib_res.status_code}: {owner}/{repo}")
                except Exception as exc:
                    logger.warning(f"Contributors fetch exception: {exc}")

            repo_data = GitHubRepoData(
                owner=owner,
                name=repo,
                full_name=repo_info.get("full_name", f"{owner}/{repo}"),
                description=repo_info.get("description"),
                stars=repo_info.get("stargazers_count", 0),
                forks=repo_info.get("forks_count", 0),
                default_branch=default_branch,
                created_at=repo_info.get("created_at"),
                updated_at=repo_info.get("updated_at"),
                pushed_at=repo_info.get("pushed_at"),
                is_fork=repo_info.get("fork", False),
                languages=languages_dict,
                language_percentages=lang_pct,
                readme_content=readme_text,
                readme_excerpt=readme_excerpt,
                dependencies=dependencies,
                file_tree_summary=file_tree,
                recent_commits=recent_commits,
                total_commits=total_commits,
                contributors=contributors,
                status="Empty repository (no commits)" if is_empty else "Active"
            )

            return UrlStatus.ACCESSIBLE, repo_data, None

    def _parse_manifest_content(self, filename: str, content: str) -> List[GitHubDependency]:
        """Parses package dependencies from manifest file content."""
        deps: List[GitHubDependency] = []

        if filename == "requirements.txt":
            for line in content.splitlines():
                line = line.strip()
                if not line or line.startswith("#") or line.startswith("-"):
                    continue
                match = re.match(r'^([a-zA-Z0-9_\-\.]+)(?:([=><~!].*))?$', line)
                if match:
                    pkg, ver = match.group(1), match.group(2)
                    deps.append(GitHubDependency(file=filename, package_name=pkg.lower(), version_spec=ver))

        elif filename == "package.json":
            try:
                pkg_data = json.loads(content)
                all_deps = {**pkg_data.get("dependencies", {}), **pkg_data.get("devDependencies", {})}
                for pkg, ver in all_deps.items():
                    deps.append(GitHubDependency(file=filename, package_name=pkg.lower(), version_spec=str(ver)))
            except Exception:
                pass

        elif filename == "pyproject.toml":
            for line in content.splitlines():
                line = line.strip()
                match = re.match(r'["\']([a-zA-Z0-9_\-\.]+)(?:([=><~!].*))?["\']', line)
                if match:
                    pkg, ver = match.group(1), match.group(2)
                    deps.append(GitHubDependency(file=filename, package_name=pkg.lower(), version_spec=ver))

        elif filename == "go.mod":
            for line in content.splitlines():
                line = line.strip()
                if line.startswith("require "):
                    parts = line.replace("require ", "").split()
                    if parts:
                        deps.append(GitHubDependency(file=filename, package_name=parts[0], version_spec=parts[1] if len(parts) > 1 else None))
                elif not line.startswith("module") and not line.startswith("go ") and "/" in line:
                    parts = line.split()
                    if parts:
                        deps.append(GitHubDependency(file=filename, package_name=parts[0], version_spec=parts[1] if len(parts) > 1 else None))

        elif filename == "Cargo.toml":
            in_deps = False
            for line in content.splitlines():
                line = line.strip()
                if line == "[dependencies]" or line.startswith("[dependencies."):
                    in_deps = True
                    continue
                if line.startswith("[") and in_deps:
                    in_deps = False
                    continue
                if in_deps and "=" in line:
                    parts = line.split("=", 1)
                    deps.append(GitHubDependency(file=filename, package_name=parts[0].strip().lower(), version_spec=parts[1].strip()))

        return deps

github_provider = GitHubProvider()
