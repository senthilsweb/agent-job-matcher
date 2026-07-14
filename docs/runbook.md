# Runbook

At the end you will know what CI does, how to manage secrets, how a
release happens, and the day-to-day commands. Design and specs live in
[openspec/](https://github.com/senthilsweb/agent-job-matcher/tree/main/openspec);
coding conventions in
[AGENTS.md](https://github.com/senthilsweb/agent-job-matcher/blob/main/AGENTS.md).

## Workflows

| Workflow | Trigger | Manual run |
|---|---|---|
| Graphify Knowledge Graph | push to main (code/spec paths), weekly, manual | `gh workflow run graphify.yml` |
| Build & publish (GHCR image) | push to main, `v*` tags, PRs | `gh workflow run build-and-publish.yml` |
| Release (semantic version) | push to main (conventional commits), manual | `gh workflow run release.yml` |
| Docs site (GitHub Pages) | push to main touching `docs/**` or `mkdocs.yml`, manual | `gh workflow run docs.yml` |

```bash
gh run list --limit 5          # recent runs
gh run watch                   # follow the latest
```

## GitHub secrets and variables from the command line

Secret values are write-only on GitHub — set them from your local
`.env`:

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

Run these from the repo folder (`-R senthilsweb/agent-job-matcher` if
not).

## Releases

Versions are computed from **Conventional Commits** on `main`: `fix:`
→ patch, `feat:` → minor, `BREAKING CHANGE:` footer → major. Anything
else (`docs:`, `chore:`, spec updates) releases nothing. The bot bumps
`backend/pyproject.toml`, tags `v<X.Y.Z>`, creates the GitHub Release
(with the generated `openapi.json`/`openapi.yaml` attached), and the
tag re-publishes the Docker image with semver tags.

## Docker operations

```bash
docker compose up -d api                 # backend only, on :6010
docker compose up -d                     # full demo stack, :6010–:6014
docker compose run --rm cli version      # CLI through the same image
# or raw:
docker pull ghcr.io/senthilsweb/agent-job-matcher:latest
docker run --rm --env-file .env ghcr.io/senthilsweb/agent-job-matcher:latest --help
```

One-time after the first publish: make the GHCR package public —
GitHub → Packages → agent-job-matcher → Package settings → Change
visibility.

## Tests

```bash
pip install -e "backend[dev]"
pytest backend -m "not live"    # offline: scoring, guards, schemas, API — no key needed
pytest backend -m live          # real-model sweep: grounding, injection, fan-out — needs .env
```

Fixtures are committed real-world captures (four JD snapshots, two
genuine JavaScript-shell fetch failures, one adversarial
prompt-injection JD) plus a synthetic resume — reproducible after the
postings close. The rubric:
[backend/evals/rubrics.md](https://github.com/senthilsweb/agent-job-matcher/blob/main/backend/evals/rubrics.md).

## Knowledge graph, locally

```bash
pip install graphifyy==0.4.23
graphify update .                        # graphify-out/: graph.json, graph.html, GRAPH_REPORT.md
python scripts/graphify-index.py graphify-out/graph.json graphify-out/graph-index.json .
open graphify-out/graph.html             # interactive viewer
```

CI does the same on every push and commits the results to the repo
root (`graph.json`, `graph-index.json`, `graph.html`,
`GRAPH_REPORT.md`, `graph-manifest.json`) — never edit those by hand.
Add `[skip graphify]` to a commit message to skip.

Next: [FAQ & Design Decisions](faq.md).
