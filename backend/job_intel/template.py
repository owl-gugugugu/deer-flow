"""五段式岗位情报报告渲染器（A-M2-1）。

确定性契约：同样的 :class:`ReportInput` 永远渲染出逐字节相同的 Markdown。
任何字段缺失、段落为空、引用 URL 非法都在渲染前抛 ``ValueError``——
宁可早失败，不渲染半残报告。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

#: 五个正文章节的固定顺序；渲染编号由该顺序决定，不接受乱序。
SECTION_ORDER: tuple[str, ...] = (
    "business",
    "dynamics",
    "interview",
    "salary",
    "gap",
)

SECTION_TITLES: dict[str, str] = {
    "business": "业务线与技术栈画像",
    "dynamics": "近六个月技术与组织动态",
    "interview": "面经要点聚合",
    "salary": "薪资带宽估计（仅汇总公开数据）",
    "gap": "与目标简历的差距分析",
}

#: 单份报告引用 URL 数量下限；低于该值说明调研密度不足，拒绝成稿。
MIN_CITATIONS = 5

_HEADER_TEMPLATE = "# 岗位情报报告：{company} · {position}"
_SUBHEADER_TEMPLATE = "> 生成日期：{report_date} ｜ 管道：job-intel v0.1（deer-flow 二开）"
_FOOTER = (
    "---\n"
    "> 局限性说明：本报告由自动化管道聚合公开信息生成，所有结论以上方引用链接为准；"
    "链接失效或内容变动恕不实时更新。薪资数据仅为公开信息汇总，不构成任何要约依据。"
)


@dataclass(frozen=True)
class SectionContent:
    """单个正文章节：LLM 产出的正文 + 该章节收集到的引用 URL 列表。"""

    content: str
    citations: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.content or not self.content.strip():
            raise ValueError("section content must be non-empty")
        for url in self.citations:
            if not url.startswith(("http://", "https://")):
                raise ValueError(f"citation url must be http(s): {url!r}")


@dataclass(frozen=True)
class ReportInput:
    """一份报告的完整输入；缺失字段在构造期即报错。"""

    company: str
    position: str
    report_date: str
    sections: Mapping[str, SectionContent]

    def __post_init__(self) -> None:
        if not self.company.strip():
            raise ValueError("company must be non-empty")
        if not self.position.strip():
            raise ValueError("position must be non-empty")
        if len(self.report_date) != 10 or self.report_date[4] != "-" or self.report_date[7] != "-":
            raise ValueError(f"report_date must be YYYY-MM-DD: {self.report_date!r}")
        missing = [key for key in SECTION_ORDER if key not in self.sections]
        if missing:
            raise ValueError(f"missing sections: {missing}")

    @classmethod
    def from_dict(cls, data: Mapping[str, object]) -> ReportInput:
        """从 JSON 反序列化（回放 fixture 的加载入口）。"""
        raw_sections = data["sections"]
        if not isinstance(raw_sections, Mapping):
            raise TypeError("sections must be an object")
        sections = {
            key: SectionContent(
                content=str(section["content"]),
                citations=tuple(section.get("citations", ())),  # type: ignore[arg-type]
            )
            for key, section in raw_sections.items()
        }
        return cls(
            company=str(data["company"]),
            position=str(data["position"]),
            report_date=str(data["report_date"]),
            sections=sections,
        )


def _collect_citations(sections: Mapping[str, SectionContent]) -> list[str]:
    """按 SECTION_ORDER 汇总引用，URL 去重且保持首次出现顺序。"""
    seen: set[str] = set()
    ordered: list[str] = []
    for key in SECTION_ORDER:
        for url in sections[key].citations:
            if url not in seen:
                seen.add(url)
                ordered.append(url)
    return ordered


def render_report(report: ReportInput) -> str:
    """渲染五段式 Markdown 报告；引用全局连续编号，URL 去重保序。"""
    urls = _collect_citations(report.sections)
    if len(urls) < MIN_CITATIONS:
        raise ValueError(
            f"report has only {len(urls)} unique citations, need >= {MIN_CITATIONS}"
        )
    index_of = {url: i + 1 for i, url in enumerate(urls)}

    lines: list[str] = [
        _HEADER_TEMPLATE.format(company=report.company, position=report.position),
        "",
        _SUBHEADER_TEMPLATE.format(report_date=report.report_date),
        "",
    ]
    for number, key in enumerate(SECTION_ORDER, start=1):
        section = report.sections[key]
        lines.append(f"## {number}. {SECTION_TITLES[key]}")
        lines.append("")
        lines.append(section.content.strip())
        local = [index_of[url] for url in section.citations]
        if local:
            lines.append("")
            lines.append("引用：" + "、".join(f"[{i}]" for i in local))
        lines.append("")

    lines.append(_FOOTER)
    lines.append("")
    return "\n".join(lines)
