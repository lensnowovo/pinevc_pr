"""
Product Owner Agent 节点

职责:
- 需求理解和探索
- 任务分解
- 与用户沟通
- 定义验收标准
"""

from typing import List, Dict, Any
from ..state import AgentState, update_state, add_result
import uuid


def understand_requirement(state: AgentState) -> AgentState:
    """理解需求 - 分析用户输入，提取关键信息"""
    task_description = state.get("task_description", "")

    analysis = {
        "original_input": task_description,
        "keywords": extract_keywords(task_description),
        "inferred_type": infer_task_type(task_description),
        "complexity": estimate_complexity(task_description),
        "questions": generate_clarifying_questions(task_description)
    }

    state = update_state(state, current_step="理解需求")
    return add_result(state, "product_owner_analysis", analysis)


def decompose_task(state: AgentState) -> AgentState:
    """分解任务 - 将复杂任务分解为子任务"""
    task_type = state.get("task_type", "feature")
    subtasks = generate_subtasks(task_type)

    return update_state(state, subtasks=subtasks, current_step="分解任务")


def define_acceptance_criteria(state: AgentState) -> AgentState:
    """定义验收标准"""
    task_type = state.get("task_type", "feature")
    task_description = state.get("task_description", "")
    criteria = generate_acceptance_criteria(task_type, task_description)

    state = update_state(state, current_step="定义验收标准")
    return add_result(state, "acceptance_criteria", criteria)


# === 辅助函数 ===

def extract_keywords(text: str) -> List[str]:
    """提取关键词"""
    keywords = []
    tech_keywords = [
        "工作流", "workflow", "Dify", "n8n",
        "知识库", "knowledge", "RAG", "API",
        "集成", "integration", "部署", "deploy",
        "Docker", "测试", "test", "文档", "docs"
    ]
    text_lower = text.lower()
    for kw in tech_keywords:
        if kw.lower() in text_lower:
            keywords.append(kw)
    return keywords


def infer_task_type(description: str) -> str:
    """推断任务类型"""
    desc_lower = description.lower()
    if any(kw in desc_lower for kw in ["bug", "修复", "fix", "问题"]):
        return "bugfix"
    elif any(kw in desc_lower for kw in ["重构", "refactor", "优化"]):
        return "refactor"
    elif any(kw in desc_lower for kw in ["文档", "docs", "readme"]):
        return "docs"
    elif any(kw in desc_lower for kw in ["发布", "publish", "推送"]):
        return "pr_publish"
    elif any(kw in desc_lower for kw in ["架构", "architecture", "adr"]):
        return "architecture"
    return "feature"


def estimate_complexity(description: str) -> str:
    """估算复杂度"""
    word_count = len(description.split())
    if word_count < 10:
        return "low"
    elif word_count < 30:
        return "medium"
    return "high"


def generate_clarifying_questions(description: str) -> List[str]:
    """生成澄清问题"""
    questions = []
    if "工作流" in description or "workflow" in description.lower():
        if "dify" not in description.lower():
            questions.append("这个工作流是在 Dify 中实现还是其他平台？")
    if "集成" in description or "integration" in description.lower():
        questions.append("需要集成哪些外部系统或 API？")
    if not questions:
        questions.append("请确认任务的优先级是高、中还是低？")
    return questions


def generate_subtasks(task_type: str) -> List[Dict[str, Any]]:
    """生成子任务列表"""
    templates = {
        "feature": [
            {"id": f"sub-{uuid.uuid4().hex[:6]}", "description": "需求分析和设计", "assigned_agent": "architect", "status": "pending"},
            {"id": f"sub-{uuid.uuid4().hex[:6]}", "description": "代码实现", "assigned_agent": "developer", "status": "pending"},
            {"id": f"sub-{uuid.uuid4().hex[:6]}", "description": "代码审查", "assigned_agent": "reviewer", "status": "pending"},
            {"id": f"sub-{uuid.uuid4().hex[:6]}", "description": "安全审计", "assigned_agent": "security", "status": "pending"},
            {"id": f"sub-{uuid.uuid4().hex[:6]}", "description": "部署验证", "assigned_agent": "operator", "status": "pending"},
        ],
        "bugfix": [
            {"id": f"sub-{uuid.uuid4().hex[:6]}", "description": "问题诊断", "assigned_agent": "developer", "status": "pending"},
            {"id": f"sub-{uuid.uuid4().hex[:6]}", "description": "修复实现", "assigned_agent": "developer", "status": "pending"},
            {"id": f"sub-{uuid.uuid4().hex[:6]}", "description": "验证测试", "assigned_agent": "developer", "status": "pending"},
        ],
        "docs": [
            {"id": f"sub-{uuid.uuid4().hex[:6]}", "description": "文档编写", "assigned_agent": "developer", "status": "pending"},
            {"id": f"sub-{uuid.uuid4().hex[:6]}", "description": "文档审查", "assigned_agent": "reviewer", "status": "pending"},
        ],
        "pr_publish": [
            {"id": f"sub-{uuid.uuid4().hex[:6]}", "description": "内容生成", "assigned_agent": "developer", "status": "pending"},
            {"id": f"sub-{uuid.uuid4().hex[:6]}", "description": "内容审核", "assigned_agent": "security", "status": "pending"},
            {"id": f"sub-{uuid.uuid4().hex[:6]}", "description": "发布确认", "assigned_agent": "human", "status": "pending"},
        ],
        "architecture": [
            {"id": f"sub-{uuid.uuid4().hex[:6]}", "description": "架构设计", "assigned_agent": "architect", "status": "pending"},
            {"id": f"sub-{uuid.uuid4().hex[:6]}", "description": "方案确认", "assigned_agent": "human", "status": "pending"},
        ],
    }
    return templates.get(task_type, templates["feature"])


def generate_acceptance_criteria(task_type: str, description: str) -> List[str]:
    """生成验收标准"""
    templates = {
        "feature": [
            "功能按设计文档实现",
            "单元测试覆盖率 >= 80%",
            "代码审查通过",
            "安全审计通过",
            "部署验证成功"
        ],
        "bugfix": ["问题根因已识别", "修复方案已实现", "回归测试通过"],
        "docs": ["文档内容准确", "格式规范", "无错别字"],
        "pr_publish": ["内容符合品牌规范", "不含敏感信息", "人类确认通过"],
        "architecture": ["ADR 文档完整", "技术选型合理", "人类确认通过"],
    }
    return templates.get(task_type, templates["feature"])


def product_owner_process(state: AgentState) -> AgentState:
    """Product Owner 完整处理流程"""
    state = understand_requirement(state)
    state = decompose_task(state)
    state = define_acceptance_criteria(state)
    return update_state(state, current_agent="product_owner", current_step="需求处理完成")
