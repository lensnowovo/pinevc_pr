# PineVC-PR 项目指令

## 项目概述

松禾资本医健团队 PR 自动化系统 - 全媒体品牌中央厨房

## 核心文档

开始工作前，请阅读以下文档了解项目状态：

1. **架构设计**: `docs/architecture/ARCHITECTURE.md`
2. **路线图**: `docs/planning/ROADMAP.md`
3. **当前冲刺**: `docs/planning/SPRINT.md`
4. **进度跟踪**: `docs/execution/PROGRESS.md`

## 协作模式

本项目采用多角色协作模式：

- **架构师**: 总体设计、技术决策 → 维护 `docs/architecture/`
- **规划师**: 任务拆解、进度跟踪 → 维护 `docs/planning/`
- **执行者**: 代码实现、部署测试 → 维护 `docs/execution/`

## 年度核心论点 (2026)

**CDE + AI**: 中国创新药竞争力 = Discovery × Clinical × Engineering，AI 是加速器

- **C (Clinical)** - 临床转化能力
- **D (Discovery)** - 创新技术来源
- **E (Engineering)** - 工程验证能力
- **AI** - 各环节智能加速

详见: `docs/knowledge/thesis-framework.md`

## 技术栈

- **工作流引擎**: Dify (自托管)
- **LLM**: Claude (主力)
- **知识库**: RAG + 向量数据库
- **部署**: Docker Compose

## 开发规范

### Git Commit 规范
```
<type>(<scope>): <subject>

type: feat|fix|docs|config|refactor|test
scope: arch|plan|exec|wf|prompt|kb

示例:
  docs(arch): 添加总体架构文档
  feat(wf): 添加文章加工工作流 v1
```

### 分支规范
- `main`: 生产可用版本
- `develop`: 开发主分支
- `task/xxx`: 具体任务分支
- `docs/xxx`: 纯文档更新

## 重要路径

```
docs/
├── architecture/     # 架构文档 (架构师)
├── planning/         # 规划文档 (规划师)
├── execution/        # 执行文档 (执行者)
└── knowledge/        # 知识库 (共享)

src/
├── workflows/        # Dify 工作流导出
├── prompts/          # Prompt 模板
├── scripts/          # 工具脚本
└── config/           # 配置文件
```

## 快速开始

```bash
# 查看当前任务
cat docs/planning/SPRINT.md

# 查看进度
cat docs/execution/PROGRESS.md

# 查看问题
cat docs/execution/ISSUES.md
```
