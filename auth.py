"""
auth.py — Authentication & organization management.

Hierarchy:
  platform_admin → approves orgs (you)
  company_admin  → approves members (HR lead)
  member         → uses the product
  pending_member → waiting for company_admin approval
"""

from __future__ import annotations

import os

import streamlit as st

from db import get_supabase
from styles import LOGO_SVG

GOOGLE_ICON = (
    '<svg width="18" height="18" viewBox="0 0 18 18">'
    '<path d="M17.64 9.2c0-.637-.057-1.251-.164-1.84H9v3.481h4.844a4.14 4.14 0 01-1.796 2.716v2.259h2.908c1.702-1.567 2.684-3.875 2.684-6.615z" fill="#4285F4"/>'
    '<path d="M9 18c2.43 0 4.467-.806 5.956-2.18l-2.908-2.259c-.806.54-1.837.86-3.048.86-2.344 0-4.328-1.584-5.036-3.711H.957v2.332A8.997 8.997 0 009 18z" fill="#34A853"/>'
    '<path d="M3.964 10.71A5.41 5.41 0 013.682 9c0-.593.102-1.17.282-1.71V4.958H.957A8.996 8.996 0 000 9c0 1.452.348 2.827.957 4.042l3.007-2.332z" fill="#FBBC05"/>'
    '<path d="M9 3.58c1.321 0 2.508.454 3.44 1.345l2.582-2.58C13.463.891 11.426 0 9 0A8.997 8.997 0 00.957 4.958L3.964 7.29C4.672 5.163 6.656 3.58 9 3.58z" fill="#EA4335"/>'
    '</svg>'
)

MICROSOFT_ICON = (
    '<svg width="18" height="18" viewBox="0 0 21 21">'
    '<rect x="1" y="1" width="9" height="9" fill="#f25022"/>'
    '<rect x="1" y="11" width="9" height="9" fill="#00a4ef"/>'
    '<rect x="11" y="1" width="9" height="9" fill="#7fba00"/>'
    '<rect x="11" y="11" width="9" height="9" fill="#ffb900"/>'
    '</svg>'
)

SLACK_ICON = (
    '<svg width="18" height="18" viewBox="0 0 24 24">'
    '<path d="M5.042 15.165a2.528 2.528 0 01-2.52 2.523A2.528 2.528 0 010 15.165a2.527 2.527 0 012.522-2.52h2.52v2.52zm1.271 0a2.527 2.527 0 012.521-2.52 2.527 2.527 0 012.521 2.52v6.313A2.528 2.528 0 018.834 24a2.528 2.528 0 01-2.521-2.522v-6.313z" fill="#E01E5A"/>'
    '<path d="M8.834 5.042a2.528 2.528 0 01-2.521-2.52A2.528 2.528 0 018.834 0a2.528 2.528 0 012.521 2.522v2.52H8.834zm0 1.271a2.528 2.528 0 012.521 2.521 2.528 2.528 0 01-2.521 2.521H2.522A2.528 2.528 0 010 8.834a2.528 2.528 0 012.522-2.521h6.312z" fill="#36C5F0"/>'
    '<path d="M18.956 8.834a2.528 2.528 0 012.522-2.521A2.528 2.528 0 0124 8.834a2.528 2.528 0 01-2.522 2.521h-2.522V8.834zm-1.27 0a2.528 2.528 0 01-2.522 2.521 2.528 2.528 0 01-2.522-2.521V2.522A2.528 2.528 0 0115.164 0a2.528 2.528 0 012.522 2.522v6.312z" fill="#2EB67D"/>'
    '<path d="M15.164 18.956a2.528 2.528 0 012.522 2.522A2.528 2.528 0 0115.164 24a2.528 2.528 0 01-2.522-2.522v-2.522h2.522zm0-1.27a2.528 2.528 0 01-2.522-2.522 2.528 2.528 0 012.522-2.522h6.314A2.528 2.528 0 0124 15.164a2.528 2.528 0 01-2.522 2.522h-6.314z" fill="#ECB22E"/>'
    '</svg>'
)

# ─── CSS ──────────────────────────────────────────────────────────────────

AUTH_CSS = """
<style>
    section[data-testid="stSidebar"] { display: none !important; }
    header[data-testid="stHeader"] { display: none !important; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }

    .block-container {
        max-width: 400px !important;
        padding-top: 10vh !important;
        position: relative;
        z-index: 2;
    }

    /* ── Animated background ──────────────────────────── */
    .auth-bg {
        position: fixed;
        inset: 0;
        z-index: 0;
        overflow: hidden;
        pointer-events: none;
    }
    .auth-bg::before {
        content: "";
        position: absolute;
        width: 600px; height: 600px;
        top: -200px; right: -200px;
        background: radial-gradient(circle, rgba(124,58,237,0.08) 0%, transparent 70%);
        animation: pulse 8s ease-in-out infinite;
    }
    .auth-bg::after {
        content: "";
        position: absolute;
        width: 500px; height: 500px;
        bottom: -150px; left: -150px;
        background: radial-gradient(circle, rgba(99,102,241,0.06) 0%, transparent 70%);
        animation: pulse 10s ease-in-out infinite reverse;
    }
    @keyframes pulse {
        0%, 100% { transform: scale(1); opacity: 0.7; }
        50% { transform: scale(1.15); opacity: 1; }
    }

    /* Floating doc particles */
    .auth-particles {
        position: fixed;
        inset: 0;
        z-index: 1;
        pointer-events: none;
    }
    .auth-particles .p {
        position: absolute;
        border: 1px solid rgba(124,58,237,0.12);
        border-radius: 4px;
        animation: float linear infinite;
        opacity: 0;
    }
    .auth-particles .p::after {
        content: "";
        position: absolute;
        top: 30%; left: 20%; right: 20%;
        height: 1px;
        background: rgba(124,58,237,0.15);
        box-shadow: 0 4px 0 rgba(124,58,237,0.1), 0 8px 0 rgba(124,58,237,0.08);
    }
    @keyframes float {
        0% { transform: translateY(100vh) rotate(0deg); opacity: 0; }
        10% { opacity: 0.6; }
        90% { opacity: 0.6; }
        100% { transform: translateY(-100px) rotate(8deg); opacity: 0; }
    }
    .auth-particles .p:nth-child(1) { width:24px;height:32px; left:10%; animation-duration:18s; animation-delay:0s; }
    .auth-particles .p:nth-child(2) { width:18px;height:24px; left:25%; animation-duration:22s; animation-delay:3s; }
    .auth-particles .p:nth-child(3) { width:20px;height:28px; left:45%; animation-duration:20s; animation-delay:6s; }
    .auth-particles .p:nth-child(4) { width:16px;height:22px; left:65%; animation-duration:24s; animation-delay:2s; }
    .auth-particles .p:nth-child(5) { width:22px;height:30px; left:80%; animation-duration:19s; animation-delay:8s; }
    .auth-particles .p:nth-child(6) { width:14px;height:20px; left:90%; animation-duration:25s; animation-delay:5s; }
    .auth-particles .p:nth-child(7) { width:20px;height:26px; left:35%; animation-duration:21s; animation-delay:10s; }

    /* ── Logo + heading ───────────────────────────────── */
    .auth-logo { text-align: center; margin-bottom: 2rem; }
    .auth-logo svg { width: 40px; height: 40px; }
    .auth-heading {
        text-align: center;
        font-size: 1.25rem;
        font-weight: 600;
        color: #f0f0f2;
        margin-bottom: 1.75rem;
        letter-spacing: -0.02em;
    }

    /* ── Inputs ───────────────────────────────────────── */
    .stTextInput > div > div > input {
        background: rgba(9,9,11,0.8) !important;
        backdrop-filter: blur(8px);
        border: 1px solid #27272a !important;
        border-radius: 10px !important;
        color: #f0f0f2 !important;
        font-size: 0.9rem !important;
        padding: 0.75rem 1rem !important;
        transition: border-color 0.15s, box-shadow 0.15s;
    }
    .stTextInput > div > div > input:focus {
        border-color: #7c3aed !important;
        box-shadow: 0 0 0 3px rgba(124,58,237,0.1) !important;
    }
    .stTextInput > div > div > input::placeholder { color: #52525b !important; }

    /* ── Buttons ──────────────────────────────────────── */
    .stButton > button {
        width: 100% !important;
        padding: 0.75rem 1rem !important;
        border-radius: 10px !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
        transition: all 0.15s ease;
    }
    .stButton > button[kind="primary"] {
        background: #f0f0f2 !important;
        color: #09090b !important;
        border: none !important;
        font-weight: 600 !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: #fff !important;
        box-shadow: 0 0 20px rgba(124,58,237,0.15) !important;
    }
    .stButton > button:not([kind="primary"]) {
        background: rgba(24,24,27,0.6) !important;
        backdrop-filter: blur(8px);
        border: 1px solid #27272a !important;
        color: #a1a1aa !important;
    }
    .stButton > button:not([kind="primary"]):hover {
        border-color: #3f3f46 !important;
        color: #f0f0f2 !important;
        background: rgba(24,24,27,0.9) !important;
    }

    /* ── Google button ────────────────────────────────── */
    .g-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.65rem;
        width: 100%;
        padding: 0.75rem 1rem;
        background: rgba(24,24,27,0.6);
        backdrop-filter: blur(8px);
        border: 1px solid #27272a;
        border-radius: 10px;
        font-size: 0.9rem;
        font-weight: 500;
        color: #a1a1aa;
        cursor: pointer;
        text-decoration: none;
        transition: all 0.15s;
    }
    .g-btn:hover { border-color: #3f3f46; color: #f0f0f2; background: rgba(24,24,27,0.9); }

    /* ── Separator ────────────────────────────────────── */
    .sep {
        display: flex; align-items: center;
        margin: 1.25rem 0; color: #3f3f46; font-size: 0.65rem;
        letter-spacing: 0.05em; text-transform: uppercase;
    }
    .sep::before, .sep::after { content: ""; flex: 1; height: 1px; background: #27272a; }
    .sep::before { margin-right: 0.75rem; }
    .sep::after { margin-left: 0.75rem; }

    /* ── Footer ───────────────────────────────────────── */
    .auth-switch {
        text-align: center; margin-top: 1.5rem;
    }
    .auth-foot {
        text-align: center; margin-top: 2.5rem;
        font-size: 0.65rem; color: #3f3f46; line-height: 1.5;
    }

    /* ── Status cards ─────────────────────────────────── */
    .wait-card {
        background: rgba(24,24,27,0.8); backdrop-filter: blur(8px);
        border: 1px solid #27272a;
        border-radius: 12px; padding: 2rem; text-align: center; margin-top: 1rem;
    }
    .wait-card h3 { font-size: 0.95rem; font-weight: 600; color: #f0f0f2; margin: 0.5rem 0 0.3rem; }
    .wait-card p { color: #71717a; font-size: 0.8rem; line-height: 1.5; margin: 0; }
</style>
"""

# Animated background HTML (floating document particles)
AUTH_BG = """
<div class="auth-bg"></div>
<div class="auth-particles">
    <div class="p"></div><div class="p"></div><div class="p"></div>
    <div class="p"></div><div class="p"></div><div class="p"></div><div class="p"></div>
</div>
"""


# ─── DB Helpers ───────────────────────────────────────────────────────────

def _get_profile(user_id: str) -> dict | None:
    sb = get_supabase()
    r = sb.table("profiles").select("*").eq("id", user_id).execute().data
    return r[0] if r else None


def _create_profile(user_id: str, full_name: str, email: str) -> dict:
    sb = get_supabase()
    return sb.table("profiles").insert({
        "id": user_id, "full_name": full_name, "email": email,
    }).execute().data[0]


def _create_org(name: str, user_id: str) -> dict:
    sb = get_supabase()
    org = sb.table("organizations").insert({
        "name": name, "created_by": user_id, "status": "pending",
    }).execute().data[0]
    sb.table("profiles").update({
        "org_id": org["id"], "role": "company_admin",
    }).eq("id", user_id).execute()
    return org


def _join_org(invite_code: str, user_id: str) -> dict | None:
    sb = get_supabase()
    r = sb.table("organizations").select("*").eq("invite_code", invite_code).eq("status", "active").execute().data
    if not r:
        return None
    org = r[0]
    sb.table("profiles").update({
        "org_id": org["id"], "role": "pending_member",
    }).eq("id", user_id).execute()
    return org


def _get_org(org_id: str) -> dict | None:
    sb = get_supabase()
    r = sb.table("organizations").select("*").eq("id", org_id).execute().data
    return r[0] if r else None


def _oauth_url(provider: str) -> str | None:
    """Build Supabase OAuth URL for a given provider (google, azure, slack)."""
    url = os.getenv("SUPABASE_URL")
    if not url:
        return None
    # Use app URL in production, localhost in dev
    redirect = os.getenv("APP_URL", "http://localhost:8502")
    return f"{url}/auth/v1/authorize?provider={provider}&redirect_to={redirect}"


def _render_oauth_buttons(prefix: str = "Continue"):
    """Render Google, Microsoft, and Slack sign-in buttons."""
    providers = [
        ("google", GOOGLE_ICON, "Google"),
        ("azure", MICROSOFT_ICON, "Microsoft"),
        ("slack", SLACK_ICON, "Slack"),
    ]
    for provider, icon, label in providers:
        url = _oauth_url(provider)
        disabled = "" if url else 'style="opacity:0.5;pointer-events:none"'
        st.markdown(
            f'<a href="{url or "#"}" class="g-btn" {disabled}>'
            f'{icon}<span>{prefix} with {label}</span></a>',
            unsafe_allow_html=True,
        )
        st.markdown('<div style="height:0.5rem"></div>', unsafe_allow_html=True)


# ─── Pages ────────────────────────────────────────────────────────────────

def _show_login():
    st.markdown(AUTH_CSS, unsafe_allow_html=True)
    st.markdown(AUTH_BG, unsafe_allow_html=True)
    st.markdown(f'<div class="auth-logo">{LOGO_SVG}</div>', unsafe_allow_html=True)
    st.markdown('<div class="auth-heading">Log in to Resume Scan AI</div>', unsafe_allow_html=True)

    # Email + password
    email = st.text_input("e", placeholder="Email address", key="l_email", label_visibility="collapsed")
    password = st.text_input("p", placeholder="Password", type="password", key="l_pass", label_visibility="collapsed")

    if st.button("Continue", type="primary", key="btn_login", use_container_width=True):
        if not email or not password:
            st.error("Enter email and password.")
        else:
            try:
                sb = get_supabase()
                res = sb.auth.sign_in_with_password({"email": email.strip(), "password": password})
                st.session_state["user"] = {
                    "id": res.user.id, "email": res.user.email,
                    "access_token": res.session.access_token,
                }
                st.rerun()
            except Exception:
                st.error("Invalid email or password.")

    # Separator
    st.markdown('<div class="sep">or</div>', unsafe_allow_html=True)

    # Social OAuth buttons
    _render_oauth_buttons("Continue")

    # Switch to signup
    st.markdown('<div class="auth-switch">', unsafe_allow_html=True)
    if st.button("Don\u2019t have an account? Sign up", key="to_signup", use_container_width=True):
        st.session_state["auth_page"] = "signup"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="auth-foot">Your data is encrypted and never shared.</div>', unsafe_allow_html=True)


def _show_signup():
    st.markdown(AUTH_CSS, unsafe_allow_html=True)
    st.markdown(AUTH_BG, unsafe_allow_html=True)
    st.markdown(f'<div class="auth-logo">{LOGO_SVG}</div>', unsafe_allow_html=True)
    st.markdown('<div class="auth-heading">Create your account</div>', unsafe_allow_html=True)

    full_name = st.text_input("n", placeholder="Full name", key="s_name", label_visibility="collapsed")
    email = st.text_input("e", placeholder="Work email", key="s_email", label_visibility="collapsed")
    password = st.text_input("p", placeholder="Password (min 6 characters)", type="password", key="s_pass", label_visibility="collapsed")

    if st.button("Sign up", type="primary", key="btn_signup", use_container_width=True):
        if not full_name or not email or not password:
            st.error("All fields are required.")
        elif len(password) < 6:
            st.error("Password must be at least 6 characters.")
        else:
            try:
                sb = get_supabase()
                res = sb.auth.sign_up({
                    "email": email.strip(), "password": password,
                    "options": {"data": {"full_name": full_name.strip()}},
                })
                if res.user and res.session:
                    st.session_state["user"] = {
                        "id": res.user.id, "email": res.user.email,
                        "access_token": res.session.access_token,
                    }
                    try:
                        _create_profile(res.user.id, full_name.strip(), email.strip())
                    except Exception:
                        pass
                    st.rerun()
                elif res.user:
                    st.success("Check your email to verify, then log in.")
                    st.session_state["auth_page"] = "login"
                else:
                    st.error("Could not create account.")
            except Exception as e:
                if "already" in str(e).lower():
                    st.error("Email already registered. Try logging in.")
                else:
                    st.error(f"Sign up failed: {e}")

    st.markdown('<div class="sep">or</div>', unsafe_allow_html=True)

    # Social OAuth buttons
    _render_oauth_buttons("Sign up")

    st.markdown('<div class="auth-switch">', unsafe_allow_html=True)
    if st.button("Already have an account? Log in", key="to_login", use_container_width=True):
        st.session_state["auth_page"] = "login"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


def _show_org_setup():
    st.markdown(AUTH_CSS, unsafe_allow_html=True)
    st.markdown(AUTH_BG, unsafe_allow_html=True)
    st.markdown('<style>.block-container { max-width: 440px !important; }</style>', unsafe_allow_html=True)
    st.markdown(f'<div class="auth-logo">{LOGO_SVG}</div>', unsafe_allow_html=True)
    st.markdown('<div class="auth-heading">Set up your workspace</div>', unsafe_allow_html=True)

    tab_new, tab_join = st.tabs(["Create organization", "Join with code"])

    with tab_new:
        org_name = st.text_input("o", placeholder="Company name", key="org_name", label_visibility="collapsed")
        if st.button("Create", type="primary", key="btn_org_create", use_container_width=True):
            if not org_name.strip():
                st.error("Enter a name.")
            else:
                try:
                    _create_org(org_name.strip(), st.session_state["user"]["id"])
                    st.rerun()
                except Exception as e:
                    st.error(str(e))
        st.caption("Your workspace will be activated by our team within 24 hours.")

    with tab_join:
        code = st.text_input("c", placeholder="Invite code", key="org_code", label_visibility="collapsed")
        if st.button("Join", type="primary", key="btn_org_join", use_container_width=True):
            if not code.strip():
                st.error("Enter the code.")
            else:
                org = _join_org(code.strip(), st.session_state["user"]["id"])
                if org:
                    st.rerun()
                else:
                    st.error("Invalid or inactive code.")
        st.caption("Ask your company admin for the invite code.")

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    if st.button("Sign out", key="org_out", use_container_width=True):
        sign_out()
    st.stop()


def _show_pending(org_name: str, reason: str):
    st.markdown(AUTH_CSS, unsafe_allow_html=True)
    st.markdown(AUTH_BG, unsafe_allow_html=True)
    st.markdown(f'<div class="auth-logo">{LOGO_SVG}</div>', unsafe_allow_html=True)

    if reason == "org_pending":
        st.markdown(
            f'<div class="wait-card">'
            f'<div style="font-size:1.5rem">⏳</div>'
            f'<h3>{org_name} is pending activation</h3>'
            f'<p>Our team is reviewing your organization. You\'ll get access once approved.</p>'
            f'</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="wait-card">'
            f'<div style="font-size:1.5rem">⏳</div>'
            f'<h3>Waiting for approval</h3>'
            f'<p>Your request to join <strong>{org_name}</strong> is pending. '
            f'Your company admin will approve your access.</p>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
    if st.button("Sign out", key="pend_out", use_container_width=True):
        sign_out()
    st.stop()


# ─── Main ─────────────────────────────────────────────────────────────────

def require_auth() -> dict:
    """Gate pages. Returns user context dict or shows auth UI + st.stop()."""

    if "user" not in st.session_state:
        page = st.session_state.get("auth_page", "login")
        (_show_signup if page == "signup" else _show_login)()
        st.stop()

    user = st.session_state["user"]

    profile = _get_profile(user["id"])
    if not profile:
        try:
            profile = _create_profile(user["id"], user["email"].split("@")[0], user["email"])
        except Exception:
            profile = _get_profile(user["id"])
            if not profile:
                st.error("Could not load profile.")
                if st.button("Sign out"):
                    sign_out()
                st.stop()

    if not profile.get("org_id"):
        _show_org_setup()

    org = _get_org(profile["org_id"])
    if not org:
        _show_org_setup()

    if org.get("status") == "pending" and profile["role"] != "platform_admin":
        _show_pending(org["name"], "org_pending")

    if profile["role"] == "pending_member":
        _show_pending(org["name"], "member_pending")

    return {
        "id": user["id"],
        "email": user["email"],
        "full_name": profile["full_name"],
        "org_id": profile["org_id"],
        "org_name": org["name"],
        "role": profile["role"],
        "invite_code": org.get("invite_code"),
    }


def sign_out():
    for k in list(st.session_state.keys()):
        if k in ("user", "auth_page") or k.startswith(("l_", "s_", "org_")):
            del st.session_state[k]
    try:
        get_supabase().auth.sign_out()
    except Exception:
        pass
    st.rerun()
