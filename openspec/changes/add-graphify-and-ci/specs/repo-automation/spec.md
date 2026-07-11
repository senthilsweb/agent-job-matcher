# Repo Automation Specification

## Requirement: Knowledge graph at the repo root
The repository SHALL carry a graphify-generated knowledge graph committed at the root of `main`: `graph.json` (full graph with community assignments), `graph-index.json` (a summary slice capped at 50 KB, grouping modules by this repo's top-level roots with per-module entry files, top labels, and inbound/outbound cross-module edges), `graph.html` (the interactive viewer), `GRAPH_REPORT.md` (human-readable analysis), and `graph-manifest.json` (provenance: source sha/ref, generator version, timestamp, run URL). The index generator SHALL trim lowest-degree modules to honour the size cap and SHALL accept both cytoscape-style and node-link graph formats.

## Requirement: Graph rebuild automation
A GitHub Actions workflow SHALL regenerate the graph on every push to `main` touching source or spec paths, on a weekly schedule, and on manual dispatch. Generation SHALL run graphify's full deterministic pipeline (`graphify update`: AST extraction, graph build, community clustering, viewer, report — no LLM required); the `OPENAI_API_KEY` secret stays wired for graphify's LLM-backed semantic pass and activates automatically if that becomes CI-runnable. The workflow SHALL commit the root graph files only when their content changed, with a `[skip graphify]` marker that (together with the path filter) prevents self-retriggering. A generation failure SHALL open or update a `graphify-failure` tracking issue and SHALL NOT block or fail the triggering push.

## Requirement: Semantic release automation
A GitHub Actions workflow SHALL compute semantic versions from Conventional Commits on `main` (`fix` → patch, `feat` → minor, `BREAKING CHANGE` → major) using python-semantic-release: bumping the version in `backend/pyproject.toml` and `job_matcher/__init__.py`, committing with a `[skip graphify]`-marked release message, tagging `v<X.Y.Z>`, and creating the GitHub Release. Non-releasable commits SHALL exit cleanly with no release. The `v*` tag SHALL flow into the existing container publish workflow's semver image tags. Commit messages in this repo SHALL follow Conventional Commits (codified in `AGENTS.md`).

## Requirement: Operations runbook
The repository SHALL carry a root `RUNBOOK.md` with copy-pasteable operational commands: first-time setup, setting GitHub secrets/variables from the local `.env` via the `gh` CLI, triggering and watching each workflow, the release flow, pulling/running the Docker image, and regenerating the knowledge graph locally. The repo-root `.env.example` SHALL stay concise — grouped keys with minimal commentary, no secret values.

## Requirement: Container publish automation
A GitHub Actions workflow SHALL build the root `Dockerfile` and publish it to `ghcr.io/senthilsweb/agent-job-matcher` on pushes to `main` (tags: branch, short sha, `latest`) and version tags (`v*` → semver tags), and SHALL build without publishing on pull requests. Registry auth SHALL use the workflow's built-in `GITHUB_TOKEN` via the `packages: write` permission; no repository secret SHALL be required for publishing.

## Requirement: Interim image contract
Until the `add-job-matcher-cli` rebuild lands, the published image SHALL package the prototype backend CLI with `python cli.py` as entrypoint (default command `--help`), run as a non-root user, and exclude secrets, specs, graph artifacts, and run outputs via `.dockerignore`. The rebuild SHALL replace this image's contents without changing the image name or publish pipeline.
