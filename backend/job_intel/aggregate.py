"""检索聚合层（A-M3-2）：切块 → 打分检索 → 上下文预算，RAG 三件套。

确定性契约：ranker 注入后，同样的输入永远得到同样的检索结果——这是
M4 评估的对照基线（20 岗位引用有效率要在此基础上测增量）。
"""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass

from job_intel.fetcher import SourceItem

#: 单块默认上限：对齐常见 embedding 输入窗口的保守值。
DEFAULT_MAX_CHARS = 500
#: 相邻块默认重叠：段落切断时保留尾部上下文。
DEFAULT_OVERLAP = 60
#: 默认检索条数。
DEFAULT_TOP_K = 5


def keyword_score(query: str, text: str) -> float:
    """默认排序器：查询词项重叠率（大小写归一，纯确定性，零依赖）。"""
    if not query.strip() or not text.strip():
        return 0.0
    terms = [t for t in re.split(r"\s+", query.lower()) if t]
    if not terms:
        return 0.0
    haystack = text.lower()
    return sum(1.0 for t in terms if t in haystack) / len(terms)


def chunk_text(
    text: str,
    *,
    max_chars: int = DEFAULT_MAX_CHARS,
    overlap: int = DEFAULT_OVERLAP,
) -> list[str]:
    """段落优先合并切块；超长段落硬切并保留 overlap 尾部。

    - 空文本 → 空列表；
    - 短文本 → 原样单块；
    - 段落合并时不跨越 max_chars；单段落超限时硬切，块间重叠 overlap 字符。
    """
    if not text or not text.strip():
        return []
    if overlap < 0 or overlap >= max_chars:
        raise ValueError(f"overlap must be in [0, max_chars): {overlap}")
    text = text.strip()
    if len(text) <= max_chars:
        return [text]

    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: list[str] = []
    buf = ""
    for para in paragraphs:
        while len(para) > max_chars:
            if buf:
                chunks.append(buf)
                buf = ""
            chunks.append(para[:max_chars])
            para = para[max_chars - overlap:]
        if len(buf) + len(para) + (2 if buf else 0) <= max_chars:
            buf = f"{buf}\n\n{para}" if buf else para
        else:
            if buf:
                chunks.append(buf)
            buf = para
    if buf:
        chunks.append(buf)
    return chunks


@dataclass(frozen=True)
class Chunk:
    """带溯源的块：检索结果必须能指回信源条目。"""

    text: str
    item: SourceItem
    index: int  # 在该信源内的块序号


@dataclass(frozen=True)
class ContextBlock:
    """进入最终上下文的一块，附带检索分（评估口径用）。"""

    chunk: Chunk
    score: float


@dataclass(frozen=True)
class ContextBundle:
    """最终注入提示词的上下文包：渲染文本 + 结构化块。"""

    blocks: tuple[ContextBlock, ...]
    budget_chars: int

    @property
    def text(self) -> str:
        parts = [
            f"[{i + 1}] {b.chunk.item.title} ({b.chunk.item.url})\n{b.chunk.text}"
            for i, b in enumerate(self.blocks)
        ]
        return "\n\n".join(parts)


def chunk_items(items: list[SourceItem], *, max_chars: int = DEFAULT_MAX_CHARS, overlap: int = DEFAULT_OVERLAP) -> list[Chunk]:
    """把信源条目全部切块并保留溯源。"""
    chunks: list[Chunk] = []
    for item in items:
        for i, piece in enumerate(chunk_text(f"{item.title}\n{item.snippet}".strip(), max_chars=max_chars, overlap=overlap)):
            chunks.append(Chunk(text=piece, item=item, index=i))
    return chunks


def retrieve(
    query: str,
    chunks: list[Chunk],
    *,
    ranker: Callable[[str, str], float] = keyword_score,
    top_k: int = DEFAULT_TOP_K,
) -> list[ContextBlock]:
    """打分 → 取 top-k；同分按原始顺序稳定排序（确定性铁律）。"""
    scored = [(ranker(query, c.text), order, c) for order, c in enumerate(chunks)]
    scored.sort(key=lambda t: (-t[0], t[1]))
    return [ContextBlock(chunk=c, score=s) for s, _, c in scored[:top_k]]


def build_context(
    query: str,
    items: list[SourceItem],
    *,
    ranker: Callable[[str, str], float] = keyword_score,
    top_k: int = DEFAULT_TOP_K,
    max_chars: int = DEFAULT_MAX_CHARS,
    overlap: int = DEFAULT_OVERLAP,
    budget_chars: int = 2000,
) -> ContextBundle:
    """端到端：切块 → 检索 → 按 budget 截断（整块保留，不截半块）。"""
    blocks = retrieve(query, chunk_items(items, max_chars=max_chars, overlap=overlap), ranker=ranker, top_k=top_k)
    kept: list[ContextBlock] = []
    used = 0
    for block in blocks:
        cost = len(block.chunk.text) + 40  # 标题+URL+分隔的保守开销
        if used + cost > budget_chars:
            continue
        kept.append(block)
        used += cost
    return ContextBundle(blocks=tuple(kept), budget_chars=budget_chars)
