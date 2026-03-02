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


def security_audit(state: AgentState) -> AgentState:
    """安全审计主流程"""
    # 1. 代码安全检查
    code_security = check_code_security(state)

    # 2. 配置安全检查
    config_security = check_config_security(state)

    # 3. 内容安全检查 (如果是 PR 发布)
    content_security = check_content_security(state)

    # 4. 计算风险等级
    risk_level = calculate_risk_level(code_security, config_security, content_security)

    # 5. 生成报告
    report = generate_security_report(
        code_security, config_security, content_security, risk_level
    )

    # 6. 决定是否通过
    passed = risk_level in ["low", "medium"]

    state = update_state(state, current_step="安全审计完成")
    result = add_result(state, "security", {
        "passed": passed,
        "risk_level": risk_level,
        "report": report
    })

    # 如果发现高危问题
    if risk_level == "high":
        result = add_error(result, "Security audit found high risk issues")

    return result


def check_code_security(state: AgentState) -> Dict[str, Any]:
    """检查代码安全"""
    checks = {
        "no_hardcoded_secrets": True,
        "no_sql_injection": True,
        "no_xss_vulnerabilities": True,
        "proper_error_handling": True,
    }

    issues = []

    # 检查硬编码密钥
    # TODO: 实际扫描代码
    if not checks["no_hardcoded_secrets"]:
        issues.append({
            "severity": "high",
            "message": "发现硬编码的密钥或密码"
        })

    if not checks["no_sql_injection"]:
        issues.append({
            "severity": "high",
            "message": "潜在的 SQL 注入风险"
        })

    if not checks["no_xss_vulnerabilities"]:
        issues.append({
            "severity": "medium",
            "message": "潜在的 XSS 漏洞"
        })

    return {
        "passed": len([i for i in issues if i["severity"] == "high"]) == 0,
        "checks": checks,
        "issues": issues
    }


def check_config_security(state: AgentState) -> Dict[str, Any]:
    """检查配置安全"""
    checks = {
        "env_in_gitignore": True,
        "api_keys_in_env": True,
        "proper_permissions": True,
        "secure_defaults": True,
    }

    issues = []

    if not checks["env_in_gitignore"]:
        issues.append({
            "severity": "high",
            "message": ".env 文件可能被提交到版本控制"
        })

    if not checks["api_keys_in_env"]:
        issues.append({
            "severity": "medium",
            "message": "API 密钥应使用环境变量"
        })

    return {
        "passed": len([i for i in issues if i["severity"] == "high"]) == 0,
        "checks": checks,
        "issues": issues
    }


def check_content_security(state: AgentState) -> Dict[str, Any]:
    """检查内容安全 (PR 发布场景)"""
    task_type = state.get("task_type", "")

    # 只在 PR 发布时检查内容
    if task_type != "pr_publish":
        return {
            "passed": True,
            "checks": {},
            "issues": [],
            "skipped": True
        }

    checks = {
        "no_internal_info": True,
        "no_unannounced_deals": True,
        "no_confidential_data": True,
        "brand_compliant": True,
    }

    issues = []

    if not checks["no_internal_info"]:
        issues.append({
            "severity": "high",
            "message": "内容包含未公开的内部信息"
        })

    if not checks["no_unannounced_deals"]:
        issues.append({
            "severity": "high",
            "message": "内容包含未公告的交易信息"
        })

    if not checks["no_confidential_data"]:
        issues.append({
            "severity": "high",
            "message": "内容包含机密数据"
        })

    return {
        "passed": len(issues) == 0,
        "checks": checks,
        "issues": issues,
        "skipped": False
    }


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

    high_count = len([i for i in all_issues if i["severity"] == "high"])
    medium_count = len([i for i in all_issues if i["severity"] == "medium"])

    if high_count > 0:
        return "high"
    elif medium_count > 2:
        return "medium"
    else:
        return "low"


def generate_security_report(
    code_security: Dict[str, Any],
    config_security: Dict[str, Any],
    content_security: Dict[str, Any],
    risk_level: str
) -> str:
    """生成安全报告"""
    report_lines = [
        "## Security Audit Report",
        "",
        f"### Risk Level: {risk_level.upper()}",
        "",
        "### Code Security",
        f"- Status: {'PASS' if code_security['passed'] else 'FAIL'}",
    ]

    if code_security["issues"]:
        report_lines.append("- Issues:")
        for issue in code_security["issues"]:
            report_lines.append(f"  - [{issue['severity'].upper()}] {issue['message']}")

    report_lines.extend([
        "",
        "### Config Security",
        f"- Status: {'PASS' if config_security['passed'] else 'FAIL'}",
    ])

    if config_security["issues"]:
        report_lines.append("- Issues:")
        for issue in config_security["issues"]:
            report_lines.append(f"  - [{issue['severity'].upper()}] {issue['message']}")

    if not content_security.get("skipped"):
        report_lines.extend([
            "",
            "### Content Security",
            f"- Status: {'PASS' if content_security['passed'] else 'FAIL'}",
        ])

        if content_security["issues"]:
            report_lines.append("- Issues:")
            for issue in content_security["issues"]:
                report_lines.append(f"  - [{issue['severity'].upper()}] {issue['message']}")

    return "\n".join(report_lines)


def security_process(state: AgentState) -> AgentState:
    """Security Specialist 完整处理流程"""
    return security_audit(state)
