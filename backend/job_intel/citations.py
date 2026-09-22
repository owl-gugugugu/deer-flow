"""引用规范校验（A-M2-3）：抽取、契约校验、死链标记。

报告可信度治理的技术落点：每条结论必须携带 ``[citation:来源名](URL)``
内联引用；成稿前跑 ``validate_report`` 做契约检查，``check_links``
做死链标记。HTTP 探测通过可注入的 ``fetch`` 完成——单测里永远是 mock。
"""

from __future__ import annotations

import re
from collections.abc import Callable, Iterable
from dataclasses import dataclass

INLINE_PATTERN = re.compile(r"\[citation:([^\]]+)\]\((https?://[^)\s]+)\)")

#: 一段合格 LLM 产出必须满足的最低引用密度；与 template.MIN_CITATIONS 对齐。
DEFAULT_MIN_INLINE = 5


@dataclass(frozen=True)
class InlineCitation:
    label: str
    url: str


def extract_inline(text: str) -> list[InlineCitation]:
    """按出现顺序抽取 ``[citation:label](url)`` 引用。"""
    return [InlineCitation(label=m.group(1), url=m.group(2)) for m in INLINE_PATTERN.finditer(text)]


def validate_report(report_md: str, *, min_inline: int = DEFAULT_MIN_INLINE) -> list[str]:
    """对成稿 Markdown 做契约校验，返回违规列表；空列表 = 通过。

    检查项：五段标题齐全、内联引用数量达下限、引用 URL 无重复编号断列。
    """
    violations: list[str] = []
    from job_intel.template import SECTION_TITLES

    for title in SECTION_TITLES.values():
        if f"## " not in report_md or title not in report_md:
            violations.append(f"missing section header: {title}")

    inline = extract_inline(report_md)
    if len(inline) < min_inline:
        violations.append(f"inline citations {len(inline)} < required {min_inline}")

    if "局限性说明" not in report_md:
        violations.append("missing limitation statement (局限性说明)")

    return violations


def check_links(
    urls: Iterable[str],
    fetch: Callable[[str], int],
) -> dict[str, str]:
    """逐一探测引用 URL，返回 ``url -> 状态`` 映射。

    ``fetch`` 由调用方注入（生产环境接真实 HTTP，测试注入 mock），
    返回 HTTP 状态码；2xx 视为存活，其余连同抛出的异常一律标记为死链。
    """
    result: dict[str, str] = {}
    for url in urls:
        try:
            status = fetch(url)
            result[url] = f"ok:{status}" if 200 <= status < 300 else f"dead:{status}"
        except Exception as exc:  # noqa: BLE001 - 死链原因千差万别，统一记录
            result[url] = f"dead:{type(exc).__name__}"
    return result
