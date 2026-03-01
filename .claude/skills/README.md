# Skills 配置指南

## 项目专用 Skills

本目录包含 PineVC-PR 项目专用的 skills：

| Skill | 用途 | 触发场景 |
|-------|------|----------|
| `workflow-designer` | Dify 工作流设计 | 设计/修改工作流 |
| `prompt-engineer` | Prompt 模板编写 | 编写/优化 Prompt |
| `knowledge-manager` | 知识库管理 | 维护企业/论点数据 |
| `project-roles` | 角色协作指南 | 了解角色职责 |

## 推荐全局 Skills

### superpowers (必装)

| Skill | 用途 |
|-------|------|
| `superpowers:brainstorming` | 创意工作前的头脑风暴 |
| `superpowers:systematic-debugging` | 系统化调试问题 |
| `superpowers:writing-plans` | 编写实施计划 |
| `superpowers:verification-before-completion` | 完成前验证 |

### everything-claude-code (推荐)

| Skill | 用途 |
|-------|------|
| `everything-claude-code:coding-standards` | 代码规范 |
| `everything-claude-code:frontend-patterns` | 前端模式 (如有 Web 界面) |
| `everything-claude-code:backend-patterns` | 后端模式 (如有 API) |
| `everything-claude-code:postgres-patterns` | 数据库模式 |

### TDD (可选)

本项目主要是工作流配置，TDD 适用性有限。但如果开发 Python 脚本：
- `everything-claude-code:tdd-workflow` - 测试驱动开发

## 使用方式

### 项目专用 Skills

在对话框中直接引用：
```
使用 workflow-designer skill 设计一个新的内容审核工作流
```

### 全局 Skills

全局 skills 已在系统中配置，直接使用即可。

## Skill 开发指南

如需创建新的项目专用 skill：

1. 在 `.claude/skills/` 创建 `.md` 文件
2. 包含以下部分：
   - 触发条件
   - 工作流程
   - 输出规范
   - 相关文档引用

3. 更新本 README 文件
