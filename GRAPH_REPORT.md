# Graph Report - /home/runner/work/agent-job-matcher/agent-job-matcher  (2026-07-11)

## Corpus Check
- 31 files · ~55,306 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 313 nodes · 634 edges · 16 communities detected
- Extraction: 57% EXTRACTED · 43% INFERRED · 0% AMBIGUOUS · INFERRED: 273 edges (avg confidence: 0.64)
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

## God Nodes (most connected - your core abstractions)
1. `JobReport` - 30 edges
2. `JobAnalysis` - 27 edges
3. `OpenObserveRestSink` - 23 edges
4. `SkillMatch` - 22 edges
5. `ScoreBreakdown` - 20 edges
6. `JsonLogSink` - 20 edges
7. `run_analysis()` - 19 edges
8. `JobFetchFailure` - 18 edges
9. `extract_resume_text()` - 17 edges
10. `fetch_job_source()` - 15 edges

## Surprising Connections (you probably didn't know these)
- `File Name: test_api.py Author: Senthilnathan Karuppaiah Date: 11-JUL-2026 Descri` --uses--> `JobReport`  [INFERRED]
  /home/runner/work/agent-job-matcher/agent-job-matcher/backend/tests/test_api.py → /home/runner/work/agent-job-matcher/agent-job-matcher/backend/job_matcher/schemas.py
- `File Name: test_scoring_determinism.py Author: Senthilnathan Karuppaiah Date: 11` --uses--> `SkillMatch`  [INFERRED]
  /home/runner/work/agent-job-matcher/agent-job-matcher/backend/tests/test_scoring_determinism.py → /home/runner/work/agent-job-matcher/agent-job-matcher/backend/job_matcher/schemas.py
- `Fixture helper — mirrors the Eve eval's mkSkills().` --uses--> `SkillMatch`  [INFERRED]
  /home/runner/work/agent-job-matcher/agent-job-matcher/backend/tests/test_scoring_determinism.py → /home/runner/work/agent-job-matcher/agent-job-matcher/backend/job_matcher/schemas.py
- `clean_env()` --calls--> `set_sinks()`  [INFERRED]
  /home/runner/work/agent-job-matcher/agent-job-matcher/backend/tests/test_telemetry_backends.py → /home/runner/work/agent-job-matcher/agent-job-matcher/backend/job_matcher/observability/__init__.py
- `test_band_boundaries()` --calls--> `match_band_for()`  [INFERRED]
  /home/runner/work/agent-job-matcher/agent-job-matcher/backend/tests/test_match_banding.py → /home/runner/work/agent-job-matcher/agent-job-matcher/backend/job_matcher/scoring.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.08
Nodes (56): BaseModel, FetchResult, The outcome of the single fetch attempt for one job source., extract_resume_text(), File Name: observability/__init__.py Author: Senthilnathan Karuppaiah Date: 11-J, Stable core entry point — lazy import so `import job_matcher` stays light., Stable core re-export of resume extraction (lazy import)., run_analysis() (+48 more)

### Community 1 - "Community 1"
Cohesion: 0.07
Nodes (42): analyze(), _custom_openapi(), health(), File Name: api.py Author: Senthilnathan Karuppaiah Date: 11-JUL-2026 Description, FastAPI-native generation plus the repo link (spec: repo path link)., One span per HTTP request — the root the pipeline's run span nests under., Run the full analysis synchronously and return the typed outcome array.      Pro, Report liveness and the running package version.      Used by container healthch (+34 more)

### Community 2 - "Community 2"
Cohesion: 0.09
Nodes (30): add_span_attributes(), _allowlisted(), current_span(), Test/advanced hook: replace the sink fan-out explicitly., The span active in this execution context, if any., Open a span nested under the context's active span (or a new trace root)., Open the per-invocation root span; the run id becomes the trace id.      When al, Attach attributes to the active span from inside a decorated call.      The sanc (+22 more)

### Community 3 - "Community 3"
Cohesion: 0.12
Nodes (26): _ensure_env_loaded(), fanout_concurrency(), _int_env(), job_min_words(), max_fetch_bytes(), max_resume_bytes(), File Name: config.py Author: Senthilnathan Karuppaiah Date: 11-JUL-2026 Descript, MODEL_<ROLE> → MODEL → ConfigError. Never a built-in default. (+18 more)

### Community 4 - "Community 4"
Cohesion: 0.14
Nodes (21): configure(), _build_exporters(), build_otel_sink(), OtelBridgeSink, otlp_env_configured(), File Name: observability/otel_bridge.py Author: Senthilnathan Karuppaiah Date: 1, True when any OTLP-shaped backend's activation env is present., Construct the bridge for whatever OTLP backends the env activates. (+13 more)

### Community 5 - "Community 5"
Cohesion: 0.18
Nodes (13): traced(), inner(), outer(), File Name: test_observability.py Author: Senthilnathan Karuppaiah Date: 11-JUL-2, recorder(), RecorderSink, test_capture_is_allowlist_only(), test_context_propagates_across_asyncio_tasks() (+5 more)

### Community 6 - "Community 6"
Cohesion: 0.16
Nodes (14): analyze_job_fit(), File Name: analyze.py Author: Senthilnathan Karuppaiah Date: 11-JUL-2026 Descrip, Best-effort token accounting across pydantic-ai versions., Declared at the decorator (AOP): token usage + model onto the LLM span;     prom, Extract the typed, evidence-grounded analysis for one job posting., _span_enrichment(), _usage_dict(), load_prompt() (+6 more)

### Community 7 - "Community 7"
Cohesion: 0.2
Nodes (14): assert_safe_relative(), report_filename(), run_timestamp(), slugify(), write_json_artifact(), _evidence_matches_flag(), File Name: test_slug_naming.py Author: Senthilnathan Karuppaiah Date: 11-JUL-202, test_report_filename_matches_contract() (+6 more)

### Community 8 - "Community 8"
Cohesion: 0.27
Nodes (13): _count_matched(), js_round(), score_job_fit(), mk_skills(), File Name: test_scoring_determinism.py Author: Senthilnathan Karuppaiah Date: 11, Fixture helper — mirrors the Eve eval's mkSkills()., test_all_matched_scores_100(), test_empty_preferred_reallocates_to_required() (+5 more)

### Community 9 - "Community 9"
Cohesion: 0.22
Nodes (10): run_analysis(), File Name: test_embeddable_core.py Author: Senthilnathan Karuppaiah Date: 11-JUL, test_full_offline_run_via_package_root(), stub_analysis(), test_all_failed_run_completes_cleanly(), test_analysis_exception_isolated_to_its_job(), test_api_mode_persists_nothing(), test_cli_mode_persistence_contract() (+2 more)

### Community 10 - "Community 10"
Cohesion: 0.2
Nodes (1): File Name: test_api.py Author: Senthilnathan Karuppaiah Date: 11-JUL-2026 Descri

### Community 11 - "Community 11"
Cohesion: 0.43
Nodes (7): File Name: test_openapi_docs.py Author: Senthilnathan Karuppaiah Date: 11-JUL-20, spec(), test_body_operations_document_request(), test_every_operation_documented(), test_every_operation_has_response_example(), test_info_and_repo_link(), test_spec_validates()

### Community 12 - "Community 12"
Cohesion: 0.6
Nodes (4): build_index(), main(), module_for(), Return the module key for a given file path, or None if unrecognised.

### Community 13 - "Community 13"
Cohesion: 0.4
Nodes (3): File Name: test_match_banding.py Author: Senthilnathan Karuppaiah Date: 11-JUL-2, test_band_boundaries(), test_recommendation_is_deterministic_lookup()

### Community 14 - "Community 14"
Cohesion: 1.0
Nodes (0): 

### Community 15 - "Community 15"
Cohesion: 1.0
Nodes (0): 

## Knowledge Gaps
- **39 isolated node(s):** `Return the module key for a given file path, or None if unrecognised.`, `File Name: test_embeddable_core.py Author: Senthilnathan Karuppaiah Date: 11-JUL`, `File Name: test_observability.py Author: Senthilnathan Karuppaiah Date: 11-JUL-2`, `File Name: test_fetch_guards.py Author: Senthilnathan Karuppaiah Date: 11-JUL-20`, `File Name: test_openapi_docs.py Author: Senthilnathan Karuppaiah Date: 11-JUL-20` (+34 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 14`** (2 nodes): `main()`, `export-openapi.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 15`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `File Name: observability/__init__.py Author: Senthilnathan Karuppaiah Date: 11-J` connect `Community 0` to `Community 2`?**
  _High betweenness centrality (0.232) - this node is a cross-community bridge._
- **Why does `run_analysis()` connect `Community 9` to `Community 0`, `Community 1`, `Community 2`, `Community 3`, `Community 7`?**
  _High betweenness centrality (0.206) - this node is a cross-community bridge._
- **Why does `JobReport` connect `Community 0` to `Community 1`, `Community 10`?**
  _High betweenness centrality (0.180) - this node is a cross-community bridge._
- **Are the 27 inferred relationships involving `JobReport` (e.g. with `File Name: test_pipeline_offline.py Author: Senthilnathan Karuppaiah Date: 11-JU` and `File Name: test_api.py Author: Senthilnathan Karuppaiah Date: 11-JUL-2026 Descri`) actually correct?**
  _`JobReport` has 27 INFERRED edges - model-reasoned connections that need verification._
- **Are the 24 inferred relationships involving `JobAnalysis` (e.g. with `File Name: test_pipeline_offline.py Author: Senthilnathan Karuppaiah Date: 11-JU` and `File Name: test_schema_conformance.py Author: Senthilnathan Karuppaiah Date: 11-`) actually correct?**
  _`JobAnalysis` has 24 INFERRED edges - model-reasoned connections that need verification._
- **Are the 17 inferred relationships involving `OpenObserveRestSink` (e.g. with `File Name: test_telemetry_backends.py Author: Senthilnathan Karuppaiah Date: 11-` and `Span`) actually correct?**
  _`OpenObserveRestSink` has 17 INFERRED edges - model-reasoned connections that need verification._
- **Are the 19 inferred relationships involving `SkillMatch` (e.g. with `File Name: test_pipeline_offline.py Author: Senthilnathan Karuppaiah Date: 11-JU` and `File Name: test_scoring_determinism.py Author: Senthilnathan Karuppaiah Date: 11`) actually correct?**
  _`SkillMatch` has 19 INFERRED edges - model-reasoned connections that need verification._