"""
File Name: config.py
Author: Senthilnathan Karuppaiah
Date: 11-JUL-2026
Description:
Environment resolution — the only place configuration is read. All
values come from the repo-root .env (or the process environment);
missing required config is a clear startup error, never a default
(AGENTS.md rule 5).

This module resolves configuration by:
1. Loading the nearest .env walking up from the current directory,
   exactly once per process.
2. resolve_model(): MODEL_ANALYST → MODEL → ConfigError. No hard-coded
   model id exists anywhere in this package.
3. Typed accessors for pipeline knobs with safe non-secret defaults.

Environment Variables (.env at repo root):
- MODEL_ANALYST / MODEL: pydantic-ai model id, e.g. anthropic:claude-haiku-4-5 (required)
- JOB_FANOUT_CONCURRENCY: max concurrent per-job tasks (default: 3)
- JOB_MIN_WORDS: minimum extractable words for a job posting (default: 100)
- MAX_FETCH_BYTES: response byte cap for job fetches (default: 2000000)
- MAX_RESUME_BYTES: resume file size cap (default: 20000000)
"""

# Import necessary libraries
import os

from dotenv import find_dotenv, load_dotenv

# Load environment variables for configuration and secrets (once per process)
_loaded = False


def _ensure_env_loaded() -> None:
    global _loaded
    if not _loaded:
        load_dotenv(find_dotenv(usecwd=True))
        _loaded = True


class ConfigError(RuntimeError):
    """Raised when required configuration is missing — an operator error."""


def resolve_model(role: str = "ANALYST") -> str:
    """MODEL_<ROLE> → MODEL → ConfigError. Never a built-in default."""
    _ensure_env_loaded()
    for var in (f"MODEL_{role}", "MODEL"):
        value = os.getenv(var, "").strip()
        if value:
            return value
    raise ConfigError(
        f"No model configured: set MODEL_{role} (or MODEL) in the repo-root .env, "
        "e.g. MODEL_ANALYST=anthropic:claude-haiku-4-5"
    )


def _int_env(name: str, default: int) -> int:
    _ensure_env_loaded()
    raw = os.getenv(name, "").strip()
    try:
        return int(raw) if raw else default
    except ValueError:
        return default


def fanout_concurrency() -> int:
    return max(1, _int_env("JOB_FANOUT_CONCURRENCY", 3))


def job_min_words() -> int:
    return _int_env("JOB_MIN_WORDS", 100)


def max_fetch_bytes() -> int:
    return _int_env("MAX_FETCH_BYTES", 2_000_000)


def max_resume_bytes() -> int:
    return _int_env("MAX_RESUME_BYTES", 20_000_000)
