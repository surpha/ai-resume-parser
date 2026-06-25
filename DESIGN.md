# AI Resume Parser — Design Log

> This file is our living design document. Updated as we build.

---

## 🎯 Vision

Replace rigid ATS keyword-matching with semantic, LLM-powered candidate analysis.
A recruiter uploads resumes + job descriptions, and gets an interactive dashboard
showing fit scores, skill breakdowns, experience summaries, credibility flags, and gaps.

---

## 🏗️ Architecture (v1)

```
┌─────────────────────────────────────────────────────────┐
│                    STREAMLIT UI (app.py)                 │
│                                                         │
│  ┌──────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ Job Mgmt │  │ Candidate    │  │ Analysis         │  │
│  │ Page     │  │ Page         │  │ Dashboard        │  │
│  └──────────┘  └──────────────┘  └──────────────────┘  │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                  PARSER (parser.py)                      │
│  • Prompt engineering                                   │
│  • LLM orchestration via Instructor + Groq              │
│  • Structured extraction → Pydantic models              │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│               SCHEMAS (schemas.py)                       │
│  • ResumeAnalysis (fit score, skills, experience, etc.) │
│  • CandidateProfile (parsed resume standalone)          │
│  • JobDescription (parsed JD structure)                 │
└─────────────────────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│               UTILS (utils.py)                          │
│  • PDF text extraction                                  │
│  • Groq/Instructor client setup                         │
│  • Text chunking helpers                                │
└─────────────────────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│               STORAGE (JSON files / local)               │
│  • data/candidates/*.json — parsed candidate profiles   │
│  • data/jobs/*.json — stored job descriptions           │
│  • data/analyses/*.json — candidate↔job analysis results│
└─────────────────────────────────────────────────────────┘
```

---

## 📐 Data Model

### Entities:
1. **Candidate** — A person + their parsed resume data
2. **Job** — A job description + its parsed requirements
3. **Analysis** — The result of evaluating Candidate × Job

### Relationships:
- One Candidate can be assessed against Many Jobs
- One Job can have Many Candidates assessed against it
- Each Analysis links exactly one Candidate to one Job

---

## 📊 Dashboard Sections (per Analysis)

| Section | What it shows |
|---------|---------------|
| Fit Score | 0–100 semantic match (capability, not keywords) |
| Skills Map | Matched / Unmatched / Missing skills with evidence |
| Experience Distillation | Career timeline → impact statements |
| Credibility Index | Flagged claims that seem inflated or unverifiable |
| Gap Analysis | Missing competencies, career breaks, short tenures |

---

## 🧩 UI Pages (Multi-page Streamlit)

| Page | Purpose |
|------|---------|
| **Jobs** | Add/view/manage job descriptions |
| **Candidates** | Upload/view resumes, see standalone profile breakdown |
| **Analyze** | Pick a candidate + job → run LLM analysis |
| **Dashboard** | View analysis results with rich visualizations |

---

## 🔧 Tech Stack

| Layer | Choice | Why |
|-------|--------|-----|
| UI | Streamlit | Python-native, free deployment, rapid iteration |
| LLM | Groq (Llama 3 70B) | Ultra-fast, free tier, great reasoning |
| Structured Output | Instructor + Pydantic | Guaranteed schema compliance from LLM |
| PDF Parsing | PyPDF2 | Simple text-layer extraction |
| Storage | Supabase (Postgres) | Free tier, persists on deploy, real SQL, JSON columns |
| Viz | Plotly + Streamlit native | Beautiful charts, zero config |

---

## 📋 Build Phases

### Phase 1: Core Pipeline ✅ DONE
- [x] Define Pydantic schemas for Candidate, Job, Analysis
- [x] PDF extraction utility
- [x] LLM client setup (Groq + Instructor)
- [x] Resume parsing prompt → structured CandidateProfile
- [x] JD parsing prompt → structured JobRequirements
- [x] Analysis prompt → Candidate × Job evaluation
- [x] Supabase database (candidates, jobs, analyses tables)
- [x] Multi-page Streamlit UI with all 4 pages
- [x] Plotly visualizations (gauge, radar chart)

### Phase 2: Polish & Enhancement
- [x] Dark professional theme (Linear/Vercel aesthetic)
- [x] Shared CSS design system (styles.py)
- [x] Cloud resume import (Google Drive, Dropbox, direct URL)
- [x] Dark-themed Plotly charts (gauge, radar)
- [ ] Comparison view (multiple candidates on one job)
- [ ] Export to PDF report
- [ ] Deploy to Streamlit Cloud

---

## 📝 Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-06-26 | Supabase Postgres over local JSON | Persists on deploy, real SQL, free tier sufficient |
| 2026-06-26 | Multi-page Streamlit app | Cleaner separation of concerns than one giant page |
| 2026-06-26 | Parse resume standalone first, then compare to JD | Enables reuse: parse once, compare to many jobs |
| 2026-06-26 | Groq + Llama 3 70B | Best free-tier speed/quality ratio for structured extraction |
| 2026-06-26 | Dark theme, no emojis in headers | Professional SaaS look, not vibecoded |
| 2026-06-26 | Shared styles.py module | Consistent design system across all pages |
| 2026-06-26 | Cloud URL resume import | Supports Google Drive, Dropbox, any public PDF link |

---

*Last updated: 2026-06-26*
