"""A-M2-4：录制回放契约测试。

对 fixtures/replay/*.json 里的每次真实（或待替换的种子）生成产物断言：
1. ReportInput.from_dict 能完整反序列化（schema 稳定）；
2. 渲染输出通过 validate_report 契约（五段齐全 + 引用密度 + 局限性说明）；
3. 渲染确定性（同一 fixture 两次渲染逐字节一致）。

真实 LLM 输出永远只进 fixture，不进本测试的执行路径——回归零闪断。
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from job_intel.citations import validate_report
from job_intel.template import ReportInput, render_report

REPLAY_DIR = Path(__file__).parent / "fixtures" / "replay"

FIXTURES = sorted(REPLAY_DIR.glob("*.json"))


def test_replay_fixtures_exist() -> None:
    assert FIXTURES, "replay fixtures missing — did the fixtures directory get committed?"


@pytest.mark.parametrize("fixture", FIXTURES, ids=lambda p: p.name)
def test_replay_contract(fixture: Path) -> None:
    payload = json.loads(fixture.read_text(encoding="utf-8"))
    report = ReportInput.from_dict(payload["report_input"])

    rendered = render_report(report)
    assert validate_report(rendered) == []
    assert render_report(report) == rendered  # 确定性
