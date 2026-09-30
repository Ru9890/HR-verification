from fastapi import APIRouter, HTTPException, Response
from backend.app.services.sample_resumes import SAMPLE_RESUMES, generate_sample_pdf

router = APIRouter(prefix="/api/samples", tags=["Samples"])

@router.get("/")
async def get_sample_resumes():
    return [
        {
            "id": s["id"],
            "name": s["name"],
            "title": s["title"],
            "description": s["description"],
            "email": s["email"]
        }
        for s in SAMPLE_RESUMES
    ]

@router.get("/{sample_id}/pdf")
async def download_sample_pdf(sample_id: str):
    sample = next((s for s in SAMPLE_RESUMES if s["id"] == sample_id), None)
    if not sample:
        raise HTTPException(status_code=404, detail="Sample resume not found")
        
    pdf_bytes = generate_sample_pdf(sample_id)
    filename = f"{sample['name'].replace(' ', '_')}_Resume.pdf"
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
