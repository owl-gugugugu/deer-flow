"""A-M3-3：社区工具注册的 AST 契约测试。

CI 环境不安装 deerflow/langchain，因此适配层用 **语法树静态校验**：
不执行模块，只检查注册契约——@tool 装饰、函数名、必填参数、docstring。
逻辑正确性由 job_intel 包自身的单测覆盖（适配层只是薄封装）。
"""

from __future__ import annotations

import ast
from pathlib import Path

ADAPTER = (
    Path(__file__).resolve().parents[2]
    / "packages" / "harness" / "deerflow" / "community" / "job_intel_sources" / "tools.py"
)


def _parse() -> ast.Module:
    source = ADAPTER.read_text(encoding="utf-8")
    return ast.parse(source)


def _tool_functions(tree: ast.Module) -> dict[str, ast.FunctionDef]:
    tools: dict[str, ast.FunctionDef] = {}
    for node in tree.body:
        if not isinstance(node, ast.FunctionDef):
            continue
        for dec in node.decorator_list:
            if isinstance(dec, ast.Name) and dec.id == "tool":
                tools[node.name] = node
    return tools


def test_adapter_exists_and_defines_tools() -> None:
    assert ADAPTER.exists(), f"adapter missing: {ADAPTER}"
    tools = _tool_functions(_parse())
    assert "job_intel_build_context" in tools
    assert "job_intel_validate_report" in tools


def test_adapter_functions_have_docstrings() -> None:
    """langchain @tool 用 docstring 作为 LLM 的工具描述——缺失即注册失效。"""
    for name, fn in _tool_functions(_parse()).items():
        assert ast.get_docstring(fn), f"{name} missing docstring (tool description)"


def test_build_context_signature_contract() -> None:
    fn = _tool_functions(_parse())["job_intel_build_context"]
    args = [a.arg for a in fn.args.args]
    assert args == ["query", "sources_json"], f"unexpected signature: {args}"
    assert all(a.annotation for a in fn.args.args), "params must be annotated"


def test_validate_report_signature_contract() -> None:
    fn = _tool_functions(_parse())["job_intel_validate_report"]
    args = [a.arg for a in fn.args.args]
    assert args == ["report_md"]
    assert fn.args.args[0].annotation is not None


def test_adapter_is_thin_no_business_logic() -> None:
    """适配层纪律：不许在适配层里写解析/检索逻辑（防止双实现漂移）。"""
    tree = _parse()
    forbidden = {"re", "html.parser"}
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(a.name.lower() for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.lower())
    assert not forbidden & imported, f"adapter must not import {forbidden & imported}"
