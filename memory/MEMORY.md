# PineVC-PR 项目记忆

> **最后更新**: 2026-03-02
> **版本**: 1.0

---

## 项目概述

PineVC-PR 是一个 AI 驱动的 PR 自动化工具，服务于 VC 机构的医疗健康团队。

### 核心架构

- **Dify**: 内容生成引擎
- **n8n**: 调度和集成平台
- **Orchestrator**: 开发团队编排器（CLI Skill）

---

## Orchestrator Skill 架构

### 文件结构

```
.claude/skills/orchestrator/
├── SKILL.md                     # 主入口（意图分类 + LangGraph 状态机）
└── references/
    ├── intent-patterns.md       # 意图分类规则
    ├── product-owner.md         # Product Owner 角色
    ├── architect.md             # Architect 角色
    ├── developer.md             # Developer 角色
    ├── reviewer.md              # Reviewer 角色
    ├── security.md              # Security 角色
    ├── operator.md              # Operator 角色
    └── tools.md                 # 工具集参考
```

### 角色定义

| 角色 | 职责 | 触发条件 |
|------|------|----------|
| Product Owner | 需求理解、任务分解 | 所有任务 |
| Architect | 架构设计、技术选型 | feature, refactor, architecture |
| Developer | 代码实现、TDD | 所有任务 |
| Reviewer | 代码质量审查 | 所有任务 |
| Security | 安全审计、敏感信息检测 | 非 docs 任务 |
| Operator | 部署运维、Git 操作 | 所有任务 |

### 工作流

```
Understand → Decompose → Product Owner → [Architect] → Developer → Reviewer → Security → [Human Check] → Operator → Synthesize
```

### 人类确认触发条件

- PR 内容发布
- 架构变更
- 敏感数据操作

---

## LangGraph 实现

### 状态定义

```python
class AgentState(TypedDict):
    task_id: str
    task_description: str
    task_type: str  # feature|bugfix|refactor|docs|pr_publish|architecture

    current_agent: str
    current_step: str
    current_status: str  # pending|in_progress|waiting_human|completed|failed

    results: Dict[str, Any]
    subtasks: List[Dict]
    errors: List[Dict]

    needs_human_approval: bool
    human_approval_type: Optional[str]
```

### 路由函数

- `route_by_task_type`: 根据任务类型路由到不同 Agent
- `check_review_result`: 审查通过/失败路由
- `check_security_result`: 安全通过/需确认路由

---

## Python Orchestrator 实现

### 文件结构

```
orchestrator/
├── __init__.py
├── state.py              # 状态定义
├── graph.py              # LangGraph 工作流
├── main.py               # 入口点
├── config/
│   └── settings.py       # 配置
├── nodes/
│   ├── product_owner.py
│   ├── developer.py
│   ├── reviewer.py
│   ├── security.py
│   └── operator.py
└── tools/
    └── git_tools.py      # Git 工具
```

---

## 技术决策

### ADR-002: LangGraph Orchestrator

- **选择**: LangGraph 作为 Orchestrator 框架
- **理由**: 稳定、灵活、支持复杂工作流
- **替代方案**: Dify workflows, AutoGen, CrewAI

### LLM 提供商

- **选择**: Claude Code CLI（本地）
- **理由**: 无需额外 API 配置，直接使用 CLI

---

## 使用方式

### 触发 Orchestrator

在 Claude Code CLI 中：

```
"我想加一个用户权限模块"
"修复登录页面的报错"
"重构数据处理模块"
"帮我写个 API 文档"
"发布这篇关于 AI 的文章"
```

### 指定停止点

```
"我想加用户权限模块，只设计"
"帮我规划一下，先规划"
```

### 配置选项

```
"严格审查"    → reviewStrictness: strict
"跳过安全"    → skipSecurity: true (仅限 docs)
"自动提交"    → autoCommit: true
```

---

## 相关文档

- [docs/architecture/AGENT-ARCHITECTURE.md](docs/architecture/AGENT-ARCHITECTURE.md) - 完整 Agent 架构
- [docs/architecture/decisions/ADR-002-langgraph-orchestrator.md](docs/architecture/decisions/ADR-002-langgraph-orchestrator.md) - 技术规范

---

## 历史记录

| 日期 | 事件 |
|------|------|
| 2026-03-02 | 创建 Hybrid Orchestrator Skill，融合 CLI Skill 和 LangGraph 状态机 |
| 2026-03-01 | 完成 LangGraph Orchestrator 框架搭建 |
| 2026-02-28 | 参考 FrostStar 项目，确定 Skills 集成方案 |
