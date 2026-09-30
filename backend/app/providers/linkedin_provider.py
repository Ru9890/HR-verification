import httpx
from bs4 import BeautifulSoup
from typing import Tuple, Optional
from backend.app.schemas import WebPageData, UrlStatus
from backend.app.services.ssrf_validator import is_safe_url
from backend.app.config import settings

class LinkedInProvider:
    """
    LinkedIn Verification Provider:
    Respects access restrictions and robot policies.
    Does NOT bypass authentication, solve captchas, or break anti-bot mechanisms.
    Only inspects publicly returned metadata.
    """
    async def inspect_linkedin_url(self, url: str) -> Tuple[UrlStatus, Optional[WebPageData], Optional[str]]:
        safe, reason = is_safe_url(url)
        if not safe:
            return UrlStatus.INVALID, None, f"Security check failed: {reason}"
            
        headers = {
            "User-Agent": settings.USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5"
        }
        
        try:
            async with httpx.AsyncClient(timeout=8.0, follow_redirects=True) as client:
                res = await client.get(url, headers=headers)
                
                # LinkedIn notoriously returns HTTP 999 (custom anti-scrape status) or redirects to /authwall / login
                if res.status_code == 999 or "/authwall" in str(res.url) or "/login" in str(res.url):
                    data = WebPageData(
                        title="LinkedIn Profile (Login Restricted)",
                        description="LinkedIn requires member authentication to view this profile publicly.",
                        status_code=res.status_code,
                        is_restricted=True,
                        restriction_reason="LinkedIn authentication wall detected. Verified non-bypassed as per policy."
                    )
                    return UrlStatus.RESTRICTED, data, "LinkedIn profile requires sign-in (Restricted)"
                    
                if res.status_code == 404:
                    return UrlStatus.BROKEN, None, "LinkedIn profile not found (404)"
                    
                if res.status_code in (401, 403):
                    data = WebPageData(
                        status_code=res.status_code,
                        is_restricted=True,
                        restriction_reason=f"HTTP {res.status_code} Access Denied"
                    )
                    return UrlStatus.RESTRICTED, data, f"Restricted profile access (HTTP {res.status_code})"
                    
                if res.status_code == 200:
                    soup = BeautifulSoup(res.text, "html.parser")
                    title = soup.title.string.strip() if soup.title and soup.title.string else "LinkedIn Member"
                    
                    # Look for og:title or og:description
                    og_desc = ""
                    meta_desc = soup.find("meta", property="og:description") or soup.find("meta", attrs={"name": "description"})
                    if meta_desc and meta_desc.get("content"):
                        og_desc = meta_desc["content"].strip()
                        
                    data = WebPageData(
                        title=title,
                        description=og_desc,
                        status_code=200,
                        is_restricted=False,
                        raw_text_snippet=og_desc[:300] if og_desc else title
                    )
                    return UrlStatus.ACCESSIBLE, data, None
                    
                return UrlStatus.RESTRICTED, None, f"LinkedIn returned HTTP {res.status_code}"
                
        except Exception as e:
            # If network error or timeout
            return UrlStatus.BROKEN, None, f"Connection failed to LinkedIn: {str(e)}"
