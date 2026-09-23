"""评估指标（A-M4-1）：引用有效率与结构完整率。

口径定义（简历数字只能从这里产生，禁止口头另算）：

- **引用有效率** = 同时满足「可达（HTTP 2xx）」且「内容相关（人工标注）」
  的唯一引用 URL 数 ÷ 报告唯一引用 URL 总数。两者缺一不计入分子；
  网络不可达（fetch 抛异常）单列为 ``unreachable``，与确认死链区分。
- **结构完整率** = 命中的必备结构要素 ÷ 全部要素（五段标题、局限性说明、
  最低引用密度），纯确定性检查。
"""

from __future__ import annotations

import re
from collections.abc import Callable, Iterable
from dataclasses import dataclass

from job_intel.citations import INLINE_PATTERN, check_links

_INLINE_URL = re.compile(r"\[citation:[^\]]+\]\((https?://[^)\s]+)\)")


@dataclass(frozen=True)
class CitationAudit:
    """单份报告的引用审计结果。"""

    unique_urls: tuple[str, ...]
    reachable: frozenset[str]
    dead: frozenset[str]        # 确认死链（HTTP 非 2xx）
    unreachable: frozenset[str]  # 网络层失败（DNS/超时/重置），不计死链
    total: int
    effective: int              # 可达 且 被人工标注相关 的数量
    effectiveness_rate: float   # effective / total；total=0 时定义为 0.0

    @property
    def reachability_rate(self) -> float:
        """可达率 = reachable / total；机器可测，无需人工标注。"""
        return round(len(self.reachable) / self.total, 4) if self.total else 0.0


def audit_citations(
    report_md: str,
    *,
    fetch: Callable[[str], int],
    relevant: Iterable[str] = (),
) -> CitationAudit:
    """对报告做引用审计。``relevant`` 为人工标注的内容相关 URL 集合。"""
    urls = list(dict.fromkeys(m.group(1) for m in _INLINE_URL.finditer(report_md)))
    if not urls:
        return CitationAudit((), frozenset(), frozenset(), frozenset(), 0, 0, 0.0)

    status = check_links(urls, fetch)
    relevant_set = set(relevant)
    reachable, dead, unreachable = set(), set(), set()
    for url, verdict in status.items():
        if verdict.startswith("ok:"):
            reachable.add(url)
        elif verdict.startswith("dead:"):
            # dead:<HTTP状态码> = 确认死链；dead:<异常名> = 网络层不可达
            code = verdict[5:]
            (dead if code.isdigit() else unreachable).add(url)
        else:
            unreachable.add(url)

    effective = sum(1 for u in reachable if u in relevant_set)
    total = len(urls)
    return CitationAudit(
        unique_urls=tuple(urls),
        reachable=frozenset(reachable),
        dead=frozenset(dead),
        unreachable=frozenset(unreachable),
        total=total,
        effective=effective,
        effectiveness_rate=round(effective / total, 4) if total else 0.0,
    )


STRUCTURE_ELEMENTS: tuple[str, ...] = (
    "业务线与技术栈画像",
    "近六个月技术与组织动态",
    "面经要点聚合",
    "薪资带宽估计（仅汇总公开数据）",
    "与目标简历的差距分析",
    "局限性说明",
)


def structure_completeness(report_md: str, *, min_inline: int = 5) -> tuple[float, list[str]]:
    """结构完整率 = 命中要素 / 全部要素；返回（比率, 缺失清单）。

    引用密度也是结构要素：内联引用数 < min_inline 记为缺失（与
    validate_report 的契约对齐，但这里只算比率，不做文字级报错）。
    """
    hits = sum(1 for element in STRUCTURE_ELEMENTS if element in report_md)
    missing = [e for e in STRUCTURE_ELEMENTS if e not in report_md]
    inline_count = len(_INLINE_URL.findall(report_md))
    if inline_count < min_inline:
        missing.append(f"inline_citations<{min_inline}")
    else:
        hits += 1
    total_elements = len(STRUCTURE_ELEMENTS) + 1
    return round(hits / total_elements, 4), missing


@dataclass(frozen=True)
class SummaryMetrics:
    """跨报告汇总：简历引用数字的唯一合法来源。"""

    reports: int
    total_unique_urls: int
    total_reachable: int
    total_effective: int
    reachability_rate: float    # 汇总口径：Σreachable / Σtotal（机器可测）
    effectiveness_rate: float   # 汇总口径：Σeffective / Σtotal（需人工标注）
    mean_structure_completeness: float


def summarize(audits: list[CitationAudit], completeness: Iterable[float]) -> SummaryMetrics:
    """汇总多份报告；比率用合并口径（Σ/Σ），结构完整率取算术均值。"""
    total = sum(a.total for a in audits)
    reachable = sum(len(a.reachable) for a in audits)
    effective = sum(a.effective for a in audits)
    comp = list(completeness)
    return SummaryMetrics(
        reports=len(audits),
        total_unique_urls=total,
        total_reachable=reachable,
        total_effective=effective,
        reachability_rate=round(reachable / total, 4) if total else 0.0,
        effectiveness_rate=round(effective / total, 4) if total else 0.0,
        mean_structure_completeness=round(sum(comp) / len(comp), 4) if comp else 0.0,
    )
