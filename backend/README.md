# backend — job_matcher

The Python backend: CLI (`jobmatch`), FastAPI surface, and the embeddable
`job_matcher` package. See the [repo README](../README.md) for the product
overview and [backend/AGENTS.md](AGENTS.md) for the workspace conventions
(header docstrings, structlog factory, env-only secrets).

```bash
pip install -e ".[dev]"          # + ,otel for Phoenix/Arize/OTLP telemetry
pytest -m "not live"             # offline suite
pytest -m live                   # real-model evals (needs .env at repo root)
jobmatch --help
uvicorn job_matcher.api:app --port 8000
```

Design and requirements: `../openspec/changes/add-job-matcher-cli/` ·
Eval contract: [`evals/rubrics.md`](evals/rubrics.md)
