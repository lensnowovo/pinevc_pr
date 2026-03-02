"""
Product Owner Agent 节点

职责:
- 需求理解和探索
- 任务分解
- 与用户沟通
- 定义验收标准
- 优先级评估
"""

import re
from typing import List, Dict, Any
from ..state import AgentState, update_state, add_result
from ..llm_client import call_llm, call_llm_json, get_system_prompt
import uuid


def understand_requirement(state: AgentState) -> AgentState:
    """理解需求 - 使用 LLM 分析用户输入"""
    task_description = state.get("task_description", "")

    # 使用 LLM 进行深度分析
    prompt = f"""请分析以下需求：

需求描述: {task_description}

请返回 JSON 格式的分析结果，包含：
1. keywords: 关键词列表
2. inferred_type: 推断的任务类型 (feature/bugfix/refactor/docs/pr_publish/architecture)
3. complexity: 复杂度评估 (low/medium/high)
4. priority: 建议优先级 (P0/P1/P2)
5. domain: 领域分类 (workflow/knowledge/api/deploy/other)
6. questions: 需要澄清的问题列表
7. related_components: 相关组件或模块"""

    llm_analysis = call_llm_json(prompt, get_system_prompt("product_owner"))

    # 合并本地分析和 LLM 分析
    analysis = {
        "original_input": task_description,
        "keywords": extract_keywords(task_description),
        "inferred_type": llm_analysis.get("inferred_type", infer_task_type(task_description)),
        "complexity": llm_analysis.get("complexity", estimate_complexity(task_description)),
        "priority": llm_analysis.get("priority", "P1"),
        "domain": llm_analysis.get("domain", "other"),
        "questions": llm_analysis.get("questions", generate_clarifying_questions(task_description)),
        "related_components": llm_analysis.get("related_components", []),
        "llm_analysis": llm_analysis
    }

    state = update_state(state, current_step="需求理解完成 (LLM)")
    return add_result(state, "product_owner_analysis", analysis)


def decompose_task(state: AgentState) -> AgentState:
    """分解任务 - 使用 LLM 生成更智能的子任务"""
    task_description = state.get("task_description", "")
    task_type = state.get("task_type", "feature")
    analysis = state.get("results", {}).get("product_owner_analysis", {})

    # 使用 LLM 生成子任务
    prompt = f"""请将以下任务分解为具体的子任务：

任务描述: {task_description}
任务类型: {task_type}
复杂度: {analysis.get('complexity', 'medium')}
相关组件: {analysis.get('related_components', [])}

请返回 JSON 格式，包含：
1. subtasks: 子任务列表，每个子任务包含：
   - id: 子任务ID (格式: sub-xxxxxx)
   - description: 子任务描述
   - assigned_agent: 分配的 Agent (architect/developer/reviewer/security/operator/human)
   - estimated_time: 预估时间
   - dependencies: 依赖的子任务ID列表
2. critical_path: 关键路径上的子任务ID
3. parallelizable: 可以并行执行的子任务组"""

    llm_decomposition = call_llm_json(prompt, get_system_prompt("product_owner"))

    # 合并 LLM 生成的子任务和模板子任务
    llm_subtasks = llm_decomposition.get("subtasks", [])
    if not llm_subtasks:
        llm_subtasks = generate_subtasks(task_type)

    # 确保每个子任务都有必要字段
    for subtask in llm_subtasks:
        if "id" not in subtask:
            subtask["id"] = f"sub-{uuid.uuid4().hex[:6]}"
        if "status" not in subtask:
            subtask["status"] = "pending"
        if "dependencies" not in subtask:
            subtask["dependencies"] = []

    state = update_state(state, subtasks=llm_subtasks, current_step="任务分解完成")
    return add_result(state, "task_decomposition", {
        "subtasks": llm_subtasks,
        "critical_path": llm_decomposition.get("critical_path", []),
        "parallelizable": llm_decomposition.get("parallelizable", []),
        "total_estimated_time": sum(
            parse_time(st.get("estimated_time", "30min"))
            for st in llm_subtasks
        )
    })


def define_acceptance_criteria(state: AgentState) -> AgentState:
    """定义验收标准 - 使用 LLM 生成更具体的标准"""
    task_type = state.get("task_type", "feature")
    task_description = state.get("task_description", "")
    analysis = state.get("results", {}).get("product_owner_analysis", {})

    prompt = f"""请为以下任务定义验收标准：

任务描述: {task_description}
任务类型: {task_type}
复杂度: {analysis.get('complexity', 'medium')}

请返回 JSON 格式，包含：
1. functional_criteria: 功能性验收标准列表
2. non_functional_criteria: 非功能性验收标准列表（性能、安全等）
3. quality_gates: 质量门禁（必须通过的检查点）
4. test_scenarios: 关键测试场景
5. documentation_required: 需要的文档"""

    llm_criteria = call_llm_json(prompt, get_system_prompt("product_owner"))

    criteria = {
        "functional": llm_criteria.get("functional_criteria", get_default_criteria(task_type)),
        "non_functional": llm_criteria.get("non_functional_criteria", []),
        "quality_gates": llm_criteria.get("quality_gates", ["代码审查通过", "安全审计通过"]),
        "test_scenarios": llm_criteria.get("test_scenarios", []),
        "documentation_required": llm_criteria.get("documentation_required", []),
        "llm_criteria": llm_criteria
    }

    state = update_state(state, current_step="验收标准定义完成")
    return add_result(state, "acceptance_criteria", criteria)


# === 辅助函数 ===

def extract_keywords(text: str) -> List[str]:
    """提取关键词"""
    keywords = []

    # 技术关键词
    tech_keywords = [
        # 工作流相关
        "工作流", "workflow", "Dify", "n8n", "自动化", "automation",
        # 知识库相关
        "知识库", "knowledge", "RAG", "向量", "vector", "embedding",
        # API 相关
        "API", "接口", "interface", "集成", "integration", "webhook",
        # 部署相关
        "部署", "deploy", "Docker", "容器", "container", "Kubernetes",
        # 测试相关
        "测试", "test", "pytest", "单元测试", "unit test",
        # 文档相关
        "文档", "docs", "readme", "markdown",
        # 项目特定
        "热点", "监控", "PR", "品牌", "内容", "发布",
        "医健", "资本", "投资", "CDE", "AI",
        "松禾", "PineVC"
    ]

    text_lower = text.lower()
    for kw in tech_keywords:
        if kw.lower() in text_lower:
            keywords.append(kw)

    return list(set(keywords))  # 去重


def infer_task_type(description: str) -> str:
    """推断任务类型"""
    desc_lower = description.lower()

    type_patterns = {
        "bugfix": ["bug", "修复", "fix", "问题", "错误", "error", "异常", "exception"],
        "refactor": ["重构", "refactor", "优化", "optimize", "改进", "improve"],
        "docs": ["文档", "docs", "readme", "说明", "documentation"],
        "pr_publish": ["发布", "publish", "推送", "推送", "宣发", "推广"],
        "architecture": ["架构", "architecture", "adr", "设计", "design", "技术选型"],
    }

    for task_type, patterns in type_patterns.items():
        if any(p in desc_lower for p in patterns):
            return task_type

    return "feature"


def estimate_complexity(description: str) -> str:
    """估算复杂度 - 基于字符数和关键词"""
    # 统计中文字符和英文单词
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', description))
    english_words = len(re.findall(r'[a-zA-Z]+', description))
    total_units = chinese_chars + english_words

    # 复杂度关键词
    high_complexity_keywords = [
        "架构", "重构", "集成", "迁移", "分布式", "微服务",
        "architecture", "refactor", "integration", "migration"
    ]
    low_complexity_keywords = [
        "修复", "更新", "调整", "简单", "小",
        "fix", "update", "simple", "minor"
    ]

    desc_lower = description.lower()

    # 基于关键词判断
    if any(kw in desc_lower for kw in high_complexity_keywords):
        return "high"
    if any(kw in desc_lower for kw in low_complexity_keywords):
        return "low"

    # 基于文本长度判断
    if total_units < 20:
        return "low"
    elif total_units < 50:
        return "medium"
    return "high"


def generate_clarifying_questions(description: str) -> List[str]:
    """生成澄清问题"""
    questions = []

    # 基于关键词生成问题
    if "工作流" in description or "workflow" in description.lower():
        if "dify" not in description.lower() and "n8n" not in description.lower():
            questions.append("这个工作流计划在哪个平台实现？(Dify/n8n/其他)")

    if "集成" in description or "integration" in description.lower():
        questions.append("需要集成哪些外部系统或 API？")

    if "部署" in description or "deploy" in description.lower():
        questions.append("目标部署环境是什么？(开发/测试/生产)")

    if "知识库" in description or "knowledge" in description.lower():
        questions.append("知识库的数据来源是什么？需要多久更新一次？")

    # 默认问题
    if not questions:
        questions.append("请确认任务的优先级是高(P0)、中(P1)还是低(P2)？")

    return questions


def generate_subtasks(task_type: str) -> List[Dict[str, Any]]:
    """生成子任务列表（模板）"""
    templates = {
        "feature": [
            {
                "id": f"sub-{uuid.uuid4().hex[:6]}",
                "description": "需求分析和设计",
                "assigned_agent": "architect",
                "status": "pending",
                "estimated_time": "1h",
                "dependencies": []
            },
            {
                "id": f"sub-{uuid.uuid4().hex[:6]}",
                "description": "代码实现",
                "assigned_agent": "developer",
                "status": "pending",
                "estimated_time": "2h",
                "dependencies": []
            },
            {
                "id": f"sub-{uuid.uuid4().hex[:6]}",
                "description": "代码审查",
                "assigned_agent": "reviewer",
                "status": "pending",
                "estimated_time": "30min",
                "dependencies": []
            },
            {
                "id": f"sub-{uuid.uuid4().hex[:6]}",
                "description": "安全审计",
                "assigned_agent": "security",
                "status": "pending",
                "estimated_time": "30min",
                "dependencies": []
            },
            {
                "id": f"sub-{uuid.uuid4().hex[:6]}",
                "description": "部署验证",
                "assigned_agent": "operator",
                "status": "pending",
                "estimated_time": "30min",
                "dependencies": []
            },
        ],
        "bugfix": [
            {
                "id": f"sub-{uuid.uuid4().hex[:6]}",
                "description": "问题诊断",
                "assigned_agent": "developer",
                "status": "pending",
                "estimated_time": "30min",
                "dependencies": []
            },
            {
                "id": f"sub-{uuid.uuid4().hex[:6]}",
                "description": "修复实现",
                "assigned_agent": "developer",
                "status": "pending",
                "estimated_time": "1h",
                "dependencies": []
            },
            {
                "id": f"sub-{uuid.uuid4().hex[:6]}",
                "description": "验证测试",
                "assigned_agent": "developer",
                "status": "pending",
                "estimated_time": "30min",
                "dependencies": []
            },
        ],
        "docs": [
            {
                "id": f"sub-{uuid.uuid4().hex[:6]}",
                "description": "文档编写",
                "assigned_agent": "developer",
                "status": "pending",
                "estimated_time": "1h",
                "dependencies": []
            },
            {
                "id": f"sub-{uuid.uuid4().hex[:6]}",
                "description": "文档审查",
                "assigned_agent": "reviewer",
                "status": "pending",
                "estimated_time": "30min",
                "dependencies": []
            },
        ],
        "pr_publish": [
            {
                "id": f"sub-{uuid.uuid4().hex[:6]}",
                "description": "内容生成",
                "assigned_agent": "developer",
                "status": "pending",
                "estimated_time": "1h",
                "dependencies": []
            },
            {
                "id": f"sub-{uuid.uuid4().hex[:6]}",
                "description": "内容审核",
                "assigned_agent": "security",
                "status": "pending",
                "estimated_time": "30min",
                "dependencies": []
            },
            {
                "id": f"sub-{uuid.uuid4().hex[:6]}",
                "description": "发布确认",
                "assigned_agent": "human",
                "status": "pending",
                "estimated_time": "15min",
                "dependencies": []
            },
        ],
        "architecture": [
            {
                "id": f"sub-{uuid.uuid4().hex[:6]}",
                "description": "架构设计",
                "assigned_agent": "architect",
                "status": "pending",
                "estimated_time": "2h",
                "dependencies": []
            },
            {
                "id": f"sub-{uuid.uuid4().hex[:6]}",
                "description": "方案确认",
                "assigned_agent": "human",
                "status": "pending",
                "estimated_time": "30min",
                "dependencies": []
            },
        ],
    }
    return templates.get(task_type, templates["feature"])


def get_default_criteria(task_type: str) -> List[str]:
    """获取默认验收标准"""
    templates = {
        "feature": [
            "功能按设计文档实现",
            "单元测试覆盖率 >= 80%",
            "代码审查通过 (score >= 80)",
            "安全审计通过 (risk_level: low)",
            "部署验证成功"
        ],
        "bugfix": [
            "问题根因已识别",
            "修复方案已实现",
            "回归测试通过",
            "无新增测试失败"
        ],
        "docs": [
            "文档内容准确",
            "格式规范 (Markdown)",
            "无错别字和语法错误",
            "示例代码可运行"
        ],
        "pr_publish": [
            "内容符合品牌规范",
            "不含敏感信息",
            "人类确认通过",
            "多渠道适配完成"
        ],
        "architecture": [
            "ADR 文档完整",
            "技术选型有理有据",
            "人类确认通过",
            "风险评估完成"
        ],
    }
    return templates.get(task_type, templates["feature"])


def parse_time(time_str: str) -> int:
    """解析时间字符串为分钟数"""
    if not time_str:
        return 30

    time_str = time_str.lower().strip()

    if "h" in time_str or "小时" in time_str:
        num = int(re.search(r'\d+', time_str).group() or 1)
        return num * 60
    elif "min" in time_str or "分钟" in time_str:
        num = int(re.search(r'\d+', time_str).group() or 30)
        return num

    try:
        return int(time_str)
    except ValueError:
        return 30


def product_owner_process(state: AgentState) -> AgentState:
    """Product Owner 完整处理流程"""
    # 1. 理解需求（使用 LLM）
    state = understand_requirement(state)

    # 2. 分解任务（使用 LLM）
    state = decompose_task(state)

    # 3. 定义验收标准（使用 LLM）
    state = define_acceptance_criteria(state)

    return update_state(state, current_agent="product_owner", current_step="需求处理完成 (LLM)")
