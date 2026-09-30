from typing import List, Dict, Any, Tuple
from backend.app.schemas import (
    VerificationSummary,
    VerificationReportResponse,
    CandidateInfo,
    ClaimVerification,
    DiscoveredUrl,
    ClaimStatus,
    UrlStatus
)

class ReportService:
    """
    Compiles the final verification report, metrics, coverage score, and risk / strength insights.
    """
    def compile_report(
        self,
        report_id: str,
        filename: str,
        created_at: str,
        candidate_data: Dict[str, Any],
        claims: List[ClaimVerification],
        urls: List[DiscoveredUrl],
        extracted_text_preview: str = ""
    ) -> VerificationReportResponse:
        
        total_claims = len(claims)
        supported_claims = sum(1 for c in claims if c.status == ClaimStatus.SUPPORTED)
        partially_supported_claims = sum(1 for c in claims if c.status == ClaimStatus.PARTIALLY_SUPPORTED)
        unverified_claims = sum(1 for c in claims if c.status == ClaimStatus.UNVERIFIED)
        broken_claims = sum(1 for c in claims if c.status == ClaimStatus.BROKEN_LINK)
        restricted_claims = sum(1 for c in claims if c.status == ClaimStatus.RESTRICTED)

        total_urls = len(urls)
        accessible_urls = sum(1 for u in urls if u.status == UrlStatus.ACCESSIBLE)
        broken_urls = sum(1 for u in urls if u.status in (UrlStatus.BROKEN, UrlStatus.INVALID, UrlStatus.TIMEOUT))
        restricted_urls = sum(1 for u in urls if u.status == UrlStatus.RESTRICTED)

        # Calculate Evidence Coverage
        if total_claims > 0:
            coverage = ((supported_claims * 1.0 + partially_supported_claims * 0.5) / total_claims) * 100
            coverage_pct = round(coverage, 1)
        else:
            coverage_pct = 0.0

        summary = VerificationSummary(
            evidence_coverage_percentage=coverage_pct,
            total_claims=total_claims,
            supported_claims=supported_claims,
            partially_supported_claims=partially_supported_claims,
            unverified_claims=unverified_claims,
            broken_claims=broken_claims,
            restricted_claims=restricted_claims,
            total_urls=total_urls,
            accessible_urls=accessible_urls,
            broken_urls=broken_urls,
            restricted_urls=restricted_urls
        )

        # Generate Strengths
        strengths = []
        if supported_claims > 0:
            strengths.append(f"{supported_claims} claims are directly corroborated by public repositories and manifests.")
        if accessible_urls > 0:
            strengths.append(f"{accessible_urls} public profiles/repositories verified accessible.")
        
        active_github = [u for u in urls if u.github_data and u.status == UrlStatus.ACCESSIBLE]
        if active_github:
            repo_names = ", ".join([u.github_data.name for u in active_github[:2]])
            strengths.append(f"Active public code repositories found ({repo_names}) with commit history.")

        # Generate Risk / Discrepancy Notes (Constructive & Objective)
        risk_notes = []
        if broken_urls > 0:
            risk_notes.append(f"{broken_urls} URL(s) listed on the resume returned 404 or connection failures.")
        if restricted_urls > 0:
            risk_notes.append(f"{restricted_urls} URL(s) require authentication or are private (e.g. LinkedIn or private repositories).")
        if unverified_claims > 0:
            risk_notes.append(f"{unverified_claims} claims have no public evidence available (may be internal/proprietary company work).")

        candidate = CandidateInfo(
            name=candidate_data.get("candidate_name") or "Candidate",
            email=candidate_data.get("candidate_email"),
            phone=candidate_data.get("candidate_phone")
        )

        return VerificationReportResponse(
            id=report_id,
            filename=filename,
            created_at=created_at,
            candidate=candidate,
            summary=summary,
            claims=claims,
            urls=urls,
            risk_notes=risk_notes,
            strengths=strengths,
            extracted_text_preview=extracted_text_preview[:1500] if extracted_text_preview else ""
        )
