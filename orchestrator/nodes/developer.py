"""
Developer Agent 节点

职责:
- 代码实现
- Bug 修复
- TDD 开发
- 代码重构
"""

from typing import Dict, Any, List
from ..state import AgentState, TaskStatus, update_state, add_result, add_error
from ..tools import read_file, write_file, git_status, git_add, git_commit, git_quick_commit


def analyze_task(state: AgentState) -> AgentState:
    """分析开发任务"""
    task_description = state.get("task_description", "")
    task_type = state.get("task_type", "feature")
    subtasks = state.get("subtasks", [])

    # 找到分配给 developer 的子任务
    dev_subtasks = [
        st for st in subtasks
        if st.get("assigned_agent") == "developer"
    ]

    analysis = {
        "task_type": task_type,
        "dev_subtasks_count": len(dev_subtasks),
        "subtasks": dev_subtasks,
        "approach": determine_approach(task_type, task_description)
    }

    state = update_state(state, current_step="分析开发任务")
    return add_result(state, "developer_analysis", analysis)


def determine_approach(task_type: str, description: str) -> str:
    """确定开发方法"""
    approaches = {
        "feature": "TDD: 先写测试，再实现功能",
        "bugfix": "调试: 先复现问题，再修复",
        "refactor": "重构: 保持功能不变，优化代码",
        "docs": "文档: 直接编写"
    }
    return approaches.get(task_type, "TDD")


def implement_code(state: AgentState) -> AgentState:
    """实现代码

    TODO: 集成 LLM 进行代码生成
    当前: 返回模拟结果
    """
    results = state.get("results", {})
    analysis = results.get("developer_analysis", {})

    # 获取工作区状态
    status = git_status()

    implementation = {
        "status": "implemented",
        "files_changed": status.get("has_changes", False),
        "approach": analysis.get("approach", "TDD"),
        "notes": [
            "代码已实现",
            "待 Code Reviewer 审查"
        ]
    }

    state = update_state(state, current_step="代码实现完成")
    return add_result(state, "developer_implementation", implementation)


def run_tests(state: AgentState) -> AgentState:
    """运行测试

    TODO: 实际执行 pytest
    """
    # 模拟测试结果
    test_result = {
        "passed": True,
        "total": 5,
        "failed": 0,
        "coverage": 85,
        "details": [
            {"name": "test_feature_1", "status": "passed"},
            {"name": "test_feature_2", "status": "passed"},
            {"name": "test_feature_3", "status": "passed"},
            {"name": "test_edge_case_1", "status": "passed"},
            {"name": "test_edge_case_2", "status": "passed"},
        ]
    }

    state = update_state(state, current_step="测试执行完成")
    return add_result(state, "test_results", test_result)


def commit_changes(state: AgentState) -> AgentState:
    """提交代码变更"""
    task_id = state.get("task_id", "unknown")
    task_description = state.get("task_description", "")

    # 检查是否有变更
    status = git_status()

    if status.get("has_changes"):
        # 生成 commit message
        commit_msg = f"feat: {task_description[:50]}... (task: {task_id})"

        # 提交
        result = git_quick_commit(commit_msg)

        if result.get("success"):
            state = update_state(state, current_step="代码已提交")
            return add_result(state, "commit", {"success": True, "message": commit_msg})
        else:
            return add_error(state, f"Commit failed: {result.get('error')}")
    else:
        return add_result(state, "commit", {"success": True, "message": "No changes to commit"})


def developer_process(state: AgentState) -> AgentState:
    """Developer 完整处理流程"""
    # 1. 分析任务
    state = analyze_task(state)

    # 2. 实现代码
    state = implement_code(state)

    # 3. 运行测试
    state = run_tests(state)

    # 4. 提交变更
    state = commit_changes(state)

    return update_state(
        state,
        current_agent="developer",
        current_step="开发完成"
    )


# === 辅助函数 ===

def generate_code_from_description(description: str, task_type: str) -> str:
    """根据描述生成代码

    TODO: 调用 LLM 生成代码
    """
    return f"# TODO: Implement {description}\npass\n"


def fix_bug(bug_description: str, code: str) -> str:
    """修复 Bug

    TODO: 调用 LLM 修复代码
    """
    return code


def refactor_code(code: str, instructions: str) -> str:
    """重构代码

    TODO: 调用 LLM 重构代码
    """
    return code
