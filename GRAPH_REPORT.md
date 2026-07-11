# Graph Report - /home/runner/work/agent-job-matcher/agent-job-matcher  (2026-07-11)

## Corpus Check
- 46 files · ~73,613 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 443 nodes · 887 edges · 21 communities detected
- Extraction: 57% EXTRACTED · 43% INFERRED · 0% AMBIGUOUS · INFERRED: 378 edges (avg confidence: 0.65)
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

## God Nodes (most connected - your core abstractions)
1. `JobReport` - 37 edges
2. `JobAnalysis` - 28 edges
3. `extract_resume_text()` - 24 edges
4. `SkillMatch` - 23 edges
5. `OpenObserveRestSink` - 23 edges
6. `run_analysis()` - 22 edges
7. `ScoreBreakdown` - 21 edges
8. `JobFetchFailure` - 20 edges
9. `JsonLogSink` - 20 edges
10. `_Strict` - 19 edges

## Surprising Connections (you probably didn't know these)
- `File Name: test_api.py Author: Senthilnathan Karuppaiah Date: 11-JUL-2026 Descri` --uses--> `JobReport`  [INFERRED]
  /home/runner/work/agent-job-matcher/agent-job-matcher/backend/tests/test_api.py → /home/runner/work/agent-job-matcher/agent-job-matcher/backend/job_matcher/schemas.py
- `File Name: test_resume_extraction.py Author: Senthilnathan Karuppaiah Date: 11-J` --uses--> `ResumeError`  [INFERRED]
  /home/runner/work/agent-job-matcher/agent-job-matcher/backend/tests/test_resume_extraction.py → /home/runner/work/agent-job-matcher/agent-job-matcher/backend/job_matcher/resume.py
- `test_hard_recommendation_byte_identical()` --calls--> `recommendation_for()`  [INFERRED]
  /home/runner/work/agent-job-matcher/agent-job-matcher/backend/tests/live/test_prompt_injection.py → /home/runner/work/agent-job-matcher/agent-job-matcher/backend/job_matcher/scoring.py
- `File Name: test_prompt_injection.py Author: Senthilnathan Karuppaiah Date: 11-JU` --uses--> `JobReport`  [INFERRED]
  /home/runner/work/agent-job-matcher/agent-job-matcher/backend/tests/live/test_prompt_injection.py → /home/runner/work/agent-job-matcher/agent-job-matcher/backend/job_matcher/schemas.py
- `File Name: test_single_and_multi_job.py Author: Senthilnathan Karuppaiah Date: 1` --uses--> `JobReport`  [INFERRED]
  /home/runner/work/agent-job-matcher/agent-job-matcher/backend/tests/live/test_single_and_multi_job.py → /home/runner/work/agent-job-matcher/agent-job-matcher/backend/job_matcher/schemas.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.05
Nodes (54): add_span_attributes(), _allowlisted(), configure(), current_span(), Test/advanced hook: replace the sink fan-out explicitly., The span active in this execution context, if any., Open a span nested under the context's active span (or a new trace root)., Open the per-invocation root span; the run id becomes the trace id.      When al (+46 more)

### Community 1 - "Community 1"
Cohesion: 0.1
Nodes (35): One skill from the JD with an evidence-grounded matched verdict., SkillMatch, _count_matched(), js_round(), match_band_for(), File Name: scoring.py Author: Senthilnathan Karuppaiah Date: 11-JUL-2026 Descrip, Map a total score (0-100) to its band; boundaries inclusive on the lower edge., Deterministic recommendation text keyed off the match band — never an LLM output (+27 more)

### Community 2 - "Community 2"
Cohesion: 0.11
Nodes (36): BaseModel, extract_jsonresume(), extract_resume_text(), File Name: observability/__init__.py Author: Senthilnathan Karuppaiah Date: 11-J, Stable core entry point — lazy import so `import job_matcher` stays light., Stable core re-export of resume extraction (lazy import)., Stable core re-export of JSON Resume extraction (lazy import, async)., run_analysis() (+28 more)

### Community 3 - "Community 3"
Cohesion: 0.1
Nodes (30): assert_contact_grounded(), Award, Basics, Certificate, _digits(), Education, extract_jsonresume(), Interest (+22 more)

### Community 4 - "Community 4"
Cohesion: 0.11
Nodes (33): analyze(), _custom_openapi(), health(), File Name: api.py Author: Senthilnathan Karuppaiah Date: 11-JUL-2026 Description, FastAPI-native generation plus the repo link (spec: repo path link)., One span per HTTP request — the root the pipeline's run span nests under., Run the full analysis synchronously and return the typed outcome array.      Pro, Extract the resume into the standard JSON Resume format.      Provide the resume (+25 more)

### Community 5 - "Community 5"
Cohesion: 0.11
Nodes (31): CandidateIdentity, contact_line(), extract_candidate_identity(), _find_email(), _find_name(), _find_phone(), _find_urls(), File Name: candidate.py Author: Senthilnathan Karuppaiah Date: 11-JUL-2026 Descr (+23 more)

### Community 6 - "Community 6"
Cohesion: 0.12
Nodes (28): _ensure_env_loaded(), fanout_concurrency(), _int_env(), job_min_words(), max_fetch_bytes(), max_resume_bytes(), File Name: config.py Author: Senthilnathan Karuppaiah Date: 11-JUL-2026 Descript, MODEL_<ROLE> → MODEL_<FALLBACK>... → MODEL → ConfigError. Never a default. (+20 more)

### Community 7 - "Community 7"
Cohesion: 0.08
Nodes (26): analyze_job_fit(), File Name: analyze.py Author: Senthilnathan Karuppaiah Date: 11-JUL-2026 Descrip, Best-effort token accounting across pydantic-ai versions., Declared at the decorator (AOP): token usage + model onto the LLM span;     prom, Extract the typed, evidence-grounded analysis for one job posting., _span_enrichment(), _usage_dict(), build_agent() (+18 more)

### Community 8 - "Community 8"
Cohesion: 0.13
Nodes (22): _job_task(), _now(), _persist(), File Name: pipeline.py Author: Senthilnathan Karuppaiah Date: 11-JUL-2026 Descri, One job source, end to end. Any failure becomes this job's outcome only., CLI-mode persistence of the full run folder (API mode never calls this)., Run the full use case. out_dir given → CLI persistence; None → payload only., What every surface gets back from a run. (+14 more)

### Community 9 - "Community 9"
Cohesion: 0.09
Nodes (19): normalize(), File Name: conftest.py Author: Senthilnathan Karuppaiah Date: 11-JUL-2026 Descri, Whitespace/case normalization — the rubric's grounding comparison space., Run the REAL pipeline while counting analysis calls. Returns (result, calls)., run_live_counted(), grounding_run(), File Name: test_evidence_grounding.py Author: Senthilnathan Karuppaiah Date: 11-, test_hard_matched_evidence_is_verbatim_from_resume() (+11 more)

### Community 10 - "Community 10"
Cohesion: 0.18
Nodes (16): _extract_docx(), _extract_pdf(), extract_resume_text(), _normalize(), File Name: resume.py Author: Senthilnathan Karuppaiah Date: 11-JUL-2026 Descript, Blank-line-joined paragraphs, wrapped at 120 columns, no carriage returns., Extract normalized plain text from a resume file, or raise ResumeError., File Name: test_resume_extraction.py Author: Senthilnathan Karuppaiah Date: 11-J (+8 more)

### Community 11 - "Community 11"
Cohesion: 0.24
Nodes (10): _build_exporters(), build_otel_sink(), OtelBridgeSink, otlp_env_configured(), File Name: observability/otel_bridge.py Author: Senthilnathan Karuppaiah Date: 1, True when any OTLP-shaped backend's activation env is present., Construct the bridge for whatever OTLP backends the env activates., Facade spans → OTel spans, fanned out to every configured OTLP exporter. (+2 more)

### Community 12 - "Community 12"
Cohesion: 0.27
Nodes (5): File Name: test_app.py Author: Senthilnathan Karuppaiah Date: 11-JUL-2026 Descri, sse_events(), test_chat_stream_ctms_contract(), test_chat_stream_empty_message_is_error(), test_chat_stream_exception_becomes_error_event()

### Community 13 - "Community 13"
Cohesion: 0.2
Nodes (1): File Name: test_api.py Author: Senthilnathan Karuppaiah Date: 11-JUL-2026 Descri

### Community 14 - "Community 14"
Cohesion: 0.43
Nodes (7): File Name: test_openapi_docs.py Author: Senthilnathan Karuppaiah Date: 11-JUL-20, spec(), test_body_operations_document_request(), test_every_operation_documented(), test_every_operation_has_response_example(), test_info_and_repo_link(), test_spec_validates()

### Community 15 - "Community 15"
Cohesion: 0.6
Nodes (4): build_index(), main(), module_for(), Return the module key for a given file path, or None if unrecognised.

### Community 16 - "Community 16"
Cohesion: 1.0
Nodes (0): 

### Community 17 - "Community 17"
Cohesion: 1.0
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

## Knowledge Gaps
- **62 isolated node(s):** `Return the module key for a given file path, or None if unrecognised.`, `File Name: app.py Author: Senthilnathan Karuppaiah Date: 11-JUL-2026 Description`, `LLM-2: pydantic-ai agent with the MCP server as its only toolset.`, `The one LLM-2 invocation per chat turn; wrapped so tests can stub it.`, `Stream a chat answer over SSE (ctms contract: content / done / error).` (+57 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 16`** (2 nodes): `main()`, `export-openapi.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 17`** (2 nodes): `index.js`, `callBackend()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 18`** (1 nodes): `smoke.mjs`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 19`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 20`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `run_analysis()` connect `Community 8` to `Community 0`, `Community 2`, `Community 4`, `Community 5`, `Community 6`, `Community 9`, `Community 10`?**
  _High betweenness centrality (0.210) - this node is a cross-community bridge._
- **Why does `JobReport` connect `Community 2` to `Community 1`, `Community 4`, `Community 5`, `Community 8`, `Community 9`, `Community 13`?**
  _High betweenness centrality (0.176) - this node is a cross-community bridge._
- **Why does `File Name: observability/__init__.py Author: Senthilnathan Karuppaiah Date: 11-J` connect `Community 2` to `Community 0`, `Community 8`, `Community 1`?**
  _High betweenness centrality (0.150) - this node is a cross-community bridge._
- **Are the 34 inferred relationships involving `JobReport` (e.g. with `File Name: test_pipeline_offline.py Author: Senthilnathan Karuppaiah Date: 11-JU` and `File Name: test_api.py Author: Senthilnathan Karuppaiah Date: 11-JUL-2026 Descri`) actually correct?**
  _`JobReport` has 34 INFERRED edges - model-reasoned connections that need verification._
- **Are the 25 inferred relationships involving `JobAnalysis` (e.g. with `File Name: test_pipeline_offline.py Author: Senthilnathan Karuppaiah Date: 11-JU` and `File Name: test_schema_conformance.py Author: Senthilnathan Karuppaiah Date: 11-`) actually correct?**
  _`JobAnalysis` has 25 INFERRED edges - model-reasoned connections that need verification._
- **Are the 18 inferred relationships involving `extract_resume_text()` (e.g. with `test_deterministic_pieces_standalone()` and `test_full_run_cover_letter_is_grounded_in_resume_text()`) actually correct?**
  _`extract_resume_text()` has 18 INFERRED edges - model-reasoned connections that need verification._
- **Are the 20 inferred relationships involving `SkillMatch` (e.g. with `File Name: test_pipeline_offline.py Author: Senthilnathan Karuppaiah Date: 11-JU` and `File Name: test_scoring_determinism.py Author: Senthilnathan Karuppaiah Date: 11`) actually correct?**
  _`SkillMatch` has 20 INFERRED edges - model-reasoned connections that need verification._