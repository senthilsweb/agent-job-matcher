"""
File Name: test_mixed_failure_run.py
Author: Senthilnathan Karuppaiah
Date: 11-JUL-2026
Description:
Live mixed-failure eval (real model + the two genuine JS-shell
captures) — evals/rubrics.md "fetch guards / mixed failure": failures
are logged, stopped, and isolated; healthy jobs complete.

This suite pins the behaviour by:
1. HARD — 1 ok + 2 failure fixtures → 1 JobReport + 2 JobFetchFailures;
   exactly ONE analysis call (failed sources never reach the LLM);
   fetch-attempts.json shows exactly one attempt per source.
2. HARD — an all-failed run completes with failure outcomes and zero
   LLM calls — not a crash, not a fabricated report.
"""

# Import necessary libraries
import json

import pytest

from job_matcher.schemas import JobFetchFailure, JobReport
from tests.live.conftest import BROKEN_1, BROKEN_2, JD_GUSTO, run_live_counted

pytestmark = pytest.mark.live


def test_hard_mixed_run_isolates_failures(tmp_path):
    result, calls = run_live_counted(
        [str(JD_GUSTO), str(BROKEN_1), str(BROKEN_2)], out_dir=tmp_path
    )
    reports = [o for o in result.outcomes if isinstance(o, JobReport)]
    failures = [o for o in result.outcomes if isinstance(o, JobFetchFailure)]
    assert len(reports) == 1 and len(failures) == 2
    assert len(calls) == 1, "a failed fetch reached the LLM"
    assert all("extractable words" in f.reason for f in failures)

    attempts = json.loads((result.run_dir / "jobs" / "fetch-attempts.json").read_text())
    assert len(attempts) == 3  # exactly one attempt per source, no retries
    assert sum(a["status"] == "failed" for a in attempts) == 2

    failed_files = list(result.run_dir.glob("*.failed.json"))
    assert len(failed_files) == 2


def test_hard_all_failed_run_completes_without_llm(tmp_path):
    result, calls = run_live_counted([str(BROKEN_1), str(BROKEN_2)], out_dir=tmp_path)
    assert all(isinstance(o, JobFetchFailure) for o in result.outcomes)
    assert calls == []
    assert (result.run_dir / "results.json").is_file()
