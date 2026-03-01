# Skill: Knowledge Manager

> 知识库管理专家

## 触发条件

当用户要求：
- 添加/更新被投企业信息
- 修改论点框架
- 维护品牌规范
- 整理往期内容

## 知识库结构

```
docs/knowledge/
├── thesis-framework.md   # 年度论点框架
├── portfolio.md          # 被投企业信息
└── prompts/              # Prompt 参考

src/config/
├── thesis-framework.yaml # 论点结构化数据
└── portfolio.yaml        # 企业结构化数据
```

## 更新规范

### 被投企业信息

添加新企业时需要：
1. 基本信息 (名称、简称、描述)
2. 论点标签 (Clinical/Discovery/Engineering/AI 的相关性)
3. 赛道标签
4. 当前阶段
5. 亮点 (用于引用)
6. 近期动态

更新频率：
- 每季度: 阶段、动态
- 重大事件: 及时更新
- 年度: 重新评估论点相关性

### 论点框架

年度论点框架变更需要：
1. 架构师审核
2. 创建 ADR 记录
3. 更新所有相关 Prompt

## 质量检查

- [ ] 信息准确性
- [ ] 简称一致性
- [ ] 标签合理性
- [ ] 无过时信息

## 相关文档

- `docs/knowledge/portfolio.md`
- `docs/knowledge/thesis-framework.md`
