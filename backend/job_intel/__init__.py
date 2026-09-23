"""job-intel: 岗位情报深研助手的确定性渲染与校验管道（deer-flow 二开）。

设计边界：LLM 只负责产出各段正文文本；本包内的所有模块都是确定性代码——
同样的输入永远得到逐字节相同的输出，因此可以被 golden 快照精确回归。
"""

from job_intel.aggregate import (
    ContextBlock,
    ContextBundle,
    Chunk,
    build_context,
    chunk_items,
    chunk_text,
    keyword_score,
    retrieve,
)
from job_intel.citations import check_links, extract_inline, validate_report
from job_intel.fetcher import SourceItem, parse_html_listing, parse_payload, parse_search_results_json
from job_intel.template import MIN_CITATIONS, SECTION_ORDER, ReportInput, render_report

__all__ = [
    "MIN_CITATIONS",
    "SECTION_ORDER",
    "Chunk",
    "ContextBlock",
    "ContextBundle",
    "ReportInput",
    "SourceItem",
    "build_context",
    "check_links",
    "chunk_items",
    "chunk_text",
    "extract_inline",
    "keyword_score",
    "parse_html_listing",
    "parse_payload",
    "parse_search_results_json",
    "render_report",
    "retrieve",
    "validate_report",
]
