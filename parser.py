"""
parser.py — LLM orchestration layer.

Three LLM calls, each producing a different Pydantic model:
  1. parse_resume()  → CandidateProfile  (standalone resume extraction)
  2. parse_job()     → JobRequirements    (standalone JD extraction)
  3. analyze()       → ResumeAnalysis     (candidate × job comparison)

KEY CONCEPT — PROMPT ENGINEERING:
  The quality of LLM output depends on HOW you ask. Each function has a
  carefully crafted system prompt that assigns a persona, defines the task,
  and specifies evaluation criteria. Instructor then appends the JSON schema
  automatically so the LLM knows the exact structure to produce.
"""

from __future__ import annotations

from schemas import CandidateProfile, JobRequirements, ResumeAnalysis
from utils import get_instructor_client, truncate_text

MODEL = "llama-3.3-70b-versatile"


# ═══════════════════════════════════════════════════════════════════════════
# 1. RESUME PARSING — extract a structured profile from raw resume text
# ═══════════════════════════════════════════════════════════════════════════

RESUME_SYSTEM_PROMPT = """You are an expert resume parser and career analyst. Your task is to 
extract a complete, structured profile from a candidate's resume text.

Rules:
- Extract ALL skills you can identify, categorizing each as 'technical', 'soft_skill', 'tool', 
  'domain', or 'language'.
- For proficiency, infer from context (years used, project complexity, certifications).
- Synthesize a professional summary — don't just copy the resume's objective statement.
- For each experience entry, distill bullet points into a single impact_summary and list 
  measurable achievements separately.
- Estimate total_years_experience from the timeline.
- Describe the career_trajectory in one sentence (e.g. 'Progressed from junior dev to tech lead 
  over 5 years with increasing scope').
- If information is not available, use null for optional fields.
- Be thorough — this profile will be reused across multiple job comparisons."""


def parse_resume(resume_text: str) -> CandidateProfile:
    """Parse raw resume text into a structured CandidateProfile."""
    client = get_instructor_client()
    text = truncate_text(resume_text, max_chars=12_000)

    return client.chat.completions.create(
        model=MODEL,
        response_model=CandidateProfile,
        max_retries=2,
        messages=[
            {"role": "system", "content": RESUME_SYSTEM_PROMPT},
            {"role": "user", "content": f"Parse this resume:\n\n{text}"},
        ],
        temperature=0.2,
        max_tokens=4096,
    )


# ═══════════════════════════════════════════════════════════════════════════
# 2. JOB DESCRIPTION PARSING — extract structured requirements from a JD
# ═══════════════════════════════════════════════════════════════════════════

JOB_SYSTEM_PROMPT = """You are an expert recruiter who specializes in analyzing job descriptions. 
Extract the structured requirements from the given job description.

Rules:
- Separate REQUIRED skills (must-have) from PREFERRED skills (nice-to-have).
- Infer seniority_level from context (title, years required, responsibilities).
- Summarize the role in 2-3 sentences focusing on the core mission.
- List key responsibilities as actionable items.
- If minimum experience years aren't explicitly stated, infer from the seniority level."""


def parse_job(job_description: str) -> JobRequirements:
    """Parse a job description into structured JobRequirements."""
    client = get_instructor_client()
    text = truncate_text(job_description, max_chars=6_000)

    return client.chat.completions.create(
        model=MODEL,
        response_model=JobRequirements,
        max_retries=2,
        messages=[
            {"role": "system", "content": JOB_SYSTEM_PROMPT},
            {"role": "user", "content": f"Parse this job description:\n\n{text}"},
        ],
        temperature=0.2,
        max_tokens=2048,
    )


# ═══════════════════════════════════════════════════════════════════════════
# 3. CANDIDATE × JOB ANALYSIS — the core comparison
# ═══════════════════════════════════════════════════════════════════════════

ANALYSIS_SYSTEM_PROMPT = """You are an elite technical recruiter and talent analyst with 20 years 
of experience. Your task: given a Job Description and a Candidate's Resume, produce a 
comprehensive structured analysis.

EVALUATION PRINCIPLES:

1. SEMANTIC MATCHING: Evaluate capability and potential, NOT exact keyword matches.
   "Built distributed systems at scale" matches "microservices architecture" even without 
   the exact phrase.

2. EVIDENCE-BASED: Every assessment must be grounded in specific resume content.

3. BALANCED: Highlight both strengths and concerns fairly.

4. CREDIBILITY CHECK: Flag claims that seem inflated relative to experience level.
   Look for: vague superlatives without metrics, scope claims mismatched with title/tenure,
   buzzword density without substance.

5. ACTIONABLE: Every insight should help a recruiter decide or prepare interview questions.

SCORING GUIDE (fit_score 0-100):
  90-100: Exceptional — exceeds requirements
  75-89:  Strong — meets most requirements, minor gaps
  60-74:  Moderate — core skills present, notable gaps
  40-59:  Weak — significant misalignment
  0-39:   Poor — fundamental mismatch

Most candidates fall 40-80. Reserve extremes for truly clear cases.

CREDIBILITY SCORING (credibility_score 0-100):
  90-100: Highly credible — claims well-supported with metrics and specifics
  70-89:  Mostly credible — some claims could use more evidence
  50-69:  Mixed — several vague or potentially inflated claims
  30-49:  Questionable — many unsupported or implausible claims
  0-29:   Unreliable — pervasive exaggeration or inconsistency"""


def analyze(resume_text: str, job_description: str) -> ResumeAnalysis:
    """Run the full candidate × job comparison analysis."""
    client = get_instructor_client()
    cv = truncate_text(resume_text, max_chars=12_000)
    jd = truncate_text(job_description, max_chars=4_000)

    user_msg = f"""Analyze this candidate against the job description.

--- JOB DESCRIPTION ---
{jd}

--- CANDIDATE RESUME ---
{cv}

Provide your complete structured analysis. Be thorough, evidence-based, and actionable."""

    return client.chat.completions.create(
        model=MODEL,
        response_model=ResumeAnalysis,
        max_retries=2,
        messages=[
            {"role": "system", "content": ANALYSIS_SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
        temperature=0.3,
        max_tokens=4096,
    )
