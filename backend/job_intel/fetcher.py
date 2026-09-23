"""数据源抓取解析（A-M3-1）：把搜索结果 JSON 与列表页 HTML 解析为统一结构。

本模块是纯函数集：只做解析，不做网络。HTTP 由调用方注入（生产接真实
抓取，测试用 fixture 字符串）——因此解析规则可以被 golden 精确回归。
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from html.parser import HTMLParser


@dataclass(frozen=True)
class SourceItem:
    """统一信源条目：所有上游格式归一到这个结构。"""

    title: str
    url: str
    snippet: str
    source: str


class _LinkExtractor(HTMLParser):
    """极简链接抽取器：收集 <a href> 及其锚文本；stdlib 实现，零外部依赖。"""

    def __init__(self, base_url: str) -> None:
        super().__init__(convert_charrefs=True)
        self._base = base_url.rstrip("/")
        self.links: list[tuple[str, str]] = []  # (absolute_url, anchor_text)
        self._in_a = False
        self._href = ""
        self._text_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "a":
            href = dict(attrs).get("href") or ""
            if href.startswith(("http://", "https://")):
                self._in_a = True
                self._href = href
                self._text_parts = []

    def handle_data(self, data: str) -> None:
        if self._in_a:
            self._text_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self._in_a:
            text = "".join(self._text_parts).strip()
            if text:
                self.links.append((self._href, text))
            self._in_a = False


def parse_search_results_json(raw: str | bytes, *, source: str, base_url: str = "") -> list[SourceItem]:
    """解析搜索结果 JSON（数组或 ``{"results": [...]}`` 包装）为统一结构。

    结构级错误（坏 JSON / 非对象数组）抛 ``ValueError``；单条缺字段的
    条目被跳过并计入坏行——单条脏数据不拖垮整批解析。
    """
    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ValueError(f"invalid search-result json: {exc}") from exc

    if isinstance(data, dict):
        data = data.get("results")
    if not isinstance(data, list):
        raise ValueError("search-result json must be a list or {results: [...]}")

    items: list[SourceItem] = []
    for entry in data:
        if not isinstance(entry, dict):
            continue
        url = str(entry.get("url") or entry.get("href") or "").strip()
        title = str(entry.get("title") or "").strip()
        if not url.startswith(("http://", "https://")) or not title:
            continue
        snippet = str(entry.get("snippet") or entry.get("content") or entry.get("description") or "").strip()
        items.append(SourceItem(title=title, url=url, snippet=snippet, source=source))
    return items


def parse_html_listing(raw_html: str, *, source: str, base_url: str) -> list[SourceItem]:
    """解析列表页 HTML：抽取带锚文本的外链为统一结构（标题即锚文本）。"""
    extractor = _LinkExtractor(base_url)
    try:
        extractor.feed(raw_html)
    except Exception as exc:  # noqa: BLE001 - 畸形 HTML 统一转为 ValueError
        raise ValueError(f"unparseable html listing: {exc}") from exc

    seen: set[str] = set()
    items: list[SourceItem] = []
    for url, title in extractor.links:
        if url in seen:
            continue
        seen.add(url)
        items.append(SourceItem(title=title, url=url, snippet="", source=source))
    return items


def parse_payload(raw: str, *, source: str, base_url: str = "https://example.com") -> list[SourceItem]:
    """按内容自动分派：JSON 以 ``{``/``[`` 开头走 JSON 解析，否则按 HTML。"""
    stripped = raw.lstrip()
    if stripped.startswith(("{", "[")):
        return parse_search_results_json(raw, source=source)
    return parse_html_listing(raw, source=source, base_url=base_url)
