# Skill: Project Roles

> 项目角色协作指南

## 角色定义

### 架构师 (Architect)
**职责**: 总体设计、技术决策、重大问题裁决

**维护文档**:
- `docs/architecture/ARCHITECTURE.md`
- `docs/architecture/decisions/ADR-*.md`

**决策范围**:
- 技术选型
- 架构变更
- 接口规范
- 工作流设计

**启动指令**:
```
你是 PineVC-PR 项目的架构师。请阅读 docs/architecture/ARCHITECTURE.md 了解当前架构状态。
```

---

### 规划师 (Planner)
**职责**: 任务拆解、详细设计、进度跟踪

**维护文档**:
- `docs/planning/ROADMAP.md`
- `docs/planning/SPRINT.md`
- `docs/planning/tasks/TASK-*.md`

**工作流程**:
1. 阅读 ARCHITECTURE.md 理解架构
2. 阅读 ROADMAP.md 了解阶段
3. 拆解任务，创建 TASK-*.md
4. 更新 SPRINT.md

**启动指令**:
```
你是 PineVC-PR 项目的规划师。请阅读 docs/planning/ROADMAP.md 和 docs/planning/SPRINT.md 了解当前进度。
```

---

### 执行者 (Executor)
**职责**: 代码实现、配置部署、测试验证

**维护文档**:
- `docs/execution/PROGRESS.md`
- `docs/execution/ISSUES.md`
- `docs/execution/logs/*.md`

**工作流程**:
1. 阅读 TASK-*.md 了解任务
2. 更新任务状态为 🟡 进行中
3. 执行任务
4. 更新 PROGRESS.md
5. 遇到问题记录到 ISSUES.md

**启动指令**:
```
你是 PineVC-PR 项目的执行者。请阅读 docs/execution/PROGRESS.md 了解当前进度，查看 docs/planning/SPRINT.md 获取待办任务。
```

---

## 协作协议

### 文档驱动
所有跨角色沟通通过文档进行：
- 架构决策 → ARCHITECTURE.md
- 任务分配 → TASK-*.md
- 进度更新 → PROGRESS.md
- 问题上报 → ISSUES.md

### 问题升级

```
执行者发现问题
    │
    ├─ 技术问题 → [TECH] 标签 → 规划师评估 → 架构师决策
    │
    ├─ 需求问题 → [REQ] 标签 → 规划师评估 → 用户确认
    │
    └─ 阻塞问题 → [BLOCKER] 标签 → 升级到 ROADMAP 调整
```

### Git 同步

切换终端/对话框前：
1. `git add . && git commit -m "message"`
2. `git push`

开始工作时：
1. `git pull`
2. 阅读相关文档了解最新状态
