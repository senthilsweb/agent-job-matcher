# Proposal: project-wiki — task-organized docs site on GitHub Pages

> Status: **APPROVED** (2026-07-14) — owner asked for the job-scout wiki
> pattern to be applied here ("Can you do that same for job-matcher"),
> with independent per-repo publishing and one shared writing style.
> Owner: @senthilsweb

## Why

The README carries everything — quick start, endpoint tables, env vars,
tech stack, observability — and RUNBOOK.md sits beside it. Both are
good but organized by file, not by reader task: there is no 5-minute
path for someone who only wants to try the API, no single configuration
reference, and no place where design reasoning (why the LLM never
scores, the two-LLM invariant) is answerable without reading specs.
The sibling monorepo (ai-agents) just shipped a task-organized wiki
with a published site and a documented writing standard; this repo
should match it, published independently at
https://senthilsweb.github.io/agent-job-matcher/.

## What changes

1. **`docs/` wiki** — seven pages in the shared style (Home, Getting
   Started, Installation, Configuration, Surfaces, Runbook, FAQ &
   Design Decisions). Content is mostly relocation from README and
   RUNBOOK.md; specs/ADRs are linked, never duplicated.
2. **README becomes a front door** — intro + diagram, an
   "I want to → run this" table, the docs list, layout. Deep tables
   (endpoints, env vars, tech stack) move to their wiki pages.
3. **RUNBOOK.md becomes a pointer** to docs/runbook.md (file kept so
   existing links do not break).
4. **Published site** — `mkdocs.yml` (Material) +
   `.github/workflows/docs.yml` (build --strict, deploy-pages);
   Pages source set to GitHub Actions.

Writing standard: the canonical
[style guide](https://senthilsweb.github.io/ai-agents/style-guide/)
in ai-agents (covers wiki pages, READMEs, AGENTS.md, SKILL.md).

## Out of scope

- Rewriting AGENTS.md / backend/AGENTS.md (they already follow the
  standard's spirit; they are behavior-defining files and change only
  through their own reviewed changes).
- Any code change.
- Cross-repo site aggregation (owner chose independent sites).

## Acceptance criteria

1. Seven pages under `docs/`, rendering on GitHub and on the site.
2. README contains no section a wiki page now owns; the quickstart
   table and diagram stay.
3. `mkdocs build --strict` passes; the Pages workflow deploys from
   main with repo-native auth only.
4. Every command shown was actually run (or is verbatim from the
   README/RUNBOOK it relocated from).
5. `docs:` commits release nothing (Conventional Commits rule holds).
