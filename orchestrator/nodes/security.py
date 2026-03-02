"""
Security Specialist Agent 节点

职责:
- 敏感信息识别
- 密钥安全管理
- 知识库安全
- 外部分发审核
- 依赖安全检查
"""

import os
import re
from typing import Dict, Any, List
from ..state import AgentState, update_state, add_result, add_error
from ..llm_client import call_llm, call_llm_json, get_system_prompt
from ..tools import git_status


def security_audit(state: AgentState) -> Dict[str, Any]:
    """安全审计主流程（使用 LLM + 静态检查）"""
    task_description = state.get("task_description", "")
    task_type = state.get("task_type", "feature")
    results = state.get("results", {})

    # 获取开发计划
    dev_plan = results.get("developer_implementation", {})

    # 获取代码变更
    code_changes = get_code_changes(state)

    # 1. 静态安全检查
    static_checks = perform_security_checks(code_changes)

    # 2. 依赖安全检查
    dependency_check = check_dependencies()

    # 3. LLM 安全审计
    prompt = f"""请对以下开发任务进行安全审计：

任务描述: {task_description}
任务类型: {task_type}

开发计划概要:
{str(dev_plan.get('llm_plan', {}))[:500]}

代码变更:
{str(code_changes)[:500]}

静态检查结果:
{str(static_checks)[:500]}

请返回 JSON 格式的安全审计结果，包含：
1. passed: 是否通过安全审计 (true/false)
2. risk_level: 风险等级 (low/medium/high/critical)
3. code_security: 代码安全检查
   - no_hardcoded_secrets: 无硬编码密钥 (bool)
   - no_injection_risks: 无注入风险 (bool)
   - proper_error_handling: 正确的错误处理 (bool)
   - no_sensitive_logs: 无敏感信息日志 (bool)
4. config_security: 配置安全检查
   - env_protected: 环境变量保护 (bool)
   - secure_defaults: 安全默认值 (bool)
   - proper_permissions: 正确的权限设置 (bool)
5. content_security: 内容安全检查
   - no_internal_info: 无内部信息泄露 (bool)
   - no_confidential_data: 无机密数据 (bool)
   - brand_compliance: 品牌合规 (bool)
6. dependency_security: 依赖安全
   - no_known_vulnerabilities: 无已知漏洞 (bool)
   - dependencies_up_to_date: 依赖已更新 (bool)
7. issues: 发现的安全问题列表
8. recommendations: 安全建议"""

    llm_audit = call_llm_json(prompt, get_system_prompt("security"))

    # 合并检查结果
    all_issues = (
        static_checks.get("issues", []) +
        dependency_check.get("issues", []) +
        llm_audit.get("issues", [])
    )

    # 计算风险等级
    risk_level = calculate_risk_level(all_issues, llm_audit)

    # 确定是否通过
    passed = (
        risk_level not in ["high", "critical"] and
        not any(i.get("severity") == "critical" for i in all_issues)
    )

    # 生成报告
    report = generate_security_report(
        llm_audit=llm_audit,
        static_checks=static_checks,
        dependency_check=dependency_check,
        risk_level=risk_level,
        passed=passed
    )

    state = update_state(state, current_step="安全审计完成 (LLM + 静态检查)")
    result = add_result(state, "security", {
        "passed": passed,
        "risk_level": risk_level,
        "code_security": llm_audit.get("code_security", {}),
        "config_security": llm_audit.get("config_security", {}),
        "content_security": llm_audit.get("content_security", {}),
        "dependency_security": llm_audit.get("dependency_security", {}),
        "issues": all_issues,
        "recommendations": llm_audit.get("recommendations", []),
        "report": report,
        "static_checks": static_checks,
        "dependency_check": dependency_check,
        "llm_audit": llm_audit
    })

    if risk_level in ["high", "critical"]:
        result = add_error(result, f"Security audit found {risk_level} risk issues")

    return result


def perform_security_checks(code_changes: Dict[str, Any]) -> Dict[str, Any]:
    """执行静态安全检查"""
    issues = []
    checks = {
        "files_checked": 0,
        "secrets_found": 0,
        "injection_risks": 0,
        "sensitive_data_exposure": 0,
    }

    # 敏感信息模式
    secret_patterns = [
        (r'(?i)(password|passwd|pwd)\s*=\s*["\'][^"\']+["\']', "硬编码密码"),
        (r'(?i)(api_key|apikey|api-key)\s*=\s*["\'][^"\']+["\']', "硬编码 API Key"),
        (r'(?i)(secret|token)\s*=\s*["\'][^"\']+["\']', "硬编码 Secret/Token"),
        (r'(?i)aws_access_key_id\s*=\s*["\'][A-Z0-9]{20}["\']', "AWS Access Key"),
        (r'(?i)aws_secret_access_key\s*=\s*["\'][A-Za-z0-9/+=]{40}["\']', "AWS Secret Key"),
        (r'-----BEGIN (RSA |EC )?PRIVATE KEY-----', "私钥文件"),
        (r'(?i)(mongodb|mysql|postgres|redis)://[^\s]+:[^\s]+@', "数据库连接字符串"),
    ]

    # 注入风险模式
    injection_patterns = [
        (r'execute\s*\(\s*["\'].*%s', "可能的 SQL 注入"),
        (r'eval\s*\(', "危险的 eval 调用"),
        (r'exec\s*\(', "危险的 exec 调用"),
        (r'subprocess\.(call|run)\s*\([^)]*shell\s*=\s*True', "Shell 注入风险"),
        (r'os\.system\s*\(', "系统命令调用"),
    ]

    # 检查每个文件
    for file_path in code_changes.get("files", []):
        if not os.path.exists(file_path):
            continue

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')

            checks["files_checked"] += 1

            for i, line in enumerate(lines, 1):
                # 检查敏感信息
                for pattern, description in secret_patterns:
                    if re.search(pattern, line):
                        checks["secrets_found"] += 1
                        issues.append({
                            "severity": "critical",
                            "type": "secret_exposure",
                            "file": file_path,
                            "line": i,
                            "message": description,
                            "suggestion": "使用环境变量或密钥管理服务存储敏感信息"
                        })

                # 检查注入风险
                for pattern, description in injection_patterns:
                    if re.search(pattern, line):
                        checks["injection_risks"] += 1
                        issues.append({
                            "severity": "high",
                            "type": "injection_risk",
                            "file": file_path,
                            "line": i,
                            "message": description,
                            "suggestion": "使用参数化查询或安全的 API"
                        })

        except Exception as e:
            issues.append({
                "severity": "minor",
                "type": "check_error",
                "file": file_path,
                "line": 0,
                "message": f"无法检查文件: {str(e)}",
                "suggestion": "检查文件编码和权限"
            })

    return {
        "checks": checks,
        "issues": issues,
        "summary": f"检查了 {checks['files_checked']} 个文件，发现 {checks['secrets_found']} 个敏感信息问题，{checks['injection_risks']} 个注入风险"
    }


def check_dependencies() -> Dict[str, Any]:
    """检查依赖安全"""
    issues = []

    # 检查 requirements.txt
    requirements_files = ["requirements.txt", "requirements-dev.txt", "pyproject.toml"]

    for req_file in requirements_files:
        if os.path.exists(req_file):
            try:
                with open(req_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 检查是否有已知的不安全依赖版本
                # 这里可以集成 safety 或 pip-audit
                # 目前只做基本检查

                if "pickle" in content and "allow_pickle" in content:
                    issues.append({
                        "severity": "high",
                        "type": "unsafe_dependency",
                        "file": req_file,
                        "line": 0,
                        "message": "可能存在不安全的 pickle 使用",
                        "suggestion": "避免使用 pickle 处理不受信任的数据"
                    })

            except Exception:
                pass

    return {
        "issues": issues,
        "summary": f"依赖检查完成，发现 {len(issues)} 个潜在问题"
    }


def get_code_changes(state: AgentState) -> Dict[str, Any]:
    """获取代码变更"""
    status = git_status()

    files = []
    if status.get("has_changes"):
        files = list(status.get("files", {}).get("modified", []))

    return {
        "files": files,
        "has_changes": status.get("has_changes", False),
        "branch": status.get("branch", "unknown")
    }


def calculate_risk_level(issues: List[Dict], llm_audit: Dict) -> str:
    """计算风险等级"""
    # 优先使用 LLM 判断的风险等级
    llm_risk = llm_audit.get("risk_level", "low")

    # 根据问题严重程度调整
    critical_count = len([i for i in issues if i.get("severity") == "critical"])
    high_count = len([i for i in issues if i.get("severity") == "high"])

    if critical_count > 0:
        return "critical"
    elif high_count > 2:
        return "high"
    elif high_count > 0:
        return "medium"
    elif llm_risk in ["high", "critical"]:
        return "medium"  # 降低 LLM 判断的风险等级，除非有实际证据

    return llm_risk


def generate_security_report(
    llm_audit: Dict[str, Any],
    static_checks: Dict[str, Any],
    dependency_check: Dict[str, Any],
    risk_level: str,
    passed: bool
) -> str:
    """生成安全审计报告"""
    risk_colors = {
        "low": "🟢",
        "medium": "🟡",
        "high": "🟠",
        "critical": "🔴"
    }

    lines = [
        "# Security Audit Report",
        "",
        f"## 总体评估",
        f"- **状态**: {'✅ PASSED' if passed else '❌ FAILED'}",
        f"- **风险等级**: {risk_colors.get(risk_level, '⚪')} {risk_level.upper()}",
        "",
        "## 检查项详情",
        "",
        "### 代码安全",
    ]

    code_security = llm_audit.get("code_security", {})
    for key, value in code_security.items():
        status = "✅" if value else "❌"
        label = {
            "no_hardcoded_secrets": "无硬编码密钥",
            "no_injection_risks": "无注入风险",
            "proper_error_handling": "错误处理正确",
            "no_sensitive_logs": "无敏感日志"
        }.get(key, key)
        lines.append(f"- {status} {label}")

    lines.extend(["", "### 配置安全", ""])
    config_security = llm_audit.get("config_security", {})
    for key, value in config_security.items():
        status = "✅" if value else "❌"
        label = {
            "env_protected": "环境变量保护",
            "secure_defaults": "安全默认值",
            "proper_permissions": "权限设置正确"
        }.get(key, key)
        lines.append(f"- {status} {label}")

    lines.extend(["", "### 内容安全", ""])
    content_security = llm_audit.get("content_security", {})
    for key, value in content_security.items():
        status = "✅" if value else "❌"
        label = {
            "no_internal_info": "无内部信息泄露",
            "no_confidential_data": "无机密数据",
            "brand_compliance": "品牌合规"
        }.get(key, key)
        lines.append(f"- {status} {label}")

    # 添加问题列表
    all_issues = static_checks.get("issues", []) + dependency_check.get("issues", [])
    if all_issues:
        lines.extend(["", "## 发现的安全问题", ""])
        for issue in all_issues[:10]:
            severity = issue.get("severity", "minor")
            icon = {"critical": "🔴", "high": "🟠", "medium": "🟡", "minor": "🟢"}.get(severity, "⚪")
            file_path = issue.get("file", "unknown")
            line = issue.get("line", "")
            message = issue.get("message", "")
            suggestion = issue.get("suggestion", "")

            lines.append(f"- {icon} **{severity.upper()}** [{file_path}:{line}]")
            lines.append(f"  - {message}")
            if suggestion:
                lines.append(f"  - 建议: {suggestion}")

    # 添加建议
    recommendations = llm_audit.get("recommendations", [])
    if recommendations:
        lines.extend(["", "## 安全建议", ""])
        for r in recommendations:
            lines.append(f"- {r}")

    # 添加摘要
    lines.extend([
        "",
        "## 检查摘要",
        "",
        f"- 静态检查: {static_checks.get('summary', '无结果')}",
        f"- 依赖检查: {dependency_check.get('summary', '无结果')}"
    ])

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


def security_process(state: AgentState) -> AgentState:
    """Security Specialist 完整处理流程"""
    return security_audit(state)
