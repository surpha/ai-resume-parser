"""
utils.py — PDF extraction, cloud URL fetching, and LLM client setup.
"""

from __future__ import annotations

import io
import os
from urllib.parse import urlparse

import instructor
import requests
from dotenv import load_dotenv
from groq import Groq
from PyPDF2 import PdfReader

load_dotenv()


def extract_text_from_pdf(pdf_file) -> str:
    """Extract all text from an uploaded PDF. Raises ValueError if empty."""
    reader = PdfReader(pdf_file)
    parts: list[str] = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            parts.append(text)

    full = "\n".join(parts)
    if not full.strip():
        raise ValueError(
            "Could not extract text from this PDF. "
            "It may be a scanned image — please use a text-based PDF."
        )
    return full


def fetch_pdf_from_url(url: str) -> str:
    """
    Download a PDF from a URL and extract text.

    Supports:
      - Direct PDF links (any .pdf URL)
      - Google Drive share links (automatically converts to direct download)
      - Dropbox links (automatically converts dl=0 to dl=1)
    """
    parsed = urlparse(url)

    # Google Drive: convert share link → direct download
    if "drive.google.com" in parsed.netloc:
        if "/file/d/" in url:
            file_id = url.split("/file/d/")[1].split("/")[0]
            url = f"https://drive.google.com/uc?export=download&id={file_id}"
        elif "id=" in url:
            file_id = parsed.query.split("id=")[1].split("&")[0]
            url = f"https://drive.google.com/uc?export=download&id={file_id}"

    # Dropbox: force direct download
    if "dropbox.com" in parsed.netloc:
        url = url.replace("dl=0", "dl=1")
        if "dl=1" not in url:
            url += ("&" if "?" in url else "?") + "dl=1"

    resp = requests.get(url, timeout=30, allow_redirects=True)
    resp.raise_for_status()

    content_type = resp.headers.get("content-type", "")
    if "pdf" not in content_type and not url.endswith(".pdf"):
        # Try anyway — some servers don't set content-type correctly
        pass

    return extract_text_from_pdf(io.BytesIO(resp.content))


def get_instructor_client() -> instructor.Instructor:
    """Return an Instructor-patched Groq client for structured LLM output."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "your_groq_api_key_here":
        raise ValueError(
            "GROQ_API_KEY not found. Add it to your .env file.\n"
            "Get a free key at: https://console.groq.com/keys"
        )
    return instructor.from_groq(
        Groq(api_key=api_key),
        mode=instructor.Mode.JSON,
    )


def truncate_text(text: str, max_chars: int = 12_000) -> str:
    """Truncate text to fit within LLM context limits (~3K tokens)."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n\n[...text truncated for length...]"
