# Spec: project wiki

## Requirement: Task-organized docs site
`docs/` SHALL contain Home, Getting Started, Installation,
Configuration, Surfaces, Runbook, and FAQ pages following the shared
style guide (plain English, "at the end you will have" openers,
copy-pasteable commands, relative links inside docs/, absolute GitHub
URLs outside), published independently at
https://senthilsweb.github.io/agent-job-matcher/.

#### Scenario: Five-minute path
- **WHEN** a reader with Docker follows Getting Started
- **THEN** they reach a rendered fit report (playground or CLI or REST)
  without reading any other page

## Requirement: Single-owner topics
Each topic SHALL have exactly one home: README keeps only intro,
diagram, quickstart table, docs list, and layout; RUNBOOK.md is a
pointer; endpoint/env/stack detail lives in wiki pages.

#### Scenario: No drift
- **WHEN** an endpoint or env var changes
- **THEN** exactly one docs page needs editing

## Requirement: Safe publishing
The docs workflow SHALL trigger only on docs paths, build with
`mkdocs build --strict`, deploy via actions/deploy-pages, and SHALL NOT
trigger releases or image builds (`docs:` commits release nothing).

#### Scenario: Docs push
- **WHEN** a page changes on main
- **THEN** the site updates and no version bump or image build occurs
