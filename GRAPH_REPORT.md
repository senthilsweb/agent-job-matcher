# Graph Report - /home/runner/work/agent-job-matcher/agent-job-matcher  (2026-09-28)

## Corpus Check
- 84 files · ~114,924 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 566 nodes · 1087 edges · 50 communities detected
- Extraction: 60% EXTRACTED · 40% INFERRED · 0% AMBIGUOUS · INFERRED: 440 edges (avg confidence: 0.67)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 32|Community 32]]
- [[_COMMUNITY_Community 33|Community 33]]
- [[_COMMUNITY_Community 34|Community 34]]
- [[_COMMUNITY_Community 35|Community 35]]
- [[_COMMUNITY_Community 36|Community 36]]
- [[_COMMUNITY_Community 37|Community 37]]
- [[_COMMUNITY_Community 38|Community 38]]
- [[_COMMUNITY_Community 39|Community 39]]
- [[_COMMUNITY_Community 40|Community 40]]
- [[_COMMUNITY_Community 41|Community 41]]
- [[_COMMUNITY_Community 42|Community 42]]
- [[_COMMUNITY_Community 43|Community 43]]
- [[_COMMUNITY_Community 44|Community 44]]
- [[_COMMUNITY_Community 45|Community 45]]
- [[_COMMUNITY_Community 46|Community 46]]
- [[_COMMUNITY_Community 47|Community 47]]
- [[_COMMUNITY_Community 48|Community 48]]
- [[_COMMUNITY_Community 49|Community 49]]

## God Nodes (most connected - your core abstractions)
1. `JobReport` - 37 edges
2. `fetch_job_source()` - 31 edges
3. `JobAnalysis` - 28 edges
4. `SkillMatch` - 23 edges
5. `OpenObserveRestSink` - 23 edges
6. `GET()` - 23 edges
7. `ScoreBreakdown` - 21 edges
8. `JobFetchFailure` - 20 edges
9. `JsonLogSink` - 20 edges
10. `_Strict` - 19 edges

## Surprising Connections (you probably didn't know these)
- `File Name: test_resume_extraction.py Author: Senthilnathan Karuppaiah Date: 11-J` --uses--> `ResumeError`  [INFERRED]
  /home/runner/work/agent-job-matcher/agent-job-matcher/backend/tests/test_resume_extraction.py → /home/runner/work/agent-job-matcher/agent-job-matcher/backend/job_matcher/resume.py
- `File Name: test_scoring_determinism.py Author: Senthilnathan Karuppaiah Date: 11` --uses--> `SkillMatch`  [INFERRED]
  /home/runner/work/agent-job-matcher/agent-job-matcher/backend/tests/test_scoring_determinism.py → /home/runner/work/agent-job-matcher/agent-job-matcher/backend/job_matcher/schemas.py
- `Fixture helper — mirrors the Eve eval's mkSkills().` --uses--> `SkillMatch`  [INFERRED]
  /home/runner/work/agent-job-matcher/agent-job-matcher/backend/tests/test_scoring_determinism.py → /home/runner/work/agent-job-matcher/agent-job-matcher/backend/job_matcher/schemas.py
- `File Name: analyze.py Author: Senthilnathan Karuppaiah Date: 11-JUL-2026 Descrip` --uses--> `JobAnalysis`  [INFERRED]
  /home/runner/work/agent-job-matcher/agent-job-matcher/backend/job_matcher/analyze.py → /home/runner/work/agent-job-matcher/agent-job-matcher/backend/job_matcher/schemas.py
- `Best-effort token accounting across pydantic-ai versions.` --uses--> `JobAnalysis`  [INFERRED]
  /home/runner/work/agent-job-matcher/agent-job-matcher/backend/job_matcher/analyze.py → /home/runner/work/agent-job-matcher/agent-job-matcher/backend/job_matcher/schemas.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.06
Nodes (72): BaseModel, FetchResult, The outcome of the single fetch attempt for one job source., File Name: observability/__init__.py Author: Senthilnathan Karuppaiah Date: 11-J, Stable core entry point — lazy import so `import job_matcher` stays light., Stable core re-export of resume extraction (lazy import)., Stable core re-export of JSON Resume extraction (lazy import, async)., _job_task() (+64 more)

### Community 1 - "Community 1"
Cohesion: 0.05
Nodes (57): add_span_attributes(), _allowlisted(), configure(), current_span(), Test/advanced hook: replace the sink fan-out explicitly., The span active in this execution context, if any., Open a span nested under the context's active span (or a new trace root)., Open the per-invocation root span; the run id becomes the trace id.      When al (+49 more)

### Community 2 - "Community 2"
Cohesion: 0.06
Nodes (38): _action_label(), chat_stream(), health(), File Name: app.py Author: Senthilnathan Karuppaiah Date: 11-JUL-2026 Description, Convert the wire-format {role, content} turns into pydantic-ai's     native mess, Stream a chat answer over SSE (ctms contract: content / done / error)., Store an uploaded resume in the configured temp dir; return its path., Liveness + the MCP tool list discovered over stdio. (+30 more)

### Community 3 - "Community 3"
Cohesion: 0.12
Nodes (38): _blocked_host_reason(), fetch_job_source(), _fetch_local(), html_to_text(), _now(), File Name: fetch.py Author: Senthilnathan Karuppaiah Date: 11-JUL-2026 Descripti, Turn a rule-extracted posting into the plain text the analyst reads., Make the one and only fetch attempt for a job source. Never retries. (+30 more)

### Community 4 - "Community 4"
Cohesion: 0.1
Nodes (36): analyze(), _custom_openapi(), health(), File Name: api.py Author: Senthilnathan Karuppaiah Date: 11-JUL-2026 Description, FastAPI-native generation plus the repo link (spec: repo path link)., One span per HTTP request — the root the pipeline's run span nests under., Run the full analysis synchronously and return the typed outcome array.      Pro, Extract the resume into the standard JSON Resume format.      Provide the resume (+28 more)

### Community 5 - "Community 5"
Cohesion: 0.08
Nodes (28): normalize(), File Name: conftest.py Author: Senthilnathan Karuppaiah Date: 11-JUL-2026 Descri, Whitespace/case normalization — the rubric's grounding comparison space., Run the REAL pipeline while counting analysis calls. Returns (result, calls)., run_live_counted(), extract_resume_text(), grounding_run(), File Name: test_evidence_grounding.py Author: Senthilnathan Karuppaiah Date: 11- (+20 more)

### Community 6 - "Community 6"
Cohesion: 0.11
Nodes (31): assert_contact_grounded(), Award, Basics, Certificate, _digits(), Education, extract_jsonresume(), Interest (+23 more)

### Community 7 - "Community 7"
Cohesion: 0.1
Nodes (28): analyze_job_fit(), File Name: analyze.py Author: Senthilnathan Karuppaiah Date: 11-JUL-2026 Descrip, Best-effort token accounting across pydantic-ai versions., Declared at the decorator (AOP): token usage + model onto the LLM span;     prom, Extract the typed, evidence-grounded analysis for one job posting., _span_enrichment(), _usage_dict(), build_agent() (+20 more)

### Community 8 - "Community 8"
Cohesion: 0.12
Nodes (22): AtsPosting, AtsRuleError, AtsTarget, _evaluate(), extract(), _load_folder(), File Name: ats.py Author: Senthilnathan Karuppaiah Date: 26-SEP-2026 Description, Return the API target for a known-ATS URL, or None when no rule matches. (+14 more)

### Community 9 - "Community 9"
Cohesion: 0.15
Nodes (20): contact_line(), extract_candidate_identity(), _find_email(), _find_name(), _find_phone(), _find_urls(), File Name: candidate.py Author: Senthilnathan Karuppaiah Date: 11-JUL-2026 Descr, Extract whatever contact fields the resume text contains, deterministically. (+12 more)

### Community 10 - "Community 10"
Cohesion: 0.14
Nodes (19): ats_rules_dir(), ensure_env_loaded(), fanout_concurrency(), _int_env(), job_min_words(), max_fetch_bytes(), max_resume_bytes(), File Name: config.py Author: Senthilnathan Karuppaiah Date: 11-JUL-2026 Descript (+11 more)

### Community 11 - "Community 11"
Cohesion: 0.27
Nodes (13): _count_matched(), js_round(), score_job_fit(), mk_skills(), File Name: test_scoring_determinism.py Author: Senthilnathan Karuppaiah Date: 11, Fixture helper — mirrors the Eve eval's mkSkills()., test_all_matched_scores_100(), test_empty_preferred_reallocates_to_required() (+5 more)

### Community 12 - "Community 12"
Cohesion: 0.2
Nodes (10): _build_exporters(), build_otel_sink(), OtelBridgeSink, otlp_env_configured(), File Name: observability/otel_bridge.py Author: Senthilnathan Karuppaiah Date: 1, True when any OTLP-shaped backend's activation env is present., Construct the bridge for whatever OTLP backends the env activates., Facade spans → OTel spans, fanned out to every configured OTLP exporter. (+2 more)

### Community 13 - "Community 13"
Cohesion: 0.22
Nodes (10): run_analysis(), test_full_run_cover_letter_is_grounded_in_resume_text(), File Name: test_embeddable_core.py Author: Senthilnathan Karuppaiah Date: 11-JUL, test_full_offline_run_via_package_root(), test_all_failed_run_completes_cleanly(), test_analysis_exception_isolated_to_its_job(), test_api_mode_persists_nothing(), test_cli_mode_persistence_contract() (+2 more)

### Community 14 - "Community 14"
Cohesion: 0.4
Nodes (0): 

### Community 15 - "Community 15"
Cohesion: 0.5
Nodes (2): Badge(), cn()

### Community 16 - "Community 16"
Cohesion: 0.67
Nodes (0): 

### Community 17 - "Community 17"
Cohesion: 0.67
Nodes (0): 

### Community 18 - "Community 18"
Cohesion: 0.67
Nodes (0): 

### Community 19 - "Community 19"
Cohesion: 0.67
Nodes (0): 

### Community 20 - "Community 20"
Cohesion: 0.67
Nodes (0): 

### Community 21 - "Community 21"
Cohesion: 1.0
Nodes (0): 

### Community 22 - "Community 22"
Cohesion: 1.0
Nodes (0): 

### Community 23 - "Community 23"
Cohesion: 1.0
Nodes (0): 

### Community 24 - "Community 24"
Cohesion: 1.0
Nodes (0): 

### Community 25 - "Community 25"
Cohesion: 1.0
Nodes (0): 

### Community 26 - "Community 26"
Cohesion: 1.0
Nodes (0): 

### Community 27 - "Community 27"
Cohesion: 1.0
Nodes (0): 

### Community 28 - "Community 28"
Cohesion: 1.0
Nodes (0): 

### Community 29 - "Community 29"
Cohesion: 1.0
Nodes (0): 

### Community 30 - "Community 30"
Cohesion: 1.0
Nodes (0): 

### Community 31 - "Community 31"
Cohesion: 1.0
Nodes (0): 

### Community 32 - "Community 32"
Cohesion: 1.0
Nodes (0): 

### Community 33 - "Community 33"
Cohesion: 1.0
Nodes (0): 

### Community 34 - "Community 34"
Cohesion: 1.0
Nodes (0): 

### Community 35 - "Community 35"
Cohesion: 1.0
Nodes (0): 

### Community 36 - "Community 36"
Cohesion: 1.0
Nodes (0): 

### Community 37 - "Community 37"
Cohesion: 1.0
Nodes (0): 

### Community 38 - "Community 38"
Cohesion: 1.0
Nodes (0): 

### Community 39 - "Community 39"
Cohesion: 1.0
Nodes (0): 

### Community 40 - "Community 40"
Cohesion: 1.0
Nodes (0): 

### Community 41 - "Community 41"
Cohesion: 1.0
Nodes (0): 

### Community 42 - "Community 42"
Cohesion: 1.0
Nodes (0): 

### Community 43 - "Community 43"
Cohesion: 1.0
Nodes (0): 

### Community 44 - "Community 44"
Cohesion: 1.0
Nodes (0): 

### Community 45 - "Community 45"
Cohesion: 1.0
Nodes (0): 

### Community 46 - "Community 46"
Cohesion: 1.0
Nodes (0): 

### Community 47 - "Community 47"
Cohesion: 1.0
Nodes (0): 

### Community 48 - "Community 48"
Cohesion: 1.0
Nodes (0): 

### Community 49 - "Community 49"
Cohesion: 1.0
Nodes (0): 

## Knowledge Gaps
- **77 isolated node(s):** `File Name: app.py Author: Senthilnathan Karuppaiah Date: 11-JUL-2026 Description`, `LLM-2: pydantic-ai agent with the MCP server as its only toolset.`, `Convert the wire-format {role, content} turns into pydantic-ai's     native mess`, `The one LLM-2 invocation per chat turn; wrapped so tests can stub it.`, `Stream a chat answer over SSE (ctms contract: content / done / error).` (+72 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 21`** (2 nodes): `index.js`, `callBackend()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 22`** (2 nodes): `layout.tsx`, `RootLayout()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 23`** (2 nodes): `separator.tsx`, `cn()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 24`** (2 nodes): `cn()`, `button.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 25`** (2 nodes): `Collapsible()`, `collapsible.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 26`** (2 nodes): `label.tsx`, `cn()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 27`** (2 nodes): `input.tsx`, `Input()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 28`** (2 nodes): `handleCopy()`, `cover-letter-section.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 29`** (2 nodes): `status-pill.tsx`, `StatusPill()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 30`** (2 nodes): `resume-dropzone.tsx`, `ResumeDropzone()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 31`** (2 nodes): `score-bar.tsx`, `ScoreBar()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 32`** (2 nodes): `use-backend-status.ts`, `useBackendStatus()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 33`** (2 nodes): `main()`, `export-openapi.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 34`** (1 nodes): `smoke.mjs`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 35`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 36`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 37`** (1 nodes): `next.config.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 38`** (1 nodes): `eslint.config.mjs`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 39`** (1 nodes): `postcss.config.mjs`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 40`** (1 nodes): `next.config.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 41`** (1 nodes): `eslint.config.mjs`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 42`** (1 nodes): `postcss.config.mjs`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 43`** (1 nodes): `report-card.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 44`** (1 nodes): `nav-rail.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 45`** (1 nodes): `results-panel.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 46`** (1 nodes): `types.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 47`** (1 nodes): `page.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 48`** (1 nodes): `layout.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 49`** (1 nodes): `tablesort.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `GET()` connect `Community 2` to `Community 1`, `Community 3`, `Community 7`, `Community 8`, `Community 12`?**
  _High betweenness centrality (0.178) - this node is a cross-community bridge._
- **Why does `fetch_job_source()` connect `Community 3` to `Community 0`, `Community 8`, `Community 2`, `Community 10`?**
  _High betweenness centrality (0.150) - this node is a cross-community bridge._
- **Why does `JobReport` connect `Community 0` to `Community 2`, `Community 4`, `Community 5`, `Community 7`?**
  _High betweenness centrality (0.121) - this node is a cross-community bridge._
- **Are the 34 inferred relationships involving `JobReport` (e.g. with `File Name: cli.py Author: Senthilnathan Karuppaiah Date: 11-JUL-2026 Description` and `Keeps single commands as named subcommands (jobmatch version, jobmatch analyze..`) actually correct?**
  _`JobReport` has 34 INFERRED edges - model-reasoned connections that need verification._
- **Are the 22 inferred relationships involving `fetch_job_source()` (e.g. with `resolve()` and `GET()`) actually correct?**
  _`fetch_job_source()` has 22 INFERRED edges - model-reasoned connections that need verification._
- **Are the 25 inferred relationships involving `JobAnalysis` (e.g. with `File Name: report.py Author: Senthilnathan Karuppaiah Date: 11-JUL-2026 Descript` and `UTC timestamp in the filename-safe contract format.`) actually correct?**
  _`JobAnalysis` has 25 INFERRED edges - model-reasoned connections that need verification._
- **Are the 20 inferred relationships involving `SkillMatch` (e.g. with `File Name: scoring.py Author: Senthilnathan Karuppaiah Date: 11-JUL-2026 Descrip` and `Round half away from zero for positives — JS Math.round semantics (2.5 → 3).`) actually correct?**
  _`SkillMatch` has 20 INFERRED edges - model-reasoned connections that need verification._