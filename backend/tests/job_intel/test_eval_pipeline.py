"""A-M4-2：评估管线的单测与 golden 回归（fetch/标注全 mock，零网络）。"""

from __future__ import annotations

from pathlib import Path

import pytest

from job_intel.eval_pipeline import (
    load_jobs,
    load_relevant_labels,
    run_pipeline,
    write_results_csv,
)

FIX = Path(__file__).parent / "fixtures" / "evals"


def _fake_fetch(statuses: dict[str, int]):
    def fetch(url: str) -> int:
        if url in statuses:
            return statuses[url]
        raise TimeoutError(url)
    return fetch


def test_load_jobs_parses_and_validates() -> None:
    jobs = load_jobs(FIX / "eval-jobs.csv")
    assert [(j.company, j.report_file) for j in jobs] == [
        ("甲公司", "eval-report-a.md"),
        ("乙公司", "eval-report-b.md"),
    ]


def test_load_jobs_rejects_missing_fields(tmp_path: Path) -> None:
    bad = tmp_path / "bad.csv"
    bad.write_text("company,position,report_file\n,position,a.md\n", encoding="utf-8")
    with pytest.raises(ValueError, match="missing"):
        load_jobs(bad)


def test_load_relevant_labels_filters_ones() -> None:
    labels = load_relevant_labels(FIX / "labels.csv")
    assert labels == {"https://a.com", "https://e.com"}


def test_pipeline_rows_are_deterministic() -> None:
    statuses = {"https://a.com": 200, "https://e.com": 200, "https://b.com": 200}
    kwargs = dict(labels_csv=FIX / "labels.csv", fetch=_fake_fetch(statuses))
    rows1, summary1 = run_pipeline(FIX / "eval-jobs.csv", FIX, **kwargs)
    rows2, summary2 = run_pipeline(FIX / "eval-jobs.csv", FIX, **kwargs)
    assert rows1 == rows2 and summary1 == summary2
    assert rows1[0]["citations_effective"] == 2  # a.com 与 e.com 均可达+标注相关
    assert rows1[0]["violations"] == ""


def test_write_results_csv_matches_golden(tmp_path: Path) -> None:
    rows, summary = run_pipeline(
        FIX / "eval-jobs.csv", FIX,
        labels_csv=FIX / "labels.csv",
        fetch=_fake_fetch({"https://a.com": 200, "https://e.com": 200, "https://b.com": 200}),
    )
    out = tmp_path / "results.csv"
    write_results_csv(rows, summary, out)
    golden = (FIX / "golden" / "eval-results.csv").read_text(encoding="utf-8")
    assert out.read_text(encoding="utf-8") == golden


def test_pipeline_without_fetch_marks_unchecked() -> None:
    rows, _summary = run_pipeline(FIX / "eval-jobs.csv", FIX)
    assert rows[0]["citations_total"] > 0
    assert rows[0]["effectiveness_rate"] == ""  # 未检可达性，不出数字
