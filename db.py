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

import streamlit as st
from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()

_client: Client | None = None


def _get_env(key: str) -> str | None:
    """Get env var from os.environ or st.secrets (Streamlit Cloud)."""
    val = os.getenv(key)
    if val:
        return val
    try:
        return st.secrets.get(key)
    except Exception:
        return None


def get_supabase() -> Client:
    """Lazy-initialize and return the Supabase client (service role bypasses RLS)."""
    global _client
    if _client is None:
        url = _get_env("SUPABASE_URL")
        key = _get_env("SUPABASE_SERVICE_KEY") or _get_env("SUPABASE_KEY")
        if not url or not key:
            raise ValueError(
                "SUPABASE_URL and SUPABASE_KEY must be set in .env or st.secrets"
            )
        _client = create_client(url, key)
    return _client


def reset_client():
    """Force re-creation of the Supabase client (e.g. after config change)."""
    global _client
    _client = None


# ─── Candidates ──────────────────────────────────────────────────────────

def insert_candidate(name: str, email: str | None, phone: str | None,
                     raw_text: str, parsed_profile: dict,
                     org_id: str | None = None) -> dict:
    sb = get_supabase()
    data = {
        "name": name,
        "email": email,
        "phone": phone,
        "raw_text": raw_text,
        "parsed_profile": parsed_profile,
        "org_id": org_id,
    }
    return sb.table("candidates").insert(data).execute().data[0]


def get_all_candidates(org_id: str | None = None) -> list[dict]:
    sb = get_supabase()
    q = sb.table("candidates").select("*")
    if org_id:
        q = q.eq("org_id", org_id)
    return q.order("created_at", desc=True).execute().data


def get_candidate(candidate_id: str) -> dict | None:
    sb = get_supabase()
    result = sb.table("candidates").select("*").eq("id", candidate_id).execute().data
    return result[0] if result else None


def delete_candidate(candidate_id: str) -> None:
    sb = get_supabase()
    sb.table("candidates").delete().eq("id", candidate_id).execute()


# ─── Jobs ────────────────────────────────────────────────────────────────

def insert_job(title: str, company: str | None, description: str,
               parsed_requirements: dict, org_id: str | None = None) -> dict:
    sb = get_supabase()
    data = {
        "title": title,
        "company": company,
        "description": description,
        "parsed_requirements": parsed_requirements,
        "org_id": org_id,
    }
    return sb.table("jobs").insert(data).execute().data[0]


def get_all_jobs(org_id: str | None = None) -> list[dict]:
    sb = get_supabase()
    q = sb.table("jobs").select("*")
    if org_id:
        q = q.eq("org_id", org_id)
    return q.order("created_at", desc=True).execute().data


def get_job(job_id: str) -> dict | None:
    sb = get_supabase()
    result = sb.table("jobs").select("*").eq("id", job_id).execute().data
    return result[0] if result else None


def delete_job(job_id: str) -> None:
    sb = get_supabase()
    sb.table("jobs").delete().eq("id", job_id).execute()


# ─── Analyses ────────────────────────────────────────────────────────────

def insert_analysis(candidate_id: str, job_id: str,
                    result: dict, fit_score: int,
                    org_id: str | None = None) -> dict:
    sb = get_supabase()
    data = {
        "candidate_id": candidate_id,
        "job_id": job_id,
        "result": result,
        "fit_score": fit_score,
        "org_id": org_id,
    }
    return sb.table("analyses").insert(data).execute().data[0]


def get_all_analyses(org_id: str | None = None) -> list[dict]:
    sb = get_supabase()
    q = sb.table("analyses").select("*")
    if org_id:
        q = q.eq("org_id", org_id)
    return q.order("created_at", desc=True).execute().data


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
