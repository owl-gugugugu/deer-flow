"""领域提示词组装（A-M2-2）：把岗位情报的五段契约注入研究提示词。

确定性契约：同样的入参永远得到逐字节相同的提示词；日期必须显式传入，
绝不隐式取“今天”——否则 golden 快照会随时间漂移。
"""

from __future__ import annotations

from job_intel.template import SECTION_ORDER, SECTION_TITLES

_ROLE = (
    "你是岗位情报分析师。请围绕目标公司输出一份《岗位情报报告》，"
    "供求职者做投递决策使用。"
)

_CITATION_RULES = (
    "引用规范（违反任意一条即为不合格产出）：\n"
    "1. 每一条事实性结论都必须紧跟内联引用，格式为 [citation:来源名](URL)；\n"
    "2. 引用 URL 必须是你在本次调研中真实访问过的公开页面，禁止编造；\n"
    "3. 无法找到来源的猜测必须显式写为“推断”，并说明推断依据；\n"
    "4. 全篇引用总数不少于 5 条，且不得全部集中在单一章节。"
)

_STRUCTURE_RULES = "结构规范：报告必须且只能包含以下五个章节，按此顺序输出。"

_LIMITATION_RULE = (
    "结尾必须附带“局限性说明”：说明哪些内容属于推断、哪些数据有时效性。"
)


def build_research_prompt(company: str, position: str, report_date: str) -> str:
    """组装研究提示词；入参缺失或日期格式非法时抛 ``ValueError``。"""
    if not company.strip():
        raise ValueError("company must be non-empty")
    if not position.strip():
        raise ValueError("position must be non-empty")
    if len(report_date) != 10 or report_date[4] != "-" or report_date[7] != "-":
        raise ValueError(f"report_date must be YYYY-MM-DD: {report_date!r}")

    structure_lines = "\n".join(
        f"{i}. {SECTION_TITLES[key]}" for i, key in enumerate(SECTION_ORDER, start=1)
    )

    parts = [
        _ROLE,
        "",
        f"目标公司：{company.strip()}",
        f"目标岗位：{position.strip()}",
        f"报告日期：{report_date}",
        "",
        _STRUCTURE_RULES,
        structure_lines,
        "",
        _CITATION_RULES,
        "",
        _LIMITATION_RULE,
        "",
        "产出要求：直接输出 Markdown 正文，不要输出与本报告无关的寒暄或解释。",
    ]
    return "\n".join(parts)
