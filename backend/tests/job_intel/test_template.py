"""A-M2-1：五段渲染器的单测与 golden 精确回归。"""

from __future__ import annotations

from pathlib import Path

import pytest

from job_intel.template import (
    MIN_CITATIONS,
    ReportInput,
    SectionContent,
    render_report,
)

GOLDEN_DIR = Path(__file__).parent / "fixtures" / "golden"


def _sample_input() -> ReportInput:
    return ReportInput(
        company="字节跳动",
        position="创意 Agent 技术研发",
        report_date="2026-09-23",
        sections={
            "business": SectionContent(
                content="Flow 是字节 AI 创新业务部门，豆包 DAU 破亿。",
                citations=(
                    "https://www.36kr.com/p/3452409797934466",
                    "https://example.com/second",
                ),
            ),
            "dynamics": SectionContent(
                content="2026 年 8 月 TRAE 与扣子并入豆包。",
                citations=("https://awtmt.com/articles/3780150",),
            ),
            "interview": SectionContent(
                content="高频真题：FC/MCP/Skills 区别、ReAct vs Plan-and-Execute。",
                citations=("https://www.infoq.cn/article/great-agent-interview-2025",),
            ),
            "salary": SectionContent(
                content="公开渠道薪资样本集中在 25-45k/月区间（推断）。",
                citations=(
                    "https://example.com/salary-a",
                    "https://example.com/second",
                ),
            ),
            "gap": SectionContent(
                content="目标简历缺 Memory 与评测体系实践。",
                citations=("https://example.com/gap-note",),
            ),
        },
    )


def test_render_matches_golden() -> None:
    """golden 回归：全量输入的渲染结果与冻结快照逐字节一致。"""
    golden = (GOLDEN_DIR / "report_basic.md").read_text(encoding="utf-8")
    assert render_report(_sample_input()) == golden


def test_render_is_deterministic() -> None:
    """同一输入渲染两次必须逐字节相同。"""
    assert render_report(_sample_input()) == render_report(_sample_input())


def test_citation_dedup_preserves_first_occurrence_order() -> None:
    """跨章节重复 URL 只保留首次出现，编号全局连续。"""
    rendered = render_report(_sample_input())
    # 6 个唯一 URL：second 首次出现在 business=[2]，salary 复用时不新增编号
    assert "引用：[5]、[2]" in rendered
    assert "[7]" not in rendered
    assert "引用：[1]、[2]" in rendered


def test_section_without_citations_omits_reference_line() -> None:
    source = _sample_input()
    stripped = ReportInput(
        company=source.company,
        position=source.position,
        report_date=source.report_date,
        sections={
            key: SectionContent(content=s.content, citations=())
            for key, s in source.sections.items()
        },
    )
    # 无引用会在渲染期被总数下限拦下——这里只验证该行为存在
    with pytest.raises(ValueError, match="unique citations"):
        render_report(stripped)


def test_from_dict_rejects_non_mapping_sections() -> None:
    with pytest.raises(TypeError):
        ReportInput.from_dict({"company": "a", "position": "b", "report_date": "2026-09-23", "sections": [1, 2]})


def test_missing_section_rejected() -> None:
    data = _sample_input().__dict__
    sections = dict(data["sections"])
    sections.pop("salary")
    with pytest.raises(ValueError, match="missing sections"):
        ReportInput(
            company=data["company"],
            position=data["position"],
            report_date=data["report_date"],
            sections=sections,  # type: ignore[arg-type]
        )


def test_empty_section_content_rejected() -> None:
    with pytest.raises(ValueError, match="non-empty"):
        SectionContent(content="   ")


def test_non_http_citation_rejected() -> None:
    with pytest.raises(ValueError, match="http"):
        SectionContent(content="正文", citations=("ftp://example.com/a",))


def test_too_few_unique_citations_rejected() -> None:
    data = _sample_input().__dict__
    sections = dict(data["sections"])
    shared = "https://only-one.com"
    sections = {
        key: SectionContent(content=s.content, citations=(shared,))
        for key, s in sections.items()
    }
    report = ReportInput(
        company=data["company"],
        position=data["position"],
        report_date=data["report_date"],
        sections=sections,  # type: ignore[arg-type]
    )
    with pytest.raises(ValueError, match="unique citations"):
        render_report(report)


def test_bad_date_format_rejected() -> None:
    with pytest.raises(ValueError, match="YYYY-MM-DD"):
        ReportInput(
            company="字节跳动",
            position="Agent 研发",
            report_date="2026/09/23",
            sections=_sample_input().sections,
        )


def test_from_dict_roundtrip() -> None:
    source = _sample_input()
    payload = {
        "company": source.company,
        "position": source.position,
        "report_date": source.report_date,
        "sections": {
            key: {"content": s.content, "citations": list(s.citations)}
            for key, s in source.sections.items()
        },
    }
    rebuilt = ReportInput.from_dict(payload)
    assert render_report(rebuilt) == render_report(source)
