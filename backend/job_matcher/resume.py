"""
File Name: resume.py
Author: Senthilnathan Karuppaiah
Date: 11-JUL-2026
Description:
Resume text extraction — pure Python, no OCR, mirroring the Eve
reference's post-Correction-3 design (pypdf for PDF, python-docx for
DOCX, TXT/MD pass through; scanned image-only PDFs rejected fast).

This module extracts resume text by:
1. Enforcing an extension allowlist (.pdf .docx .txt .md .markdown —
   legacy .doc rejected with a clear message) and a size cap before
   reading, so wrong inputs fail here, not deep in a model call.
2. Extracting per-page/per-paragraph text and normalizing it: joined
   with blank lines, word-wrapped at 120 columns (deterministic output;
   grounding evals are whitespace-insensitive so wrapping is safe).
3. Guarding on minimum extractable words — an image-only PDF yields
   almost nothing and is rejected ("no OCR") instead of silently
   producing an empty analysis.

Environment Variables (.env at repo root):
- MAX_RESUME_BYTES: resume file size cap (default: 20000000)
"""

# Import necessary libraries
import textwrap
from pathlib import Path

from job_matcher.config import max_resume_bytes
from job_matcher.observability import traced

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md", ".markdown"}
MIN_RESUME_WORDS = 30
WRAP_COLUMNS = 120


class ResumeError(ValueError):
    """Operator-facing extraction failure (bad format, scanned PDF, oversized file)."""


def _normalize(text: str) -> str:
    """Blank-line-joined paragraphs, wrapped at 120 columns, no carriage returns."""
    paragraphs = [p.strip() for p in text.replace("\r", "").split("\n") if p.strip()]
    wrapped = [textwrap.fill(p, width=WRAP_COLUMNS) for p in paragraphs]
    return "\n\n".join(wrapped)


def _extract_pdf(path: Path) -> str:
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    pages = [(page.extract_text() or "") for page in reader.pages]
    return "\n\n".join(pages)


def _extract_docx(path: Path) -> str:
    from docx import Document

    doc = Document(str(path))
    return "\n".join(p.text for p in doc.paragraphs)


@traced("extract_resume_text")
def extract_resume_text(path: Path) -> str:
    """Extract normalized plain text from a resume file, or raise ResumeError."""
    path = Path(path)
    if not path.is_file():
        raise ResumeError(f"resume file not found: {path}")

    ext = path.suffix.lower()
    if ext == ".doc":
        raise ResumeError("legacy .doc is not supported — save as .docx or PDF")
    if ext not in SUPPORTED_EXTENSIONS:
        raise ResumeError(f"unsupported resume format {ext!r} (supported: {sorted(SUPPORTED_EXTENSIONS)})")

    size = path.stat().st_size
    if size > max_resume_bytes():
        raise ResumeError(f"resume exceeds the {max_resume_bytes()} byte cap ({size} bytes)")

    if ext == ".pdf":
        raw = _extract_pdf(path)
    elif ext == ".docx":
        raw = _extract_docx(path)
    else:
        raw = path.read_text(encoding="utf-8", errors="replace")

    text = _normalize(raw)
    if len(text.split()) < MIN_RESUME_WORDS:
        raise ResumeError(
            "no extractable text found — scanned image-only PDFs are not supported (no OCR in this pipeline)"
        )
    return text
