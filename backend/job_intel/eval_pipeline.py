"""评估管线（A-M4-2）：岗位清单 × 报告目录 → 确定性指标 CSV。

确定性契约：同样的输入（报告 + 抓取结果 + 人工标注）永远得到逐字节
相同的 CSV——评估结果因此可回放、可审计、可对照增量。
"""

from __future__ import annotations

import csv
import re
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from job_intel.citations import validate_report
from job_intel.metrics import CitationAudit, audit_citations, structure_completeness, summarize

_INLINE_URL = re.compile(r"\[citation:[^\]]+\]\((https?://[^)\s]+)\)")


def _unique_urls(md: str) -> tuple[str, ...]:
    """按出现顺序去重的内联引用 URL（纯文本解析，零网络）。"""
    return tuple(dict.fromkeys(m.group(1) for m in _INLINE_URL.finditer(md)))

RESULT_FIELDS = (
    "company",
    "position",
    "report_file",
    "citations_total",
    "citations_reachable",
    "citations_dead",
    "citations_unreachable",
    "reachability_rate",
    "citations_effective",
    "effectiveness_rate",
    "structure_completeness",
    "violations",
)


@dataclass(frozen=True)
class JobEntry:
    company: str
    position: str
    report_file: str


def load_jobs(csv_path: Path) -> list[JobEntry]:
    """读岗位清单 CSV（表头：company,position,report_file）。"""
    with open(csv_path, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    jobs = []
    for row in rows:
        company = (row.get("company") or "").strip()
        report_file = (row.get("report_file") or "").strip()
        if not company or not report_file:
            raise ValueError(f"job row missing company/report_file: {row!r}")
        jobs.append(JobEntry(company=company, position=(row.get("position") or "").strip(), report_file=report_file))
    return jobs


def load_relevant_labels(csv_path: Path | None) -> set[str]:
    """读人工标注 CSV（表头：url,relevant，relevant∈{0,1}）；仅 relevant=1 入池。"""
    if csv_path is None:
        return set()
    with open(csv_path, encoding="utf-8", newline="") as f:
        return {
            row["url"].strip()
            for row in csv.DictReader(f)
            if (row.get("relevant") or "").strip() == "1"
        }


def run_pipeline(
    jobs_csv: Path,
    reports_dir: Path,
    *,
    labels_csv: Path | None = None,
    fetch: Callable[[str], int] | None = None,
) -> tuple[list[dict[str, object]], object]:
    """跑批量评估，返回（逐报告行, 汇总）。``fetch=None`` 时可达性记为未检。"""
    jobs = load_jobs(jobs_csv)
    relevant = load_relevant_labels(labels_csv)
    rows: list[dict[str, object]] = []
    audits: list[CitationAudit] = []
    completeness: list[float] = []

    for job in jobs:
        report_path = reports_dir / job.report_file
        md = report_path.read_text(encoding="utf-8")
        violations = validate_report(md)

        if fetch is None:
            # 未提供 fetch：只做纯文本统计，可达性相关字段记 0（rate 留空）
            urls = _unique_urls(md)
            audit = CitationAudit(
                unique_urls=urls, reachable=frozenset(), dead=frozenset(), unreachable=frozenset(),
                total=len(urls), effective=0, effectiveness_rate=0.0,
            )
        else:
            audit = audit_citations(md, fetch=fetch, relevant=relevant)

        rate, missing = structure_completeness(md)
        if missing:
            violations = list(violations) + [f"structure-missing:{m}" for m in missing]
        audits.append(audit)
        completeness.append(rate)
        rows.append({
            "company": job.company,
            "position": job.position,
            "report_file": job.report_file,
            "citations_total": audit.total,
            "citations_reachable": len(audit.reachable),
            "citations_dead": len(audit.dead),
            "citations_unreachable": len(audit.unreachable),
            "reachability_rate": audit.reachability_rate if fetch is not None else "",
            "citations_effective": audit.effective,
            "effectiveness_rate": audit.effectiveness_rate if fetch is not None else "",
            "structure_completeness": rate,
            "violations": ";".join(violations),
        })

    return rows, summarize(audits, completeness)


def write_results_csv(rows: list[dict[str, object]], summary: object, out_path: Path) -> None:
    """写出确定性结果 CSV：数据行 + 汇总行，字段顺序恒定。"""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(RESULT_FIELDS))
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
        summary_row = {field: "" for field in RESULT_FIELDS}
        summary_row.update({
            "company": "SUMMARY",
            "citations_total": summary.total_unique_urls,  # type: ignore[attr-defined]
            "citations_reachable": summary.total_reachable,  # type: ignore[attr-defined]
            "citations_effective": summary.total_effective,  # type: ignore[attr-defined]
            "reachability_rate": summary.reachability_rate,  # type: ignore[attr-defined]
            "effectiveness_rate": summary.effectiveness_rate,  # type: ignore[attr-defined]
            "structure_completeness": summary.mean_structure_completeness,  # type: ignore[attr-defined]
        })
        writer.writerow(summary_row)
