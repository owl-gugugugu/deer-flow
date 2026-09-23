"""A-M3-2：切块/检索/上下文预算的单测与 golden 回归。

golden 检索基线的意义：M4 评估（20 岗位引用有效率）的增量都要对照
这份固定输入→固定检索结果来度量。
"""

from __future__ import annotations

from pathlib import Path

import pytest

from job_intel.aggregate import (
    DEFAULT_MAX_CHARS,
    build_context,
    chunk_items,
    chunk_text,
    keyword_score,
    retrieve,
)
from job_intel.fetcher import SourceItem

GOLDEN_DIR = Path(__file__).parent / "fixtures" / "golden"


def _sample_items() -> list[SourceItem]:
    return [
        SourceItem(
            title="字节 2027 校招 Flow Agent 岗",
            url="https://jobs.bytedance.com/flow-agent",
            snippet="负责豆包创意 Agent 技术研发，Multi-Agent 框架与评测机制建设。",
            source="web",
        ),
        SourceItem(
            title="牛客面经：Agent 岗手撕真题",
            url="https://www.nowcoder.com/discuss/900446",
            snippet="手撕合并 K 个升序链表；追问 Function Calling 与 MCP 的区别。",
            source="nowcoder",
        ),
        SourceItem(
            title="无关条目",
            url="https://example.com/unrelated",
            snippet="今天天气不错，适合出门散步。",
            source="web",
        ),
    ]


# ---------- chunk_text ----------

def test_chunk_empty_and_short() -> None:
    assert chunk_text("") == []
    assert chunk_text("   ") == []
    assert chunk_text("短文本") == ["短文本"]


def test_chunk_paragraph_merge_respects_limit() -> None:
    paras = "A" * 200 + "\n\n" + "B" * 200
    chunks = chunk_text(paras, max_chars=DEFAULT_MAX_CHARS)
    assert chunks == [paras]  # 400 < 500，合并为一块


def test_chunk_merges_until_limit_then_splits() -> None:
    paras = "A" * 300 + "\n\n" + "B" * 300
    chunks = chunk_text(paras, max_chars=500, overlap=0)
    assert chunks == ["A" * 300, "B" * 300]


def test_chunk_hard_split_with_overlap() -> None:
    text = "X" * 1200
    chunks = chunk_text(text, max_chars=500, overlap=60)
    assert [len(c) for c in chunks] == [500, 500, 320]
    # 相邻块重叠 60 字符
    assert chunks[0][440:] == chunks[1][:60]
    assert chunks[1][440:] == chunks[2][:60]
    # 覆盖完整性：去掉重叠后拼接应等于原文
    assert chunks[0] + chunks[1][60:] + chunks[2][60:] == text


def test_chunk_rejects_bad_overlap() -> None:
    with pytest.raises(ValueError, match="overlap"):
        chunk_text("x" * 1000, max_chars=100, overlap=100)


# ---------- retrieve / build_context ----------

def test_keyword_score_ordering() -> None:
    assert keyword_score("agent 面经", "agent 岗位面经真题") > keyword_score("agent 面经", "天气不错")
    assert keyword_score("", "x") == 0.0


def test_retrieve_ranks_relevant_first_and_stable() -> None:
    chunks = chunk_items(_sample_items())
    blocks = retrieve("agent 面经", chunks, top_k=3)
    titles = [b.chunk.item.title for b in blocks]
    # 相关块在前，无关块垫底
    assert titles[-1] == "无关条目"
    assert set(titles[:2]) == {"字节 2027 校招 Flow Agent 岗", "牛客面经：Agent 岗手撕真题"}
    # 确定性：再跑一次完全一致
    assert retrieve("agent 面经", chunks, top_k=3) == blocks


def test_build_context_matches_golden() -> None:
    """golden 检索基线：M4 评估的对照锚点。"""
    golden = (GOLDEN_DIR / "context-flow-agent.txt").read_text(encoding="utf-8")
    bundle = build_context(
        "字节跳动 Flow 团队 Agent 岗位 面试 考察点",
        _sample_items(),
        top_k=4,
        budget_chars=2000,
    )
    assert bundle.text == golden


def test_build_context_respects_budget() -> None:
    bundle = build_context("agent", _sample_items(), top_k=5, budget_chars=150)
    assert sum(len(b.chunk.text) + 40 for b in bundle.blocks) <= 150
    assert len(bundle.blocks) >= 1  # 至少保住一块


def test_chunk_items_preserves_provenance() -> None:
    chunks = chunk_items(_sample_items())
    assert all(c.item.url for c in chunks)
    first_item_chunks = [c for c in chunks if c.item.source == "web" and "校招" in c.item.title]
    assert [c.index for c in first_item_chunks] == list(range(len(first_item_chunks)))
