"""
Orchestrator 状态定义

基于 ADR-002: LangGraph Orchestrator 技术选型
"""

from typing import TypedDict, List, Dict, Any, Optional
from enum import Enum


class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    WAITING_HUMAN = "waiting_human"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskType(Enum):
    """任务类型枚举"""
    FEATURE = "feature"
    BUGFIX = "bugfix"
    REFACTOR = "refactor"
    DOCS = "docs"
    PR_PUBLISH = "pr_publish"  # PR 内容发布 - 需要人类确认
    ARCHITECTURE = "architecture"  # 架构变更 - 需要人类确认


class HumanApprovalType(Enum):
    """人类确认类型"""
    PR_PUBLISH = "pr_publish"
    ARCHITECTURE_CHANGE = "architecture_change"
    PRODUCTION_DEPLOY = "production_deploy"


class SubTask(TypedDict):
    """子任务定义"""
    id: str
    description: str
    assigned_agent: str
    status: TaskStatus
    result: Optional[Dict[str, Any]]
    errors: List[str]


class AgentState(TypedDict):
    """
    Orchestrator 状态定义

    这是 LangGraph 工作流的核心状态，在所有节点之间传递
    """
    # === 任务信息 ===
    task_id: str
    task_description: str
    task_type: str  # TaskType 枚举值

    # === 分解后的子任务 ===
    subtasks: List[SubTask]

    # === 当前状态 ===
    current_status: TaskStatus
    current_agent: str
    current_step: str  # 当前执行步骤描述

    # === 各 Agent 的执行结果 ===
    results: Dict[str, Any]  # key: agent_name, value: 执行结果

    # === 人类确认 ===
    needs_human_approval: bool
    human_approval_type: Optional[str]  # HumanApprovalType 枚举值
    human_approved: Optional[bool]
    human_feedback: Optional[str]

    # === 最终输出 ===
    final_output: Any

    # === 错误信息 ===
    errors: List[str]

    # === 元数据 ===
    created_at: str
    updated_at: str
    retry_count: int


# === 状态工厂函数 ===

def create_initial_state(
    task_id: str,
    task_description: str,
    task_type: str = "feature"
) -> AgentState:
    """
    创建初始状态

    Args:
        task_id: 任务唯一标识
        task_description: 任务描述
        task_type: 任务类型 (默认 feature)

    Returns:
        初始化的 AgentState
    """
    from datetime import datetime

    now = datetime.now().isoformat()

    return AgentState(
        task_id=task_id,
        task_description=task_description,
        task_type=task_type,
        subtasks=[],
        current_status=TaskStatus.PENDING,
        current_agent="",
        current_step="初始化",
        results={},
        needs_human_approval=False,
        human_approval_type=None,
        human_approved=None,
        human_feedback=None,
        final_output=None,
        errors=[],
        created_at=now,
        updated_at=now,
        retry_count=0
    )


def update_state(
    state: AgentState,
    **kwargs
) -> AgentState:
    """
    更新状态

    Args:
        state: 当前状态
        **kwargs: 要更新的字段

    Returns:
        更新后的状态
    """
    from datetime import datetime

    new_state = {**state}
    new_state.update(kwargs)
    new_state["updated_at"] = datetime.now().isoformat()

    return AgentState(**new_state)


def add_error(state: AgentState, error: str) -> AgentState:
    """
    添加错误信息

    Args:
        state: 当前状态
        error: 错误信息

    Returns:
        更新后的状态
    """
    errors = state.get("errors", []) + [error]
    return update_state(state, errors=errors)


def add_result(state: AgentState, agent_name: str, result: Any) -> AgentState:
    """
    添加 Agent 执行结果

    Args:
        state: 当前状态
        agent_name: Agent 名称
        result: 执行结果

    Returns:
        更新后的状态
    """
    results = {**state.get("results", {}), agent_name: result}
    return update_state(state, results=results)
