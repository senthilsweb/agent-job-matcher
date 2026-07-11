"""
File Name: test_single_and_multi_job.py
Author: Senthilnathan Karuppaiah
Date: 11-JUL-2026
Description:
Live fan-out eval (real model) — evals/rubrics.md "single & multi job":
N sources → N outcomes and exactly one analysis call per fetched job
(call-count spy replaces Eve's child-session counting).

This suite pins fan-out by:
1. HARD — 1 JD → exactly 1 outcome and exactly 1 analysis call.
2. HARD — 3 JDs → 3 report outcomes, 3 analysis calls (one per index),
   ranking.md ordered by descending total_score, results.json parses as
   the typed array.
3. SOFT — bands for the real corpus recorded for the rubric's
   recalibration table.
"""

# Import necessary libraries
import json

import pytest
import structlog

from job_matcher.report import REPORT_FILENAME_RE
from job_matcher.schemas import JobReport
from tests.live.conftest import JD_ANTHROPIC, JD_BAIN, JD_TEMPORAL, run_live_counted

pytestmark = pytest.mark.live
log = structlog.get_logger("live-evals")


def test_hard_single_job_single_call(tmp_path):
    result, calls = run_live_counted([str(JD_ANTHROPIC)], out_dir=tmp_path)
    assert len(result.outcomes) == 1
    assert isinstance(result.outcomes[0], JobReport)
    assert len(calls) == 1


def test_hard_multi_job_fanout_and_ranking(tmp_path):
    result, calls = run_live_counted(
        [str(JD_ANTHROPIC), str(JD_BAIN), str(JD_TEMPORAL)], out_dir=tmp_path
    )
    reports = [o for o in result.outcomes if isinstance(o, JobReport)]
    assert len(reports) == 3, f"expected 3 reports, got {result.outcomes}"
    assert sorted(calls) == [0, 1, 2]  # exactly one analysis call per job

    run_dir = result.run_dir
    per_job = [p.name for p in run_dir.glob("*_*.json") if p.name not in ("results.json", "summary.json")]
    assert len(per_job) == 3 and all(REPORT_FILENAME_RE.match(n) for n in per_job)

    # ranking.md ordered by descending total_score
    ranking = (run_dir / "ranking.md").read_text()
    scores_in_order = [
        int(line.split("|")[4].strip())
        for line in ranking.splitlines()
        if line.startswith("|") and line.split("|")[4].strip().isdigit()
    ]
    assert scores_in_order == sorted(scores_in_order, reverse=True)

    results = json.loads((run_dir / "results.json").read_text())
    assert len(results) == 3 and all(r["fetch_status"] == "ok" for r in results)

    for r in reports:
        log.info("soft_observation", eval="corpus_band",
                 job=r.analysis.job_title, company=r.analysis.company_name,
                 total=r.score_breakdown.total_score, band=r.match_status)
