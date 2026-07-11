# Runbook — agent-job-matcher

Day-to-day operational commands. Design/spec live in `openspec/`; coding
conventions in `AGENTS.md`.

## First-time setup

```bash
git clone https://github.com/senthilsweb/agent-job-matcher && cd agent-job-matcher
cp .env.example .env        # then fill in the values you need
```

## GitHub secrets & variables from the command line

Secret values are write-only on GitHub — set them from your local `.env`:

```bash
# one key, value pulled from .env
gh secret set OPENAI_API_KEY -b "$(grep '^OPENAI_API_KEY=' .env | cut -d= -f2-)"

# any other key the same way
gh secret set <NAME> -b "$(grep '^<NAME>=' .env | cut -d= -f2-)"

# Actions variables (non-secret)
gh variable set OPENAI_MODEL -b "gpt-5-mini"

# inspect what's configured
gh secret list && gh variable list
```

Run these from the repo folder (`-R senthilsweb/agent-job-matcher` if not).

## Workflows

| Workflow | Trigger | Manual run |
|---|---|---|
| Graphify Knowledge Graph | push to main (code/spec paths), weekly, manual | `gh workflow run graphify.yml` |
| Build & publish (GHCR image) | push to main, `v*` tags, PRs | `gh workflow run build-and-publish.yml` |
| Release (semantic version) | push to main (conventional commits), manual | `gh workflow run release.yml` |

```bash
gh run list --limit 5          # recent runs
gh run watch                   # follow the latest
```

## Releases

Versions are computed from **Conventional Commits** on `main`:
`fix:` → patch, `feat:` → minor, `BREAKING CHANGE:` footer → major.
Anything else (docs:, chore:, spec updates) releases nothing. The bot
bumps `backend/pyproject.toml`, tags `v<X.Y.Z>`, creates the GitHub
Release, and the tag re-publishes the Docker image with semver tags.

## Docker image

```bash
docker compose up -d api                 # FastAPI on :8000
docker compose run --rm cli version      # CLI through the same image
# or raw:
docker pull ghcr.io/senthilsweb/agent-job-matcher:latest
docker run --rm --env-file .env ghcr.io/senthilsweb/agent-job-matcher:latest --help
```

(One-time: make the package public — GitHub → Packages → agent-job-matcher
→ Package settings → Change visibility.)

## Knowledge graph, locally

```bash
pip install graphifyy==0.4.23
graphify update .                                   # graphify-out/: graph.json, graph.html, GRAPH_REPORT.md
python scripts/graphify-index.py graphify-out/graph.json graphify-out/graph-index.json .
open graphify-out/graph.html                        # interactive viewer
```

CI does the same on every push and commits the results to the repo root
(`graph.json`, `graph-index.json`, `graph.html`, `GRAPH_REPORT.md`,
`graph-manifest.json`). Add `[skip graphify]` to a commit message to skip.

## Backend (once Bolt 1+ lands)

```bash
pip install -e "backend[dev]"
pytest backend -m "not live"    # offline suite, no API key needed
pytest backend -m live          # needs a configured model in .env
jobmatch --help
```
