"""job-intel 数据源社区工具：把确定性 RAG 层暴露为 DeerFlow Agent 工具。

设计边界：本模块只做薄适配——真正的解析/检索/预算逻辑都在
``job_intel``（backend/job_intel）独立包里，可脱离 DeerFlow 单测。
"""

from __future__ import annotations

import json
import logging

from langchain.tools import tool

from job_intel import build_context, parse_payload, validate_report

logger = logging.getLogger(__name__)


@tool
def job_intel_build_context(query: str, sources_json: str) -> str:
    """Build a citation-ready research context from job-intel sources.

    Args:
        query: the research question to rank source chunks against.
        sources_json: JSON array of sources, each with title/url/snippet/source.

    Returns:
        Rendered context text with per-block [n] title (url) attribution.
    """
    try:
        raw_sources = json.loads(sources_json)
    except json.JSONDecodeError as exc:
        return f"Error: sources_json is not valid JSON: {exc}"
    if not isinstance(raw_sources, list):
        return "Error: sources_json must be a JSON array"

    from job_intel.fetcher import SourceItem

    items = [
        SourceItem(
            title=str(s.get("title", ""))[:200],
            url=str(s.get("url", "")),
            snippet=str(s.get("snippet", ""))[:2000],
            source=str(s.get("source", "web")),
        )
        for s in raw_sources
        if isinstance(s, dict) and str(s.get("url", "")).startswith(("http://", "https://"))
    ]
    if not items:
        return "Error: no valid sources after parsing"
    return build_context(query, items, top_k=6, budget_chars=2400).text


@tool
def job_intel_validate_report(report_md: str) -> str:
    """Validate a job-intel report against the citation contract.

    Args:
        report_md: full markdown report text.

    Returns:
        "PASS" when the report satisfies the five-section/citation contract,
        otherwise a newline-joined list of violations.
    """
    violations = validate_report(report_md)
    return "PASS" if not violations else "FAIL:\n" + "\n".join(violations)
