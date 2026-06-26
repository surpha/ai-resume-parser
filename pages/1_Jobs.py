"""
Jobs page — Add, view, and manage job descriptions.
"""

import streamlit as st

from auth import require_auth
from db import delete_job, get_all_jobs, insert_job
from parser import parse_job
from styles import apply_theme

st.set_page_config(page_title="Jobs - Resume Scan AI", page_icon="◆", layout="wide")

user = require_auth()
apply_theme(username=user["email"], name=user["full_name"])

st.markdown("# Jobs")
st.markdown('<p class="page-subtitle">Manage the roles you are hiring for</p>', unsafe_allow_html=True)

# ── Add new job ───────────────────────────────────────────────────────────
with st.expander("Add New Job", expanded=not bool(st.session_state.get("_jobs_loaded"))):
    with st.form("add_job_form"):
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Job Title", placeholder="Senior Backend Engineer")
        with col2:
            company = st.text_input("Company", placeholder="Acme Inc.")

        description = st.text_area(
            "Job Description",
            height=250,
            placeholder="Paste the complete job description here — responsibilities, requirements, qualifications...",
        )
        submitted = st.form_submit_button("Parse & Save", use_container_width=True, type="primary")

    if submitted:
        if not title.strip() or not description.strip():
            st.error("Title and description are required.")
        else:
            with st.status("Parsing job description...", expanded=True) as status:
                st.write("Sending to LLM for structured extraction...")
                try:
                    parsed = parse_job(description)
                    st.write("Saving to database...")
                    insert_job(
                        title=title.strip(),
                        company=company.strip() or None,
                        description=description.strip(),
                        parsed_requirements=parsed.model_dump(),
                        org_id=user["org_id"],
                    )
                    status.update(label="Job added", state="complete")
                    st.rerun()
                except Exception as e:
                    status.update(label="Failed", state="error")
                    st.error(str(e))

# ── List jobs ─────────────────────────────────────────────────────────────
st.markdown("---")

try:
    jobs = get_all_jobs(org_id=user["org_id"])
    st.session_state["_jobs_loaded"] = True
except Exception as e:
    st.error(f"Could not load jobs: {e}")
    jobs = []

if not jobs:
    st.markdown(
        '<div class="card" style="text-align:center;padding:3rem">'
        '<div style="color:#71717a;font-size:0.95rem">No jobs yet. Add your first role above.</div>'
        '</div>',
        unsafe_allow_html=True,
    )
else:
    for job in jobs:
        parsed = job.get("parsed_requirements", {})
        company_str = f" · {job['company']}" if job.get("company") else ""

        with st.container():
            col_main, col_del = st.columns([12, 1])

            with col_main:
                # Header
                seniority = parsed.get("seniority_level", "")
                badge = ""
                if seniority:
                    badge = f' <span class="pill pill-purple">{seniority.upper()}</span>'
                st.markdown(
                    f'<div class="card-header" style="font-size:1.15rem">'
                    f'{job["title"]}<span style="color:#71717a;font-weight:400">{company_str}</span>'
                    f'{badge}</div>',
                    unsafe_allow_html=True,
                )

                if parsed:
                    st.markdown(
                        f'<div style="color:#a1a1aa;font-size:0.9rem;margin-bottom:0.75rem">'
                        f'{parsed.get("role_summary", "")}</div>',
                        unsafe_allow_html=True,
                    )

                    # Skills pills
                    req = parsed.get("required_skills", [])
                    pref = parsed.get("preferred_skills", [])

                    pills_html = ""
                    for s in req:
                        pills_html += f'<span class="pill pill-purple">{s}</span> '
                    for s in pref:
                        pills_html += f'<span class="pill pill-muted">{s}</span> '
                    if pills_html:
                        st.markdown(pills_html, unsafe_allow_html=True)

                    min_exp = parsed.get("min_experience_years")
                    if min_exp:
                        st.caption(f"Min. {min_exp} years experience")

                    with st.expander("Responsibilities"):
                        for r in parsed.get("key_responsibilities", []):
                            st.markdown(f"- {r}")
                else:
                    st.caption("Not yet parsed")

            with col_del:
                if st.button("✕", key=f"del_job_{job['id']}", help="Delete"):
                    delete_job(job["id"])
                    st.rerun()

            st.markdown("---")
