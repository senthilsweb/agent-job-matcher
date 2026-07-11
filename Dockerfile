# syntax=docker/dockerfile:1.6
# =====================================================================
# agent-job-matcher — backend CLI image (jobmatch)
#
# Packages the job_matcher backend (add-job-matcher-cli Bolt 3). The
# FastAPI surface (Bolt 4) will extend this with a served entrypoint,
# following privacyshield's combined-image pattern when the frontend
# lands.
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

# cryptography 49.0.0's aarch64 wheel crashes with SIGILL at import
# (pulled in transitively via pydantic-ai); pin to the last known-good
# major until a fixed wheel ships.
COPY backend/ ./backend/
RUN pip install --upgrade pip \
 && pip install ./backend "cryptography<49"

# Drop privileges. Runs and logs land under /work (mount it).
RUN useradd --system --create-home --uid 1001 app \
 && mkdir -p /work && chown -R app:app /app /work
USER app
WORKDIR /work

ENTRYPOINT ["jobmatch"]
CMD ["--help"]
