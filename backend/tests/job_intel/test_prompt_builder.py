"""A-M2-2：领域提示词组装的单测与 golden 快照。"""

from __future__ import annotations

from pathlib import Path

import pytest

from job_intel.prompt_builder import build_research_prompt

GOLDEN_DIR = Path(__file__).parent / "fixtures" / "golden"


def test_prompt_matches_golden() -> None:
    golden = (GOLDEN_DIR / "prompt_basic.txt").read_text(encoding="utf-8")
    prompt = build_research_prompt("字节跳动", "创意 Agent 技术研发", "2026-09-23")
    assert prompt == golden


def test_prompt_is_deterministic() -> None:
    a = build_research_prompt("字节跳动", "Agent 研发", "2026-09-23")
    b = build_research_prompt("字节跳动", "Agent 研发", "2026-09-23")
    assert a == b


@pytest.mark.parametrize("company,position", [("", "x"), ("  ", "x"), ("字节", "")])
def test_blank_inputs_rejected(company: str, position: str) -> None:
    with pytest.raises(ValueError):
        build_research_prompt(company, position, "2026-09-23")


def test_bad_date_rejected() -> None:
    with pytest.raises(ValueError, match="YYYY-MM-DD"):
        build_research_prompt("字节跳动", "Agent 研发", "20260923")


def test_prompt_states_citation_contract() -> None:
    """契约关键词必须出现在提示词里——这是回放契约测试的上游保证。"""
    prompt = build_research_prompt("字节跳动", "Agent 研发", "2026-09-23")
    assert "[citation:" in prompt
    assert "局限性说明" in prompt
    assert "五个章节" in prompt
