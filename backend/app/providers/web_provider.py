import httpx
from bs4 import BeautifulSoup
import re
from typing import Tuple, Optional, List
from backend.app.schemas import WebPageData, UrlStatus
from backend.app.services.ssrf_validator import is_safe_url
from backend.app.config import settings

COMMON_TECHS = [
    "python", "javascript", "typescript", "react", "next.js", "vue", "angular", "node.js",
    "fastapi", "flask", "django", "docker", "kubernetes", "aws", "gcp", "azure", "postgresql",
    "mongodb", "redis", "langchain", "langgraph", "pytorch", "tensorflow", "graphql", "tailwind",
    "rust", "golang", "java", "spring", "c++", "c#", ".net", "solidity", "kafka", "elasticsearch"
]

class WebProvider:
    """
    SSRF-protected Web & Portfolio inspection provider.
    Extracts projects, technologies, headings, outbound links, and body text snippets.
    """
    async def inspect_url(self, url: str) -> Tuple[UrlStatus, Optional[WebPageData], Optional[str]]:
        safe, reason = is_safe_url(url)
        if not safe:
            return UrlStatus.INVALID, None, f"SSRF blocked: {reason}"
            
        headers = {
            "User-Agent": settings.USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }
        
        try:
            async with httpx.AsyncClient(timeout=settings.HTTP_TIMEOUT_SECONDS, follow_redirects=True) as client:
                res = await client.get(url, headers=headers)
                
                if res.status_code == 404:
                    return UrlStatus.BROKEN, None, f"Page not found (HTTP 404)"
                elif res.status_code in (401, 403):
                    data = WebPageData(
                        status_code=res.status_code,
                        is_restricted=True,
                        restriction_reason=f"Access restricted (HTTP {res.status_code})"
                    )
                    return UrlStatus.RESTRICTED, data, f"Access restricted (HTTP {res.status_code})"
                elif res.status_code >= 400:
                    return UrlStatus.BROKEN, None, f"Server returned HTTP {res.status_code}"
                    
                content_type = res.headers.get("content-type", "").lower()
                if "text/html" not in content_type and "text/plain" not in content_type:
                    # Non-HTML content
                    data = WebPageData(
                        title=url,
                        description=f"Direct resource ({content_type})",
                        status_code=res.status_code,
                        is_restricted=False
                    )
                    return UrlStatus.ACCESSIBLE, data, None
                    
                soup = BeautifulSoup(res.text, "html.parser")
                
                # Remove scripts, styles, noscript
                for tag in soup(["script", "style", "noscript", "svg", "header", "footer", "nav"]):
                    tag.extract()
                    
                title = soup.title.string.strip() if soup.title and soup.title.string else ""
                
                # Description
                meta_desc = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", property="og:description")
                desc_text = meta_desc["content"].strip() if meta_desc and meta_desc.get("content") else ""
                
                # Headings
                h1_list = [h.get_text().strip() for h in soup.find_all("h1") if h.get_text().strip()][:8]
                h2_list = [h.get_text().strip() for h in soup.find_all("h2") if h.get_text().strip()][:15]
                
                # Outbound links (especially GitHub links or project demos)
                outbound: List[str] = []
                for a in soup.find_all("a", href=True):
                    href = a["href"].strip()
                    if href.startswith("http") and not href.startswith(url):
                        outbound.append(href)
                        
                # Extract visible text
                body_text = soup.get_text(separator=" ", strip=True)
                lower_text = body_text.lower()
                
                # Detect tech keywords
                found_techs = []
                for tech in COMMON_TECHS:
                    # Word boundary search
                    if re.search(rf'\b{re.escape(tech)}\b', lower_text):
                        found_techs.append(tech.title())
                        
                # Extract project-like keywords from H2/H3
                projects = []
                for h in h2_list:
                    if len(h) < 60 and not any(ign in h.lower() for ign in ["contact", "about", "skills", "experience", "education"]):
                        projects.append(h)
                        
                web_data = WebPageData(
                    title=title or url,
                    description=desc_text,
                    h1_headings=h1_list,
                    h2_headings=h2_list,
                    discovered_projects=projects[:10],
                    discovered_techs=found_techs,
                    outbound_links=list(set(outbound))[:25],
                    raw_text_snippet=body_text[:3000],
                    status_code=res.status_code,
                    is_restricted=False
                )
                
                return UrlStatus.ACCESSIBLE, web_data, None
                
        except httpx.TimeoutException:
            return UrlStatus.TIMEOUT, None, f"Connection timed out ({settings.HTTP_TIMEOUT_SECONDS}s)"
        except Exception as e:
            return UrlStatus.BROKEN, None, f"Web request failed: {str(e)}"
