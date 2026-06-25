"""
schemas.py — Pydantic models defining the EXACT structure of all LLM outputs.

ARCHITECTURE:
  Three main schemas, each used for a different LLM call:
  1. CandidateProfile  — standalone resume parse (parse once, reuse)
  2. JobRequirements    — standalone JD parse
  3. ResumeAnalysis     — candidate × job comparison

WHY PYDANTIC + INSTRUCTOR?
  When you ask an LLM "analyze this resume," it returns free-form text.
  Pydantic models act as a CONTRACT: "you MUST return data in this shape."
  The Instructor library enforces this — it serializes the schema into the
  LLM prompt, validates the response, and retries on failure.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


# ═══════════════════════════════════════════════════════════════════════════
# 1. CANDIDATE PROFILE — standalone resume extraction
#    Parsed once when a resume is uploaded, stored in Supabase, reused
#    across multiple job comparisons.
# ═══════════════════════════════════════════════════════════════════════════

class ContactInfo(BaseModel):
    name: str = Field(description="Candidate's full name")
    email: str | None = Field(default=None, description="Email address if found")
    phone: str | None = Field(default=None, description="Phone number if found")
    location: str | None = Field(default=None, description="City/Country if found")
    linkedin: str | None = Field(default=None, description="LinkedIn URL if found")


class SkillItem(BaseModel):
    name: str = Field(description="Skill name, e.g. 'Python', 'Project Management'")
    category: str = Field(description="Category: 'technical', 'soft_skill', 'tool', 'domain', 'language'")
    proficiency: str = Field(description="'beginner', 'intermediate', 'advanced', or 'expert'")
    evidence: str = Field(description="Brief context from the resume demonstrating this skill")


class ExperienceEntry(BaseModel):
    company: str = Field(description="Company or organization name")
    title: str = Field(description="Job title held")
    start_date: str | None = Field(default=None, description="Start date, e.g. 'Jan 2020'")
    end_date: str | None = Field(default=None, description="End date or 'Present'")
    duration_months: int | None = Field(default=None, description="Approximate duration in months")
    impact_summary: str = Field(description="One-sentence distillation of key contribution")
    achievements: list[str] = Field(description="Measurable achievements with numbers where possible")


class EducationEntry(BaseModel):
    institution: str = Field(description="University or school name")
    degree: str = Field(description="Degree type, e.g. 'B.Tech', 'MBA'")
    field: str = Field(description="Field of study")
    year: str | None = Field(default=None, description="Graduation year or date range")


class CandidateProfile(BaseModel):
    """Complete structured profile extracted from a resume (no JD context)."""
    contact: ContactInfo
    professional_summary: str = Field(description="2-3 sentence professional summary synthesized from the resume")
    skills: list[SkillItem] = Field(description="All skills identified in the resume")
    experience: list[ExperienceEntry] = Field(description="Work history, most recent first")
    education: list[EducationEntry] = Field(description="Educational background")
    certifications: list[str] = Field(default_factory=list, description="Certifications or licenses")
    total_years_experience: float = Field(description="Total years of professional experience")
    career_trajectory: str = Field(description="One sentence describing career arc, e.g. 'IC → Team Lead → Engineering Manager'")


# ═══════════════════════════════════════════════════════════════════════════
# 2. JOB REQUIREMENTS — standalone JD extraction
#    Parsed when a JD is added, stored in Supabase, reused for comparisons.
# ═══════════════════════════════════════════════════════════════════════════

class JobRequirements(BaseModel):
    """Structured representation of a job description."""
    role_summary: str = Field(description="2-3 sentence summary of the role")
    required_skills: list[str] = Field(description="Must-have skills for the role")
    preferred_skills: list[str] = Field(description="Nice-to-have skills")
    min_experience_years: float | None = Field(default=None, description="Minimum years of experience required")
    key_responsibilities: list[str] = Field(description="Core responsibilities of the role")
    seniority_level: str = Field(description="'intern', 'junior', 'mid', 'senior', 'lead', 'manager', 'director', 'executive'")


# ═══════════════════════════════════════════════════════════════════════════
# 3. RESUME ANALYSIS — candidate × job comparison
#    Generated when a recruiter runs analysis on a candidate-job pair.
# ═══════════════════════════════════════════════════════════════════════════

class SkillMatch(BaseModel):
    skill: str = Field(description="Skill name from the JD requirements")
    status: str = Field(description="'matched', 'partial', or 'missing'")
    candidate_proficiency: str | None = Field(default=None, description="Candidate's level if matched")
    evidence: str | None = Field(default=None, description="Supporting evidence from resume")


class CredibilityFlag(BaseModel):
    claim: str = Field(description="The specific statement from the resume")
    concern: str = Field(description="Why this needs verification")
    severity: str = Field(description="'low', 'medium', or 'high'")


class GapItem(BaseModel):
    gap_type: str = Field(description="'missing_skill', 'career_break', 'short_tenure', or 'experience_gap'")
    description: str = Field(description="What the gap is")
    severity: str = Field(description="'low', 'medium', or 'high'")
    interview_question: str = Field(description="Suggested question for the recruiter to probe this gap")


class FitScore(BaseModel):
    score: int = Field(ge=0, le=100, description="Overall fit 0-100, semantic not keyword-based")
    summary: str = Field(description="2-3 sentence executive summary of fit")
    top_strengths: list[str] = Field(description="Top 3 reasons this candidate could excel")
    top_concerns: list[str] = Field(description="Top 3 concerns about this candidate")


class ResumeAnalysis(BaseModel):
    """Full candidate × job analysis. The main dashboard payload."""
    fit_score: FitScore
    skill_matches: list[SkillMatch] = Field(description="How each JD skill maps to the candidate")
    missing_skills: list[str] = Field(description="JD skills completely absent from resume")
    experience_relevance: str = Field(description="How relevant their experience is to this role")
    experience_highlights: list[str] = Field(description="Most relevant experience points for this role")
    credibility_flags: list[CredibilityFlag] = Field(description="Claims that seem inflated or need verification")
    credibility_score: int = Field(ge=0, le=100, description="Overall credibility 0-100")
    gaps: list[GapItem] = Field(description="Gaps, mismatches, and concerns")
    overall_recommendation: str = Field(description="'strong_yes', 'yes', 'maybe', 'no', or 'strong_no'")
    recommendation_summary: str = Field(description="2-3 sentence final recommendation for the recruiter")
