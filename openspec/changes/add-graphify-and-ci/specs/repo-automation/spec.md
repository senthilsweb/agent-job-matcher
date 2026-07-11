# Repo Automation Specification

## Requirement: Knowledge graph at the repo root
The repository SHALL carry a graphify-generated knowledge graph committed at the root of `main`: `graph.json` (full cytoscape-style graph), `graph-index.json` (a summary slice capped at 50 KB, grouping modules by this repo's top-level roots with per-module entry files, top labels, and inbound/outbound cross-module edges), and `graph-manifest.json` (provenance: source sha/ref, generator version, timestamp, run URL). The index generator SHALL trim lowest-degree modules to honour the size cap.

## Requirement: Graph rebuild automation
A GitHub Actions workflow SHALL regenerate the graph on every push to `main` touching source or spec paths, on a weekly schedule, and on manual dispatch. Generation SHALL use graphify's deterministic AST/structural extraction requiring no LLM; when an `OPENAI_API_KEY` secret is present it MAY additionally run semantic extraction. The workflow SHALL commit the three root files only when their content changed, with a `[skip graphify]` marker that (together with the path filter) prevents self-retriggering. A generation failure SHALL open or update a `graphify-failure` tracking issue and SHALL NOT block or fail the triggering push.

## Requirement: Container publish automation
A GitHub Actions workflow SHALL build the root `Dockerfile` and publish it to `ghcr.io/senthilsweb/agent-job-matcher` on pushes to `main` (tags: branch, short sha, `latest`) and version tags (`v*` → semver tags), and SHALL build without publishing on pull requests. Registry auth SHALL use the workflow's built-in `GITHUB_TOKEN` via the `packages: write` permission; no repository secret SHALL be required for publishing.

## Requirement: Interim image contract
Until the `add-job-matcher-cli` rebuild lands, the published image SHALL package the prototype backend CLI with `python cli.py` as entrypoint (default command `--help`), run as a non-root user, and exclude secrets, specs, graph artifacts, and run outputs via `.dockerignore`. The rebuild SHALL replace this image's contents without changing the image name or publish pipeline.
