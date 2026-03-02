"""
LangGraph 工作流定义

基于 ADR-002: LangGraph Orchestrator 技术选型
"""

from langgraph.graph import StateGraph, END
from typing import Literal

from .state import AgentState, TaskStatus, TaskType, HumanApprovalType


# === 节点函数 ===

def understand_task(state: AgentState) -> AgentState:
    """
    理解任务节点

    分析用户输入，理解任务意图
    """
    from .state import update_state

    return update_state(
        state,
        current_agent="understand",
        current_step="理解任务",
        current_status=TaskStatus.IN_PROGRESS
    )


def decompose_task(state: AgentState) -> AgentState:
    """
    分解任务节点

    将复杂任务分解为子任务
    """
    from .state import update_state

    return update_state(
        state,
        current_agent="decompose",
        current_step="分解任务"
    )


def product_owner_node(state: AgentState) -> AgentState:
    """
    Product Owner 节点

    需求管理、任务分解、与用户沟通
    """
    from .nodes.product_owner import product_owner_process

    return product_owner_process(state)


def architect_node(state: AgentState) -> AgentState:
    """
    Architect 节点

    架构设计、技术选型、ADR 撰写
    """
    from .state import update_state

    return update_state(
        state,
        current_agent="architect",
        current_step="架构设计"
    )


def developer_node(state: AgentState) -> AgentState:
    """
    Developer 节点

    代码实现、Bug 修复、TDD 开发
    """
    from .nodes.developer import developer_process

    return developer_process(state)


def reviewer_node(state: AgentState) -> AgentState:
    """
    Code Reviewer 节点

    代码质量审查
    """
    from .nodes.reviewer import reviewer_process

    return reviewer_process(state)


def security_node(state: AgentState) -> AgentState:
    """
    Security Specialist 节点

    安全审计
    """
    from .nodes.security import security_process

    return security_process(state)


def operator_node(state: AgentState) -> AgentState:
    """
    Operator 节点

    部署运维
    """
    from .nodes.operator import operator_process

    return operator_process(state)


def human_check_node(state: AgentState) -> AgentState:
    """
    人类确认节点

    暂停工作流，等待人类确认
    """
    from .state import update_state

    return update_state(
        state,
        current_status=TaskStatus.WAITING_HUMAN,
        current_step="等待人类确认"
    )


def synthesize_results(state: AgentState) -> AgentState:
    """
    汇总结果节点

    汇总各 Agent 执行结果
    """
    from .state import update_state

    return update_state(
        state,
        current_agent="synthesize",
        current_step="汇总结果",
        current_status=TaskStatus.COMPLETED
    )


# === 路由函数 ===

def route_by_task_type(state: AgentState) -> Literal["architect", "developer", "operator"]:
    """
    根据任务类型路由到不同的 Agent
    """
    task_type = state.get("task_type", "feature")

    if task_type in ["feature", "refactor"]:
        return "architect"
    elif task_type in ["bugfix", "docs"]:
        return "developer"
    elif task_type == "pr_publish":
        return "operator"
    else:
        return "developer"


def check_human_approval(state: AgentState) -> Literal["needs_approval", "continue"]:
    """
    检查是否需要人类确认

    触发条件:
    - PR 内容发布
    - 架构变更
    """
    task_type = state.get("task_type", "")
    task_description = state.get("task_description", "").lower()

    # PR 内容发布需要确认
    if task_type == "pr_publish":
        return "needs_approval"

    # 架构变更需要确认
    if "architecture" in task_description or "架构" in task_description:
        return "needs_approval"

    # 检查是否显式标记需要确认
    if state.get("needs_human_approval", False):
        return "needs_approval"

    return "continue"


def check_review_result(state: AgentState) -> Literal["pass", "fail"]:
    """
    检查代码审查结果
    """
    results = state.get("results", {})
    review_result = results.get("reviewer", {})

    if review_result.get("passed", False):
        return "pass"
    return "fail"


def check_security_result(state: AgentState) -> Literal["pass", "fail"]:
    """
    检查安全审计结果
    """
    results = state.get("results", {})
    security_result = results.get("security", {})

    if security_result.get("passed", False):
        return "pass"
    return "fail"


# === 构建工作流图 ===

def build_orchestrator_graph():
    """
    构建 Orchestrator 工作流图

    工作流:
    understand -> decompose -> product_owner -> [architect | developer | operator]
    architect -> developer -> reviewer -> security -> [human_check | operator]
    operator -> synthesize -> END
    """
    workflow = StateGraph(AgentState)

    # 添加节点
    workflow.add_node("understand", understand_task)
    workflow.add_node("decompose", decompose_task)
    workflow.add_node("product_owner", product_owner_node)
    workflow.add_node("architect", architect_node)
    workflow.add_node("developer", developer_node)
    workflow.add_node("reviewer", reviewer_node)
    workflow.add_node("security", security_node)
    workflow.add_node("operator", operator_node)
    workflow.add_node("human_check", human_check_node)
    workflow.add_node("synthesize", synthesize_results)

    # 定义入口
    workflow.set_entry_point("understand")

    # 定义边
    workflow.add_edge("understand", "decompose")
    workflow.add_edge("decompose", "product_owner")

    # 条件路由: Product Owner -> 专业 Agent
    workflow.add_conditional_edges(
        "product_owner",
        route_by_task_type,
        {
            "architect": "architect",
            "developer": "developer",
            "operator": "operator",
        }
    )

    # Architect -> Developer
    workflow.add_edge("architect", "developer")

    # Developer -> Reviewer
    workflow.add_edge("developer", "reviewer")

    # 条件路由: Reviewer -> Security (pass) 或返回 Developer (fail)
    workflow.add_conditional_edges(
        "reviewer",
        check_review_result,
        {
            "pass": "security",
            "fail": "developer",  # 返回修复
        }
    )

    # 条件路由: Security -> Human Check 或 Operator
    workflow.add_conditional_edges(
        "security",
        check_human_approval,
        {
            "needs_approval": "human_check",
            "continue": "operator",
        }
    )

    # Human Check -> Operator
    workflow.add_edge("human_check", "operator")

    # Operator -> Synthesize
    workflow.add_edge("operator", "synthesize")

    # Synthesize -> END
    workflow.add_edge("synthesize", END)

    return workflow.compile()


# === 便捷函数 ===

def run_workflow(task_id: str, task_description: str, task_type: str = "feature") -> AgentState:
    """
    运行工作流

    Args:
        task_id: 任务 ID
        task_description: 任务描述
        task_type: 任务类型

    Returns:
        最终状态
    """
    from .state import create_initial_state

    # 创建初始状态
    initial_state = create_initial_state(task_id, task_description, task_type)

    # 构建并运行工作流
    graph = build_orchestrator_graph()
    final_state = graph.invoke(initial_state)

    return final_state
