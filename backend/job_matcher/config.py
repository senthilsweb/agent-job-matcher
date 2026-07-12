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


def ensure_env_loaded() -> None:
    """Load the repo-root .env into os.environ, exactly once per process.

    Any module that reads os.getenv() for a value that may live in .env
    must call this first — resolve_model() below does; the observability
    facade (job_matcher/observability/__init__.py) also must, since its
    configure() can be the very first thing that touches the environment
    in a request path (e.g. the agent service's per-request root span
    opens before its model-resolving code ever runs). Skipping this call
    anywhere is what silently dropped Arize/OpenObserve telemetry in
    practice: configure()'s result is cached for the process's lifetime,
    so reading a pre-.env environment once means never seeing those vars
    again for that process, however long it runs.
    """
    global _loaded
    if not _loaded:
        load_dotenv(find_dotenv(usecwd=True))
        _loaded = True


class ConfigError(RuntimeError):
    """Raised when required configuration is missing — an operator error."""


def resolve_model(role: str = "ANALYST", *fallback_roles: str) -> str:
    """MODEL_<ROLE> → MODEL_<FALLBACK>... → MODEL → ConfigError. Never a default.

    The agent service resolves resolve_model("CHAT", "ANALYST") per ADR 0001.
    """
    ensure_env_loaded()
    chain = [f"MODEL_{role}", *(f"MODEL_{fb}" for fb in fallback_roles), "MODEL"]
    for var in chain:
        value = os.getenv(var, "").strip()
        if value:
            return value
    raise ConfigError(
        f"No model configured: set {' or '.join(chain)} in the repo-root .env, "
        "e.g. MODEL_ANALYST=openai:gpt-5.4-mini"
    )


def _int_env(name: str, default: int) -> int:
    ensure_env_loaded()
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
