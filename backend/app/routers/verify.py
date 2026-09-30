import asyncio
import uuid
import json
import logging
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional

from backend.app.database import get_db
from backend.app.models import VerificationReportDB, ClaimDB, DiscoveredUrlDB
from backend.app.schemas import (
    VerificationReportResponse,
    DiscoveredUrl,
    UrlPlatform,
    UrlStatus,
    ClaimStatus
)
from backend.app.parsers.pdf_parser import extract_pdf_data
from backend.app.parsers.claim_extractor import ClaimExtractor
from backend.app.providers.url_classifier import classify_url
from backend.app.providers.github_provider import GitHubProvider
from backend.app.providers.linkedin_provider import LinkedInProvider
from backend.app.providers.web_provider import WebProvider
from backend.app.providers.platform_provider import PlatformProvider
from backend.app.services.matcher import ClaimEvidenceMatcher
from backend.app.services.report_service import ReportService
from backend.app.services.sample_resumes import SAMPLE_RESUMES, generate_sample_pdf

logger = logging.getLogger("resume_verify")
logging.basicConfig(level=logging.INFO)

router = APIRouter(prefix="/api/verify", tags=["Verification"])

claim_extractor = ClaimExtractor()
matcher = ClaimEvidenceMatcher()
report_service = ReportService()
github_provider = GitHubProvider()
linkedin_provider = LinkedInProvider()
web_provider = WebProvider()
platform_provider = PlatformProvider()

async def run_verification_pipeline(pdf_bytes: bytes, filename: str, db: AsyncSession) -> VerificationReportResponse:
    report_id = str(uuid.uuid4())
    created_at = datetime.utcnow().isoformat()
    
    # 1. Extract text and links from PDF using PyMuPDF
    try:
        pdf_data = extract_pdf_data(pdf_bytes)
    except ValueError as ve:
        logger.error(f"PDF extraction error for {filename}: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.exception(f"Unexpected error parsing PDF {filename}")
        raise HTTPException(status_code=400, detail=f"Failed to parse PDF document: {str(e)}")
        
    raw_urls = pdf_data.get("raw_links", [])
    
    # 2. Extract Claims from resume text & sections
    try:
        raw_claims = claim_extractor.extract_claims(pdf_data)
    except Exception as e:
        logger.exception(f"Error extracting claims from {filename}: {str(e)}")
        raw_claims = []
    
    # 3. Classify and inspect all discovered URLs concurrently
    classified_urls = []
    for raw_url in raw_urls:
        try:
            platform, meta = classify_url(raw_url)
            classified_urls.append((raw_url, platform, meta))
        except Exception:
            continue
        
    async def inspect_single_url(raw_url: str, platform: UrlPlatform, meta: Dict[str, Any]) -> DiscoveredUrl:
        norm_url = raw_url
        try:
            if platform == UrlPlatform.GITHUB_REPO and "owner" in meta and "repo" in meta:
                status, g_data, err = await github_provider.inspect_repository(meta["owner"], meta["repo"])
                return DiscoveredUrl(
                    raw_url=raw_url,
                    normalized_url=norm_url,
                    platform=platform,
                    status=status,
                    status_code=200 if status == UrlStatus.ACCESSIBLE else None,
                    title=g_data.full_name if g_data else None,
                    github_data=g_data,
                    error_message=err
                )
            elif platform == UrlPlatform.LINKEDIN:
                status, w_data, err = await linkedin_provider.inspect_linkedin_url(raw_url)
                return DiscoveredUrl(
                    raw_url=raw_url,
                    normalized_url=norm_url,
                    platform=platform,
                    status=status,
                    status_code=w_data.status_code if w_data else None,
                    title=w_data.title if w_data else "LinkedIn Profile",
                    web_data=w_data,
                    error_message=err
                )
            elif platform in (UrlPlatform.LEETCODE, UrlPlatform.KAGGLE, UrlPlatform.HUGGINGFACE, UrlPlatform.ARXIV, UrlPlatform.DEV_BLOG):
                status, w_data, err = await platform_provider.inspect_platform(raw_url, platform)
                return DiscoveredUrl(
                    raw_url=raw_url,
                    normalized_url=norm_url,
                    platform=platform,
                    status=status,
                    status_code=w_data.status_code if w_data else None,
                    title=w_data.title if w_data else f"{platform.value}",
                    web_data=w_data,
                    error_message=err
                )
            else: # PORTFOLIO or OTHER
                status, w_data, err = await web_provider.inspect_url(raw_url)
                return DiscoveredUrl(
                    raw_url=raw_url,
                    normalized_url=norm_url,
                    platform=platform,
                    status=status,
                    status_code=w_data.status_code if w_data else None,
                    title=w_data.title if w_data else "Web Page",
                    web_data=w_data,
                    error_message=err
                )
        except Exception as e:
            return DiscoveredUrl(
                raw_url=raw_url,
                normalized_url=norm_url,
                platform=platform,
                status=UrlStatus.BROKEN,
                error_message=f"Inspection failed: {str(e)}"
            )

    # Run URL inspections concurrently with safe exception handling
    inspected_urls: List[DiscoveredUrl] = []
    if classified_urls:
        results = await asyncio.gather(
            *[inspect_single_url(u[0], u[1], u[2]) for u in classified_urls],
            return_exceptions=True
        )
        for idx, res in enumerate(results):
            if isinstance(res, DiscoveredUrl):
                inspected_urls.append(res)
            elif isinstance(res, Exception):
                inspected_urls.append(DiscoveredUrl(
                    raw_url=classified_urls[idx][0],
                    normalized_url=classified_urls[idx][0],
                    platform=classified_urls[idx][1],
                    status=UrlStatus.BROKEN,
                    error_message=str(res)
                ))

    # 4. Match Claims vs Collected Public Evidence
    try:
        verified_claims = matcher.match_claims(raw_claims, inspected_urls)
    except Exception as e:
        logger.exception(f"Error matching claims: {str(e)}")
        verified_claims = []
    
    # 5. Compile Final Verification Report
    candidate_meta = {
        "candidate_name": pdf_data.get("candidate_name"),
        "candidate_email": pdf_data.get("candidate_email"),
        "candidate_phone": pdf_data.get("candidate_phone")
    }
    
    final_report = report_service.compile_report(
        report_id=report_id,
        filename=filename,
        created_at=created_at,
        candidate_data=candidate_meta,
        claims=verified_claims,
        urls=inspected_urls,
        extracted_text_preview=pdf_data.get("full_text", "")
    )

    # 6. Save to Database
    try:
        db_report = VerificationReportDB(
            id=report_id,
            candidate_name=final_report.candidate.name,
            candidate_email=final_report.candidate.email,
            filename=filename,
            evidence_coverage_percentage=final_report.summary.evidence_coverage_percentage,
            total_claims=final_report.summary.total_claims,
            supported_claims=final_report.summary.supported_claims,
            partially_supported_claims=final_report.summary.partially_supported_claims,
            unverified_claims=final_report.summary.unverified_claims,
            broken_claims=final_report.summary.broken_claims,
            restricted_claims=final_report.summary.restricted_claims,
            total_urls=final_report.summary.total_urls,
            accessible_urls=final_report.summary.accessible_urls,
            broken_urls=final_report.summary.broken_urls,
            restricted_urls=final_report.summary.restricted_urls,
            full_report_json=final_report.model_dump()
        )
        db.add(db_report)
        await db.commit()
    except Exception as e:
        logger.warning(f"Could not persist report to DB: {str(e)}")
    
    return final_report

@router.post("/upload", response_model=VerificationReportResponse)
async def upload_resume_pdf(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    filename = file.filename or "uploaded_resume.pdf"
    content = await file.read()
    
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty (0 bytes). Please select a valid PDF.")
        
    if len(content) > 15 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size exceeds maximum limit of 15MB.")

    # Validate PDF format: check extension OR %PDF magic header
    is_pdf_ext = filename.lower().endswith(".pdf")
    is_pdf_magic = content.startswith(b"%PDF") or b"%PDF" in content[:1024]
    
    if not is_pdf_ext and not is_pdf_magic:
        raise HTTPException(status_code=400, detail=f"File '{filename}' does not appear to be a valid PDF format. Please upload a PDF document.")

    return await run_verification_pipeline(content, filename, db)

@router.post("/sample/{sample_id}", response_model=VerificationReportResponse)
async def verify_sample_resume(
    sample_id: str,
    db: AsyncSession = Depends(get_db)
):
    sample = next((s for s in SAMPLE_RESUMES if s["id"] == sample_id), None)
    if not sample:
        raise HTTPException(status_code=404, detail=f"Sample resume '{sample_id}' not found.")
        
    pdf_bytes = generate_sample_pdf(sample_id)
    return await run_verification_pipeline(pdf_bytes, f"{sample['name'].replace(' ', '_')}_Resume.pdf", db)

@router.get("/{report_id}", response_model=VerificationReportResponse)
async def get_verification_report(
    report_id: str,
    db: AsyncSession = Depends(get_db)
):
    report_db = await db.get(VerificationReportDB, report_id)
    if not report_db:
        raise HTTPException(status_code=404, detail="Verification report not found.")
        
    if report_db.full_report_json:
        return VerificationReportResponse(**report_db.full_report_json)
    raise HTTPException(status_code=500, detail="Report data corrupted.")
