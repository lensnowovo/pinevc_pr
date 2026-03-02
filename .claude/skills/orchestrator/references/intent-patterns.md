# 意图分类规则

> **用途**: Orchestrator 意图检测参考
> **基于**: ADR-002 LangGraph Orchestrator

---

## 意图类型定义

```typescript
type TaskType =
  | 'feature'     // 新功能开发
  | 'bugfix'      // Bug 修复
  | 'refactor'    // 代码重构
  | 'docs'        // 文档编写
  | 'pr_publish'  // PR 内容发布
  | 'architecture' // 架构设计
```

---

## 分类规则

### feature (新功能)

**触发短语**:
- "我想加..."
- "新增功能..."
- "帮我实现..."
- "开发一个..."
- "添加一个..."
- "需要做一个..."
- "实现一个..."

**执行流程**: 完整流程 (Understand → Decompose → PO → Architect → Developer → Reviewer → Security → Operator)

**示例**:
```
用户: "我想加一个用户权限模块"
意图: feature
目标: 用户权限模块
流程: 完整流程
```

---

### bugfix (Bug 修复)

**触发短语**:
- "修复..."
- "fix..."
- "解决..."
- "问题..."
- "bug..."
- "报错了..."
- "出错了..."

**执行流程**: Developer → Reviewer → Security → Operator

**示例**:
```
用户: "修复登录页面的报错"
意图: bugfix
目标: 登录页面报错
流程: 跳过 Architect
```

---

### refactor (代码重构)

**触发短语**:
- "重构..."
- "优化..."
- "refactor..."
- "改进..."
- "整理代码..."

**执行流程**: Architect → Developer → Reviewer → Security → Operator

**示例**:
```
用户: "重构数据处理模块"
意图: refactor
目标: 数据处理模块
流程: Architect → Developer → ...
```

---

### docs (文档编写)

**触发短语**:
- "文档..."
- "docs..."
- "readme..."
- "写个文档..."
- "记录一下..."

**执行流程**: Developer → Reviewer

**示例**:
```
用户: "帮我写个 API 文档"
意图: docs
目标: API 文档
流程: 跳过 Architect, Security
```

---

### pr_publish (PR 内容发布)

**触发短语**:
- "发布内容..."
- "推送..."
- "publish..."
- "发文章..."
- "发布到..."

**执行流程**: Developer → Security → **Human Check** → Operator

**人类确认**: 必须

**示例**:
```
用户: "发布这篇关于 AI 的文章"
意图: pr_publish
目标: AI 文章发布
流程: 需人类确认
```

---

### architecture (架构设计)

**触发短语**:
- "架构..."
- "architecture..."
- "ADR..."
- "技术选型..."
- "设计方案..."

**执行流程**: Architect → **Human Check**

**人类确认**: 必须

**示例**:
```
用户: "设计用户认证架构"
意图: architecture
目标: 用户认证架构
流程: Architect → Human Check
```

---

## 人类确认触发条件

```typescript
function checkHumanApproval(state: AgentState): boolean {
  // PR 内容发布需要确认
  if (state.task_type === 'pr_publish') return true

  // 架构变更需要确认
  if (state.task_type === 'architecture') return true

  // 任务描述包含关键词
  const keywords = ['架构', 'architecture', '发布', 'publish', '敏感']
  if (keywords.some(k => state.task_description.includes(k))) return true

  // 显式标记
  if (state.needs_human_approval) return true

  return false
}
```

---

## 复杂度估算

```typescript
function estimateComplexity(description: string): 'low' | 'medium' | 'high' {
  const wordCount = description.split(/\s+/).length

  if (wordCount < 10) return 'low'
  if (wordCount < 30) return 'medium'
  return 'high'
}
```

---

## 路由决策矩阵

| 意图 | Architect | Developer | Reviewer | Security | Human | Operator |
|------|-----------|-----------|----------|----------|-------|----------|
| feature | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |
| bugfix | ❌ | ✅ | ✅ | ✅ | ❌ | ✅ |
| refactor | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |
| docs | ❌ | ✅ | ✅ | ❌ | ❌ | ✅ |
| pr_publish | ❌ | ✅ | ❌ | ✅ | ✅ | ✅ |
| architecture | ✅ | ❌ | ❌ | ❌ | ✅ | ❌ |

---

## 停止点映射

| 短语 | stopAfter |
|------|-----------|
| "只设计" | architect |
| "设计完暂停" | architect |
| "先规划" | product_owner |
| "规划完暂停" | product_owner |
| "不要执行" | architect |
| "只实现" | developer |

---

## 边界情况处理

### 模糊意图

如果无法确定意图，返回询问：

```markdown
我不太确定你的意图，请问你是想：

1. **开发新功能** - 完整的开发流程
2. **修复问题** - 定位并修复 Bug
3. **重构优化** - 改进现有代码
4. **编写文档** - 添加或更新文档
5. **发布内容** - 发布 PR 内容（需确认）
6. **设计架构** - 架构设计（需确认）

请告诉我你的选择。
```

### 混合意图

如果用户请求包含多个意图，按优先级处理：

```
priority: pr_publish > architecture > bugfix > refactor > feature > docs
```

---

*此文档由 Orchestrator 定义*
