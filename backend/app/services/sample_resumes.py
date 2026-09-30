import pymupdf as fitz
import io
from typing import Dict, Any, List

SAMPLE_RESUMES = [
    {
        "id": "alex-chen-ai-engineer",
        "name": "Alex Chen",
        "title": "Senior AI & Full-Stack Engineer",
        "email": "alex.chen.dev@example.com",
        "phone": "+1 (555) 349-2049",
        "description": "Resume with real public GitHub projects, LinkedIn profile, Kaggle, and a deliberate broken demo link to demonstrate all statuses.",
        "text": """ALEX CHEN
San Francisco, CA | alex.chen.dev@example.com | +1 (555) 349-2049
GitHub: https://github.com/fastapi/fastapi | LinkedIn: https://www.linkedin.com/in/alexchen-ai | Portfolio: https://alexchen.dev

PROFESSIONAL SUMMARY
Senior AI Engineer with 6+ years of experience building scalable backend services, LLM applications, and distributed systems.

TECHNICAL SKILLS
• Languages: Python, TypeScript, JavaScript, Golang, SQL
• Frameworks: FastAPI, React, Next.js, PyTorch, LangChain, LangGraph
• Cloud & DevOps: Docker, Kubernetes, AWS, PostgreSQL, Redis, Celery
• AI / ML: OpenAI, Gemini, ChromaDB, HuggingFace, RAG Pipelines

PROJECTS

AI Document Extraction Agent | https://github.com/fastapi/fastapi
• Built an AI application using Python, FastAPI and LangGraph.
• Designed asynchronous document parsing pipelines processing 10,000+ pages per hour with Redis queueing.
• Integrated AWS Bedrock for multimodal analysis and automated document summarization.
• Open-source repository maintained at https://github.com/fastapi/fastapi with active community contributions.

Autonomous Agentic Workflow Engine | https://github.com/langchain-ai/langchain
• Developed multi-agent orchestration service using Python, LangChain, and Docker.
• Implemented tool-calling capabilities and structured output validation with Pydantic.
• Containerized microservices using Docker and deployed on AWS ECS.

Legacy Analytics Dashboard (Deprecated Demo) | https://broken-demo-domain-404-check.org/dashboard
• Built real-time analytics portal using React, TypeScript and WebSockets.
• Reduced dashboard initial page load time by 45%.

WORK EXPERIENCE

Senior Software Engineer — CloudScale Labs (2022 – Present)
• Spearheaded backend architecture migration to FastAPI and PostgreSQL, reducing API latency by 35%.
• Mentored team of 5 junior engineers in modern Python async programming and testing.

Software Engineer — DataSphere Systems (2019 – 2022)
• Built REST APIs using Python, Flask and Redis caching handling 2M daily requests.
• Automated CI/CD deployment pipelines using GitHub Actions and Docker.

EDUCATION & CERTIFICATIONS
• B.S. in Computer Science — University of California, Berkeley
• AWS Certified Solutions Architect - Associate
• LeetCode Profile: https://leetcode.com/alexchen_dev
"""
    },
    {
        "id": "maya-patel-frontend-lead",
        "name": "Maya Patel",
        "title": "Lead Frontend & Fullstack Architect",
        "email": "maya.patel@example.com",
        "phone": "+1 (555) 892-1102",
        "description": "Frontend Architect resume featuring React, Next.js, TailwindCSS, TypeScript, and open source repository links.",
        "text": """MAYA PATEL
Seattle, WA | maya.patel@example.com | +1 (555) 892-1102
GitHub: https://github.com/facebook/react | Portfolio: https://mayapatel.design | LinkedIn: https://www.linkedin.com/in/mayapatel-lead

SUMMARY
Passionate Lead Frontend Engineer with 7+ years of experience crafting enterprise-grade web applications.

CORE COMPETENCIES
• Frontend: React, Next.js, TypeScript, JavaScript, Tailwind CSS, Redux, Zustand, HTML5, CSS3
• Backend & Cloud: Node.js, Express, PostgreSQL, GraphQL, REST, Docker
• Testing & Tooling: Jest, Vitest, Cypress, Webpack, Vite, Git

KEY PROJECTS

Enterprise Design System & UI Library | https://github.com/facebook/react
• Architected modular component library in TypeScript, React, and Tailwind CSS.
• Achieved 98% test coverage with automated visual regression tests.
• Deployed interactive documentation storybook.

Real-Time Collaborative Whiteboard | https://github.com/facebook/react
• Built collaborative canvas application using TypeScript, React, and WebSockets.
• Optimized state synchronization for concurrent multi-user sessions.

EXPERIENCE

Lead Frontend Engineer — Apex Digital (2021 – Present)
• Led frontend team of 8 engineers delivering enterprise SaaS application using React and TypeScript.
• Reduced bundle size by 40% and improved Core Web Vitals score from 65 to 94.

Frontend Developer — TechStudio (2018 – 2021)
• Developed interactive responsive web applications using React, Next.js, and CSS modules.
"""
    }
]

def generate_sample_pdf(sample_id: str) -> bytes:
    """Generates an authentic PDF binary in memory from sample resume text using PyMuPDF."""
    sample = next((s for s in SAMPLE_RESUMES if s["id"] == sample_id), SAMPLE_RESUMES[0])
    
    doc = fitz.open()
    page = doc.new_page(width=612, height=792) # Letter size
    
    # We can write styled text blocks
    text_content = sample["text"]
    
    rect = fitz.Rect(50, 50, 562, 742)
    rc = page.insert_textbox(rect, text_content, fontsize=10, fontname="helv", color=(0.1, 0.1, 0.1))
    
    # Add embedded link annotations for URLs in the text
    for line in text_content.splitlines():
        if "https://" in line or "http://" in line:
            for word in line.split():
                if word.startswith("http://") or word.startswith("https://"):
                    clean_url = word.strip("(),;\"'")
                    # Find rect for this url
                    areas = page.search_for(clean_url)
                    for r in areas:
                        page.insert_link({"kind": fitz.LINK_URI, "from": r, "uri": clean_url})
                        
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes
