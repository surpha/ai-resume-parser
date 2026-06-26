"""
app.py — Home / Overview page.
"""

import streamlit as st

from auth import require_auth, sign_out
from db import get_all_analyses, get_all_candidates, get_all_jobs
from styles import apply_theme, score_color

st.set_page_config(
    page_title="Resume Scan AI",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)

user = require_auth()
apply_theme(username=user["email"], name=user["full_name"])

# ── Sidebar: org info + sign out ──────────────────────────────────────────
with st.sidebar:
    st.markdown(
        f'<div style="padding:0.5rem 0;margin-bottom:0.5rem">'
        f'<div style="font-size:0.68rem;text-transform:uppercase;letter-spacing:0.06em;'
        f'color:#52525b;font-weight:500">Organization</div>'
        f'<div style="font-size:0.88rem;color:#f0f0f2;font-weight:600;margin-top:0.1rem">'
        f'{user["org_name"]}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    if user.get("invite_code") and user["role"] in ("company_admin", "platform_admin"):
        st.markdown(
            f'<div style="background:#18181b;border:1px solid #27272a;border-radius:8px;'
            f'padding:0.5rem 0.75rem;margin-bottom:1rem">'
            f'<div style="font-size:0.65rem;color:#52525b;text-transform:uppercase;'
            f'letter-spacing:0.04em">Invite Code</div>'
            f'<div style="font-size:0.85rem;color:#a78bfa;font-weight:600;font-family:monospace">'
            f'{user["invite_code"]}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    if st.button("Sign out", key="signout"):
        sign_out()

# ── Page content ──────────────────────────────────────────────────────────
st.markdown("# Overview")
st.markdown('<p class="page-subtitle">Your hiring pipeline at a glance</p>', unsafe_allow_html=True)

# ── Stats ─────────────────────────────────────────────────────────────────
org_id = user["org_id"]
try:
    candidates = get_all_candidates(org_id=org_id)
    jobs = get_all_jobs(org_id=org_id)
    analyses = get_all_analyses(org_id=org_id)
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

# ── Getting Started ───────────────────────────────────────────────────────
st.markdown("---")
st.markdown("#### Getting Started")

steps = [
    ("01", "Add Roles", "Navigate to **Jobs** and paste a job description. The AI extracts skills, seniority, and responsibilities."),
    ("02", "Upload Resumes", "Navigate to **Candidates** and upload a PDF or paste a cloud URL. The AI builds a structured profile."),
    ("03", "Run Analysis", "Navigate to **Analyze**, select a candidate and a role, then run the semantic comparison."),
    ("04", "View Results", "Navigate to **Dashboard** to explore fit scores, skill maps, credibility flags, and gaps."),
]

cols = st.columns(4)
for col, (num, title, desc) in zip(cols, steps):
    with col:
        st.markdown(
            f'<div class="card" style="min-height:150px">'
            f'<div style="color:#7c3aed;font-size:0.7rem;font-weight:700;letter-spacing:0.05em;margin-bottom:0.5rem">'
            f'STEP {num}</div>'
            f'<div class="card-header">{title}</div>'
            f'<div class="card-body">{desc}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

# ── Recent analyses ───────────────────────────────────────────────────────
if analyses:
    st.markdown("---")
    st.markdown("#### Recent Analyses")

    cand_map = {c["id"]: c["name"] for c in candidates}
    job_map = {j["id"]: j["title"] for j in jobs}

    for a in analyses[:8]:
        cname = cand_map.get(a["candidate_id"], "Unknown")
        jname = job_map.get(a["job_id"], "Unknown")
        score = a.get("fit_score", 0)
        sc = score_color(score) if isinstance(score, int) else "#71717a"

        st.markdown(
            f'<div class="accent-bar">'
            f'<span style="color:{sc};font-weight:700;font-size:1.05rem">{score}</span>'
            f'<span style="color:#3f3f46;margin:0 0.6rem">|</span>'
            f'<span style="color:#f0f0f2;font-weight:500">{cname}</span>'
            f'<span style="color:#52525b;margin:0 0.4rem">&rarr;</span>'
            f'<span style="color:#a1a1aa">{jname}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
