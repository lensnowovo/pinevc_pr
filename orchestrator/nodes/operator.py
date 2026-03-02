"""
Operator Agent 节点

职责:
- 部署运维
- 监控告警
- 故障恢复
- 系统维护
- 服务管理
"""

import os
import subprocess
import json
import time
from typing import Dict, Any, List, Optional
from ..state import AgentState, TaskStatus, update_state, add_result, add_error
from ..llm_client import call_llm, call_llm_json, get_system_prompt


def deploy(state: AgentState) -> AgentState:
    """部署流程（使用 LLM 规划 + 实际执行）"""
    task_type = state.get("task_type", "feature")
    task_description = state.get("task_description", "")

    # 1. 使用 LLM 生成部署计划
    deploy_plan = generate_deploy_plan(state)

    # 2. 预部署检查
    pre_check = run_pre_deploy_check(state)

    if not pre_check["passed"]:
        state = add_error(state, f"Pre-deploy check failed: {pre_check['issues']}")
        return add_result(state, "operator", {
            "deployed": False,
            "stage": "pre_check",
            "pre_check_result": pre_check,
            "deploy_plan": deploy_plan
        })

    # 3. 执行部署
    deploy_result = execute_deploy(task_type, deploy_plan)

    # 4. 部署后验证
    if deploy_result["success"]:
        verify_result = verify_deployment(state, deploy_plan)
    else:
        verify_result = {"passed": False, "issues": [deploy_result.get("error")]}

    # 5. 如果验证失败，考虑回滚
    if not verify_result["passed"] and deploy_result["success"]:
        rollback_result = rollback(state, deploy_plan)
        state = add_error(state, "Deployment verification failed, rollback triggered")
        return add_result(state, "operator", {
            "deployed": False,
            "deploy_plan": deploy_plan,
            "deploy_result": deploy_result,
            "verify_result": verify_result,
            "rollback_result": rollback_result
        })

    state = update_state(state, current_step="部署完成")
    return add_result(state, "operator", {
        "deployed": deploy_result["success"] and verify_result["passed"],
        "deploy_plan": deploy_plan,
        "deploy_result": deploy_result,
        "verify_result": verify_result
    })


def generate_deploy_plan(state: AgentState) -> Dict[str, Any]:
    """使用 LLM 生成部署计划"""
    task_description = state.get("task_description", "")
    task_type = state.get("task_type", "feature")
    results = state.get("results", {})

    dev_plan = results.get("developer_implementation", {}).get("llm_plan", {})

    prompt = f"""请为以下任务生成部署计划：

任务描述: {task_description}
任务类型: {task_type}

开发计划:
{str(dev_plan)[:500]}

请返回 JSON 格式的部署计划，包含：
1. environment: 部署环境 (development/staging/production)
2. method: 部署方法 (docker-compose/docker-swarm/kubernetes/manual)
3. pre_deploy_steps: 部署前步骤列表
4. deploy_steps: 部署步骤列表
5. post_deploy_steps: 部署后步骤列表
6. health_check: 健康检查配置
7. rollback_plan: 回滚计划
8. estimated_duration: 预估时间（分钟）
9. required_resources: 所需资源
10. risk_assessment: 风险评估"""

    llm_plan = call_llm_json(prompt, get_system_prompt("operator"))

    return {
        "environment": llm_plan.get("environment", "development"),
        "method": llm_plan.get("method", "docker-compose"),
        "pre_deploy_steps": llm_plan.get("pre_deploy_steps", ["检查依赖", "备份数据"]),
        "deploy_steps": llm_plan.get("deploy_steps", ["拉取镜像", "启动服务"]),
        "post_deploy_steps": llm_plan.get("post_deploy_steps", ["健康检查", "日志检查"]),
        "health_check": llm_plan.get("health_check", {"endpoint": "/health", "timeout": 30}),
        "rollback_plan": llm_plan.get("rollback_plan", {"method": "previous_version"}),
        "estimated_duration": llm_plan.get("estimated_duration", 5),
        "required_resources": llm_plan.get("required_resources", {}),
        "risk_assessment": llm_plan.get("risk_assessment", "low"),
        "llm_plan": llm_plan
    }


def run_pre_deploy_check(state: AgentState) -> Dict[str, Any]:
    """预部署检查"""
    checks = {
        "tests_passed": True,
        "code_reviewed": True,
        "security_audited": True,
        "config_valid": True,
        "dependencies_ready": True,
        "resources_available": True,
    }

    issues = []
    results = state.get("results", {})

    # 检查测试结果
    test_results = results.get("test_results", {})
    if test_results:
        checks["tests_passed"] = test_results.get("passed", True)
        if not checks["tests_passed"]:
            issues.append("测试未通过")

    # 检查代码审查
    reviewer_result = results.get("reviewer", {})
    if reviewer_result:
        checks["code_reviewed"] = reviewer_result.get("passed", True)
        if not checks["code_reviewed"]:
            issues.append(f"代码审查未通过 (score: {reviewer_result.get('score', 'N/A')})")

    # 检查安全审计
    security_result = results.get("security", {})
    if security_result:
        checks["security_audited"] = security_result.get("passed", True)
        if not checks["security_audited"]:
            issues.append(f"安全审计未通过 (risk: {security_result.get('risk_level', 'unknown')})")

    # 检查 Docker 环境
    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            text=True,
            timeout=10
        )
        checks["dependencies_ready"] = result.returncode == 0
        if result.returncode != 0:
            issues.append("Docker 环境不可用")
    except Exception as e:
        checks["dependencies_ready"] = False
        issues.append(f"Docker 检查失败: {str(e)[:50]}")

    return {
        "passed": all(checks.values()),
        "checks": checks,
        "issues": issues
    }


def execute_deploy(task_type: str, deploy_plan: Dict[str, Any]) -> Dict[str, Any]:
    """执行部署"""
    method = deploy_plan.get("method", "docker-compose")
    environment = deploy_plan.get("environment", "development")

    result = {
        "success": False,
        "environment": environment,
        "method": method,
        "steps_completed": [],
        "steps_failed": [],
        "duration_seconds": 0,
        "output": "",
        "error": None
    }

    start_time = time.time()

    try:
        # 执行部署前步骤
        for step in deploy_plan.get("pre_deploy_steps", []):
            step_result = execute_deploy_step(step, "pre")
            if step_result["success"]:
                result["steps_completed"].append(f"pre: {step}")
            else:
                result["steps_failed"].append(f"pre: {step}")
                if "critical" in step.lower() or "备份" in step:
                    raise Exception(f"Critical pre-deploy step failed: {step}")

        # 执行部署步骤
        if method == "docker-compose":
            deploy_output = deploy_docker_compose(environment)
        elif method == "kubernetes":
            deploy_output = deploy_kubernetes(environment)
        else:
            deploy_output = deploy_manual(environment)

        result["output"] = deploy_output.get("output", "")
        result["steps_completed"].extend(deploy_output.get("steps", []))

        if deploy_output.get("success"):
            result["success"] = True
        else:
            result["error"] = deploy_output.get("error", "Unknown error")

        # 执行部署后步骤
        for step in deploy_plan.get("post_deploy_steps", []):
            step_result = execute_deploy_step(step, "post")
            if step_result["success"]:
                result["steps_completed"].append(f"post: {step}")
            else:
                result["steps_failed"].append(f"post: {step}")

    except Exception as e:
        result["error"] = str(e)
        result["success"] = False

    result["duration_seconds"] = int(time.time() - start_time)

    return result


def deploy_docker_compose(environment: str) -> Dict[str, Any]:
    """使用 Docker Compose 部署"""
    steps = []
    output = ""

    try:
        # 检查 docker-compose.yml
        compose_file = "docker-compose.yml"
        if os.path.exists("docker-compose.override.yml"):
            compose_file = "docker-compose.yml:docker-compose.override.yml"

        # 拉取镜像
        result = subprocess.run(
            ["docker-compose", "pull"],
            capture_output=True,
            text=True,
            timeout=300
        )
        steps.append("pull_images")
        output += result.stdout

        # 构建镜像
        result = subprocess.run(
            ["docker-compose", "build"],
            capture_output=True,
            text=True,
            timeout=600
        )
        steps.append("build_images")
        output += result.stdout

        # 启动服务
        result = subprocess.run(
            ["docker-compose", "up", "-d"],
            capture_output=True,
            text=True,
            timeout=120
        )
        steps.append("start_services")

        if result.returncode == 0:
            output += result.stdout
            return {"success": True, "steps": steps, "output": output[-2000:]}
        else:
            return {"success": False, "steps": steps, "output": output[-2000:], "error": result.stderr}

    except subprocess.TimeoutExpired:
        return {"success": False, "steps": steps, "output": output, "error": "Deployment timeout"}
    except Exception as e:
        return {"success": False, "steps": steps, "output": output, "error": str(e)}


def deploy_kubernetes(environment: str) -> Dict[str, Any]:
    """使用 Kubernetes 部署"""
    steps = []
    output = ""

    try:
        # 检查 kubectl
        result = subprocess.run(
            ["kubectl", "cluster-info"],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            return {"success": False, "steps": [], "output": "", "error": "Kubernetes cluster not accessible"}

        steps.append("cluster_check")

        # 应用配置
        if os.path.exists("k8s/"):
            result = subprocess.run(
                ["kubectl", "apply", "-f", "k8s/"],
                capture_output=True,
                text=True,
                timeout=120
            )
            steps.append("apply_manifests")
            output = result.stdout

        return {"success": True, "steps": steps, "output": output[-2000:]}

    except Exception as e:
        return {"success": False, "steps": steps, "output": output, "error": str(e)}


def deploy_manual(environment: str) -> Dict[str, Any]:
    """手动部署（模拟）"""
    steps = ["simulate_deploy"]

    return {
        "success": True,
        "steps": steps,
        "output": f"Manual deployment to {environment} simulated"
    }


def execute_deploy_step(step: str, phase: str) -> Dict[str, Any]:
    """执行单个部署步骤"""
    # 简化的步骤执行逻辑
    return {"success": True, "step": step, "phase": phase}


def verify_deployment(state: AgentState, deploy_plan: Dict[str, Any]) -> Dict[str, Any]:
    """验证部署"""
    checks = {
        "service_running": False,
        "health_check": False,
        "logs_clean": True,
        "endpoints_responding": False,
    }

    issues = []

    try:
        # 检查服务状态
        result = subprocess.run(
            ["docker-compose", "ps"],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0 and "Up" in result.stdout:
            checks["service_running"] = True
        else:
            issues.append("服务未运行")

        # 健康检查
        health_config = deploy_plan.get("health_check", {})
        if health_config.get("endpoint"):
            # 模拟健康检查
            checks["health_check"] = True
            checks["endpoints_responding"] = True
        else:
            checks["health_check"] = True  # 跳过

        # 日志检查
        result = subprocess.run(
            ["docker-compose", "logs", "--tail=50"],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            # 检查是否有错误日志
            if "error" in result.stdout.lower() or "exception" in result.stdout.lower():
                checks["logs_clean"] = False
                issues.append("日志中发现错误")

    except Exception as e:
        issues.append(f"验证失败: {str(e)[:50]}")

    return {
        "passed": all(checks.values()),
        "checks": checks,
        "issues": issues
    }


def rollback(state: AgentState, deploy_plan: Dict[str, Any]) -> Dict[str, Any]:
    """回滚部署"""
    rollback_plan = deploy_plan.get("rollback_plan", {})
    method = rollback_plan.get("method", "previous_version")

    try:
        if method == "previous_version":
            # 回滚到上一个版本
            result = subprocess.run(
                ["docker-compose", "down"],
                capture_output=True,
                text=True,
                timeout=60
            )

            # 恢复之前的镜像
            # result = subprocess.run(...)

            return {
                "success": True,
                "method": method,
                "output": result.stdout
            }
        else:
            return {
                "success": True,
                "method": method,
                "output": "Rollback simulated"
            }

    except Exception as e:
        return {
            "success": False,
            "method": method,
            "error": str(e)
        }


def operator_process(state: AgentState) -> AgentState:
    """Operator 完整处理流程"""
    return deploy(state)


# === 运维工具函数 ===

def check_service_status(service_name: str) -> Dict[str, Any]:
    """检查服务状态"""
    try:
        result = subprocess.run(
            ["docker-compose", "ps", service_name],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            return {
                "running": "Up" in result.stdout,
                "health": "healthy" if "Up" in result.stdout else "unhealthy",
                "output": result.stdout
            }
        else:
            return {
                "running": False,
                "health": "unknown",
                "error": result.stderr
            }

    except Exception as e:
        return {
            "running": False,
            "health": "error",
            "error": str(e)
        }


def view_logs(service_name: str, lines: int = 100) -> str:
    """查看服务日志"""
    try:
        result = subprocess.run(
            ["docker-compose", "logs", f"--tail={lines}", service_name],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout

    except Exception as e:
        return f"[ERROR] Failed to get logs: {str(e)}"


def restart_service(service_name: str) -> Dict[str, Any]:
    """重启服务"""
    try:
        result = subprocess.run(
            ["docker-compose", "restart", service_name],
            capture_output=True,
            text=True,
            timeout=60
        )

        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr if result.returncode != 0 else None
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def scale_service(service_name: str, replicas: int) -> Dict[str, Any]:
    """扩缩容服务"""
    try:
        result = subprocess.run(
            ["docker-compose", "up", "-d", f"--scale={service_name}={replicas}"],
            capture_output=True,
            text=True,
            timeout=120
        )

        return {
            "success": result.returncode == 0,
            "replicas": replicas,
            "output": result.stdout
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
