# ADR-002: LangGraph Orchestrator 技术选型

> 状态: 已确认
> 日期: 2026-03-02
> 决策者: 架构师

## 背景

PineVC-PR Agent 系统需要一个 Orchestrator 来协调多个 Agent 之间的工作。Orchestrator 负责：
- 接收 Product Agent 的需求
- 分解任务并分配给专业 Agent
- 协调 Agent 之间的通信
- 管理工作流状态
- 处理人类确认点

## 决策

**选择 LangGraph 作为 Orchestrator 实现**

## 技术规格

### 核心组件

```
orchestrator/
├── main.py                 # 入口点
├── graph.py               # LangGraph 工作流定义
├── state.py               # 状态定义
├── nodes/                 # 工作流节点
│   ├── product_owner.py   # PO 节点
│   ├── architect.py       # 架构师节点
│   ├── developer.py       # 开发者节点
│   ├── reviewer.py        # 代码审查节点
│   ├── security.py        # 安全审计节点
│   └── operator.py        # 运维节点
├── tools/                 # Agent 工具
│   ├── git_tools.py       # Git 操作
│   ├── dify_tools.py      # Dify API
│   └── n8n_tools.py       # n8n API
└── config/
    └── settings.py        # 配置
```

### 状态定义

```python
from typing import TypedDict, List, Dict, Any, Optional
from enum import Enum

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    WAITING_HUMAN = "waiting_human"
    COMPLETED = "completed"
    FAILED = "failed"

class AgentState(TypedDict):
    # 任务信息
    task_id: str
    task_description: str
    task_type: str  # "feature", "bugfix", "refactor", "docs"

    # 分解后的子任务
    subtasks: List[Dict[str, Any]]

    # 当前状态
    current_status: TaskStatus
    current_agent: str

    # 各 Agent 的执行结果
    results: Dict[str, Any]

    # 人类确认
    needs_human_approval: bool
    human_approval_type: Optional[str]  # "pr_publish", "architecture_change"
    human_approved: Optional[bool]

    # 最终输出
    final_output: Any

    # 错误信息
    errors: List[str]
```

### 工作流图

```python
from langgraph.graph import StateGraph, END

def build_orchestrator_graph():
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

    # 条件路由
    workflow.add_conditional_edges(
        "product_owner",
        route_by_task_type,
        {
            "architect": "architect",
            "developer": "developer",
            "operator": "operator",
        }
    )

    workflow.add_edge("architect", "developer")
    workflow.add_edge("developer", "reviewer")
    workflow.add_edge("reviewer", "security")

    # 人类确认检查
    workflow.add_conditional_edges(
        "security",
        check_human_approval,
        {
            "needs_approval": "human_check",
            "continue": "operator",
        }
    )

    workflow.add_edge("human_check", "operator")
    workflow.add_edge("operator", "synthesize")
    workflow.add_edge("synthesize", END)

    return workflow.compile()
```

### 人类确认机制

```python
def check_human_approval(state: AgentState) -> str:
    """检查是否需要人类确认"""

    # PR 内容发布需要确认
    if state["task_type"] == "pr_publish":
        state["needs_human_approval"] = True
        state["human_approval_type"] = "pr_publish"
        return "needs_approval"

    # 架构变更需要确认
    if "architecture" in state["task_description"].lower():
        state["needs_human_approval"] = True
        state["human_approval_type"] = "architecture_change"
        return "needs_approval"

    return "continue"

def human_check_node(state: AgentState) -> AgentState:
    """人类确认节点 - 暂停等待确认"""

    approval_type = state["human_approval_type"]

    # 发送确认请求到 VS Code
    # (实际实现需要与 Claude Code 扩展集成)

    # 暂停工作流，等待人类响应
    state["current_status"] = TaskStatus.WAITING_HUMAN

    return state
```

### LLM 调用

```python
import subprocess
import json

def call_claude_cli(prompt: str, context: dict = None) -> str:
    """通过 Claude Code CLI 调用 LLM"""

    # 构建完整 prompt
    full_prompt = prompt
    if context:
        full_prompt = f"上下文:\n{json.dumps(context, ensure_ascii=False)}\n\n{prompt}"

    # 调用 Claude Code CLI
    # 注意: 实际实现可能需要调整
    result = subprocess.run(
        ["claude", "--prompt", full_prompt],
        capture_output=True,
        text=True
    )

    return result.stdout
```

## 依赖

```
# requirements.txt
langgraph>=0.2.0
langchain>=0.3.0
pydantic>=2.0.0
python-dotenv>=1.0.0
```

## 部署

```yaml
# docker-compose.orchestrator.yml
version: '3.8'

services:
  orchestrator:
    build: ./orchestrator
    ports:
      - "8000:8000"
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    volumes:
      - ./orchestrator:/app
      - ../:/workspace  # 项目根目录
    working_dir: /workspace
```

## 与现有系统的集成

```
┌─────────────────────────────────────────────────────────────┐
│                    集成架构                                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Orchestrator                                               │
│       │                                                     │
│       ├──► Git (项目代码管理)                               │
│       │                                                     │
│       ├──► Dify API (内容生成工作流)                        │
│       │    • POST /v1/workflows/run                        │
│       │    • GET /v1/workflows/run/{task_id}               │
│       │                                                     │
│       ├──► n8n API (调度任务)                               │
│       │    • POST /webhook/xxx                             │
│       │    • GET /executions/{id}                          │
│       │                                                     │
│       └──► VS Code (人类交互)                               │
│            • 确认请求                                       │
│            • 状态通知                                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 开发任务

规划师请参考以下任务拆分：

### TASK-010: Orchestrator 基础框架
- 创建 `orchestrator/` 目录结构
- 实现状态定义 (`state.py`)
- 实现基础工作流图 (`graph.py`)

### TASK-011: Product Owner 节点
- 实现需求理解逻辑
- 实现任务分解逻辑
- 集成 Claude Code CLI

### TASK-012: 人类确认机制
- 实现确认检查逻辑
- 设计 VS Code 通知方式

### TASK-013: Git 工具集成
- 实现代码提交能力
- 实现文件读写能力

## 参考

- LangGraph 文档: https://langchain-ai.github.io/langgraph/
- AGENT-ARCHITECTURE.md: 项目架构文档
