"""
Dashboard page — Detailed visualization of analysis results.
"""

import plotly.graph_objects as go
import streamlit as st

from auth import require_auth
from db import get_all_analyses, get_all_candidates, get_all_jobs
from styles import apply_theme, score_color, severity_icon

st.set_page_config(page_title="Dashboard - Resume Scan AI", page_icon="◆", layout="wide")

user = require_auth()
apply_theme(username=user["email"], name=user["full_name"])

st.markdown("# Dashboard")
st.markdown('<p class="page-subtitle">Detailed analysis results and insights</p>', unsafe_allow_html=True)

# ── Data ──────────────────────────────────────────────────────────────────
try:
    analyses = get_all_analyses(org_id=user["org_id"])
    candidates = get_all_candidates(org_id=user["org_id"])
    jobs = get_all_jobs(org_id=user["org_id"])
except Exception as e:
    st.error(f"Could not load data: {e}")
    st.stop()

if not analyses:
    st.markdown(
        '<div class="card" style="text-align:center;padding:3rem">'
        '<div style="color:#71717a">No analyses yet. Go to <b>Analyze</b> to run your first comparison.</div>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.stop()

# ── Select ────────────────────────────────────────────────────────────────
cand_map = {c["id"]: c["name"] for c in candidates}
job_map = {j["id"]: j["title"] + (f" · {j['company']}" if j.get("company") else "") for j in jobs}

options = {}
for a in analyses:
    cn = cand_map.get(a["candidate_id"], "Unknown")
    jn = job_map.get(a["job_id"], "Unknown")
    options[a["id"]] = f"{cn}  →  {jn}  ({a.get('fit_score', '?')})"

selected_id = st.selectbox("Select analysis", list(options.keys()), format_func=lambda x: options[x])

row = next(a for a in analyses if a["id"] == selected_id)
r = row["result"]
fit = r["fit_score"]
score = fit["score"]
sc = score_color(score)

# ═══════════════════════════════════════════════════════════════════════════
# HEADER ROW: Score + Summary + Metrics
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("---")

col_score, col_summary, col_metrics = st.columns([1, 2, 1])

with col_score:
    # Dark-themed gauge
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={"suffix": "", "font": {"size": 42, "color": "#f0f0f2"}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#27272a",
                     "tickfont": {"color": "#71717a"}},
            "bar": {"color": sc, "thickness": 0.75},
            "bgcolor": "#18181b",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 40], "color": "rgba(248,113,113,0.08)"},
                {"range": [40, 60], "color": "rgba(251,191,36,0.08)"},
                {"range": [60, 75], "color": "rgba(96,165,250,0.08)"},
                {"range": [75, 100], "color": "rgba(52,211,153,0.08)"},
            ],
        },
    ))
    fig.update_layout(
        height=220,
        margin=dict(t=30, b=0, l=25, r=25),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#f0f0f2"},
    )
    st.plotly_chart(fig, use_container_width=True)

with col_summary:
    rec = r.get("overall_recommendation", "maybe")
    rec_label = rec.replace("_", " ").title()
    st.markdown(
        f'<span class="rec-badge rec-{rec}">{rec_label}</span>',
        unsafe_allow_html=True,
    )
    st.markdown(f"**{fit['summary']}**")
    st.markdown(
        f'<div style="color:#a1a1aa;font-size:0.9rem;margin-top:0.25rem">'
        f'{r.get("recommendation_summary", "")}</div>',
        unsafe_allow_html=True,
    )

with col_metrics:
    matched = sum(1 for s in r.get("skill_matches", []) if s["status"] == "matched")
    partial = sum(1 for s in r.get("skill_matches", []) if s["status"] == "partial")
    missing_ct = len(r.get("missing_skills", []))
    cred = r.get("credibility_score", 0)

    st.metric("Matched Skills", matched)
    st.metric("Partial", partial)
    st.metric("Missing", missing_ct)
    st.metric("Credibility", f"{cred}")

# Strengths & Concerns
col_s, col_c = st.columns(2)
with col_s:
    st.markdown("#### Strengths")
    for s in fit.get("top_strengths", []):
        st.markdown(f'<div class="accent-bar" style="border-left-color:#34d399">{s}</div>', unsafe_allow_html=True)
with col_c:
    st.markdown("#### Concerns")
    for c in fit.get("top_concerns", []):
        st.markdown(f'<div class="accent-bar" style="border-left-color:#f87171">{c}</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# SKILLS
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown("#### Skills Analysis")

skill_matches = r.get("skill_matches", [])
missing_skills = r.get("missing_skills", [])

if skill_matches:
    matched_skills = [s for s in skill_matches if s["status"] in ("matched", "partial")]
    if len(matched_skills) >= 3:
        prof_map = {"expert": 4, "advanced": 3, "intermediate": 2, "beginner": 1}
        labels = [s["skill"] for s in matched_skills]
        values = [prof_map.get((s.get("candidate_proficiency") or "intermediate").lower(), 2)
                  for s in matched_skills]
        labels_c = labels + [labels[0]]
        values_c = values + [values[0]]

        fig_r = go.Figure()
        fig_r.add_trace(go.Scatterpolar(
            r=values_c, theta=labels_c,
            fill="toself",
            fillcolor="rgba(124,58,237,0.1)",
            line=dict(color="#a78bfa", width=2),
        ))
        fig_r.update_layout(
            polar=dict(
                bgcolor="rgba(0,0,0,0)",
                radialaxis=dict(
                    visible=True, range=[0, 4], showticklabels=False,
                    gridcolor="#27272a",
                ),
                angularaxis=dict(
                    gridcolor="#27272a",
                    tickfont=dict(color="#a1a1aa", size=11),
                ),
            ),
            showlegend=False,
            height=380,
            margin=dict(t=20, b=20, l=60, r=60),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_r, use_container_width=True)

    # Skill columns
    col_m, col_p, col_x = st.columns(3)

    with col_m:
        st.markdown("**Matched**")
        for s in skill_matches:
            if s["status"] == "matched":
                with st.expander(f"{s['skill']}"):
                    st.markdown(f'<span class="pill pill-green">{s.get("candidate_proficiency", "—")}</span>',
                                unsafe_allow_html=True)
                    if s.get("evidence"):
                        st.markdown(f'<div style="color:#a1a1aa;font-size:0.85rem">{s["evidence"]}</div>',
                                    unsafe_allow_html=True)

    with col_p:
        st.markdown("**Partial**")
        for s in skill_matches:
            if s["status"] == "partial":
                with st.expander(f"{s['skill']}"):
                    st.markdown(f'<span class="pill pill-yellow">{s.get("candidate_proficiency", "—")}</span>',
                                unsafe_allow_html=True)
                    if s.get("evidence"):
                        st.markdown(f'<div style="color:#a1a1aa;font-size:0.85rem">{s["evidence"]}</div>',
                                    unsafe_allow_html=True)

    with col_x:
        st.markdown("**Missing**")
        for s in skill_matches:
            if s["status"] == "missing":
                st.markdown(f'<span class="pill pill-red">{s["skill"]}</span>', unsafe_allow_html=True)
        for s in missing_skills:
            st.markdown(f'<span class="pill pill-red">{s}</span>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# EXPERIENCE
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown("#### Experience Relevance")

st.markdown(
    f'<div class="card"><div class="card-body">{r.get("experience_relevance", "")}</div></div>',
    unsafe_allow_html=True,
)

for h in r.get("experience_highlights", []):
    st.markdown(f'<div class="accent-bar">{h}</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# CREDIBILITY
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown("#### Credibility Assessment")

cred_val = r.get("credibility_score", 0)
cred_c = score_color(cred_val)

col_cg, col_cf = st.columns([1, 3])

with col_cg:
    fig_c = go.Figure(go.Indicator(
        mode="gauge+number",
        value=cred_val,
        number={"font": {"size": 30, "color": "#f0f0f2"}},
        gauge={
            "axis": {"range": [0, 100], "tickfont": {"color": "#71717a"}},
            "bar": {"color": cred_c, "thickness": 0.7},
            "bgcolor": "#18181b",
            "borderwidth": 0,
        },
    ))
    fig_c.update_layout(
        height=180,
        margin=dict(t=30, b=0, l=20, r=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_c, use_container_width=True)

with col_cf:
    flags = r.get("credibility_flags", [])
    if flags:
        for f in flags:
            sev = f.get("severity", "low").lower()
            icon = severity_icon(sev)
            st.markdown(
                f'<div class="flag-{sev}">'
                f'<span style="font-weight:600">{icon} {sev.upper()}</span>'
                f'<div style="color:#f0f0f2;margin-top:0.2rem">"{f.get("claim", "")}"</div>'
                f'<div style="color:#71717a;font-size:0.85rem;margin-top:0.15rem">{f.get("concern", "")}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            '<div class="card" style="border-left:3px solid #34d399">'
            '<div style="color:#34d399;font-weight:500">No credibility concerns</div></div>',
            unsafe_allow_html=True,
        )

# ═══════════════════════════════════════════════════════════════════════════
# GAP ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown("#### Gap & Mismatch Analysis")

gaps = r.get("gaps", [])

if gaps:
    col_g, col_q = st.columns(2)

    with col_g:
        st.markdown("**Identified Gaps**")
        for g in gaps:
            sev = g.get("severity", "low").lower()
            gtype = g.get("gap_type", "").replace("_", " ").title()
            icon = severity_icon(sev)
            st.markdown(
                f'<div class="flag-{sev}">'
                f'<span style="font-weight:600;font-size:0.85rem">{icon} {gtype}</span>'
                f'<div style="color:#a1a1aa;font-size:0.88rem;margin-top:0.15rem">{g.get("description", "")}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    with col_q:
        st.markdown("**Interview Questions**")
        for i, g in enumerate(gaps, 1):
            q = g.get("interview_question", "")
            if q:
                st.markdown(
                    f'<div class="accent-bar">'
                    f'<span style="color:#7c3aed;font-weight:600;font-size:0.85rem">{i}.</span> {q}'
                    f'</div>',
                    unsafe_allow_html=True,
                )
else:
    st.markdown(
        '<div class="card" style="border-left:3px solid #34d399;text-align:center;padding:2rem">'
        '<div style="color:#34d399;font-weight:500">No significant gaps identified</div></div>',
        unsafe_allow_html=True,
    )

# ── Footer ────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    '<div style="color:#71717a;font-size:0.8rem;text-align:center">'
    'AI-generated analysis. Use as a complement to — not a substitute for — human judgment.'
    '</div>',
    unsafe_allow_html=True,
)
