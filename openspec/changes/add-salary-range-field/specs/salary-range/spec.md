# Spec: `salary_range` extraction and display

## Requirement: `JobAnalysis.salary_range` is optional and verbatim
`JobAnalysis` SHALL carry `salary_range: str | None`, defaulting to
`None`. When populated, the value SHALL be copied verbatim from the job
posting text — the model SHALL NOT estimate, infer, or unit-convert a
range that is stated differently, and SHALL NOT fabricate one when the
posting states none.

## Requirement: Not a scoring input, not evidence-grounded
`salary_range` SHALL NOT participate in `scoring.py`'s rubric — it is
purely informational. Unlike `SkillMatch.evidence`, it is not required
to be grounded against the resume (it describes the job posting, not
the candidate) and carries no matched/unmatched cross-validation rule.

## Requirement: Displayed prominently, not buried
Any surface rendering a `JobReport` visually (the playground) SHALL
show a present `salary_range` in the compact/collapsed view, not only
inside an expanded detail panel. An absent value SHALL render nothing
— no placeholder text implying a gap in extraction.
