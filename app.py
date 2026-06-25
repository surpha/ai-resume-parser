"""
app.py — Home page. Shows overview stats and recent activity.
"""

import streamlit as st

from db import get_all_analyses, get_all_candidates, get_all_jobs
from styles import apply_theme, score_color

st.set_page_config(
    page_title="ResumeAI",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_theme()

# ── Header ────────────────────────────────────────────────────────────────
st.markdown(
    '<h1 style="font-size:2rem;margin-bottom:0">Overview</h1>',
    unsafe_allow_html=True,
)
st.markdown('<p class="page-subtitle">Your hiring pipeline at a glance</p>', unsafe_allow_html=True)

# ── Stats ─────────────────────────────────────────────────────────────────
try:
    candidates = get_all_candidates()
    jobs = get_all_jobs()
    analyses = get_all_analyses()
except Exception:
    candidates, jobs, analyses = [], [], []

col1, col2, col3, col4 = st.columns(4)

for col, value, label in [
    (col1, len(candidates), "Candidates"),
    (col2, len(jobs), "Open Roles"),
    (col3, len(analyses), "Analyses"),
    (col4, f"{round(sum(a.get('fit_score', 0) for a in analyses) / max(len(analyses), 1))}%" if analyses else "—", "Avg Fit"),
]:
    with col:
        st.markdown(
            f'<div class="stat-card">'
            f'<div class="stat-value">{value}</div>'
            f'<div class="stat-label">{label}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

# ── Workflow steps ────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("#### Getting Started")

steps = [
    ("01", "Add Roles", "Go to **Jobs** and paste a job description. The AI extracts required skills, seniority, and responsibilities."),
    ("02", "Upload Resumes", "Go to **Candidates** and upload a PDF (or paste a cloud URL). The AI builds a structured profile."),
    ("03", "Run Analysis", "Go to **Analyze**, pick a candidate and a job, and run the semantic comparison."),
    ("04", "View Results", "Go to **Dashboard** to see fit scores, skill maps, credibility flags, and gap analysis."),
]

cols = st.columns(4)
for col, (num, title, desc) in zip(cols, steps):
    with col:
        st.markdown(
            f'<div class="card" style="min-height:160px">'
            f'<div style="color:#a78bfa;font-size:0.75rem;font-weight:700;margin-bottom:0.5rem">{num}</div>'
            f'<div class="card-header">{title}</div>'
            f'<div class="card-body">{desc}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

# ── Recent analyses ──────────────────────────────────────────────────────
if analyses:
    st.markdown("---")
    st.markdown("#### Recent Analyses")

    cand_map = {c["id"]: c["name"] for c in candidates}
    job_map = {j["id"]: j["title"] for j in jobs}

    for a in analyses[:8]:
        cname = cand_map.get(a["candidate_id"], "Unknown")
        jname = job_map.get(a["job_id"], "Unknown")
        score = a.get("fit_score", 0)
        sc = score_color(score) if isinstance(score, int) else "#6b7280"

        st.markdown(
            f'<div class="accent-bar">'
            f'<span style="color:{sc};font-weight:700;font-size:1.1rem">{score}</span>'
            f'<span style="color:#6b7280;margin:0 0.5rem">|</span>'
            f'<span style="color:#e2e2e5;font-weight:500">{cname}</span>'
            f'<span style="color:#6b7280;margin:0 0.4rem">→</span>'
            f'<span style="color:#9ca3af">{jname}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
