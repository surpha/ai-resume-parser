"""
db.py — Supabase database operations.

ARCHITECTURE:
  Thin wrapper around supabase-py providing CRUD for our three entities:
  - candidates: resume data + parsed profile
  - jobs: JD text + parsed requirements
  - analyses: candidate × job evaluation results

  Each function returns plain dicts (from Supabase JSON responses).
  Pydantic conversion happens in the calling layer.
"""

from __future__ import annotations

import os

from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()

_client: Client | None = None


def get_supabase() -> Client:
    """Lazy-initialize and return the Supabase client."""
    global _client
    if _client is None:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        if not url or not key:
            raise ValueError(
                "SUPABASE_URL and SUPABASE_KEY must be set in .env"
            )
        _client = create_client(url, key)
    return _client


# ─── Candidates ──────────────────────────────────────────────────────────

def insert_candidate(name: str, email: str | None, phone: str | None,
                     raw_text: str, parsed_profile: dict) -> dict:
    sb = get_supabase()
    data = {
        "name": name,
        "email": email,
        "phone": phone,
        "raw_text": raw_text,
        "parsed_profile": parsed_profile,
    }
    return sb.table("candidates").insert(data).execute().data[0]


def get_all_candidates() -> list[dict]:
    sb = get_supabase()
    return sb.table("candidates").select("*").order("created_at", desc=True).execute().data


def get_candidate(candidate_id: str) -> dict | None:
    sb = get_supabase()
    result = sb.table("candidates").select("*").eq("id", candidate_id).execute().data
    return result[0] if result else None


def delete_candidate(candidate_id: str) -> None:
    sb = get_supabase()
    sb.table("candidates").delete().eq("id", candidate_id).execute()


# ─── Jobs ────────────────────────────────────────────────────────────────

def insert_job(title: str, company: str | None, description: str,
               parsed_requirements: dict) -> dict:
    sb = get_supabase()
    data = {
        "title": title,
        "company": company,
        "description": description,
        "parsed_requirements": parsed_requirements,
    }
    return sb.table("jobs").insert(data).execute().data[0]


def get_all_jobs() -> list[dict]:
    sb = get_supabase()
    return sb.table("jobs").select("*").order("created_at", desc=True).execute().data


def get_job(job_id: str) -> dict | None:
    sb = get_supabase()
    result = sb.table("jobs").select("*").eq("id", job_id).execute().data
    return result[0] if result else None


def delete_job(job_id: str) -> None:
    sb = get_supabase()
    sb.table("jobs").delete().eq("id", job_id).execute()


# ─── Analyses ────────────────────────────────────────────────────────────

def insert_analysis(candidate_id: str, job_id: str,
                    result: dict, fit_score: int) -> dict:
    sb = get_supabase()
    data = {
        "candidate_id": candidate_id,
        "job_id": job_id,
        "result": result,
        "fit_score": fit_score,
    }
    return sb.table("analyses").insert(data).execute().data[0]


def get_all_analyses() -> list[dict]:
    sb = get_supabase()
    return sb.table("analyses").select("*").order("created_at", desc=True).execute().data


def get_analysis(analysis_id: str) -> dict | None:
    sb = get_supabase()
    result = sb.table("analyses").select("*").eq("id", analysis_id).execute().data
    return result[0] if result else None


def get_analyses_for_candidate(candidate_id: str) -> list[dict]:
    sb = get_supabase()
    return sb.table("analyses").select("*").eq("candidate_id", candidate_id).order("created_at", desc=True).execute().data


def get_analyses_for_job(job_id: str) -> list[dict]:
    sb = get_supabase()
    return sb.table("analyses").select("*").eq("job_id", job_id).order("fit_score", desc=True).execute().data


def delete_analysis(analysis_id: str) -> None:
    sb = get_supabase()
    sb.table("analyses").delete().eq("id", analysis_id).execute()
