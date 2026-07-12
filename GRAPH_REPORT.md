# Graph Report - /home/runner/work/agent-job-matcher/agent-job-matcher  (2026-07-12)

## Corpus Check
- 81 files · ~99,523 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 518 nodes · 970 edges · 47 communities detected
- Extraction: 57% EXTRACTED · 43% INFERRED · 0% AMBIGUOUS · INFERRED: 418 edges (avg confidence: 0.66)
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

## God Nodes (most connected - your core abstractions)
1. `JobReport` - 37 edges
2. `JobAnalysis` - 28 edges
3. `extract_resume_text()` - 24 edges
4. `SkillMatch` - 23 edges
5. `OpenObserveRestSink` - 23 edges
6. `run_analysis()` - 22 edges
7. `ScoreBreakdown` - 21 edges
8. `GET()` - 21 edges
9. `JobFetchFailure` - 20 edges
10. `JsonLogSink` - 20 edges

## Surprising Connections (you probably didn't know these)
- `test_api_endpoint_returns_document()` --calls--> `POST()`  [INFERRED]
  /home/runner/work/agent-job-matcher/agent-job-matcher/backend/tests/test_jsonresume.py → /home/runner/work/agent-job-matcher/agent-job-matcher/playground/app/api/analyze/route.ts
- `test_api_endpoint_operator_error_422()` --calls--> `POST()`  [INFERRED]
  /home/runner/work/agent-job-matcher/agent-job-matcher/backend/tests/test_jsonresume.py → /home/runner/work/agent-job-matcher/agent-job-matcher/playground/app/api/analyze/route.ts
- `File Name: test_api.py Author: Senthilnathan Karuppaiah Date: 11-JUL-2026 Descri` --uses--> `JobReport`  [INFERRED]
  /home/runner/work/agent-job-matcher/agent-job-matcher/backend/tests/test_api.py → /home/runner/work/agent-job-matcher/agent-job-matcher/backend/job_matcher/schemas.py
- `File Name: test_resume_extraction.py Author: Senthilnathan Karuppaiah Date: 11-J` --uses--> `ResumeError`  [INFERRED]
  /home/runner/work/agent-job-matcher/agent-job-matcher/backend/tests/test_resume_extraction.py → /home/runner/work/agent-job-matcher/agent-job-matcher/backend/job_matcher/resume.py
- `test_hard_recommendation_byte_identical()` --calls--> `recommendation_for()`  [INFERRED]
  /home/runner/work/agent-job-matcher/agent-job-matcher/backend/tests/live/test_prompt_injection.py → /home/runner/work/agent-job-matcher/agent-job-matcher/backend/job_matcher/scoring.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.06
Nodes (70): BaseModel, extract_jsonresume(), extract_resume_text(), Stable core entry point — lazy import so `import job_matcher` stays light., Stable core re-export of resume extraction (lazy import)., Stable core re-export of JSON Resume extraction (lazy import, async)., run_analysis(), assert_safe_relative() (+62 more)

### Community 1 - "Community 1"
Cohesion: 0.05
Nodes (46): add_span_attributes(), _allowlisted(), current_span(), File Name: observability/__init__.py Author: Senthilnathan Karuppaiah Date: 11-J, Test/advanced hook: replace the sink fan-out explicitly., The span active in this execution context, if any., Open a span nested under the context's active span (or a new trace root)., Open the per-invocation root span; the run id becomes the trace id.      When al (+38 more)

### Community 2 - "Community 2"
Cohesion: 0.05
Nodes (46): _action_label(), build_agent(), chat_stream(), health(), File Name: app.py Author: Senthilnathan Karuppaiah Date: 11-JUL-2026 Description, Convert the wire-format {role, content} turns into pydantic-ai's     native mess, The one LLM-2 invocation per chat turn; wrapped so tests can stub it., Stream a chat answer over SSE (ctms contract: content / done / error). (+38 more)

### Community 3 - "Community 3"
Cohesion: 0.08
Nodes (44): analyze(), _custom_openapi(), health(), File Name: api.py Author: Senthilnathan Karuppaiah Date: 11-JUL-2026 Description, FastAPI-native generation plus the repo link (spec: repo path link)., One span per HTTP request — the root the pipeline's run span nests under., Run the full analysis synchronously and return the typed outcome array.      Pro, Extract the resume into the standard JSON Resume format.      Provide the resume (+36 more)

### Community 4 - "Community 4"
Cohesion: 0.11
Nodes (34): CandidateIdentity, Whatever contact fields were found in the resume text — never a guess., FetchResult, The outcome of the single fetch attempt for one job source., _cover_letter_text(), _job_task(), _now(), _persist() (+26 more)

### Community 5 - "Community 5"
Cohesion: 0.1
Nodes (32): assert_contact_grounded(), Award, Basics, Certificate, _digits(), Education, extract_jsonresume(), Interest (+24 more)

### Community 6 - "Community 6"
Cohesion: 0.13
Nodes (22): configure(), _build_exporters(), build_otel_sink(), OtelBridgeSink, otlp_env_configured(), File Name: observability/otel_bridge.py Author: Senthilnathan Karuppaiah Date: 1, True when any OTLP-shaped backend's activation env is present., Construct the bridge for whatever OTLP backends the env activates. (+14 more)

### Community 7 - "Community 7"
Cohesion: 0.09
Nodes (19): normalize(), File Name: conftest.py Author: Senthilnathan Karuppaiah Date: 11-JUL-2026 Descri, Whitespace/case normalization — the rubric's grounding comparison space., Run the REAL pipeline while counting analysis calls. Returns (result, calls)., run_live_counted(), grounding_run(), File Name: test_evidence_grounding.py Author: Senthilnathan Karuppaiah Date: 11-, test_hard_matched_evidence_is_verbatim_from_resume() (+11 more)

### Community 8 - "Community 8"
Cohesion: 0.15
Nodes (20): contact_line(), extract_candidate_identity(), _find_email(), _find_name(), _find_phone(), _find_urls(), File Name: candidate.py Author: Senthilnathan Karuppaiah Date: 11-JUL-2026 Descr, Extract whatever contact fields the resume text contains, deterministically. (+12 more)

### Community 9 - "Community 9"
Cohesion: 0.19
Nodes (17): _blocked_host_reason(), fetch_job_source(), _fetch_local(), html_to_text(), _now(), File Name: fetch.py Author: Senthilnathan Karuppaiah Date: 11-JUL-2026 Descripti, Make the one and only fetch attempt for a job source. Never retries., Pre-connect SSRF guard: loopback/private/link-local/reserved targets. (+9 more)

### Community 10 - "Community 10"
Cohesion: 0.18
Nodes (16): _extract_docx(), _extract_pdf(), extract_resume_text(), _normalize(), File Name: resume.py Author: Senthilnathan Karuppaiah Date: 11-JUL-2026 Descript, Blank-line-joined paragraphs, wrapped at 120 columns, no carriage returns., Extract normalized plain text from a resume file, or raise ResumeError., File Name: test_resume_extraction.py Author: Senthilnathan Karuppaiah Date: 11-J (+8 more)

### Community 11 - "Community 11"
Cohesion: 0.16
Nodes (14): analyze_job_fit(), File Name: analyze.py Author: Senthilnathan Karuppaiah Date: 11-JUL-2026 Descrip, Best-effort token accounting across pydantic-ai versions., Declared at the decorator (AOP): token usage + model onto the LLM span;     prom, Extract the typed, evidence-grounded analysis for one job posting., _span_enrichment(), _usage_dict(), load_prompt() (+6 more)

### Community 12 - "Community 12"
Cohesion: 0.4
Nodes (0): 

### Community 13 - "Community 13"
Cohesion: 0.5
Nodes (2): Badge(), cn()

### Community 14 - "Community 14"
Cohesion: 0.67
Nodes (0): 

### Community 15 - "Community 15"
Cohesion: 0.67
Nodes (0): 

### Community 16 - "Community 16"
Cohesion: 0.67
Nodes (0): 

### Community 17 - "Community 17"
Cohesion: 0.67
Nodes (0): 

### Community 18 - "Community 18"
Cohesion: 1.0
Nodes (0): 

### Community 19 - "Community 19"
Cohesion: 1.0
Nodes (0): 

### Community 20 - "Community 20"
Cohesion: 1.0
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

## Knowledge Gaps
- **65 isolated node(s):** `Return the module key for a given file path, or None if unrecognised.`, `File Name: app.py Author: Senthilnathan Karuppaiah Date: 11-JUL-2026 Description`, `LLM-2: pydantic-ai agent with the MCP server as its only toolset.`, `Convert the wire-format {role, content} turns into pydantic-ai's     native mess`, `The one LLM-2 invocation per chat turn; wrapped so tests can stub it.` (+60 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 18`** (2 nodes): `main()`, `export-openapi.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 19`** (2 nodes): `index.js`, `callBackend()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 20`** (2 nodes): `utils.ts`, `cn()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 21`** (2 nodes): `use-backend-status.ts`, `useBackendStatus()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 22`** (2 nodes): `separator.tsx`, `cn()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 23`** (2 nodes): `Collapsible()`, `collapsible.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 24`** (2 nodes): `cn()`, `button.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 25`** (2 nodes): `input.tsx`, `Input()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 26`** (2 nodes): `sidebar-form.tsx`, `handleSubmit()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 27`** (2 nodes): `score-bar.tsx`, `ScoreBar()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 28`** (2 nodes): `resume-dropzone.tsx`, `ResumeDropzone()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 29`** (2 nodes): `status-pill.tsx`, `StatusPill()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 30`** (2 nodes): `handleCopy()`, `cover-letter-section.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 31`** (2 nodes): `layout.tsx`, `RootLayout()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 32`** (1 nodes): `smoke.mjs`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 33`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 34`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 35`** (1 nodes): `eslint.config.mjs`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 36`** (1 nodes): `postcss.config.mjs`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 37`** (1 nodes): `next.config.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 38`** (1 nodes): `types.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 39`** (1 nodes): `report-card.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 40`** (1 nodes): `nav-rail.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 41`** (1 nodes): `results-panel.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 42`** (1 nodes): `layout.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 43`** (1 nodes): `page.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 44`** (1 nodes): `eslint.config.mjs`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 45`** (1 nodes): `postcss.config.mjs`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 46`** (1 nodes): `next.config.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `GET()` connect `Community 2` to `Community 1`, `Community 11`, `Community 9`, `Community 6`?**
  _High betweenness centrality (0.170) - this node is a cross-community bridge._
- **Why does `run_analysis()` connect `Community 4` to `Community 0`, `Community 1`, `Community 3`, `Community 7`, `Community 8`, `Community 10`?**
  _High betweenness centrality (0.167) - this node is a cross-community bridge._
- **Why does `JobReport` connect `Community 0` to `Community 1`, `Community 2`, `Community 3`, `Community 4`, `Community 7`?**
  _High betweenness centrality (0.110) - this node is a cross-community bridge._
- **Are the 34 inferred relationships involving `JobReport` (e.g. with `File Name: test_pipeline_offline.py Author: Senthilnathan Karuppaiah Date: 11-JU` and `File Name: test_api.py Author: Senthilnathan Karuppaiah Date: 11-JUL-2026 Descri`) actually correct?**
  _`JobReport` has 34 INFERRED edges - model-reasoned connections that need verification._
- **Are the 25 inferred relationships involving `JobAnalysis` (e.g. with `File Name: test_pipeline_offline.py Author: Senthilnathan Karuppaiah Date: 11-JU` and `File Name: test_schema_conformance.py Author: Senthilnathan Karuppaiah Date: 11-`) actually correct?**
  _`JobAnalysis` has 25 INFERRED edges - model-reasoned connections that need verification._
- **Are the 18 inferred relationships involving `extract_resume_text()` (e.g. with `test_deterministic_pieces_standalone()` and `test_full_run_cover_letter_is_grounded_in_resume_text()`) actually correct?**
  _`extract_resume_text()` has 18 INFERRED edges - model-reasoned connections that need verification._
- **Are the 20 inferred relationships involving `SkillMatch` (e.g. with `File Name: test_pipeline_offline.py Author: Senthilnathan Karuppaiah Date: 11-JU` and `File Name: test_scoring_determinism.py Author: Senthilnathan Karuppaiah Date: 11`) actually correct?**
  _`SkillMatch` has 20 INFERRED edges - model-reasoned connections that need verification._