# Graph Report - /Users/krs/work/agent-job-matcher  (2026-07-11)

## Corpus Check
- 5 files · ~16,135 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 79 nodes · 125 edges · 9 communities detected
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 2 edges (avg confidence: 0.8)
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

## God Nodes (most connected - your core abstractions)
1. `render_dashboard()` - 10 edges
2. `main()` - 9 edges
3. `main()` - 6 edges
4. `get_analysis_prompt()` - 5 edges
5. `format_cover_letter()` - 5 edges
6. `format_cover_letter()` - 5 edges
7. `get_analysis_prompt()` - 5 edges
8. `create_agent()` - 5 edges
9. `render_template()` - 4 edges
10. `load_prompt()` - 4 edges

## Surprising Connections (you probably didn't know these)
- `main()` --calls--> `create_agent()`  [INFERRED]
  /Users/krs/work/agent-job-matcher/backend/job_fit_from_files.py → /Users/krs/work/agent-job-matcher/backend/app.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.18
Nodes (15): FullReport, generate_docx(), generate_md(), generate_pdf(), get_status_class(), get_status_emoji(), Job Fit Analyzer - Production Version Clean, consolidated app with deterministic, Generate PDF from text. (+7 more)

### Community 1 - "Community 1"
Cohesion: 0.14
Nodes (15): analyze(), fetch_job_description(), format_cover_letter(), get_analysis_prompt(), JobFitReport, load_template(), main(), Format cover letter using external template. (+7 more)

### Community 2 - "Community 2"
Cohesion: 0.31
Nodes (8): MatchStatus, MatchStatus, Enum, build_index(), main(), module_for(), Return the module key for a given file path, or None if unrecognised., str

### Community 3 - "Community 3"
Cohesion: 0.39
Nodes (7): analyze(), get_analysis_prompt(), get_system_prompt(), load_prompt(), Load prompt from prompts folder., Load system prompt from external file., Load and render analysis prompt from external file.

### Community 4 - "Community 4"
Cohesion: 0.25
Nodes (8): CoverLetterContent, ScoreBreakdown, SkillMatch, BaseModel, CoverLetterContent, JobFitReport, ScoreBreakdown, SkillMatch

### Community 5 - "Community 5"
Cohesion: 0.25
Nodes (7): create_agent(), get_system_prompt(), load_prompt(), Load system prompt from external file., Create analysis agent., Load prompt from prompts folder., main()

### Community 6 - "Community 6"
Cohesion: 0.29
Nodes (7): fetch_job_description(), FullReport, main(), Complete report with all input and output data., Fetch and parse job description from URL., Parse resume from file., read_resume()

### Community 7 - "Community 7"
Cohesion: 0.33
Nodes (6): format_cover_letter(), load_template(), Format cover letter using external template., Render mustache-style template with {{variable}} placeholders., Load template from templates folder., render_template()

### Community 8 - "Community 8"
Cohesion: 1.0
Nodes (0): 

## Knowledge Gaps
- **26 isolated node(s):** `Render mustache-style template with {{variable}} placeholders.`, `Load template from templates folder.`, `Load prompt from prompts folder.`, `Load system prompt from external file.`, `Load and render analysis prompt from external file.` (+21 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 8`** (2 nodes): `main()`, `graphify-build.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `main()` connect `Community 1` to `Community 0`, `Community 2`, `Community 5`?**
  _High betweenness centrality (0.083) - this node is a cross-community bridge._
- **Why does `create_agent()` connect `Community 5` to `Community 0`, `Community 1`?**
  _High betweenness centrality (0.075) - this node is a cross-community bridge._
- **What connects `Render mustache-style template with {{variable}} placeholders.`, `Load template from templates folder.`, `Load prompt from prompts folder.` to the rest of the system?**
  _26 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.14 - nodes in this community are weakly interconnected._