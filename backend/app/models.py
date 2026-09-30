import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.app.database import Base

class VerificationReportDB(Base):
    __tablename__ = "verification_reports"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    candidate_name = Column(String(255), nullable=True)
    candidate_email = Column(String(255), nullable=True)
    filename = Column(String(255), nullable=False)
    file_hash = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Overall summary scores
    evidence_coverage_percentage = Column(Float, default=0.0)
    total_claims = Column(Integer, default=0)
    supported_claims = Column(Integer, default=0)
    partially_supported_claims = Column(Integer, default=0)
    unverified_claims = Column(Integer, default=0)
    broken_claims = Column(Integer, default=0)
    restricted_claims = Column(Integer, default=0)
    
    total_urls = Column(Integer, default=0)
    accessible_urls = Column(Integer, default=0)
    broken_urls = Column(Integer, default=0)
    restricted_urls = Column(Integer, default=0)
    
    # Full JSON snapshot
    full_report_json = Column(JSON, nullable=True)

    claims = relationship("ClaimDB", back_populates="report", cascade="all, delete-orphan")
    urls = relationship("DiscoveredUrlDB", back_populates="report", cascade="all, delete-orphan")

class ClaimDB(Base):
    __tablename__ = "claims"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    report_id = Column(String(36), ForeignKey("verification_reports.id"), nullable=False)
    category = Column(String(50), nullable=False) # project_tech, skill, experience, metric, certification, repository
    section = Column(String(50), nullable=False) # Projects, Skills, Experience, Certifications, etc.
    claim_text = Column(Text, nullable=False)
    claimed_items = Column(JSON, default=list) # e.g. ["Python", "FastAPI", "LangGraph"]
    status = Column(String(50), nullable=False) # Supported, Partially Supported, Unverified, Broken Link, Restricted
    confidence = Column(Float, default=0.0)
    associated_url = Column(String(500), nullable=True)
    evidence_snippets = Column(JSON, default=list)
    explanation = Column(Text, nullable=True)

    report = relationship("VerificationReportDB", back_populates="claims")

class DiscoveredUrlDB(Base):
    __tablename__ = "discovered_urls"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    report_id = Column(String(36), ForeignKey("verification_reports.id"), nullable=False)
    raw_url = Column(String(1000), nullable=False)
    normalized_url = Column(String(1000), nullable=False)
    platform = Column(String(50), nullable=False) # GITHUB_REPO, GITHUB_USER, LINKEDIN, PORTFOLIO, LEETCODE, KAGGLE, OTHER
    status = Column(String(50), nullable=False) # Accessible, Broken, Restricted, Invalid
    status_code = Column(Integer, nullable=True)
    title = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    platform_data = Column(JSON, default=dict)

    report = relationship("VerificationReportDB", back_populates="urls")
