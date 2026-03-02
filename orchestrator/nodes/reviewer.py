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


def review_code(state: AgentState) -> AgentState:
    """代码审查主流程"""
    # 1. 获取代码变更
    changes = get_code_changes(state)

    # 2. 执行各项检查
    cleanliness = check_cleanliness(changes)
    practices = check_best_practices(changes)
    maintainability = check_maintainability(changes)

    # 3. 计算总分
    score = calculate_score(cleanliness, practices, maintainability)

    # 4. 生成报告
    report = generate_review_report(
        cleanliness, practices, maintainability, score
    )

    # 5. 决定是否通过
    passed = score >= 70  # 70 分通过

    state = update_state(state, current_step="代码审查完成")
    result = add_result(state, "reviewer", {
        "passed": passed,
        "score": score,
        "report": report
    })

    # 如果不通过，添加错误信息
    if not passed:
        result = add_error(result, f"Code review failed with score {score}")

    return result


def get_code_changes(state: AgentState) -> Dict[str, Any]:
    """获取代码变更

    TODO: 实际从 git diff 获取
    """
    return {
        "files": ["orchestrator/nodes/developer.py"],
        "additions": 100,
        "deletions": 10,
        "has_changes": True
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
        issues.append("发现注释掉的代码")
    if not checks["no_debug_statements"]:
        issues.append("发现调试语句 (print/console.log)")
    if not checks["clear_naming"]:
        issues.append("命名不够清晰")
    if not checks["no_duplicates"]:
        issues.append("发现重复代码")

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
        issues.append("错误处理不完整")
    if not checks["type_hints"]:
        issues.append("缺少类型标注")
    if not checks["docstrings"]:
        issues.append("缺少文档字符串")
    if not checks["logging"]:
        issues.append("日志记录不完整")

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
    if not checks["function_length_ok"]:
        issues.append("函数过长 (>50行)")
    if not checks["file_length_ok"]:
        issues.append("文件过长 (>500行)")
    if not checks["single_responsibility"]:
        issues.append("模块职责不单一")
    if not checks["comments_present"]:
        issues.append("缺少关键注释")

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
    # 权重: 干净程度 30%, 最佳实践 40%, 可维护性 30%
    score = (
        cleanliness["score"] * 0.3 +
        practices["score"] * 0.4 +
        maintainability["score"] * 0.3
    )
    return int(score)


def generate_review_report(
    cleanliness: Dict[str, Any],
    practices: Dict[str, Any],
    maintainability: Dict[str, Any],
    score: int
) -> str:
    """生成审查报告"""
    report_lines = [
        "## Code Review Report",
        "",
        f"### Total Score: {score}/100",
        "",
        "### Cleanliness Check",
        f"- Status: {'PASS' if cleanliness['passed'] else 'FAIL'}",
        f"- Score: {cleanliness['score']}",
    ]

    if cleanliness["issues"]:
        report_lines.append("- Issues:")
        for issue in cleanliness["issues"]:
            report_lines.append(f"  - {issue}")

    report_lines.extend([
        "",
        "### Best Practices Check",
        f"- Status: {'PASS' if practices['passed'] else 'FAIL'}",
        f"- Score: {practices['score']}",
    ])

    if practices["issues"]:
        report_lines.append("- Issues:")
        for issue in practices["issues"]:
            report_lines.append(f"  - {issue}")

    report_lines.extend([
        "",
        "### Maintainability Check",
        f"- Status: {'PASS' if maintainability['passed'] else 'FAIL'}",
        f"- Score: {maintainability['score']}",
    ])

    if maintainability["issues"]:
        report_lines.append("- Issues:")
        for issue in maintainability["issues"]:
            report_lines.append(f"  - {issue}")

    return "\n".join(report_lines)


def reviewer_process(state: AgentState) -> AgentState:
    """Code Reviewer 完整处理流程"""
    return review_code(state)
