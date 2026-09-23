"""A-M2-4：录制回放契约测试。

两类 fixture，统一走契约校验：
- ``kind=synthetic-seed``：结构化 ``report_input`` → 反序列化 + 渲染 + 校验；
- ``kind=real-recording``：真实 LLM 产出的 ``report_md`` 原文 → 直接契约校验。

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
    real = [f for f in FIXTURES if json.loads(f.read_text(encoding="utf-8")).get("kind") == "real-recording"]
    assert real, "no real recordings registered yet"


@pytest.mark.parametrize("fixture", FIXTURES, ids=lambda p: p.name)
def test_replay_contract(fixture: Path) -> None:
    payload = json.loads(fixture.read_text(encoding="utf-8"))

    if payload.get("kind") == "real-recording":
        report_md = payload["report_md"]
        assert validate_report(report_md) == []
        return

    report = ReportInput.from_dict(payload["report_input"])
    rendered = render_report(report)
    assert validate_report(rendered) == []
    assert render_report(report) == rendered  # 确定性
