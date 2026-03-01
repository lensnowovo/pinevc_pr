# Skill: Prompt Engineer

> Prompt 模板编写专家

## 触发条件

当用户要求：
- 编写新的 Prompt 模板
- 优化现有 Prompt
- 调试 Prompt 效果问题
- 设计多轮对话 Prompt

## 工作流程

### 1. 需求分析
- 明确 Prompt 的目标输出
- 识别需要的输入变量
- 确定输出格式

### 2. 结构设计

遵循以下 Prompt 结构：

```markdown
## 角色定义
[你是谁，你的职责]

## 背景知识
[年度核心论点、品牌规范等]

## 任务说明
[具体要做什么]

## 输入变量
- {{variable_1}}: 说明
- {{variable_2}}: 说明

## 输出格式
[期望的输出结构]

## 约束条件
- 约束 1
- 约束 2

## 示例 (Few-shot)
[输入 → 输出示例]
```

### 3. 质量检查

检查清单：
- [ ] 角色定义清晰
- [ ] 任务说明具体
- [ ] 输出格式明确
- [ ] 约束条件完整
- [ ] 包含示例

### 4. 版本管理

```
src/prompts/
├── article-generation-v1.md
├── article-generation-v2.md
└── ...
```

## 松禾 PR Prompt 规范

### 必须包含
1. 年度核心论点 (CDE+AI)
2. 被投企业引用要求
3. 品牌语调指南
4. 禁用词列表

### 禁止
- 生成虚假信息
- 过于绝对的表述
- 股价/市值预测

## 示例模板

参考: `src/prompts/article-generation-v1.md`

## 相关文档

- `docs/knowledge/thesis-framework.md` - 论点框架
- `docs/knowledge/portfolio.md` - 被投企业
