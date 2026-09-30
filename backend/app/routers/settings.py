from fastapi import APIRouter, HTTPException
import httpx
from typing import Dict, Any
from backend.app.config import settings
from backend.app.schemas import VerificationSettingsUpdate, TestConnectionResponse
from backend.app.providers.github_provider import github_provider

router = APIRouter(prefix="/api/settings", tags=["Settings"])

def mask_token(token: str | None) -> str | None:
    if not token:
        return None
    if len(token) <= 8:
        return "********"
    return token[:4] + "****" + token[-4:]

@router.get("/")
async def get_settings():
    return {
        "app_name": settings.APP_NAME,
        "app_version": settings.APP_VERSION,
        "has_github_token": bool(settings.GITHUB_TOKEN),
        "github_token_masked": mask_token(settings.GITHUB_TOKEN),
        "llm_provider": settings.LLM_PROVIDER,
        "openai_configured": bool(settings.OPENAI_API_KEY),
        "gemini_configured": bool(settings.GEMINI_API_KEY),
        "groq_configured": bool(settings.GROQ_API_KEY),
        "ollama_base_url": settings.OLLAMA_BASE_URL,
        "http_timeout": settings.HTTP_TIMEOUT_SECONDS
    }

@router.post("/")
async def update_settings(payload: VerificationSettingsUpdate):
    if payload.github_token is not None:
        settings.GITHUB_TOKEN = payload.github_token if payload.github_token.strip() else None
        github_provider.token = settings.GITHUB_TOKEN
        if settings.GITHUB_TOKEN:
            github_provider.headers["Authorization"] = f"Bearer {settings.GITHUB_TOKEN}"
        else:
            github_provider.headers.pop("Authorization", None)
            
    if payload.llm_provider:
        settings.LLM_PROVIDER = payload.llm_provider
    if payload.openai_api_key is not None:
        settings.OPENAI_API_KEY = payload.openai_api_key
    if payload.gemini_api_key is not None:
        settings.GEMINI_API_KEY = payload.gemini_api_key
    if payload.groq_api_key is not None:
        settings.GROQ_API_KEY = payload.groq_api_key
    if payload.ollama_base_url is not None:
        settings.OLLAMA_BASE_URL = payload.ollama_base_url
        
    return {"message": "Settings updated successfully", "has_github_token": bool(settings.GITHUB_TOKEN)}

@router.post("/test-github", response_model=TestConnectionResponse)
async def test_github_connection():
    """
    Tests the connection to the GitHub REST API and retrieves the current rate limit.
    """
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "ResumeVerifyAI/1.0"
    }
    if settings.GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {settings.GITHUB_TOKEN}"
        
    try:
        async with httpx.AsyncClient(timeout=6.0) as client:
            res = await client.get("https://api.github.com/rate_limit", headers=headers)
            if res.status_code == 200:
                data = res.json()
                rate = data.get("rate", {})
                limit = rate.get("limit", 60)
                remaining = rate.get("remaining", 0)
                reset_ts = rate.get("reset", 0)
                
                is_auth = limit > 60
                msg = f"Connected to GitHub REST API. Rate Limit: {remaining}/{limit} requests remaining."
                if is_auth:
                    msg += " (Authenticated with Personal Access Token)"
                else:
                    msg += " (Unauthenticated public tier: 60 req/hr)"
                    
                return TestConnectionResponse(
                    service="GitHub REST API",
                    success=True,
                    message=msg,
                    details={
                        "limit": limit,
                        "remaining": remaining,
                        "reset_timestamp": reset_ts,
                        "authenticated": is_auth
                    }
                )
            else:
                return TestConnectionResponse(
                    service="GitHub REST API",
                    success=False,
                    message=f"GitHub returned HTTP {res.status_code}: {res.text[:100]}"
                )
    except Exception as e:
        return TestConnectionResponse(
            service="GitHub REST API",
            success=False,
            message=f"Connection failed: {str(e)}"
        )
