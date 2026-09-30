from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Dict, Any
from backend.app.database import get_db
from backend.app.models import VerificationReportDB

router = APIRouter(prefix="/api/reports", tags=["Reports"])

@router.get("/")
async def list_reports(db: AsyncSession = Depends(get_db)):
    stmt = select(VerificationReportDB).order_by(desc(VerificationReportDB.created_at)).limit(20)
    result = await db.execute(stmt)
    reports = result.scalars().all()
    
    return [
        {
            "id": r.id,
            "candidate_name": r.candidate_name,
            "candidate_email": r.candidate_email,
            "filename": r.filename,
            "created_at": r.created_at.isoformat() if r.created_at else None,
            "evidence_coverage_percentage": r.evidence_coverage_percentage,
            "total_claims": r.total_claims,
            "supported_claims": r.supported_claims,
            "partially_supported_claims": r.partially_supported_claims,
            "unverified_claims": r.unverified_claims,
            "broken_claims": r.broken_claims,
            "restricted_claims": r.restricted_claims,
            "total_urls": r.total_urls,
            "accessible_urls": r.accessible_urls
        }
        for r in reports
    ]

@router.delete("/{report_id}")
async def delete_report(report_id: str, db: AsyncSession = Depends(get_db)):
    report = await db.get(VerificationReportDB, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
        
    await db.delete(report)
    await db.commit()
    return {"message": "Report deleted successfully", "id": report_id}
