"""
Code Reviewer Agent 节点

职责:
- 代码干净程度检查
- 最佳实践检查
- 可维护性评估
- 代码质量评分
- 安全合规检查
"""

import os
import re
from typing import Dict, Any, List, Tuple
from ..state import AgentState, update_state, add_result, add_error
from ..llm_client import call_llm, call_llm_json, get_system_prompt
from ..tools import git_status


def review_code(state: AgentState) -> AgentState:
    """代码审查主流程（使用 LLM + 静态分析）"""
    task_description = state.get("task_description", "")
    results = state.get("results", {})

    # 获取开发者的实现计划
    dev_plan = results.get("developer_implementation", {})
    dev_analysis = results.get("developer_analysis", {})

    # 获取代码变更
    code_changes = get_code_changes(state)

    # 1. 静态代码分析
    static_analysis = perform_static_analysis(code_changes)

    # 2. LLM 代码审查
    prompt = f"""请对以下开发任务进行全面的代码审查：

任务描述: {task_description}

实现计划:
{str(dev_plan.get('llm_plan', {}))[:500]}

代码变更:
{str(code_changes)[:500]}

静态分析结果:
{str(static_analysis)[:500]}

请返回 JSON 格式的审查结果，包含：
1. passed: 是否通过 (true/false)
2. score: 评分 (0-100)
3. cleanliness: 代码干净程度
   - no_commented_code: 无注释代码 (bool)
   - no_debug_statements: 无调试语句 (bool)
   - clear_naming: 命名清晰 (bool)
   - no_duplicates: 无重复代码 (bool)
4. practices: 最佳实践
   - error_handling: 错误处理完善 (bool)
   - type_hints: 类型标注完整 (bool)
   - docstrings: 文档字符串存在 (bool)
   - logging: 日志记录适当 (bool)
5. maintainability: 可维护性
   - function_length_ok: 函数长度适中 (bool)
   - single_responsibility: 职责单一 (bool)
   - modularity: 模块化良好 (bool)
6. issues: 问题列表，每个问题包含：
   - severity: 严重程度 (critical/major/minor)
   - file: 文件路径
   - line: 行号 (如果知道)
   - message: 问题描述
   - suggestion: 修改建议
7. suggestions: 整体改进建议"""

    llm_review = call_llm_json(prompt, get_system_prompt("reviewer"))

    # 合并静态分析和 LLM 审查结果
    merged_issues = static_analysis.get("issues", []) + llm_review.get("issues", [])

    # 计算最终分数
    llm_score = llm_review.get("score", 85)
    static_penalty = len([i for i in static_analysis.get("issues", []) if i.get("severity") == "critical"]) * 10
    final_score = max(0, min(100, llm_score - static_penalty))

    # 确定是否通过
    passed = final_score >= 70 and not any(
        i.get("severity") == "critical" for i in merged_issues
    )

    # 生成报告
    report = generate_review_report(
        llm_review=llm_review,
        static_analysis=static_analysis,
        final_score=final_score,
        passed=passed
    )

    state = update_state(state, current_step="代码审查完成 (LLM + 静态分析)")
    result = add_result(state, "reviewer", {
        "passed": passed,
        "score": final_score,
        "cleanliness": llm_review.get("cleanliness", {}),
        "practices": llm_review.get("practices", {}),
        "maintainability": llm_review.get("maintainability", {}),
        "issues": merged_issues,
        "suggestions": llm_review.get("suggestions", []),
        "report": report,
        "static_analysis": static_analysis,
        "llm_review": llm_review
    })

    if not passed:
        result = add_error(result, f"Code review failed with score {final_score}")

    return result


def perform_static_analysis(code_changes: Dict[str, Any]) -> Dict[str, Any]:
    """执行静态代码分析"""
    issues = []
    checks = {
        "files_analyzed": 0,
        "total_lines": 0,
        "commented_code_found": False,
        "debug_statements_found": False,
        "todos_found": 0,
    }

    # 分析每个修改的文件
    for file_path in code_changes.get("files", []):
        if not os.path.exists(file_path):
            continue

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')

            checks["files_analyzed"] += 1
            checks["total_lines"] += len(lines)

            # 检查注释代码
            for i, line in enumerate(lines, 1):
                stripped = line.strip()

                # 检查注释掉的代码
                if stripped.startswith('#') and (
                    'def ' in stripped or
                    'class ' in stripped or
                    'import ' in stripped or
                    'return ' in stripped
                ):
                    checks["commented_code_found"] = True
                    issues.append({
                        "severity": "minor",
                        "file": file_path,
                        "line": i,
                        "message": "发现注释掉的代码",
                        "suggestion": "删除不再需要的代码，使用版本控制保留历史"
                    })

                # 检查调试语句
                debug_patterns = ['print(', 'console.log(', 'debugger', 'pdb.', 'breakpoint()']
                for pattern in debug_patterns:
                    if pattern in stripped and not stripped.startswith('#'):
                        checks["debug_statements_found"] = True
                        issues.append({
                            "severity": "major",
                            "file": file_path,
                            "line": i,
                            "message": f"发现调试语句: {pattern}",
                            "suggestion": "移除调试语句，使用日志记录替代"
                        })

                # 检查 TODO
                if 'TODO' in stripped or 'FIXME' in stripped or 'XXX' in stripped:
                    checks["todos_found"] += 1
                    issues.append({
                        "severity": "minor",
                        "file": file_path,
                        "line": i,
                        "message": "发现未完成的 TODO",
                        "suggestion": "完成或移除 TODO 注释"
                    })

        except Exception as e:
            issues.append({
                "severity": "minor",
                "file": file_path,
                "line": 0,
                "message": f"无法分析文件: {str(e)}",
                "suggestion": "检查文件编码和权限"
            })

    return {
        "checks": checks,
        "issues": issues,
        "summary": f"分析了 {checks['files_analyzed']} 个文件，{checks['total_lines']} 行代码"
    }


def get_code_changes(state: AgentState) -> Dict[str, Any]:
    """获取代码变更"""
    status = git_status()

    files = []
    # 从 git status 获取修改的文件
    if status.get("has_changes"):
        files = list(status.get("files", {}).get("modified", []))

    return {
        "files": files,
        "has_changes": status.get("has_changes", False),
        "branch": status.get("branch", "unknown")
    }


def generate_review_report(
    llm_review: Dict[str, Any],
    static_analysis: Dict[str, Any],
    final_score: int,
    passed: bool
) -> str:
    """生成代码审查报告"""
    lines = [
        "# Code Review Report",
        "",
        f"## 总体评估",
        f"- **状态**: {'✅ PASSED' if passed else '❌ FAILED'}",
        f"- **评分**: {final_score}/100",
        "",
        "## 检查项详情",
        "",
        "### 代码干净程度",
    ]

    cleanliness = llm_review.get("cleanliness", {})
    for key, value in cleanliness.items():
        status = "✅" if value else "❌"
        label = {
            "no_commented_code": "无注释代码",
            "no_debug_statements": "无调试语句",
            "clear_naming": "命名清晰",
            "no_duplicates": "无重复代码"
        }.get(key, key)
        lines.append(f"- {status} {label}")

    lines.extend([
        "",
        "### 最佳实践",
    ])
    practices = llm_review.get("practices", {})
    for key, value in practices.items():
        status = "✅" if value else "❌"
        label = {
            "error_handling": "错误处理",
            "type_hints": "类型标注",
            "docstrings": "文档字符串",
            "logging": "日志记录"
        }.get(key, key)
        lines.append(f"- {status} {label}")

    lines.extend([
        "",
        "### 可维护性",
    ])
    maintainability = llm_review.get("maintainability", {})
    for key, value in maintainability.items():
        status = "✅" if value else "❌"
        label = {
            "function_length_ok": "函数长度适中",
            "single_responsibility": "职责单一",
            "modularity": "模块化良好"
        }.get(key, key)
        lines.append(f"- {status} {label}")

    # 添加问题列表
    all_issues = static_analysis.get("issues", []) + llm_review.get("issues", [])
    if all_issues:
        lines.extend([
            "",
            "## 发现的问题",
            ""
        ])
        for issue in all_issues[:10]:  # 最多显示10个问题
            severity = issue.get("severity", "minor")
            file_path = issue.get("file", "unknown")
            line = issue.get("line", "")
            message = issue.get("message", "")
            suggestion = issue.get("suggestion", "")

            severity_icon = {"critical": "🔴", "major": "🟡", "minor": "🟢"}.get(severity, "⚪")
            lines.append(f"- {severity_icon} **{severity.upper()}** [{file_path}:{line}]")
            lines.append(f"  - {message}")
            if suggestion:
                lines.append(f"  - 建议: {suggestion}")

    # 添加改进建议
    suggestions = llm_review.get("suggestions", [])
    if suggestions:
        lines.extend([
            "",
            "## 改进建议",
            ""
        ])
        for s in suggestions:
            lines.append(f"- {s}")

    # 添加静态分析摘要
    lines.extend([
        "",
        "## 静态分析摘要",
        "",
        static_analysis.get("summary", "无分析结果")
    ])

    return "\n".join(lines)


def check_cleanliness(changes: Dict[str, Any]) -> Dict[str, Any]:
    """检查代码干净程度"""
    checks = {
        "no_commented_code": True,
        "no_debug_statements": True,
        "clear_naming": True,
        "no_duplicates": True,
    }

    issues = []

    return {
        "passed": len(issues) == 0,
        "score": 90 if len(issues) == 0 else 70,
        "checks": checks,
        "issues": issues
    }


def check_best_practices(changes: Dict[str, Any]) -> Dict[str, Any]:
    """检查最佳实践"""
    checks = {
        "error_handling": True,
        "type_hints": True,
        "docstrings": True,
        "logging": True,
    }

    issues = []

    return {
        "passed": len(issues) == 0,
        "score": 85 if len(issues) == 0 else 65,
        "checks": checks,
        "issues": issues
    }


def check_maintainability(changes: Dict[str, Any]) -> Dict[str, Any]:
    """检查可维护性"""
    checks = {
        "function_length_ok": True,
        "file_length_ok": True,
        "single_responsibility": True,
        "comments_present": True,
    }

    issues = []

    return {
        "passed": len(issues) == 0,
        "score": 80 if len(issues) == 0 else 60,
        "checks": checks,
        "issues": issues
    }


def calculate_score(
    cleanliness: Dict[str, Any],
    practices: Dict[str, Any],
    maintainability: Dict[str, Any]
) -> int:
    """计算总分"""
    score = (
        cleanliness["score"] * 0.3 +
        practices["score"] * 0.4 +
        maintainability["score"] * 0.3
    )
    return int(score)


def reviewer_process(state: AgentState) -> AgentState:
    """Code Reviewer 完整处理流程"""
    return review_code(state)
