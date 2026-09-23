"""A-M4-1：评估指标的单测（fetch 与人工标注全部 mock，零网络）。"""

from __future__ import annotations

from job_intel.metrics import (
    CitationAudit,
    audit_citations,
    structure_completeness,
    summarize,
)

REPORT = """\
# 岗位情报报告：测试公司 · Agent 研发

## 1. 业务线与技术栈画像
结论一 [citation:A](https://a.com)。

## 2. 近六个月技术与组织动态
结论二 [citation:B](https://b.com)。

## 3. 面经要点聚合
结论三 [citation:C](https://c.com)。

## 4. 薪资带宽估计（仅汇总公开数据）
结论四（推断）[citation:D](https://d.com)。

## 5. 与目标简历的差距分析
结论五 [citation:E](https://e.com)。

---
> 局限性说明：已标注推断。
"""


def _fake_fetch(statuses: dict[str, int]):
    def fetch(url: str) -> int:
        if url in statuses:
            return statuses[url]
        raise TimeoutError(url)
    return fetch


def test_audit_counts_effective_only_when_reachable_and_relevant() -> None:
    statuses = {"https://a.com": 200, "https://b.com": 200, "https://c.com": 404}
    relevant = {"https://a.com"}  # b 可达但人工标注不相关；c 死链
    audit = audit_citations(REPORT, fetch=_fake_fetch(statuses), relevant=relevant)
    assert audit.total == 5
    assert audit.reachable == {"https://a.com", "https://b.com"}
    assert audit.dead == {"https://c.com"}
    assert audit.unreachable == {"https://d.com", "https://e.com"}  # 网络失败≠死链
    assert audit.effective == 1
    assert audit.effectiveness_rate == round(1 / 5, 4)


def test_audit_empty_report_is_zero_not_crash() -> None:
    audit = audit_citations("no citations here", fetch=_fake_fetch({}))
    assert audit.total == 0 and audit.effectiveness_rate == 0.0


def test_audit_dedupes_urls() -> None:
    text = REPORT + "\n补充 [citation:A2](https://a.com)。"
    audit = audit_citations(text, fetch=_fake_fetch({"https://a.com": 200}), relevant={"https://a.com"})
    assert audit.total == 5  # a.com 重复引用只计一次


def test_structure_completeness_full_pass() -> None:
    rate, missing = structure_completeness(REPORT)
    assert rate == 1.0 and missing == []


def test_structure_completeness_detects_gaps() -> None:
    broken = REPORT.replace("## 3. 面经要点聚合\n结论三 [citation:C](https://c.com)。", "")
    rate, missing = structure_completeness(broken)
    assert rate < 1.0
    assert "面经要点聚合" in missing


def test_structure_completeness_counts_citation_density() -> None:
    thin = "\n".join(l for l in REPORT.splitlines() if "[citation:" not in l or "结论一" in l)
    rate, missing = structure_completeness(thin)
    assert any("inline_citations" in m for m in missing)


def test_summarize_uses_pooled_rate_not_mean_of_rates() -> None:
    a1 = CitationAudit(("u",), frozenset({"u"}), frozenset(), frozenset(), 1, 1, 1.0)
    a2 = CitationAudit(tuple(f"v{i}" for i in range(4)), frozenset(), frozenset(), frozenset(), 4, 0, 0.0)
    summary = summarize([a1, a2], [1.0, 0.5])
    assert summary.effectiveness_rate == round(1 / 5, 4)  # Σ/Σ，不是 (1.0+0.0)/2
    assert summary.mean_structure_completeness == 0.75
    assert summary.reports == 2 and summary.total_unique_urls == 5
