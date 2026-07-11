# AGENTS — backend workspace (Python)

Workspace-level conventions for all Python code under `backend/`. These
implement the repo-level requirements in `../AGENTS.md`; read that first.

## File header convention (every .py file)

Every Python file opens with this docstring shape (style reference: the
owner's `bot_frappe_api_to_db.py` pipeline scripts):

```python
"""
File Name: <name>.py
Author: Senthilnathan Karuppaiah
Date: <DD-MON-YYYY>
Description:
<One-paragraph summary of what this module does.>

This module <does X> by:
1. <step / responsibility>
2. <step / responsibility>
3. <step / responsibility>

Requirements:            # entry points only — modules may omit
- <pip package>
- <pip package>

Environment Variables (.env at repo root):   # only the ones THIS file reads
- VAR_NAME: what it controls (default: ...)
"""
```

Inline comments follow the same style: short `# comment` lines introducing
each logical block (imports, env loading, configuration, each major
function), explaining intent — not restating the code.

## Custom logger (mandatory, no exceptions)

All logging goes through `job_matcher/logging.py` — a single factory
wrapping **structlog** in the owner's established configuration. No module
configures logging itself; no `print()` for diagnostics.

The factory implements exactly this pattern (centralized, not copy-pasted
per file):

```python
# job_matcher/logging.py — the ONE place logging is configured
import logging, os
from datetime import datetime
import structlog

def get_logger(script_name: str):
    # Create logs directory if it doesn't exist
    os.makedirs("./logs", exist_ok=True)
    # Generate a log filename with the current timestamp
    log_filename = f"./logs/{script_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    logging.basicConfig(filename=log_filename, level=logging.INFO, format="%(message)s")
    structlog.configure(
        logger_factory=structlog.stdlib.LoggerFactory(),
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
    )
    return structlog.get_logger()
```

Usage in modules: `log = get_logger(script_name)` at the entry point;
library modules take `structlog.get_logger(__name__)` and inherit the
entry point's configuration. Log events are key-value structured
(`log.info("job_fetched", job_source=url, words=n)`), never interpolated
prose strings.

## Telemetry (OpenObserve over REST)

- The `@traced`/`@timed` decorators (see `job_matcher/observability.py`)
  emit span records to the configured sink. `OBSERVABILITY_SINK=json`
  (default) writes them through the logger; `openobserve` additionally
  batches and POSTs them to
  `{OPENOBSERVE_URL}/api/{OPENOBSERVE_ORG}/{OPENOBSERVE_STREAM}/_json`
  with basic auth (`OPENOBSERVE_USER`/`OPENOBSERVE_PASSWORD`); `none`
  disables.
- Shipping is async/batched and fire-and-forget: an unreachable
  OpenObserve logs one warning and never fails or slows a run.
- Do not import any OTel/vendor SDK in application code. If OTel is
  inserted later it becomes another sink implementation behind the same
  interface.

## Other workspace rules

- Async end-to-end per job: each job source runs fetch → analyze → score →
  report as one asyncio task, bounded by `JOB_FANOUT_CONCURRENCY`; one
  job's failure is logged gracefully and never disturbs the others.
- Results are typed JSON arrays of `JobOutcome` (Pydantic). CLI persists
  them under `runs/<ts>/`; the API returns them as the response payload.
- **Secrets ONLY from the repo-root `.env`.** No hardcoded credentials,
  API keys, database passwords, service endpoints, or auth tokens in
  source code, comments, or fallback defaults — not even marked as
  "example" or "placeholder". Missing secrets must produce a clear
  startup error; this is expected behaviour. Never let a secret slip
  into code review or CI artifacts.
- Tests: offline by default; anything calling a model sits behind
  `pytest -m live`.
