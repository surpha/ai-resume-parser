"""
Analyze page — Run semantic comparison between candidate and role.
"""

import streamlit as st

from auth import require_auth
from db import (
    get_all_candidates,
    get_all_jobs,
    get_candidate,
    get_job,
    insert_analysis,
)
from parser import analyze
from styles import apply_theme, score_color

st.set_page_config(page_title="Analyze - Resume Scan AI", page_icon="◆", layout="wide")

user = require_auth()
apply_theme(username=user["email"], name=user["full_name"])

st.markdown("# Analyze")
st.markdown('<p class="page-subtitle">Run a semantic comparison between a candidate and a role</p>', unsafe_allow_html=True)

# ── Load data ─────────────────────────────────────────────────────────────
try:
    candidates = get_all_candidates(org_id=user["org_id"])
    jobs = get_all_jobs(org_id=user["org_id"])
except Exception as e:
    st.error(f"Could not load data: {e}")
    st.stop()

if not candidates:
    st.markdown(
        '<div class="card" style="text-align:center;padding:2rem">'
        '<div style="color:#71717a">No candidates found. Go to <b>Candidates</b> to upload a resume first.</div>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.stop()

if not jobs:
    st.markdown(
        '<div class="card" style="text-align:center;padding:2rem">'
        '<div style="color:#71717a">No jobs found. Go to <b>Jobs</b> to add a role first.</div>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.stop()

# ── Selection ─────────────────────────────────────────────────────────────
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Candidate")
    cand_options = {c["id"]: c["name"] for c in candidates}
    selected_cand_id = st.selectbox(
        "Candidate",
        options=list(cand_options.keys()),
        format_func=lambda x: cand_options[x],
        label_visibility="collapsed",
    )

    sel_cand = next((c for c in candidates if c["id"] == selected_cand_id), None)
    if sel_cand and sel_cand.get("parsed_profile"):
        p = sel_cand["parsed_profile"]
        st.markdown(
            f'<div class="card">'
            f'<div style="font-weight:600;color:#f0f0f2">{p.get("contact", {}).get("name", sel_cand["name"])}</div>'
            f'<div style="color:#71717a;font-size:0.85rem">'
            f'{p.get("total_years_experience", "?")} yrs · {len(p.get("skills", []))} skills</div>'
            f'<div style="color:#a1a1aa;font-size:0.85rem;margin-top:0.25rem">'
            f'{p.get("career_trajectory", "")}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

with col2:
    st.markdown("#### Role")
    job_options = {
        j["id"]: j["title"] + (f" · {j['company']}" if j.get("company") else "")
        for j in jobs
    }
    selected_job_id = st.selectbox(
        "Job",
        options=list(job_options.keys()),
        format_func=lambda x: job_options[x],
        label_visibility="collapsed",
    )

    sel_job = next((j for j in jobs if j["id"] == selected_job_id), None)
    if sel_job and sel_job.get("parsed_requirements"):
        req = sel_job["parsed_requirements"]
        skills_pills = " ".join(
            f'<span class="pill pill-purple">{s}</span>' for s in req.get("required_skills", [])[:6]
        )
        st.markdown(
            f'<div class="card">'
            f'<div style="font-weight:600;color:#f0f0f2">{sel_job["title"]}</div>'
            f'<div style="color:#71717a;font-size:0.85rem">'
            f'{req.get("seniority_level", "?").title()} · '
            f'{len(req.get("required_skills", []))} required skills</div>'
            f'<div style="margin-top:0.4rem">{skills_pills}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

# ── Run ───────────────────────────────────────────────────────────────────
st.markdown("---")

if st.button("Run Analysis", use_container_width=True, type="primary"):
    cand_data = get_candidate(selected_cand_id)
    job_data = get_job(selected_job_id)

    if not cand_data or not job_data:
        st.error("Could not load candidate or job data.")
        st.stop()

    with st.status("Running semantic analysis...", expanded=True) as status:
        st.write(f"Candidate: **{cand_data['name']}**")
        st.write(f"Role: **{job_data['title']}**")
        st.write("Sending to LLM...")

        try:
            result = analyze(
                resume_text=cand_data["raw_text"],
                job_description=job_data["description"],
            )
        except Exception as e:
            status.update(label="Failed", state="error")
            st.error(str(e))
            st.stop()

        st.write("Saving results...")
        try:
            insert_analysis(
                candidate_id=selected_cand_id,
                job_id=selected_job_id,
                result=result.model_dump(),
                fit_score=result.fit_score.score,
                org_id=user["org_id"],
            )
            status.update(label="Complete", state="complete")
        except Exception as e:
            status.update(label="Save failed", state="error")
            st.error(str(e))
            st.stop()

    # Quick result
    score = result.fit_score.score
    sc = score_color(score)
    rec = result.overall_recommendation.replace("_", " ").title()

    st.markdown(
        f'<div class="card" style="border-left:3px solid {sc};margin-top:1rem">'
        f'<div style="display:flex;align-items:baseline;gap:1rem">'
        f'<span style="font-size:2rem;font-weight:700;color:{sc}">{score}</span>'
        f'<span class="rec-badge rec-{result.overall_recommendation}">{rec}</span>'
        f'</div>'
        f'<div style="color:#a1a1aa;margin-top:0.5rem">{result.fit_score.summary}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div style="color:#71717a;font-size:0.85rem;margin-top:0.5rem">'
        'Go to <b>Dashboard</b> for the full detailed breakdown.</div>',
        unsafe_allow_html=True,
    )
