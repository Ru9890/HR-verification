import httpx
from bs4 import BeautifulSoup
from typing import Tuple, Optional
from backend.app.schemas import WebPageData, UrlStatus, UrlPlatform
from backend.app.services.ssrf_validator import is_safe_url
from backend.app.config import settings

class PlatformProvider:
    """
    Provider for inspecting developer profile platforms:
    - LeetCode
    - Kaggle
    - Hugging Face
    - arXiv
    - Dev.to / Medium / Substack
    """
    async def inspect_platform(self, url: str, platform: UrlPlatform) -> Tuple[UrlStatus, Optional[WebPageData], Optional[str]]:
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
                    return UrlStatus.BROKEN, None, f"{platform.value} profile / link not found (404)"
                elif res.status_code in (401, 403):
                    data = WebPageData(
                        status_code=res.status_code,
                        is_restricted=True,
                        restriction_reason=f"Access restricted by platform (HTTP {res.status_code})"
                    )
                    return UrlStatus.RESTRICTED, data, f"Platform access restricted (HTTP {res.status_code})"
                elif res.status_code >= 400:
                    return UrlStatus.BROKEN, None, f"Platform returned HTTP {res.status_code}"
                    
                soup = BeautifulSoup(res.text, "html.parser")
                title = soup.title.string.strip() if soup.title and soup.title.string else f"{platform.value} Page"
                
                # Extract meta description
                meta_desc = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", property="og:description")
                desc_text = meta_desc["content"].strip() if meta_desc and meta_desc.get("content") else ""
                
                body_text = soup.get_text(separator=" ", strip=True)
                
                data = WebPageData(
                    title=title,
                    description=desc_text,
                    raw_text_snippet=body_text[:2000],
                    status_code=res.status_code,
                    is_restricted=False
                )
                return UrlStatus.ACCESSIBLE, data, None
                
        except httpx.TimeoutException:
            return UrlStatus.TIMEOUT, None, f"{platform.value} request timed out"
        except Exception as e:
            return UrlStatus.BROKEN, None, f"Connection failed: {str(e)}"
