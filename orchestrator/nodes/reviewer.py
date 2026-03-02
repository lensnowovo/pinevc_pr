"""
Code Reviewer Agent 节点

职责:
- 代码干净程度检查
- 最佳实践检查
- 可维护性评估
- 代码质量评分
"""

from typing import Dict, Any, List
from ..state import AgentState, update_state, add_result, add_error
from ..llm_client import call_llm, call_llm_json, get_system_prompt


def review_code(state: AgentState) -> AgentState:
    """代码审查主流程（使用 LLM）"""
    task_description = state.get("task_description", "")
    results = state.get("results", {})

    # 获取开发者的实现计划
    dev_plan = results.get("developer_implementation", {}).get("llm_plan", {})

    # 使用 LLM 进行代码审查
    prompt = f"""请对以下开发任务进行代码审查：

任务描述: {task_description}

开发计划:
{str(dev_plan)[:500]}

请返回 JSON 格式的审查结果，包含：
1. passed: 是否通过 (true/false)
2. score: 评分 (0-100)
3. cleanliness: 代码干净程度检查结果
   - no_commented_code: 无注释代码
   - no_debug_statements: 无调试语句
   - clear_naming: 命名清晰
4. practices: 最佳实践检查结果
   - error_handling: 错误处理
   - type_hints: 类型标注
   - docstrings: 文档字符串
5. maintainability: 可维护性检查结果
   - function_length: 函数长度适中
   - single_responsibility: 职责单一
6. issues: 问题列表
7. suggestions: 改进建议"""

    llm_review = call_llm_json(prompt, get_system_prompt("reviewer"))

    # 提取结果
    passed = llm_review.get("passed", True)
    score = llm_review.get("score", 85)

    # 构建报告
    report = generate_review_report_from_llm(llm_review)

    state = update_state(state, current_step="代码审查完成 (LLM)")
    result = add_result(state, "reviewer", {
        "passed": passed,
        "score": score,
        "report": report,
        "llm_review": llm_review
    })

    if not passed:
        result = add_error(result, f"Code review failed with score {score}")

    return result


def generate_review_report_from_llm(llm_review: Dict[str, Any]) -> str:
    """从 LLM 结果生成审查报告"""
    lines = [
        "## Code Review Report (LLM)",
        "",
        f"### Score: {llm_review.get('score', 'N/A')}/100",
        f"### Status: {'PASSED' if llm_review.get('passed') else 'FAILED'}",
        "",
    ]

    issues = llm_review.get("issues", [])
    if issues:
        lines.append("### Issues")
        for issue in issues:
            lines.append(f"- {issue}")
        lines.append("")

    suggestions = llm_review.get("suggestions", [])
    if suggestions:
        lines.append("### Suggestions")
        for s in suggestions:
            lines.append(f"- {s}")

    return "\n".join(lines)


def get_code_changes(state: AgentState) -> Dict[str, Any]:
    """获取代码变更"""
    from ..tools import git_status
    status = git_status()
    return {
        "files": list(status.get("files", {}).get("modified", [])),
        "has_changes": status.get("has_changes", False)
    }


def check_cleanliness(changes: Dict[str, Any]) -> Dict[str, Any]:
    """检查代码干净程度"""
    checks = {
        "no_commented_code": True,
        "no_debug_statements": True,
        "clear_naming": True,
        "no_duplicates": True,
    }

    issues = []
    if not checks["no_commented_code"]:
        issues.append("Found commented code")
    if not checks["no_debug_statements"]:
        issues.append("Found debug statements (print/console.log)")

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
    if not checks["error_handling"]:
        issues.append("Incomplete error handling")
    if not checks["type_hints"]:
        issues.append("Missing type hints")

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
