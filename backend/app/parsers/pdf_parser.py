import pymupdf as fitz
import re
from typing import Dict, List, Any, Tuple, Optional
from urllib.parse import urlparse

URL_REGEX = re.compile(
    r'(?:https?://|www\.)[a-zA-Z0-9_\-\.]+(?:\.[a-zA-Z]{2,})+(?:/[^\s,;\)\]\}\>"]*)?',
    re.IGNORECASE
)

# Common domain shortcuts in resumes without http, e.g. github.com/user/repo, linkedin.com/in/user
DOMAIN_SHORTCUT_REGEX = re.compile(
    r'(?:(?:github\.com|linkedin\.com/in|linkedin\.com/company|kaggle\.com|leetcode\.com|huggingface\.co)/[a-zA-Z0-9_\-\./]+)',
    re.IGNORECASE
)

EMAIL_REGEX = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
PHONE_REGEX = re.compile(r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}')

SECTION_HEADERS = {
    "EXPERIENCE": [
        "experience", "work experience", "employment history", "professional experience", 
        "work history", "career history", "relevant experience", "employment"
    ],
    "PROJECTS": [
        "projects", "personal projects", "academic projects", "key projects", 
        "notable projects", "selected projects", "technical projects", "open source"
    ],
    "SKILLS": [
        "skills", "technical skills", "technologies", "core competencies", 
        "skills & tools", "programming skills", "technical proficiencies", "tech stack", "competencies"
    ],
    "EDUCATION": [
        "education", "academic background", "degrees", "educational qualifications", "academic qualifications"
    ],
    "CERTIFICATIONS": [
        "certifications", "certificates", "licenses & certifications", "credentials", "courses", "licenses"
    ],
    "PUBLICATIONS": [
        "publications", "research", "papers", "achievements", "awards", "honors"
    ]
}

def clean_url(url: Any) -> str:
    """Cleans trailing punctuation, quotes, brackets, control chars from URLs and adds scheme if missing."""
    if not url or not isinstance(url, str):
        return ""
        
    url = url.strip()
    # Remove control characters, newlines, tabs
    url = re.sub(r'[\r\n\t\s]+', '', url)
    url = url.strip("'\"()[]{}<>.,;:")
    
    # Strip any trailing punctuation
    while url and url[-1] in ('.', ',', ';', ':', ')', ']', '>', '}'):
        url = url[:-1]
        
    if not url:
        return ""
    
    if url.startswith("www."):
        url = "https://" + url
    elif not url.startswith("http://") and not url.startswith("https://"):
        if any(d in url.lower() for d in ["github.com", "linkedin.com", "leetcode.com", "kaggle.com", "huggingface.co"]):
            url = "https://" + url
        elif "." in url and "/" in url:
            url = "https://" + url
            
    return url

def extract_pdf_data(pdf_bytes: bytes) -> Dict[str, Any]:
    """
    Robustly extracts text, layout blocks, embedded links, inline URLs, and structured resume sections using PyMuPDF.
    Supports multi-column layouts, encrypted unlocked PDFs, and legacy PDF formats.
    """
    if not pdf_bytes or len(pdf_bytes) == 0:
        raise ValueError("Uploaded PDF file is empty (0 bytes).")

    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    except Exception as e:
        try:
            # Fallback without filetype constraint
            doc = fitz.open(stream=pdf_bytes)
        except Exception:
            raise ValueError(f"Could not open document as a valid PDF: {str(e)}")

    if doc.is_encrypted:
        # Try decrypting with empty password
        try:
            auth_res = doc.authenticate("")
            if not auth_res:
                raise ValueError("This PDF is password-protected. Please upload an unlocked PDF file.")
        except Exception:
            raise ValueError("This PDF is password-protected or encrypted. Please upload an unlocked PDF file.")

    if doc.page_count == 0:
        doc.close()
        raise ValueError("The uploaded PDF contains no pages.")

    full_text_list = []
    discovered_urls_set = set()
    raw_links = []
    
    for page_num in range(doc.page_count):
        page = doc[page_num]
        
        # 1. Extract text with layout-aware blocks (sorts columns naturally)
        try:
            blocks = page.get_text("blocks")
            # Sort blocks top-to-bottom, left-to-right: (y0, x0)
            sorted_blocks = sorted(blocks, key=lambda b: (b[1], b[0]))
            page_text = "\n".join([b[4] for b in sorted_blocks if isinstance(b[4], str) and b[4].strip()])
        except Exception:
            page_text = page.get_text("text") or ""

        full_text_list.append(page_text)
        
        # 2. Extract embedded PDF URI links (links attached to text/buttons in PDF metadata)
        try:
            links = page.get_links() or []
            for link in links:
                if isinstance(link, dict):
                    uri = link.get("uri")
                    if uri and isinstance(uri, str):
                        cleaned = clean_url(uri)
                        if cleaned and (cleaned.startswith("http://") or cleaned.startswith("https://")):
                            if cleaned not in discovered_urls_set:
                                discovered_urls_set.add(cleaned)
                                raw_links.append({
                                    "url": cleaned,
                                    "page": page_num + 1,
                                    "source": "pdf_annotation"
                                })
        except Exception:
            pass

    doc.close()
    full_text = "\n".join(full_text_list).strip()
    
    if not full_text:
        full_text = "Uploaded PDF contains no extractable text layer (may be scanned image)."

    # 3. Extract inline text URLs via regex from full text
    try:
        text_matches = URL_REGEX.findall(full_text)
        for match in text_matches:
            if isinstance(match, str):
                cleaned = clean_url(match)
                if cleaned and (cleaned.startswith("http://") or cleaned.startswith("https://")):
                    if cleaned not in discovered_urls_set:
                        discovered_urls_set.add(cleaned)
                        raw_links.append({
                            "url": cleaned,
                            "page": 1,
                            "source": "inline_text"
                        })
    except Exception:
        pass
            
    try:
        shortcut_matches = DOMAIN_SHORTCUT_REGEX.findall(full_text)
        for match in shortcut_matches:
            if isinstance(match, str):
                cleaned = clean_url(match)
                if cleaned and (cleaned.startswith("http://") or cleaned.startswith("https://")):
                    if cleaned not in discovered_urls_set:
                        discovered_urls_set.add(cleaned)
                        raw_links.append({
                            "url": cleaned,
                            "page": 1,
                            "source": "domain_shortcut"
                        })
    except Exception:
        pass

    # 4. Extract candidate header info (Name, Email, Phone)
    lines = [l.strip() for l in full_text.split("\n") if l.strip()]
    candidate_name = "Candidate"
    
    for line in lines[:8]:
        cleaned_line = re.sub(r'^[#\*\-•\s\d\.\:]+', '', line).strip()
        if (
            cleaned_line
            and "@" not in cleaned_line
            and "http" not in cleaned_line.lower()
            and "www." not in cleaned_line.lower()
            and not any(h in cleaned_line.lower() for h in ["resume", "curriculum", "page", "cv", "phone", "email", "contact", "profile", "summary"])
            and len(cleaned_line.split()) <= 4
            and len(cleaned_line) >= 2
        ):
            candidate_name = cleaned_line
            break

    emails = EMAIL_REGEX.findall(full_text)
    candidate_email = emails[0] if emails else None
    
    phones = PHONE_REGEX.findall(full_text)
    candidate_phone = phones[0] if phones else None

    # 5. Segment resume into sections
    sections = parse_resume_sections(full_text)

    return {
        "candidate_name": candidate_name,
        "candidate_email": candidate_email,
        "candidate_phone": candidate_phone,
        "full_text": full_text,
        "pages_count": len(full_text_list),
        "raw_links": list(discovered_urls_set),
        "sections": sections
    }

def parse_resume_sections(text: str) -> Dict[str, str]:
    """
    Parses resume text into discrete sections (Experience, Projects, Skills, Education, Certifications, Publications, etc.).
    """
    lines = text.split("\n")
    sections: Dict[str, List[str]] = {
        "HEADER": [],
        "EXPERIENCE": [],
        "PROJECTS": [],
        "SKILLS": [],
        "EDUCATION": [],
        "CERTIFICATIONS": [],
        "PUBLICATIONS": [],
        "OTHER": []
    }
    
    current_section = "HEADER"
    
    for line in lines:
        cleaned_line = line.strip()
        if not cleaned_line:
            continue
            
        lower_line = re.sub(r'^[#\*\-•\s\d\.\:]+', '', cleaned_line).lower().rstrip(":").strip()
        
        # Check if line matches a known section header
        matched_section = None
        for sec_key, header_names in SECTION_HEADERS.items():
            if lower_line in header_names or (len(lower_line) < 32 and any(lower_line == h for h in header_names)):
                matched_section = sec_key
                break
                
        if matched_section:
            current_section = matched_section
            if current_section not in sections:
                sections[current_section] = []
            continue
            
        sections.setdefault(current_section, []).append(cleaned_line)
        
    return {k: "\n".join(v) for k, v in sections.items() if v}
