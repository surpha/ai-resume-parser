"""
styles.py — Shared CSS and UI helpers for a consistent dark professional theme.

Design system:
  - Background: #0f0f11 (base), #1a1a1f (surface), #252529 (elevated)
  - Accent: #a78bfa (purple), #818cf8 (indigo)
  - Success: #34d399, Warning: #fbbf24, Error: #f87171
  - Text: #e2e2e5 (primary), #9ca3af (secondary), #6b7280 (muted)
  - Border: #2d2d33
  - Radius: 0.75rem (cards), 9999px (pills)
"""

import streamlit as st

GLOBAL_CSS = """
<style>
    /* ── Base overrides ─────────────────────────────────────────── */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }

    /* Hide Streamlit branding but keep navigation */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header[data-testid="stHeader"] {
        background: #0f0f11 !important;
        border-bottom: 1px solid #2d2d33;
    }

    /* ── Typography ─────────────────────────────────────────────── */
    h1 {
        font-weight: 700 !important;
        letter-spacing: -0.025em !important;
        color: #e2e2e5 !important;
    }
    h2, h3 {
        font-weight: 600 !important;
        color: #e2e2e5 !important;
    }
    .page-subtitle {
        color: #9ca3af;
        font-size: 0.95rem;
        margin-top: -0.5rem;
        margin-bottom: 1.5rem;
    }

    /* ── Cards ──────────────────────────────────────────────────── */
    .card {
        background: #1a1a1f;
        border: 1px solid #2d2d33;
        border-radius: 0.75rem;
        padding: 1.25rem;
        margin-bottom: 0.75rem;
    }
    .card-elevated {
        background: #252529;
        border: 1px solid #2d2d33;
        border-radius: 0.75rem;
        padding: 1.25rem;
        margin-bottom: 0.75rem;
    }
    .card-header {
        font-size: 1.1rem;
        font-weight: 600;
        color: #e2e2e5;
        margin-bottom: 0.5rem;
    }
    .card-body {
        color: #9ca3af;
        font-size: 0.9rem;
        line-height: 1.6;
    }

    /* ── Stat cards ─────────────────────────────────────────────── */
    .stat-card {
        background: #1a1a1f;
        border: 1px solid #2d2d33;
        border-radius: 0.75rem;
        padding: 1.25rem 1.5rem;
        text-align: center;
    }
    .stat-value {
        font-size: 2rem;
        font-weight: 700;
        color: #a78bfa;
        line-height: 1.2;
    }
    .stat-label {
        font-size: 0.75rem;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-top: 0.25rem;
    }

    /* ── Pills / Chips ─────────────────────────────────────────── */
    .pill {
        display: inline-block;
        padding: 0.2rem 0.65rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 500;
        margin: 0.15rem;
        border: 1px solid transparent;
    }
    .pill-purple { background: rgba(167,139,250,0.15); color: #a78bfa; border-color: rgba(167,139,250,0.25); }
    .pill-green { background: rgba(52,211,153,0.15); color: #34d399; border-color: rgba(52,211,153,0.25); }
    .pill-yellow { background: rgba(251,191,36,0.15); color: #fbbf24; border-color: rgba(251,191,36,0.25); }
    .pill-red { background: rgba(248,113,113,0.15); color: #f87171; border-color: rgba(248,113,113,0.25); }
    .pill-blue { background: rgba(96,165,250,0.15); color: #60a5fa; border-color: rgba(96,165,250,0.25); }
    .pill-muted { background: rgba(107,114,128,0.15); color: #9ca3af; border-color: rgba(107,114,128,0.25); }

    /* ── Severity / status indicators ──────────────────────────── */
    .flag-high {
        background: rgba(248,113,113,0.08);
        border-left: 3px solid #f87171;
        border-radius: 0 0.5rem 0.5rem 0;
        padding: 0.75rem 1rem;
        margin-bottom: 0.5rem;
    }
    .flag-medium {
        background: rgba(251,191,36,0.08);
        border-left: 3px solid #fbbf24;
        border-radius: 0 0.5rem 0.5rem 0;
        padding: 0.75rem 1rem;
        margin-bottom: 0.5rem;
    }
    .flag-low {
        background: rgba(96,165,250,0.08);
        border-left: 3px solid #60a5fa;
        border-radius: 0 0.5rem 0.5rem 0;
        padding: 0.75rem 1rem;
        margin-bottom: 0.5rem;
    }

    /* ── Accent bar (left-bordered items) ──────────────────────── */
    .accent-bar {
        border-left: 3px solid #a78bfa;
        padding: 0.6rem 1rem;
        background: rgba(167,139,250,0.05);
        border-radius: 0 0.5rem 0.5rem 0;
        margin-bottom: 0.5rem;
    }

    /* ── Recommendation badges ─────────────────────────────────── */
    .rec-badge {
        display: inline-block;
        padding: 0.3rem 1rem;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .rec-strong_yes, .rec-yes { background: rgba(52,211,153,0.15); color: #34d399; }
    .rec-maybe { background: rgba(251,191,36,0.15); color: #fbbf24; }
    .rec-no, .rec-strong_no { background: rgba(248,113,113,0.15); color: #f87171; }

    /* ── Streamlit element overrides ───────────────────────────── */
    .stExpander {
        border: 1px solid #2d2d33 !important;
        border-radius: 0.75rem !important;
        background: #1a1a1f !important;
    }
    div[data-testid="stMetric"] {
        background: #1a1a1f;
        border: 1px solid #2d2d33;
        border-radius: 0.75rem;
        padding: 0.75rem 1rem;
    }
    div[data-testid="stMetric"] label {
        color: #6b7280 !important;
        font-size: 0.75rem !important;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #a78bfa !important;
        font-weight: 700 !important;
    }

    /* Buttons */
    .stButton > button[kind="primary"] {
        background: #a78bfa !important;
        color: #0f0f11 !important;
        border: none !important;
        font-weight: 600 !important;
        border-radius: 0.5rem !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: #8b5cf6 !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        border-bottom: 1px solid #2d2d33;
    }
    .stTabs [data-baseweb="tab"] {
        color: #6b7280;
        border-bottom: 2px solid transparent;
        padding: 0.5rem 1rem;
    }
    .stTabs [aria-selected="true"] {
        color: #a78bfa !important;
        border-bottom: 2px solid #a78bfa !important;
        background: transparent !important;
    }

    /* Dividers */
    hr {
        border-color: #2d2d33 !important;
        margin: 1.5rem 0 !important;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: #131316 !important;
        border-right: 1px solid #2d2d33;
    }
    section[data-testid="stSidebar"] .block-container {
        padding-top: 2rem;
    }
</style>
"""


def apply_theme():
    """Inject the global dark theme CSS and sidebar branding. Call once at the top of each page."""
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown(
            '<div style="font-size:1.3rem;font-weight:700;color:#a78bfa;'
            'letter-spacing:-0.02em;margin-bottom:0.25rem">◆ ResumeAI</div>'
            '<div style="color:#6b7280;font-size:0.8rem;margin-bottom:1rem">'
            'Semantic Candidate Intelligence</div>',
            unsafe_allow_html=True,
        )


def score_color(score: int) -> str:
    """Return the appropriate color hex for a 0-100 score."""
    if score >= 75:
        return "#34d399"
    if score >= 50:
        return "#fbbf24"
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
