"""
File Name: prompts.py
Author: Senthilnathan Karuppaiah
Date: 11-JUL-2026
Description:
Prompt and template loading — prompts are data, never compiled into
Python source (spec: "Templates and prompts staged as data"), and
operators can override them without a code change.

This module loads text assets by:
1. Resolution order for a prompt <name>: $PROMPTS_DIR/<name>.txt →
   ./prompts/<name>.txt (working directory) → the package's built-in
   default under job_matcher/prompts/.
2. The same resolution order for templates via $TEMPLATES_DIR →
   ./templates/ → the package's built-in default under
   job_matcher/templates/ (revision 7 correction: a template feature
   that never activates without operator configuration isn't shipped —
   templates now have a package default exactly like prompts do; an
   operator can still fully override at either preceding path).
3. render() — mustache-lite {{variable}} substitution (the owner's
   established template style); unknown placeholders are left intact.

Environment Variables (.env at repo root):
- PROMPTS_DIR: optional prompt override directory
- TEMPLATES_DIR: optional template override directory
"""

# Import necessary libraries
import os
import re
from importlib import resources
from pathlib import Path


def load_prompt(name: str) -> str:
    """Load a prompt by name via override dirs, falling back to package data."""
    for base in (os.getenv("PROMPTS_DIR", "").strip(), "prompts"):
        if base:
            candidate = Path(base) / f"{name}.txt"
            if candidate.is_file():
                return candidate.read_text(encoding="utf-8")
    return (resources.files("job_matcher") / "prompts" / f"{name}.txt").read_text(encoding="utf-8")


def load_template(name: str) -> str:
    """Load a template by name via override dirs, falling back to package data."""
    for base in (os.getenv("TEMPLATES_DIR", "").strip(), "templates"):
        if base:
            candidate = Path(base) / f"{name}.txt"
            if candidate.is_file():
                return candidate.read_text(encoding="utf-8")
    return (resources.files("job_matcher") / "templates" / f"{name}.txt").read_text(encoding="utf-8")


def render(template: str, **values: str) -> str:
    """Mustache-style {{variable}} substitution; unknown keys stay as-is."""

    def replace(match: re.Match) -> str:
        key = match.group(1).strip()
        return str(values[key]) if key in values else match.group(0)

    return re.sub(r"\{\{(\s*\w+\s*)\}\}", replace, template)
