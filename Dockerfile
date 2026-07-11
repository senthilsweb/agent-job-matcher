# syntax=docker/dockerfile:1.6
# =====================================================================
# agent-job-matcher — INTERIM image
#
# Packages the current talent-align prototype CLI (backend/cli.py) so
# the GHCR publish pipeline is live from day one. Superseded when the
# add-job-matcher-cli change lands: the runtime becomes the job_matcher
# package (jobmatch CLI + FastAPI), following privacyshield's combined
# backend+frontend image pattern.
# =====================================================================

FROM python:3.12-slim

# OPENSSL_armcap=0 disables OpenSSL's ARM CPU-feature probing, which
# uses trap-and-catch SIGILL and kills the process under Docker Desktop
# on Apple Silicon (observed via cryptography's Rust bindings). Harmless
# on amd64; costs only OpenSSL hw acceleration, irrelevant for this CLI.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    OPENSSL_armcap=0

WORKDIR /app

# Python deps — install first for better layer caching.
COPY backend/requirements-job-fit.txt ./requirements.txt
# cryptography 49.0.0's aarch64 wheel crashes with SIGILL at import
# (pulled in transitively via pydantic-ai → Authlib/google-auth); pin to
# the last known-good major until a fixed wheel ships.
RUN pip install --upgrade pip \
 && pip install -r requirements.txt "cryptography<49"

# Application code.
COPY backend/ ./

# Drop privileges.
RUN useradd --system --create-home --uid 1001 app \
 && chown -R app:app /app
USER app

ENTRYPOINT ["python", "cli.py"]
CMD ["--help"]
