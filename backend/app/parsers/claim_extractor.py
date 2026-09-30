import re
import uuid
from typing import List, Dict, Any, Optional
from backend.app.schemas import ClaimStatus

# Comprehensive tech dictionary for entity extraction
TECH_KEYWORDS = [
    # Languages
    "Python", "TypeScript", "JavaScript", "Golang", "Go", "Rust", "Java", "C++", "C#", "C", "Ruby", "PHP", "Swift", "Kotlin", "Scala", "Dart", "Solidity",
    # AI / ML / Data
    "LangGraph", "LangChain", "OpenAI", "Llama", "Gemini", "PyTorch", "TensorFlow", "HuggingFace", "Scikit-Learn", "Keras", "Pandas", "NumPy", "OpenCV", "ChromaDB", "Pinecone", "Qdrant", "FAISS", "spaCy", "NLTK", "Ollama", "CrewAI", "AutoGen",
    # Frameworks & Backend
    "FastAPI", "Flask", "Django", "Node.js", "Express", "NestJS", "Spring Boot", "ASP.NET", "Ruby on Rails", "Gin", "Echo", "Actix", "Axum", "Fiber",
    # Frontend & UI
    "React", "Next.js", "Vue", "Nuxt", "Angular", "Svelte", "SvelteKit", "Tailwind CSS", "TailwindCSS", "Tailwind", "Redux", "Zustand", "GraphQL", "REST", "gRPC", "WebSocket", "Vite", "Webpack",
    # Cloud & DevOps
    "AWS", "Amazon Web Services", "AWS Bedrock", "AWS Lambda", "S3", "EC2", "ECS", "GCP", "Google Cloud", "Azure", "Docker", "Kubernetes", "K8s", "Terraform", "Ansible", "CI/CD", "GitHub Actions", "GitLab CI", "Prometheus", "Grafana", "Nginx",
    # Databases & Storage
    "PostgreSQL", "Postgres", "MySQL", "MongoDB", "Redis", "Elasticsearch", "Cassandra", "DynamoDB", "SQLite", "Supabase", "Firebase", "Neo4j", "Kafka", "RabbitMQ", "Celery"
]

# Case-insensitive lookup map
TECH_MAP = {k.lower(): k for k in TECH_KEYWORDS}

class ClaimExtractor:
    """
    Extracts atomic, verifiable claims from resume text and sections.
    Identifies technologies, project claims, experience bullet points, certifications, and metrics.
    """
    def extract_claims(self, resume_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        claims: List[Dict[str, Any]] = []
        sections = resume_data.get("sections", {})
        discovered_urls = resume_data.get("raw_links", [])
        
        # 1. Extract Project Claims
        project_text = sections.get("PROJECTS", "")
        if project_text:
            p_claims = self._extract_project_claims(project_text, discovered_urls)
            claims.extend(p_claims)
            
        # 2. Extract Skill Claims
        skill_text = sections.get("SKILLS", "")
        if skill_text:
            s_claims = self._extract_skill_claims(skill_text)
            claims.extend(s_claims)
            
        # 3. Extract Experience Claims
        exp_text = sections.get("EXPERIENCE", "")
        if exp_text:
            e_claims = self._extract_experience_claims(exp_text, discovered_urls)
            claims.extend(e_claims)
            
        # 4. Extract Certifications & Achievements / Publications
        cert_text = sections.get("CERTIFICATIONS", "")
        if cert_text:
            c_claims = self._extract_certification_claims(cert_text, discovered_urls)
            claims.extend(c_claims)
            
        pub_text = sections.get("PUBLICATIONS", "")
        if pub_text:
            p_claims = self._extract_certification_claims(pub_text, discovered_urls)
            claims.extend(p_claims)
            
        # 5. Extract Repository URL Direct Claims
        for url in discovered_urls:
            if "github.com/" in url and len(url.split("/")) >= 5:
                # Direct repo link claim
                repo_path = "/".join(url.split("/")[-2:])
                claims.append({
                    "id": str(uuid.uuid4()),
                    "category": "repository_link",
                    "section": "Links / Portfolio",
                    "claim_text": f"Maintains public repository at {url}",
                    "claimed_items": [repo_path],
                    "associated_url": url,
                    "default_status": ClaimStatus.UNVERIFIED
                })

        # If no specific sections matched, fallback to sentence-level extraction from full text
        if not claims:
            full_text = resume_data.get("full_text", "")
            claims = self._extract_fallback_claims(full_text, discovered_urls)
            
        # Clean leading bullet symbols from all claims
        for c in claims:
            c["claim_text"] = self._clean_text(c["claim_text"])
            
        return claims

    def _clean_text(self, text: str) -> str:
        """Strips leading bullet points, question marks from unicode fonts, dashes and whitespace."""
        text = text.strip()
        text = re.sub(r'^[•\*\-\?·▪►✓✔\uf0b7\s]+', '', text).strip()
        return text

    def _extract_tech_entities(self, text: str) -> List[str]:
        """Extracts normalized technology entity names found in a piece of text."""
        found = []
        for low_name, clean_name in TECH_MAP.items():
            # Use regex word boundaries for accurate matching
            pattern = rf'(?<![a-zA-Z0-9_\-\./]){re.escape(low_name)}(?![a-zA-Z0-9_\-\./])'
            if re.search(pattern, text.lower()):
                if clean_name not in found:
                    found.append(clean_name)
        return found

    def _find_associated_url(self, text_chunk: str, all_urls: List[str]) -> Optional[str]:
        """Finds if a specific URL is explicitly cited inside a text chunk."""
        for url in all_urls:
            # Check url or url without https
            clean = url.replace("https://", "").replace("http://", "").rstrip("/")
            if clean.lower() in text_chunk.lower() or url.lower() in text_chunk.lower():
                return url
        return None

    def _extract_project_claims(self, project_text: str, discovered_urls: List[str]) -> List[Dict[str, Any]]:
        claims = []
        # Split projects by double newlines or bullet points
        blocks = re.split(r'\n(?=[A-Z0-9#\-\*•])|\n\n', project_text)
        
        current_project_url = None
        for block in blocks:
            lines = [l.strip() for l in block.split("\n") if l.strip()]
            if not lines:
                continue
                
            block_url = self._find_associated_url(block, discovered_urls)
            if block_url:
                current_project_url = block_url
                
            for line in lines:
                techs = self._extract_tech_entities(line)
                # If the line contains active verbs or technical achievements
                if techs or any(v in line.lower() for v in ["built", "developed", "architected", "implemented", "designed", "created", "deployed", "integrated", "using", "powered by"]):
                    line_url = self._find_associated_url(line, discovered_urls) or current_project_url
                    claims.append({
                        "id": str(uuid.uuid4()),
                        "category": "project_tech",
                        "section": "Projects",
                        "claim_text": line,
                        "claimed_items": techs,
                        "associated_url": line_url,
                        "default_status": ClaimStatus.UNVERIFIED
                    })
        return claims

    def _extract_skill_claims(self, skill_text: str) -> List[Dict[str, Any]]:
        claims = []
        lines = [l.strip() for l in skill_text.split("\n") if l.strip()]
        for line in lines:
            techs = self._extract_tech_entities(line)
            if techs:
                claims.append({
                    "id": str(uuid.uuid4()),
                    "category": "skill",
                    "section": "Skills",
                    "claim_text": line,
                    "claimed_items": techs,
                    "associated_url": None,
                    "default_status": ClaimStatus.UNVERIFIED
                })
        return claims

    def _extract_experience_claims(self, exp_text: str, discovered_urls: List[str]) -> List[Dict[str, Any]]:
        claims = []
        lines = [l.strip() for l in exp_text.split("\n") if l.strip()]
        for line in lines:
            techs = self._extract_tech_entities(line)
            # Check for metric or impact claims (e.g. 40%, 10k, $2M, 50ms)
            has_metric = bool(re.search(r'\b\d+(?:\.\d+)?(?:%|k|M|ms|s|x|GB|TB)?\b', line))
            
            if techs or has_metric or any(v in line.lower() for v in ["led", "spearheaded", "optimized", "managed", "scaled", "migrated", "reduced", "increased"]):
                claims.append({
                    "id": str(uuid.uuid4()),
                    "category": "metric" if has_metric else "experience",
                    "section": "Experience",
                    "claim_text": line,
                    "claimed_items": techs,
                    "associated_url": self._find_associated_url(line, discovered_urls),
                    "default_status": ClaimStatus.UNVERIFIED
                })
        return claims

    def _extract_certification_claims(self, cert_text: str, discovered_urls: List[str]) -> List[Dict[str, Any]]:
        claims = []
        lines = [l.strip() for l in cert_text.split("\n") if l.strip()]
        for line in lines:
            if len(line) > 5 and not any(ign in line.lower() for ign in ["certifications", "licenses", "awards"]):
                techs = self._extract_tech_entities(line)
                claims.append({
                    "id": str(uuid.uuid4()),
                    "category": "certification",
                    "section": "Certifications",
                    "claim_text": line,
                    "claimed_items": techs or [line[:40]],
                    "associated_url": self._find_associated_url(line, discovered_urls),
                    "default_status": ClaimStatus.UNVERIFIED
                })
        return claims

    def _extract_fallback_claims(self, full_text: str, discovered_urls: List[str]) -> List[Dict[str, Any]]:
        claims = []
        sentences = [s.strip() for s in re.split(r'[\.\n•\*\-]', full_text) if len(s.strip()) > 15]
        for s in sentences:
            techs = self._extract_tech_entities(s)
            if techs:
                claims.append({
                    "id": str(uuid.uuid4()),
                    "category": "general_claim",
                    "section": "Resume Content",
                    "claim_text": s,
                    "claimed_items": techs,
                    "associated_url": self._find_associated_url(s, discovered_urls),
                    "default_status": ClaimStatus.UNVERIFIED
                })
        return claims
