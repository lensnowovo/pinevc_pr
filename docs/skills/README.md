# Skills 技能库

> OpenClaw Agent 技能文件集合

## 概述

每个 Skill 文件定义了 Agent 的一个具体能力。OpenClaw 会将这些技能作为记忆的一部分，在执行任务时自动调用。

## 文件结构

```
docs/skills/
├── README.md              # 本文件
├── article_process.md     # 文章加工 (笔杆子)
├── web_patrol.md          # 网页巡逻 (参谋官)
├── quality_check.md       # 质量检查 (进化官)
└── daily_brief.md         # 早报生成 (早报官)
```

## Skill 清单

### 核心技能

| Skill | Agent | 用途 | 优先级 |
|-------|-------|------|--------|
| article_process | 笔杆子 | 加工老板转发的文章 | P0 |
| web_patrol | 参谋官 | 全网巡逻收集热点 | P1 |
| quality_check | 进化官 | 检查内容质量 | P0 |
| daily_brief | 早报官 | 生成每日早报 | P2 |

### 待创建技能

| Skill | Agent | 用途 | 优先级 |
|-------|-------|------|--------|
| thesis_injection | 笔杆子 | 论点注入 | P0 |
| company_quote | 笔杆子 | 企业引用 | P0 |
| hotspot_filter | 参谋官 | 热点筛选 | P1 |
| platform_adapt | 运营官 | 平台适配 | P1 |
| error_learn | 进化官 | 错误学习 | P1 |
| portfolio_update | 知识官 | 企业更新 | P2 |

## Skill 模板

```markdown
# Skill: [技能名称]

> [所属 Agent] 技能

## 触发条件
[什么时候使用这个技能]

## 执行步骤
1. 步骤 1
2. 步骤 2
...

## 输出格式
[期望的输出结构]

## 注意事项
- 注意点 1
- 注意点 2

## 错误记录
| 日期 | 错误描述 | 修正规则 |
|------|----------|----------|
| (待记录) | - | - |
```

## 如何使用

### 导入到 OpenClaw

1. 打开 OpenClaw (元气AI)
2. 在对话中提及技能内容
3. OpenClaw 会自动学习并记录

示例对话:
```
你: 我要给你一个技能文件，请学习:

[粘贴 article_process.md 内容]

AI: 我已学习这个技能。以后处理文章时我会按这个流程执行。
```

### 更新技能

当发现 AI 执行不当时:

1. 分析问题原因
2. 更新对应的 Skill 文件
3. 在对话中告知 AI 更新内容

示例:
```
你: 关于 article_process 技能，我需要更新一点:
企业引用时，必须先验证企业是否还在被投列表中。

AI: 我已更新 article_process 技能，增加了这个规则。
```

## 最佳实践

### 1. 一次一个技能
不要一次性导入太多技能，让 AI 一个一个学习掌握。

### 2. 及时记录错误
每次 AI 犯错后，立即更新错误记录，形成闭环。

### 3. 保持简洁
Skill 文件不要太长，聚焦核心步骤。

### 4. 版本管理
重要更新后，更新文件底部的版本号。

## 相关文档

- [架构文档](../architecture/ARCHITECTURE.md)
- [论点框架](../knowledge/thesis-framework.md)
- [被投企业](../knowledge/portfolio.md)

---

*版本: v1.0 | 创建: 2026-03-01*
