"""
Settings page — Organization management, team members, invite codes.
Only visible to company_admin and platform_admin roles.
"""

import streamlit as st

from auth import require_auth, sign_out
from db import get_supabase
from styles import apply_theme

st.set_page_config(page_title="Settings - Resume Scan AI", page_icon="◆", layout="wide")

user = require_auth()
apply_theme(username=user["email"], name=user["full_name"])

st.markdown("# Settings")
st.markdown('<p class="page-subtitle">Organization and team management</p>', unsafe_allow_html=True)

sb = get_supabase()

# ── Organization Info ─────────────────────────────────────────────────────
st.markdown("#### Organization")

org = sb.table("organizations").select("*").eq("id", user["org_id"]).execute().data
if org:
    org = org[0]
    status_color = {"active": "#4ade80", "pending": "#facc15", "suspended": "#f87171"}.get(org["status"], "#71717a")

    st.markdown(
        f'<div class="card">'
        f'<div style="display:flex;justify-content:space-between;align-items:center">'
        f'<div>'
        f'<div class="card-header">{org["name"]}</div>'
        f'<div class="card-body">Invite code: <code style="color:#a78bfa;background:#27272a;'
        f'padding:0.15rem 0.5rem;border-radius:4px;font-size:0.82rem">{org["invite_code"]}</code></div>'
        f'</div>'
        f'<div><span class="pill pill-{"green" if org["status"] == "active" else "yellow"}">'
        f'{org["status"].upper()}</span></div>'
        f'</div></div>',
        unsafe_allow_html=True,
    )

    if org["status"] == "pending":
        st.info("Your organization is pending platform approval. Members cannot access data until approved.")

# ── Team Members ──────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("#### Team Members")

if user["role"] not in ("company_admin", "platform_admin"):
    st.markdown(
        '<div style="color:#71717a;font-size:0.85rem">'
        'Only organization admins can manage team members.</div>',
        unsafe_allow_html=True,
    )
else:
    members = sb.table("profiles").select("*").eq("org_id", user["org_id"]).order("created_at").execute().data

    if members:
        for member in members:
            role = member["role"]
            role_colors = {
                "company_admin": "pill-purple",
                "member": "pill-green",
                "pending_member": "pill-yellow",
                "platform_admin": "pill-blue",
            }
            pill_cls = role_colors.get(role, "pill-muted")
            role_label = role.replace("_", " ").title()

            col_info, col_role, col_action = st.columns([5, 2, 2])

            with col_info:
                st.markdown(
                    f'<div style="font-weight:500;color:#f0f0f2;font-size:0.9rem">{member["full_name"]}</div>'
                    f'<div style="color:#71717a;font-size:0.78rem">{member["email"]}</div>',
                    unsafe_allow_html=True,
                )

            with col_role:
                st.markdown(
                    f'<div style="padding-top:0.3rem"><span class="pill {pill_cls}">{role_label}</span></div>',
                    unsafe_allow_html=True,
                )

            with col_action:
                if role == "pending_member" and member["id"] != user["id"]:
                    if st.button("Approve", key=f"approve_{member['id']}", type="primary"):
                        sb.table("profiles").update({"role": "member"}).eq("id", member["id"]).execute()
                        st.rerun()

            st.markdown('<div style="border-bottom:1px solid #27272a;margin:0.5rem 0"></div>', unsafe_allow_html=True)

    # Share invite code
    st.markdown("---")
    st.markdown("#### Invite Team Members")
    st.markdown(
        f'<div class="card">'
        f'<div class="card-body">Share this invite code with your team. '
        f'They\'ll sign up and request to join — you approve them above.</div>'
        f'<div style="margin-top:0.75rem;font-size:1.2rem;font-weight:700;color:#a78bfa;'
        f'font-family:monospace;letter-spacing:0.1em">{user["invite_code"]}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

# ── Platform Admin: Org Approval ──────────────────────────────────────────
if user["role"] == "platform_admin":
    st.markdown("---")
    st.markdown("#### Platform Admin — Pending Organizations")

    pending_orgs = sb.table("organizations").select("*").eq("status", "pending").order("created_at").execute().data

    if not pending_orgs:
        st.markdown('<div style="color:#71717a;font-size:0.85rem">No pending organizations.</div>',
                    unsafe_allow_html=True)
    else:
        for org_item in pending_orgs:
            col_name, col_action = st.columns([4, 1])
            with col_name:
                creator = sb.table("profiles").select("full_name, email").eq("id", org_item["created_by"]).execute().data
                creator_info = f"{creator[0]['full_name']} ({creator[0]['email']})" if creator else "Unknown"
                st.markdown(
                    f'<div style="font-weight:500;color:#f0f0f2">{org_item["name"]}</div>'
                    f'<div style="color:#71717a;font-size:0.78rem">Created by: {creator_info}</div>',
                    unsafe_allow_html=True,
                )
            with col_action:
                if st.button("Activate", key=f"activate_{org_item['id']}", type="primary"):
                    sb.table("organizations").update({
                        "status": "active",
                        "approved_at": "now()",
                    }).eq("id", org_item["id"]).execute()
                    st.rerun()

# ── Account ───────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("#### Account")

col1, col2 = st.columns([3, 1])
with col1:
    st.markdown(
        f'<div style="color:#a1a1aa;font-size:0.85rem">'
        f'Signed in as <strong style="color:#f0f0f2">{user["full_name"]}</strong> '
        f'({user["email"]})</div>',
        unsafe_allow_html=True,
    )
with col2:
    if st.button("Sign out", key="settings_signout"):
        sign_out()
