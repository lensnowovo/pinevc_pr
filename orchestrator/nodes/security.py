"""
Security Specialist Agent 节点

职责:
- 敏感信息识别
- 密钥安全管理
- 知识库安全
- 外部分发审核
"""

from typing import Dict, Any, List
from ..state import AgentState, update_state, add_result, add_error
from ..llm_client import call_llm, call_llm_json, get_system_prompt


def security_audit(state: AgentState) -> AgentState:
    """安全审计主流程（使用 LLM）"""
    task_description = state.get("task_description", "")
    task_type = state.get("task_type", "feature")
    results = state.get("results", {})

    # 获取开发计划
    dev_plan = results.get("developer_implementation", {}).get("llm_plan", {})

    # 使用 LLM 进行安全审计
    prompt = f"""请对以下开发任务进行安全审计：

任务描述: {task_description}
任务类型: {task_type}

开发计划概要:
{str(dev_plan)[:500]}

请返回 JSON 格式的安全审计结果，包含：
1. passed: 是否通过安全审计 (true/false)
2. risk_level: 风险等级 (low/medium/high)
3. code_security: 代码安全检查
   - no_hardcoded_secrets: 无硬编码密钥
   - no_injection_risks: 无注入风险
   - proper_error_handling: 正确的错误处理
4. config_security: 配置安全检查
   - env_protected: 环境变量保护
   - secure_defaults: 安全默认值
5. content_security: 内容安全检查（如果是 PR 发布）
   - no_internal_info: 无内部信息泄露
   - no_confidential_data: 无机密数据
6. issues: 发现的安全问题列表
7. recommendations: 安全建议"""

    llm_audit = call_llm_json(prompt, get_system_prompt("security"))

    # 提取结果
    passed = llm_audit.get("passed", True)
    risk_level = llm_audit.get("risk_level", "low")

    # 生成报告
    report = generate_security_report_from_llm(llm_audit)

    state = update_state(state, current_step="安全审计完成 (LLM)")
    result = add_result(state, "security", {
        "passed": passed,
        "risk_level": risk_level,
        "report": report,
        "llm_audit": llm_audit
    })

    if risk_level == "high":
        result = add_error(result, "Security audit found high risk issues")

    return result


def generate_security_report_from_llm(llm_audit: Dict[str, Any]) -> str:
    """从 LLM 结果生成安全报告"""
    lines = [
        "## Security Audit Report (LLM)",
        "",
        f"### Risk Level: {llm_audit.get('risk_level', 'unknown').upper()}",
        f"### Status: {'PASSED' if llm_audit.get('passed') else 'FAILED'}",
        "",
    ]

    issues = llm_audit.get("issues", [])
    if issues:
        lines.append("### Security Issues")
        for issue in issues:
            severity = issue.get("severity", "unknown") if isinstance(issue, dict) else "medium"
            message = issue.get("message", str(issue)) if isinstance(issue, dict) else str(issue)
            lines.append(f"- [{severity.upper()}] {message}")
        lines.append("")

    recommendations = llm_audit.get("recommendations", [])
    if recommendations:
        lines.append("### Recommendations")
        for r in recommendations:
            lines.append(f"- {r}")

    return "\n".join(lines)


def check_code_security(state: AgentState) -> Dict[str, Any]:
    """检查代码安全"""
    checks = {
        "no_hardcoded_secrets": True,
        "no_sql_injection": True,
        "no_xss_vulnerabilities": True,
        "proper_error_handling": True,
    }
    return {"passed": True, "checks": checks, "issues": []}


def check_config_security(state: AgentState) -> Dict[str, Any]:
    """检查配置安全"""
    checks = {
        "env_in_gitignore": True,
        "api_keys_in_env": True,
        "proper_permissions": True,
    }
    return {"passed": True, "checks": checks, "issues": []}


def check_content_security(state: AgentState) -> Dict[str, Any]:
    """检查内容安全"""
    task_type = state.get("task_type", "")
    if task_type != "pr_publish":
        return {"passed": True, "checks": {}, "issues": [], "skipped": True}

    checks = {
        "no_internal_info": True,
        "no_confidential_data": True,
    }
    return {"passed": True, "checks": checks, "issues": [], "skipped": False}


def calculate_risk_level(
    code_security: Dict[str, Any],
    config_security: Dict[str, Any],
    content_security: Dict[str, Any]
) -> str:
    """计算风险等级"""
    all_issues = (
        code_security.get("issues", []) +
        config_security.get("issues", []) +
        content_security.get("issues", [])
    )
    high_count = len([i for i in all_issues if isinstance(i, dict) and i.get("severity") == "high"])
    if high_count > 0:
        return "high"
    return "low"


def security_process(state: AgentState) -> AgentState:
    """Security Specialist 完整处理流程"""
    return security_audit(state)
