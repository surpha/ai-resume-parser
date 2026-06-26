"""
styles.py — Professional SaaS design system.

Enterprise-grade dark UI with:
  - Fixed top header bar (logo left, user right)
  - Clean sidebar navigation
  - Refined typography and spacing
  - Consistent component library
"""

import streamlit as st

GLOBAL_CSS = """
<style>
    /* ── Reset & Base ──────────────────────────────────────────────── */
    .block-container {
        padding-top: 2.5rem;
        padding-bottom: 2rem;
        max-width: 1180px;
    }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header[data-testid="stHeader"] { display: none !important; }

    /* ── Top Bar ───────────────────────────────────────────────────── */
    .top-bar {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        height: 56px;
        background: #111114;
        border-bottom: 1px solid #23232a;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 2rem;
        z-index: 9999;
    }
    .top-bar-logo {
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }
    .top-bar-logo svg {
        width: 26px;
        height: 26px;
    }
    .top-bar-brand {
        font-size: 1rem;
        font-weight: 600;
        color: #f0f0f2;
        letter-spacing: -0.02em;
    }
    .top-bar-user {
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    .top-bar-user-name {
        font-size: 0.82rem;
        color: #a1a1aa;
        font-weight: 500;
    }
    .top-bar-avatar {
        width: 30px;
        height: 30px;
        border-radius: 50%;
        background: linear-gradient(135deg, #7c3aed, #6366f1);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.75rem;
        font-weight: 600;
        color: #fff;
    }

    /* Push page content below fixed top bar */
    section[data-testid="stMain"] {
        margin-top: 56px;
    }

    /* ── Sidebar ───────────────────────────────────────────────────── */
    section[data-testid="stSidebar"] {
        background: #111114 !important;
        border-right: 1px solid #23232a;
        margin-top: 56px;
    }
    section[data-testid="stSidebar"] .block-container {
        padding-top: 1.5rem;
    }
    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] {
        padding-top: 0.5rem;
    }
    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a {
        color: #a1a1aa !important;
        font-size: 0.88rem !important;
        font-weight: 500 !important;
        padding: 0.55rem 1rem !important;
        border-radius: 6px !important;
        transition: all 0.15s ease;
        text-decoration: none !important;
    }
    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a:hover {
        color: #f0f0f2 !important;
        background: rgba(255,255,255,0.04) !important;
    }
    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a[aria-current="page"] {
        color: #f0f0f2 !important;
        background: rgba(124,58,237,0.1) !important;
    }

    /* ── Typography ────────────────────────────────────────────────── */
    h1 {
        font-size: 1.6rem !important;
        font-weight: 700 !important;
        color: #f0f0f2 !important;
        letter-spacing: -0.03em !important;
        margin-bottom: 0.15rem !important;
    }
    h2 {
        font-size: 1.15rem !important;
        font-weight: 600 !important;
        color: #f0f0f2 !important;
        letter-spacing: -0.01em !important;
    }
    h3, h4 {
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        color: #e4e4e7 !important;
    }
    .page-subtitle {
        color: #71717a;
        font-size: 0.87rem;
        margin-top: -0.15rem;
        margin-bottom: 1.75rem;
        font-weight: 400;
    }

    /* ── Cards ─────────────────────────────────────────────────────── */
    .card {
        background: #18181b;
        border: 1px solid #27272a;
        border-radius: 10px;
        padding: 1.25rem;
        margin-bottom: 0.75rem;
    }
    .card-elevated {
        background: #1f1f23;
        border: 1px solid #27272a;
        border-radius: 10px;
        padding: 1.25rem;
        margin-bottom: 0.75rem;
    }
    .card-header {
        font-size: 0.95rem;
        font-weight: 600;
        color: #f0f0f2;
        margin-bottom: 0.4rem;
    }
    .card-body {
        color: #a1a1aa;
        font-size: 0.85rem;
        line-height: 1.6;
    }

    /* ── Stat cards ────────────────────────────────────────────────── */
    .stat-card {
        background: #18181b;
        border: 1px solid #27272a;
        border-radius: 10px;
        padding: 1.25rem 1.5rem;
        text-align: center;
    }
    .stat-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #f0f0f2;
        line-height: 1.2;
    }
    .stat-label {
        font-size: 0.68rem;
        color: #71717a;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-top: 0.3rem;
        font-weight: 500;
    }

    /* ── Pills / Chips ─────────────────────────────────────────────── */
    .pill {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 9999px;
        font-size: 0.72rem;
        font-weight: 500;
        margin: 0.12rem;
        border: 1px solid transparent;
    }
    .pill-purple { background: rgba(124,58,237,0.12); color: #a78bfa; border-color: rgba(124,58,237,0.2); }
    .pill-green { background: rgba(34,197,94,0.1); color: #4ade80; border-color: rgba(34,197,94,0.2); }
    .pill-yellow { background: rgba(234,179,8,0.1); color: #facc15; border-color: rgba(234,179,8,0.2); }
    .pill-red { background: rgba(239,68,68,0.1); color: #f87171; border-color: rgba(239,68,68,0.2); }
    .pill-blue { background: rgba(59,130,246,0.1); color: #60a5fa; border-color: rgba(59,130,246,0.2); }
    .pill-muted { background: rgba(113,113,122,0.1); color: #a1a1aa; border-color: rgba(113,113,122,0.2); }

    /* ── Severity flags ────────────────────────────────────────────── */
    .flag-high {
        background: rgba(239,68,68,0.06);
        border-left: 3px solid #ef4444;
        border-radius: 0 8px 8px 0;
        padding: 0.75rem 1rem;
        margin-bottom: 0.5rem;
    }
    .flag-medium {
        background: rgba(234,179,8,0.06);
        border-left: 3px solid #eab308;
        border-radius: 0 8px 8px 0;
        padding: 0.75rem 1rem;
        margin-bottom: 0.5rem;
    }
    .flag-low {
        background: rgba(59,130,246,0.06);
        border-left: 3px solid #3b82f6;
        border-radius: 0 8px 8px 0;
        padding: 0.75rem 1rem;
        margin-bottom: 0.5rem;
    }

    /* ── Accent bar ────────────────────────────────────────────────── */
    .accent-bar {
        border-left: 2px solid #7c3aed;
        padding: 0.55rem 1rem;
        background: rgba(124,58,237,0.04);
        border-radius: 0 8px 8px 0;
        margin-bottom: 0.5rem;
    }

    /* ── Recommendation badges ─────────────────────────────────────── */
    .rec-badge {
        display: inline-block;
        padding: 0.25rem 0.85rem;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.78rem;
    }
    .rec-strong_yes, .rec-yes { background: rgba(34,197,94,0.12); color: #4ade80; }
    .rec-maybe { background: rgba(234,179,8,0.12); color: #facc15; }
    .rec-no, .rec-strong_no { background: rgba(239,68,68,0.12); color: #f87171; }

    /* ── Streamlit overrides ───────────────────────────────────────── */
    .stExpander {
        border: 1px solid #27272a !important;
        border-radius: 10px !important;
        background: #18181b !important;
    }
    div[data-testid="stMetric"] {
        background: #18181b;
        border: 1px solid #27272a;
        border-radius: 10px;
        padding: 0.75rem 1rem;
    }
    div[data-testid="stMetric"] label {
        color: #71717a !important;
        font-size: 0.7rem !important;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        font-weight: 500 !important;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #f0f0f2 !important;
        font-weight: 700 !important;
    }

    /* Buttons */
    .stButton > button[kind="primary"] {
        background: #7c3aed !important;
        color: #fff !important;
        border: none !important;
        font-weight: 500 !important;
        border-radius: 8px !important;
        font-size: 0.84rem !important;
        padding: 0.5rem 1.25rem !important;
        transition: background 0.15s ease;
    }
    .stButton > button[kind="primary"]:hover {
        background: #6d28d9 !important;
    }
    .stButton > button:not([kind="primary"]) {
        border: 1px solid #27272a !important;
        border-radius: 8px !important;
        color: #a1a1aa !important;
        font-weight: 500 !important;
        font-size: 0.84rem !important;
        background: transparent !important;
    }
    .stButton > button:not([kind="primary"]):hover {
        border-color: #3f3f46 !important;
        color: #f0f0f2 !important;
        background: rgba(255,255,255,0.03) !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        border-bottom: 1px solid #27272a;
    }
    .stTabs [data-baseweb="tab"] {
        color: #71717a;
        border-bottom: 2px solid transparent;
        padding: 0.5rem 1rem;
        font-size: 0.84rem;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        color: #f0f0f2 !important;
        border-bottom: 2px solid #7c3aed !important;
        background: transparent !important;
    }

    /* Inputs */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div {
        border-color: #27272a !important;
        background: #18181b !important;
        color: #f0f0f2 !important;
        border-radius: 8px !important;
        font-size: 0.87rem !important;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #7c3aed !important;
        box-shadow: 0 0 0 1px rgba(124,58,237,0.25) !important;
    }

    /* Dividers */
    hr {
        border-color: #27272a !important;
        margin: 1.5rem 0 !important;
    }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #0f0f11; }
    ::-webkit-scrollbar-thumb { background: #27272a; border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: #3f3f46; }

    /* File uploader */
    [data-testid="stFileUploader"] {
        border-color: #27272a !important;
    }
    [data-testid="stFileUploader"] section {
        background: #18181b !important;
        border-radius: 10px !important;
    }
</style>
"""

# SVG logo mark — abstract document with scan line + neural dot
LOGO_SVG = (
    '<svg viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">'
    '<rect width="32" height="32" rx="8" fill="#7c3aed"/>'
    '<path d="M9 8h10l4 4v12a2 2 0 01-2 2H9a2 2 0 01-2-2V10a2 2 0 012-2z" '
    'fill="none" stroke="#fff" stroke-width="1.5" stroke-linecap="round"/>'
    '<path d="M19 8v4h4" fill="none" stroke="#fff" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>'
    '<line x1="10" y1="16" x2="20" y2="16" stroke="#c4b5fd" stroke-width="1.2" stroke-linecap="round"/>'
    '<line x1="10" y1="19" x2="17" y2="19" stroke="#c4b5fd" stroke-width="1.2" stroke-linecap="round" opacity="0.7"/>'
    '<circle cx="24" cy="22" r="4" fill="#4f46e5"/>'
    '<circle cx="24" cy="22" r="1.5" fill="#fff"/>'
    '<path d="M22.5 20.5l3 3" stroke="#fff" stroke-width="0.8" stroke-linecap="round" opacity="0.6"/>'
    '</svg>'
)


def _render_top_bar(username: str | None = None, name: str | None = None):
    """Render the fixed top bar with logo and optional user info."""
    user_html = ""
    if username and name:
        initials = "".join(w[0].upper() for w in name.split()[:2]) if name else "U"
        user_html = (
            f'<div class="top-bar-user">'
            f'<span class="top-bar-user-name">{name}</span>'
            f'<div class="top-bar-avatar">{initials}</div>'
            f'</div>'
        )

    st.markdown(
        f'<div class="top-bar">'
        f'<div class="top-bar-logo">{LOGO_SVG}<span class="top-bar-brand">Resume Scan AI</span></div>'
        f'{user_html}'
        f'</div>',
        unsafe_allow_html=True,
    )


def apply_theme(username: str | None = None, name: str | None = None):
    """Inject the full professional theme. Call at top of every page after auth."""
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
    _render_top_bar(username=username, name=name)


def score_color(score: int) -> str:
    """Return the appropriate color hex for a 0-100 score."""
    if score >= 75:
        return "#4ade80"
    if score >= 50:
        return "#facc15"
    return "#f87171"


def proficiency_pill(proficiency: str) -> str:
    """Return a pill HTML string for a proficiency level."""
    pill_cls = {
        "expert": "pill-green",
        "advanced": "pill-blue",
        "intermediate": "pill-yellow",
        "beginner": "pill-red",
    }.get(proficiency.lower(), "pill-muted")
    return f'<span class="pill {pill_cls}">{proficiency}</span>'


def severity_icon(severity: str) -> str:
    """Return an icon for severity levels."""
    return {"high": "●", "medium": "◐", "low": "○"}.get(severity.lower(), "·")
