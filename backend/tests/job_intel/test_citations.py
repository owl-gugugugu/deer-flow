"""A-M2-3：引用校验与死链标记的单测（HTTP 全 mock，零真实网络）。"""

from __future__ import annotations

import pytest

from job_intel.citations import check_links, extract_inline, validate_report

SAMPLE_MD = """\
# 岗位情报报告：字节跳动 · Agent 研发

## 1. 业务线与技术栈画像
豆包 DAU 破亿 [citation:36氪](https://www.36kr.com/a)。

引用：[1]

## 2. 近六个月技术与组织动态
扣子并入豆包 [citation:华尔街见闻](https://awtmt.com/b)。

引用：[2]

## 3. 面经要点聚合
高频真题 FC/MCP/Skills [citation:InfoQ](https://www.infoq.cn/c)。

引用：[3]

## 4. 薪资带宽估计（仅汇总公开数据）
样本 25-45k [citation:样本A](https://example.com/d) [citation:样本B](https://example.com/e)。

引用：[4]、[5]

## 5. 与目标简历的差距分析
缺 Memory 实践 [citation:自评](https://example.com/f)。

---
> 局限性说明：推断内容已标注。
"""


def test_extract_inline_ordered() -> None:
    inline = extract_inline(SAMPLE_MD)
    assert [c.label for c in inline][:3] == ["36氪", "华尔街见闻", "InfoQ"]
    assert all(c.url.startswith("https://") for c in inline)


def test_valid_report_passes() -> None:
    assert validate_report(SAMPLE_MD) == []


def test_missing_section_detected() -> None:
    broken = SAMPLE_MD.replace("## 4. 薪资带宽估计（仅汇总公开数据）", "## 4. 薪资")
    violations = validate_report(broken)
    assert any("薪资带宽估计" in v for v in violations)


def test_too_few_inline_citations_detected() -> None:
    thin = "\n".join(line for line in SAMPLE_MD.splitlines() if "[citation:" not in line or "豆包 DAU" in line)
    violations = validate_report(thin)
    assert any("inline citations" in v for v in violations)


def test_missing_limitation_detected() -> None:
    broken = SAMPLE_MD.replace("局限性说明：推断内容已标注。", "")
    assert any("局限性说明" in v for v in validate_report(broken))


def test_check_links_marks_dead_and_ok() -> None:
    statuses = {"https://ok.com": 200, "https://moved.com": 301, "https://dead.com": 404}
    result = check_links(list(statuses), fetch=statuses.get)
    assert result["https://ok.com"] == "ok:200"
    assert result["https://moved.com"] == "dead:301"
    assert result["https://dead.com"] == "dead:404"


def test_check_links_swallows_fetch_errors() -> None:
    def boom(url: str) -> int:
        raise TimeoutError(url)

    result = check_links(["https://timeout.com"], fetch=boom)
    assert result == {"https://timeout.com": "dead:TimeoutError"}


def test_validate_never_does_network() -> None:
    """契约：validate_report 是纯函数——给它的文本不含 URL 也不能抛网络异常。"""
    with pytest.MonkeyPatch.context() as mp:
        import socket

        mp.setattr(socket, "create_connection", None)  # 真要联网会当场炸
        assert validate_report(SAMPLE_MD) == []
