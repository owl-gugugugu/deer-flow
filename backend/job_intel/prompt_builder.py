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

#: 无头运行的运维规则：工具持续失败时果断降级，绝不空转烧预算。
_OPERATION_RULE = (
    "工具故障协议：若网页抓取类工具连续 2 次失败（超时/报错），立即放弃该工具，"
    "仅基于已获得的搜索结果快照完成报告，并在局限性说明中记录哪些引用未能逐一打开核验；"
    "严禁对持续失败的工具反复重试。"
)


def build_research_prompt(
    company: str,
    position: str,
    report_date: str,
    candidate_profile: str | None = None,
) -> str:
    """组装研究提示词；入参缺失或日期格式非法时抛 ``ValueError``。

    ``candidate_profile`` 提供时注入第 5 章所需的候选人画像；不提供时
    显式指示 Agent 退化为通用能力差距模型——绝不让 Agent 因缺输入而
    停下来反问（无头运行会因此短路）。
    """
    if not company.strip():
        raise ValueError("company must be non-empty")
    if not position.strip():
        raise ValueError("position must be non-empty")
    if len(report_date) != 10 or report_date[4] != "-" or report_date[7] != "-":
        raise ValueError(f"report_date must be YYYY-MM-DD: {report_date!r}")

    structure_lines = "\n".join(
        f"{i}. {SECTION_TITLES[key]}" for i, key in enumerate(SECTION_ORDER, start=1)
    )

    if candidate_profile and candidate_profile.strip():
        gap_block = (
            "第 5 章候选人画像（gap 分析以此为基准，无需向用户索要更多信息）：\n"
            f"{candidate_profile.strip()}"
        )
    else:
        gap_block = (
            "未提供候选人画像：第 5 章请基于该岗位典型任职要求输出通用能力差距模型，"
            "并在章首标注“未提供个人简历，以下为通用模型”。不得因缺少个人信息而"
            "暂停输出或向用户反问。"
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
        gap_block,
        "",
        _CITATION_RULES,
        "",
        _LIMITATION_RULE,
        "",
        _OPERATION_RULE,
        "",
        "产出要求：直接输出 Markdown 正文，不要输出与本报告无关的寒暄或解释；"
        "不得以任何理由中途暂停索要补充材料。",
    ]
    return "\n".join(parts)
