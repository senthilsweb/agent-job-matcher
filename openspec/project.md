# Project — agent-job-matcher

A standalone job-fit matching product: resume + one or more job postings →
one scored, evidence-grounded JSON report per job.

Lineage:

- `ai-agents/agents/talent-align/` — the original vibe-coded prototype
  (pydantic-ai + Streamlit/CLI). Moved here as the initial `backend/`
  contents; will be rebuilt, not preserved.
- `ai-agents/agents/job-matcher/` — the governed Eve (TypeScript) rebuild.
  Its **core features, eval datasets, rubrics, and deterministic scoring
  logic are the reference design** for this project. We are not keeping the
  Eve runtime; we are porting the ideas to a pythonic, CLI-triggered
  backend.

Target shape (modelled on `privacyshield`):

```
agent-job-matcher/
├── .env                # secrets, never committed (.env.example is)
├── openspec/           # AI-DLC change specs — every non-trivial change
├── backend/            # Python GenAI backend: CLI + FastAPI + embeddable core
├── mcp/                # Node MCP server (stdio), bridges tools → backend REST
└── frontend/           # later phase, not yet started
```

## Process — AI-DLC via OpenSpec

Every non-trivial change goes through `openspec/changes/<name>/`
(proposal → design → tasks → spec) **before and during** implementation.

Status lifecycle: `proposed → approved → implemented → verified → archived`.
Archived changes move to `openspec/archive/<date>-<name>/`.

Conventions carried over from the reference projects:

- Evals are written from the spec, before or alongside the code —
  executable acceptance criteria, not after-the-fact tests.
- Eval criteria are **HARD** (objective, deterministic; any violation
  blocks `implemented → verified`) or **SOFT** (directional expectations
  about LLM output quality; misses are logged and reviewed, not blocking).
- Corrections discovered during Construction are logged in place with a
  dated `**Correction:**` entry — specs follow evidence, never silently
  rewritten.
- No hard-coded model ids, candidate identity, or credentials in source.
  Models and keys resolve from the root `.env`.
