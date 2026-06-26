"""
Candidates page — Central candidate repository with browsable profiles.
"""

import streamlit as st

from auth import require_auth
from db import delete_candidate, get_all_candidates, insert_candidate
from parser import parse_resume
from styles import apply_theme
from utils import extract_text_from_pdf, fetch_pdf_from_url

st.set_page_config(page_title="Candidates - Resume Scan AI", page_icon="◆", layout="wide")

user = require_auth()
apply_theme(username=user["email"], name=user["full_name"])

st.markdown("# Candidates")
st.markdown('<p class="page-subtitle">Upload, browse, and explore candidate profiles</p>',
            unsafe_allow_html=True)

# ── Upload section ────────────────────────────────────────────────────────
with st.expander("Add New Candidate", expanded=not bool(st.session_state.get("_cands_loaded"))):
    tab_upload, tab_url = st.tabs(["Upload PDF", "Import from URL"])

    raw_text = None

    with tab_upload:
        uploaded_file = st.file_uploader(
            "Resume PDF", type=["pdf"],
            help="Text-based PDFs only.", label_visibility="collapsed",
        )
        if uploaded_file and st.button("Parse Resume", key="btn_upload", use_container_width=True, type="primary"):
            with st.spinner("Extracting text..."):
                try:
                    raw_text = extract_text_from_pdf(uploaded_file)
                except ValueError as e:
                    st.error(str(e))

    with tab_url:
        st.markdown(
            '<div style="color:#a1a1aa;font-size:0.85rem;margin-bottom:0.5rem">'
            'Supports Google Drive, Dropbox, or any direct PDF link.</div>',
            unsafe_allow_html=True,
        )
        pdf_url = st.text_input("PDF URL", placeholder="https://drive.google.com/file/d/...",
                                label_visibility="collapsed")
        if pdf_url and st.button("Fetch & Parse", key="btn_url", use_container_width=True, type="primary"):
            with st.spinner("Downloading PDF..."):
                try:
                    raw_text = fetch_pdf_from_url(pdf_url.strip())
                except Exception as e:
                    st.error(f"Could not fetch PDF: {e}")

    if raw_text:
        with st.status("Parsing with AI...", expanded=True) as status:
            st.write(f"Extracted {len(raw_text):,} characters")
            st.write("Running structured extraction via LLM...")
            try:
                profile = parse_resume(raw_text)
                st.write(f"Identified: **{profile.contact.name}**")
                insert_candidate(
                    name=profile.contact.name,
                    email=profile.contact.email,
                    phone=profile.contact.phone,
                    raw_text=raw_text,
                    parsed_profile=profile.model_dump(),
                    org_id=user["org_id"],
                )
                status.update(label=f"Added: {profile.contact.name}", state="complete")
                st.rerun()
            except Exception as e:
                status.update(label="Failed", state="error")
                st.error(str(e))

# ── Load candidates ──────────────────────────────────────────────────────
st.markdown("---")

try:
    candidates = get_all_candidates(org_id=user["org_id"])
    st.session_state["_cands_loaded"] = True
except Exception as e:
    st.error(f"Could not load candidates: {e}")
    candidates = []

if not candidates:
    st.markdown(
        '<div class="card" style="text-align:center;padding:3rem">'
        '<div style="color:#71717a">No candidates yet. Upload a resume above.</div></div>',
        unsafe_allow_html=True,
    )
    st.stop()

# ── Candidate count + search ─────────────────────────────────────────────
col_count, col_search = st.columns([1, 2])
with col_count:
    st.markdown(
        f'<div style="color:#71717a;font-size:0.85rem;padding-top:0.5rem">'
        f'{len(candidates)} candidate{"s" if len(candidates) != 1 else ""}</div>',
        unsafe_allow_html=True,
    )
with col_search:
    search = st.text_input("Search", placeholder="Filter by name or skill...",
                           label_visibility="collapsed")

# Filter
if search:
    search_lower = search.lower()
    filtered = []
    for c in candidates:
        if search_lower in c["name"].lower():
            filtered.append(c)
            continue
        p = c.get("parsed_profile", {})
        skills = p.get("skills", [])
        if any(search_lower in s.get("name", "").lower() for s in skills):
            filtered.append(c)
    candidates = filtered

# ── Candidate list ────────────────────────────────────────────────────────
# Track which candidate is expanded
if "selected_candidate" not in st.session_state:
    st.session_state["selected_candidate"] = None

for cand in candidates:
    profile = cand.get("parsed_profile", {})
    contact = profile.get("contact", {}) if profile else {}
    name = contact.get("name", cand["name"]) if contact else cand["name"]

    # Summary line
    details = []
    if contact.get("email"):
        details.append(contact["email"])
    if contact.get("location"):
        details.append(contact["location"])
    details_str = " · ".join(details)

    yrs = profile.get("total_years_experience", "?") if profile else "?"
    n_skills = len(profile.get("skills", [])) if profile else 0
    n_roles = len(profile.get("experience", [])) if profile else 0

    # Card row
    col_info, col_stats, col_actions = st.columns([5, 3, 1])

    with col_info:
        st.markdown(
            f'<div style="font-weight:600;color:#f0f0f2;font-size:1.05rem">{name}</div>'
            f'<div style="color:#71717a;font-size:0.8rem">{details_str}</div>',
            unsafe_allow_html=True,
        )

    with col_stats:
        st.markdown(
            f'<div style="display:flex;gap:1.5rem;padding-top:0.2rem">'
            f'<div><span style="color:#7c3aed;font-weight:600">{yrs}</span>'
            f'<span style="color:#71717a;font-size:0.75rem"> yrs</span></div>'
            f'<div><span style="color:#7c3aed;font-weight:600">{n_skills}</span>'
            f'<span style="color:#71717a;font-size:0.75rem"> skills</span></div>'
            f'<div><span style="color:#7c3aed;font-weight:600">{n_roles}</span>'
            f'<span style="color:#71717a;font-size:0.75rem"> roles</span></div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    with col_actions:
        bcol1, bcol2 = st.columns(2)
        with bcol1:
            if st.button("⤢", key=f"view_{cand['id']}", help="View profile"):
                if st.session_state["selected_candidate"] == cand["id"]:
                    st.session_state["selected_candidate"] = None
                else:
                    st.session_state["selected_candidate"] = cand["id"]
                st.rerun()
        with bcol2:
            if st.button("✕", key=f"del_{cand['id']}", help="Delete"):
                delete_candidate(cand["id"])
                st.session_state["selected_candidate"] = None
                st.rerun()

    # ── Expanded profile ──────────────────────────────────────────────────
    if st.session_state["selected_candidate"] == cand["id"] and profile:
        # Summary
        summary = profile.get("professional_summary", "")
        trajectory = profile.get("career_trajectory", "")

        st.markdown(
            f'<div class="card" style="border-left:3px solid #7c3aed;margin-top:0.25rem">'
            f'<div style="color:#a1a1aa;font-size:0.9rem;line-height:1.6">{summary}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        if trajectory:
            st.markdown(
                f'<div class="accent-bar" style="margin-bottom:0.75rem">'
                f'<span style="color:#71717a;font-size:0.8rem">TRAJECTORY</span><br>'
                f'<span style="color:#f0f0f2;font-size:0.9rem">{trajectory}</span></div>',
                unsafe_allow_html=True,
            )

        # Quick stats
        mc1, mc2, mc3, mc4 = st.columns(4)
        with mc1:
            st.metric("Experience", f"{profile.get('total_years_experience', '?')} yrs")
        with mc2:
            st.metric("Skills", str(n_skills))
        with mc3:
            st.metric("Roles", str(n_roles))
        with mc4:
            st.metric("Certifications", str(len(profile.get("certifications", []))))

        # Tabs
        tab_skills, tab_exp, tab_edu = st.tabs(["Skills", "Experience", "Education"])

        with tab_skills:
            skills = profile.get("skills", [])
            if skills:
                categories: dict[str, list] = {}
                for s in skills:
                    cat = s.get("category", "other").replace("_", " ").title()
                    categories.setdefault(cat, []).append(s)

                for cat_name, cat_skills in categories.items():
                    chips = ""
                    for s in cat_skills:
                        prof = s.get("proficiency", "intermediate").lower()
                        cls = {"expert": "pill-green", "advanced": "pill-blue",
                               "intermediate": "pill-yellow", "beginner": "pill-red"}.get(prof, "pill-muted")
                        chips += f'<span class="pill {cls}">{s["name"]}</span> '
                    st.markdown(f"**{cat_name}**")
                    st.markdown(chips, unsafe_allow_html=True)

        with tab_exp:
            for exp in profile.get("experience", []):
                dates = ""
                if exp.get("start_date"):
                    dates = exp["start_date"]
                    if exp.get("end_date"):
                        dates += f" – {exp['end_date']}"
                dur = f" · {exp['duration_months']}mo" if exp.get("duration_months") else ""

                st.markdown(
                    f'<div class="accent-bar">'
                    f'<div style="font-weight:600;color:#f0f0f2">{exp.get("title", "")}</div>'
                    f'<div style="color:#71717a;font-size:0.82rem">'
                    f'{exp.get("company", "")} · {dates}{dur}</div>'
                    f'<div style="color:#a1a1aa;font-size:0.88rem;margin-top:0.2rem">'
                    f'{exp.get("impact_summary", "")}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
                for a in exp.get("achievements", []):
                    st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;→ {a}")

        with tab_edu:
            for edu in profile.get("education", []):
                year = f" ({edu.get('year', '')})" if edu.get("year") else ""
                st.markdown(
                    f"**{edu.get('degree', '')}** in {edu.get('field', '')} "
                    f"— {edu.get('institution', '')}{year}"
                )
            certs = profile.get("certifications", [])
            if certs:
                st.markdown("**Certifications**")
                for c in certs:
                    st.markdown(f"- {c}")

    st.markdown("---")
