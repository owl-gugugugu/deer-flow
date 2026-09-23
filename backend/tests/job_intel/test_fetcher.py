"""A-M3-1：数据源解析的单测（全部使用 fixture 字符串，零网络）。"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from job_intel.fetcher import parse_html_listing, parse_payload, parse_search_results_json

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "sources"


def _load(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_parse_search_results_json_basic() -> None:
    items = parse_search_results_json(_load("search-results.json"), source="web")
    assert len(items) == 3
    assert items[0].title == "字节跳动 2027 届校招 Flow 团队 Agent 岗"
    assert items[0].url.startswith("https://jobs.bytedance.com")
    assert items[0].source == "web"
    assert items[1].snippet == "牛客网面经：手撕合并 K 个升序链表"


def test_parse_search_results_json_wrapper_form() -> None:
    items = parse_search_results_json(_load("search-results-wrapped.json"), source="web")
    assert [i.url for i in items] == ["https://example.com/a", "https://example.com/b"]


def test_parse_bad_json_raises() -> None:
    with pytest.raises(ValueError, match="invalid search-result json"):
        parse_search_results_json("{not-json", source="web")


def test_parse_non_list_json_raises() -> None:
    with pytest.raises(ValueError, match="list"):
        parse_search_results_json('{"foo": "bar"}', source="web")


def test_parse_tolerates_individual_bad_entries() -> None:
    raw = json.dumps(
        [
            {"title": "ok", "url": "https://example.com/ok", "snippet": "s"},
            {"title": "no-url"},
            {"url": "https://example.com/no-title"},
            "garbage-string-entry",
            {"title": "ftp-entry", "url": "ftp://x", "snippet": "s"},
        ],
        ensure_ascii=False,
    )
    items = parse_search_results_json(raw, source="web")
    assert [i.url for i in items] == ["https://example.com/ok"]


def test_parse_html_listing_extracts_links() -> None:
    items = parse_html_listing(
        _load("listing.html"), source="github-calendar", base_url="https://github.com/x"
    )
    urls = [i.url for i in items]
    assert "https://github.com/example/campus2027" in urls
    assert "https://nowcoder.com/feed" in urls
    # 无锚文本的链接被丢弃
    assert "https://example.com/anchorless" not in urls
    assert items[0].title == "2027 届校招日历"


def test_parse_html_dedupes_repeated_links() -> None:
    items = parse_html_listing(
        '<a href="https://a.com">x</a><a href="https://a.com">x</a>',
        source="s",
        base_url="https://b.com",
    )
    assert len(items) == 1


def test_parse_payload_dispatches_by_shape() -> None:
    as_json = parse_payload('{"results": [{"title": "t", "url": "https://e.com"}]}', source="web")
    as_html = parse_payload("<a href=\"https://e.com\">t</a>", source="web", base_url="https://b.com")
    assert len(as_json) == 1 and len(as_html) == 1
    assert as_json[0].url == as_html[0].url == "https://e.com"
